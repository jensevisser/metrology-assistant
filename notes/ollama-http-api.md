# Ollama HTTP API en sampling

## Kern
Ollama is een server op `http://localhost:11434`; de CLI is ook maar een client.
Vanuit Python sturen we een POST naar `/api/chat` met model, messages en options, en krijgen één JSON terug (`stream: false`).
Het model kiest elk token door te trekken uit een kansverdeling; de samplingknoppen bepalen hoe.

## Begrippen
- **Token**: stukje woord; het model genereert er één per stap.
- **Sampling**: het trekken van het volgende token uit de kansverdeling.
- **`/api/chat`**: endpoint met `messages` (rollen `system`/`user`/`assistant`); basis voor RAG en tool calling.
- **`done_reason`**: `stop` = klaar, `length` = afgekapt door `num_predict`.
- **`eval_count`** / **`prompt_eval_count`**: tokens uit / in. Duren in nanoseconden.
- **Koude start**: eerste aanroep laadt het model in VRAM (traag).
- **httpx**: Python-library voor HTTP-verzoeken (`httpx.post(url, json=..., timeout=...)`); kan ook async. Standaard-timeout 5 s.

## Knoppen
| Knop | Effect | Laag ↔ hoog |
|---|---|---|
| temperature | verdeling scherper/platter | consistent ↔ gevarieerd/onzin |
| top_k | alleen k beste tokens | smal ↔ breed |
| top_p | kleinste groep met ≥ p kans | smal ↔ breed |
| seed | startwaarde toeval | zelfde seed = zelfde output (onder vaste condities) |
| num_predict | max. tokens uit | afgekapt ↔ lang/traag |
| timeout (httpx) | wachttijd client | vals alarm bij koude start ↔ hangt lang |

## Foutmodi
- `json.loads` faalt met "Extra data" → `stream` niet op `false` (NDJSON).
- `ReadTimeout` bij eerste aanroep → koude start, timeout te kort.
- Half antwoord → `num_predict` te laag; check `done_reason == "length"`.
- Leeg antwoord → denkstap at het tokenbudget op (`think`).
- Andere output ondanks zelfde seed → ander model/versie/hardware/instelling.

## Voorbeeld
`{"model": "qwen3.5:4b", "messages": [...], "stream": false, "options": {"temperature": 0.2, "seed": 42, "num_predict": 512}}`
Misgaat: `num_predict: 30` zonder `stream: false` → stroom regels, afgekapt antwoord.

## Analogie
Seed = Monte Carlo (GUM-S1) met vaste seed: reproduceerbaar.
Temperature = spreiding van herhaalmetingen: laag = hoge herhaalbaarheid.
Houdt op: herhaalbaar ≠ juist. Een LLM op temperature 0 is consequent fout zoals een meter met een systematische afwijking, maar die "afwijking" verschilt per vraag en is niet te corrigeren met een offset.
