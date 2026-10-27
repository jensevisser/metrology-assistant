# VOORTGANG
Datum:          2026-10-27
Waar ben ik:    Project 1 · Sprint 0 (Een LLM aanroepen en meten) · lessen 00–02c gelezen · rondleiding `src/llm_client.py`: deel A gelezen, B–D geschreven maar nog te lezen · bouwplan stap 1 van 7 (code staat, nog niet zelf gedraaid)
Wat werkt:      repo op GitHub (`vllm-docs-assistant`, branch `sprint-0-ollama-api`, SSH) ·
                `chat()` praat met Ollama via `/api/chat`, geeft een `ChatResult` terug en vertaalt fouten naar `LLMError` (door Claude gedraaid: 200 OK, 404, geen verbinding, timeout) ·
                lessen in `notes/`, rondleidingen in `notes/code/`, voorbeelden in `notes/code/voorbeelden/`, spiekbriefjes in `notes/naslag/`
Open / wankel:  `raise` en `from e` bleven nog niet goed plakken (uitleg herschreven in rondleiding deel C) ·
                gat in `chat()`: `ReadError` en `RemoteProtocolError` worden niet opgevangen (dichten in bouwstap 2) ·
                vacaturecheck bij de start van Project 1 nog niet gedaan (natuurlijk moment: na Sprint 0) ·
                lokale map heet nog `metrology-assistant`
Besluiten:      domein = officiële vLLM-documentatie, vastgezet op één release-tag ·
                model `qwen3.5:9b` (`4b` voor snel testen); `think: false` meesturen, want thinking staat bij dit model standaard aan ·
                `httpx` raw-first; in Sprint 0 Ollama's eigen API, aan het eind ook `/v1/chat/completions`, beide via `ChatResult` ·
                vLLM vanaf Sprint 2, na de dunne RAG ·
                lestempo zoals les 00: hooguit 3–4 nieuwe begrippen per deel; uitleg van bouwstappen in `notes/code/`, niet in de chat ·
                geen `Co-Authored-By` in commits
Volgende stap:  rondleiding deel B, C en D lezen → `chat()` zelf draaien (deel D, sectie 6) → bouwstap 2.
                Bouwplan Sprint 0:
                1. `ChatResult` in `chat()` (code staat; zelf draaien)
                2. `tests/test_llm_client.py`: nep-server (`httpx.MockTransport`) voor de vijf schakels uit les 02c, plus vangnet `except httpx.TransportError`
                3. `eval/baseline.jsonl`: 5 vragen over de vLLM-docs (vaste release-tag), met referentieantwoord en bron
                4. `src/run_baseline.py`: de meetlat; alle knoppen expliciet; resultaten naar `data/runs/` (keuze `.json` of `.jsonl` in les 04)
                5. baseline draaien en beoordelen in `eval/results.md`, plus één sampling-experiment; controlepunt: kent het model vLLM al te goed?
                6. tweede route via `/v1/chat/completions` die hetzelfde `ChatResult` vult; backend via config
                7. afronden: VOORTGANG, README, pull request naar `main`
                Lessen die nog komen: 03 samplingknoppen (vóór stap 3–5) · 04 meten met een vaste promptset · 05 de OpenAI-compatibele API (vóór stap 6)
