# slurpee
personal AI-powered link management system

i used to have ~200 open tabs on my phone, where i do most of my reading and browsing. i finally realized this was an issue when safari began to lag when i went to search for certain tabs, which in of itself was hell.

this project was made an a day of work, so expect it to be sloppy. it works by accepting links over a [shortcut i made](https://www.icloud.com/shortcuts/4bdfcd0281e942a097b096cc4f489a2e) and favorited in safari. it then scrapes the site for content and uses gemini 1.0 pro to generate a paragraph summary, which then is put into a faiss vector database with `sentence-transformers/all-MiniLM-L6-v2`.

the summary isn't shown to the user, which i might change later, but allows efficient and accurate semantic search over site content. this way, i have a streamlined method to save things i find interesting and search over the content. without search, it shows the most recent links at the top and serves as a nice time capsule of sorts.

this system is mainly for myself and put here for those interested. adapting it to your own workflow shouldn't be that bad because the "codebase" is effectively one file.
