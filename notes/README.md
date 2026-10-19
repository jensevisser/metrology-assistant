# Lessen

0. [00 — Het grote plaatje](00-het-grote-plaatje.md): wat we in Project 1 bouwen, wat RAG is, waarom we meten, en waar Sprint 0 past. Zonder code.
1. [01a — Van vraag naar antwoord: tokens en token voor token](01a-tokens-en-genereren.md): wat een token is, de kansverdeling over het volgende token, waarom uitvoer trager is dan invoer.
1. [01b — Wat het model ziet en wat het weet](01b-wat-het-model-ziet.md): chat template, geen geheugen tussen aanroepen, context window, knowledge cutoff.
2. [02a — Je vraag naar Ollama en het antwoord terug](02a-vraag-en-antwoord-over-http.md): server en client, HTTP-verzoek en -antwoord met statuscode, JSON.
2. [02b — Streaming, wachten en de koude start](02b-streaming-en-timeouts.md): waarom `stream: false`, wat een timeout is, en waarom de eerste vraag na een pauze traag is.
2. [02 — Een LLM aanroepen over HTTP](02-http-aanroep.md): client/server, verzoek en antwoord, JSON, streaming (NDJSON), timeouts, foutafhandeling in `chat()`. *(wordt herschreven als 02a, 02b en 02c)*
