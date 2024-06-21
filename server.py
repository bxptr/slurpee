import flask

import numpy as np
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold

import json
import pickle

import requests
import bs4
import datetime

with open("credentials.json") as handler: key = json.load(handler)["key"]

safety = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
}
llm = ChatGoogleGenerativeAI(model = "gemini-pro", google_api_key = key, safety_settings = safety)
prompt = "Below is some text taken from \"[TITLE]\". Your job is to summarize it in a paragraph. \n\n[CONTENT]."
title_prompt = "Below is some text taken from a webpage. You job is to generate a short title for it. \n\n[CONTENT]."

embd_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
try:
    with open("index.bin", "rb") as handler:
        index = pickle.load(handler)
except FileNotFoundError:
    print("file not found, starting from blank")
    index = []

app = flask.Flask("slurpee")

def scrape(url: str) -> tuple:
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, features = "html.parser")
    content = " ".join([p.text for p in soup.find_all("p")])
    title = None
    try:
        title = soup.find("meta", property = "og:title")
        title = title["content"]
        if not title:
            title = soup.find("title")
            title = title.string
    except:
        pass
    if not title: # final
        p = title_prompt.replace("[CONTENT]", content)
        title = llm.invoke(p)
        title = title.content
    return (title, content, url)

def summarize(title: str, content: str, url: str) -> None:
    titles = [entry["title"] for entry in index]
    if title in titles:
        return None
    p = prompt.replace("[TITLE]", title).replace("[CONTENT]", content)
    summary = llm.invoke(p)
    summary = summary.content
    vector = embd_model.encode(title + " " + content).flatten()
    index.append({
        "title": title,
        "url": url,
        "summary": summary,
        "vector": vector,
        "time": str(datetime.datetime.now().strftime("%m.%d.%y"))
    })

cosine = lambda x: np.dot(x[0], x[1]) / (np.linalg.norm(x[0]) * np.linalg.norm(x[1])) if (np.linalg.norm(x[0]) != 0 and np.linalg.norm(x[1]) != 0) else 0
def search(query: str) -> list:
    vector = embd_model.encode(query).flatten()
    scores = {
        i: cosine((entry["vector"], vector))
        for i, entry in enumerate(index)
    }
    idx = sorted(scores, key = scores.get, reverse = True) 
    results = []
    for i in idx:
        res = index[i].copy()
        res.pop("vector")
        results.append(res)
    return results


@app.route("/")
def route_index() -> object:
    clean = []
    for i in index:
        i = i.copy()
        i.pop("vector")
        clean.append(i)
    clean = reversed(clean)
    response = flask.make_response(flask.render_template("index.html", index = clean))
    # don't cache
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/search", methods = ["POST"])
def route_search() -> str:
    data = flask.request.get_json(force = True) # idc for mimetype
    return search(data["query"])

@app.route("/new", methods = ["POST"])
def route_new() -> str:
    data = flask.request.get_json(force = True)
    url = data["url"]
    result = scrape(url)
    summarize(*result)
    with open("index.bin", "wb") as handler:
        pickle.dump(index, handler)
    return "done"

if __name__ == "__main__":
    app.run(debug = True, port = 4000)
