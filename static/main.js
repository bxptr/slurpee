let query = document.getElementById("query");
let results_div = document.getElementById("results");

function show(results) {
    results_div.textContent = "";
    results.forEach((entry) => {
        console.log(entry);
        let link = document.createElement("a");
        let title = document.createElement("p");
        let time = document.createElement("span");
        title.innerHTML = entry.title;
        title.classList.add("title");
        time.innerHTML = entry.time;
        time.classList.add("time");
        link.appendChild(time);
        link.appendChild(title);
        link.href = entry.url;
        results_div.appendChild(link);
    });
}

query.addEventListener("input", () => {
    if (query.value != "") {
        fetch("/search", {
            method: "POST",
            headers: {"Content-Type": "application/json"}, 
            body: JSON.stringify({ query: query.value })
        })
        .then(results => results.json())
        .then(results => show(results));
    } else {
        show(all_results);
    }
});
