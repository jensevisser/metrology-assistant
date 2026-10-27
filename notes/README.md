# Lessen

- [00 — Het grote plaatje](00-het-grote-plaatje.md): wat we in Project 1 bouwen, wat RAG is, waarom we meten, en waar Sprint 0 past. Zonder code.
- [01a — Van vraag naar antwoord: tokens en token voor token](01a-tokens-en-genereren.md): wat een token is, de kansverdeling over het volgende token, waarom uitvoer trager is dan invoer.
- [01b — Wat het model ziet en wat het weet](01b-wat-het-model-ziet.md): chat template, geen geheugen tussen aanroepen, context window, knowledge cutoff.
- [02a — Je vraag naar Ollama en het antwoord terug](02a-vraag-en-antwoord-over-http.md): server en client, HTTP-verzoek en -antwoord met statuscode, JSON.
- [02b — Streaming, wachten en de koude start](02b-streaming-en-timeouts.md): waarom `stream: false`, wat een timeout is, en waarom de eerste vraag na een pauze traag is.
- [02c — Wat er mis kan gaan, en hoe `chat()` het meldt](02c-wat-er-mis-kan-gaan.md): de foutketen van vijf schakels, het eigen fouttype `LLMError`, de oorzaak bewaren en een foutmelding van onderen lezen.

# Code-rondleidingen en bouwuitleg

- [`src/llm_client.py` — deel A](code/llm_client-a.md): het bestand in vogelvlucht, logging, de ingang van `chat()` (standaardwaarden en `*`), het verzoek opbouwen (`x or y`) en versturen.
- [`src/llm_client.py` — deel B](code/llm_client-b.md): fouten opvangen (`try / except / finally`), en waar een fout naartoe gaat als niemand hem opvangt.
- [`src/llm_client.py` — deel C](code/llm_client-c.md): fouten gooien en vertalen (`raise`, het eigen fouttype `LLMError`, `raise ... from e`), en één gat in de foutafhandeling.
- [`src/llm_client.py` — deel D](code/llm_client-d.md): de stopwatch, de inhoud controleren, `ChatResult` met `@dataclass`, en `chat()` zelf draaien.

De voorbeelden uit de rondleidingen staan als losse bestanden in [`code/voorbeelden/`](code/voorbeelden/).

# Naslag

Spiekbriefjes om snel iets op te zoeken, één onderwerp per bestand.

- [Markdown](naslag/markdown-spiekbriefje.md): opmaak, code, lijsten, links, tabellen, en waarom iets er niet uitziet zoals bedoeld.
- [README](naslag/readme-checklist.md): wat een sterke README bevat.
- [Python](naslag/python-spiekbriefje.md): de Python-constructies uit dit project, met waar je ze tegenkomt. Groeit mee.
- [Python fouten](naslag/python-fouten-spiekbriefje.md): fouten opvangen, gooien en vertalen; de stamboom van fouten.
