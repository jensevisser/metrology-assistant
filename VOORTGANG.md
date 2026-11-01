# VOORTGANG
Datum:          2026-11-01
Waar ben ik:    Project 1 · Sprint 0 (Een LLM aanroepen en meten) · lessen 00–02c gelezen · rondleiding `src/llm_client.py`: deel A gelezen, B–D nog te lezen (bij deel D sectie 3) · bouwplan stap 1 van 7 (code staat, nog niet zelf gedraaid)
Wat werkt:      repo op GitHub (`vllm-docs-assistant`, branch `sprint-0-ollama-api`, SSH) ·
                `chat()` praat met Ollama via `/api/chat`, geeft een `ChatResult` terug en vertaalt fouten naar `LLMError` (door Claude gedraaid: 200 OK, 404, geen verbinding, timeout) ·
                lessen in `notes/`, rondleidingen in `notes/code/`, zijpaden en voorbeelden in `notes/code/`, spiekbriefjes in `notes/naslag/` ·
                FM-001 vastgelegd: Ollama kort een te lange prompt stil in (gemeten: 6968 tokens → 2050 bij `num_ctx` 4096, met 200 OK)
Open / wankel:  `raise` en `from e` bleven nog niet goed plakken (mogelijke oorzaak gevonden: les 02c had de leesvolgorde van een foutmelding omgekeerd; gecorrigeerd) ·
                vier bevindingen voor bouwstap 2, zelf gereproduceerd: `AttributeError` als het antwoord een lijst is · `except ValueError` staat te ruim om `http.post` · `httpx.RequestError` is beter dan `TransportError` (vangt ook `DecodingError`) · de waarschuwing bij `done_reason=length` noemt altijd `num_predict`, maar een vol venster geeft hetzelfde ·
                pytest vindt `src` niet; `pythonpath = ["."]` in `pyproject.toml` nodig (gereproduceerd) ·
                `/v1` negeert bij Ollama `truncate`, `num_ctx` en `think: false`; dat raakt het besluit "één aanroep-interface" (§6). Besluit bij les 05, vóór bouwstap 6 ·
                vacaturecheck bij de start van Project 1 nog niet gedaan (natuurlijk moment: na Sprint 0)
Besluiten:      domein = officiële vLLM-documentatie, vastgezet op één release-tag ·
                model `qwen3.5:9b` (`4b` voor snel testen); `think: false` meesturen, want thinking staat bij dit model standaard aan ·
                `httpx` raw-first; in Sprint 0 Ollama's eigen API, aan het eind ook `/v1/chat/completions`, beide via `ChatResult` ·
                `"truncate": false` meesturen naar `/api/chat`, zodat stil inkorten een luide 400 wordt (FM-001) ·
                vLLM vanaf Sprint 2, na de dunne RAG ·
                lestempo zoals les 00: hooguit 3–4 nieuwe begrippen per deel; uitleg van bouwstappen in `notes/code/`, niet in de chat ·
                bij elke bouwstap biedt Claude een stuk aan dat ik zelf kan schrijven, nadat hij het mechanisme één keer heeft voorgedaan; ik beslis per keer (CLAUDE.md §4) ·
                Azure (Project 3) en LangGraph (Project 2) blijven open; besluit na de vacaturecheck eind Project 2 ·
                geen `Co-Authored-By` in commits
Volgende stap:  rondleiding deel B, C en D lezen → `chat()` zelf draaien (deel D, sectie 6) → bouwstap 2.
                Bouwplan Sprint 0:
                1. `ChatResult` in `chat()` (code staat; zelf draaien)
                2. `tests/test_llm_client.py`: nep-server (`httpx.MockTransport`) voor de vijf schakels uit les 02c; plus `pythonpath` en de vier bevindingen hierboven. Claude doet de eerste test voor en biedt de volgende aan
                3. `eval/baseline.jsonl`: 5 vragen over de vLLM-docs (vaste release-tag), met referentieantwoord en bron
                4. `src/run_baseline.py`: de meetlat; alle knoppen expliciet; resultaten naar `data/runs/` (keuze `.json` of `.jsonl` in les 04). Ollama-versie, model-ID en git-commit per run vastleggen, want dezelfde seed gaf op 25 oktober 53 en op 1 november 43 tokens
                5. baseline draaien en beoordelen in `eval/results.md`, plus één sampling-experiment; controlepunt: kent het model vLLM al te goed?
                6. tweede route via `/v1/chat/completions` die hetzelfde `ChatResult` vult; backend via config
                7. afronden: VOORTGANG, README (titel klopt nog niet op `main`), pull request naar `main`
                Lessen die nog komen: 03 samplingknoppen (vóór stap 3–5) · 04 meten met een vaste promptset, inclusief meetonzekerheid bij scores (±12 punten bij 40 vragen en 80%) · 05 de OpenAI-compatibele API (vóór stap 6)
