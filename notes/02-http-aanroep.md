# Les 02 — Een LLM aanroepen over HTTP

## 1. Wat je al weet

Les 01 (`01-llm-aanroep.md`) liet zien wat er bínnen het model gebeurt bij één aanroep. Deze les gaat over het transport ernaartoe: hoe je Python-programma de vraag bij Ollama krijgt en het antwoord terug. `requests` heb je eerder gezien; `httpx` werkt bijna hetzelfde. De code waar deze les over gaat, staat al in `src/llm_client.py`.

## 2. Het probleem

In de CLI typ je een vraag en lees je het antwoord. Dat werkt voor één vraag, maar niet voor vijftig vragen met vaste instellingen waarvan je alles wilt vastleggen. Daarvoor moet je programma zelf met Ollama praten.

En als dat misgaat, wil je weten wáár. Draait de server niet? Bestaat het model niet? Duurt het te lang? Of klopt het antwoordformaat niet? Zonder kennis van de transportlaag zie je bij elke fout dezelfde muur van traceback-regels, en zoek je op de verkeerde plek.

## 3. Het idee in het kort

Ollama is een **server**: een programma dat op de achtergrond draait en luistert op poort 11434 van je eigen machine. Jouw Python-programma is de **client**. Die stuurt een **HTTP-verzoek** met de vraag als **JSON**, en krijgt een **HTTP-antwoord** terug, ook met JSON. Elke schakel in die keten kan op een eigen manier falen, en een goede client vertaalt elke fout naar een melding die zegt wat er mis is.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Client en server

- **Server:** Ollama, draait op de achtergrond. Ook het `ollama`-commando is een client van die server.
- **Adres:** `http://localhost:11434`. `localhost` betekent "deze machine", `11434` is het **poortnummer**: het "deurtje" waarachter Ollama luistert. Andere programma's luisteren op andere poorten.
- **Endpoint:** het pad achter het adres bepaalt wat je vraagt. `/api/chat` is "beantwoord dit gesprek", `/api/tags` is "welke modellen heb je", `/api/version` is "welke versie ben je".

### Stap 2 — Het verzoek (request)

Een HTTP-verzoek bestaat uit vier delen:

| Deel | Bij ons | Betekenis |
|---|---|---|
| **Methode** | `POST` | "ik stuur je gegevens" (`GET` = "geef me iets", zonder inhoud) |
| **URL** | `http://localhost:11434/api/chat` | adres + endpoint |
| **Headers** | `Content-Type: application/json` | etiketten over de inhoud |
| **Body** | de JSON met model, messages, options | de eigenlijke vraag |

Zelf proberen kan zonder Python, met `curl`:

```bash
curl -s -i http://localhost:11434/api/chat -d '{"model":"qwen3.5:9b","messages":[{"role":"user","content":"Zeg alleen: hallo"}],"stream":false,"think":false,"options":{"seed":42,"temperature":0.2}}'
```

`-d` zet de body en maakt er automatisch een `POST` van; `-i` laat ook de headers van het antwoord zien.

### Stap 3 — Het antwoord (response)

Echte uitvoer van het commando hierboven (14 oktober 2026):

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 323

{"model":"qwen3.5:9b","created_at":"2026-10-14T19:05:44.849813077Z",
 "message":{"role":"assistant","content":"hallo"},
 "done":true,"done_reason":"stop",
 "total_duration":88002519,"load_duration":529552,
 "prompt_eval_count":18,"prompt_eval_cached_count":0,"prompt_eval_duration":34645000,
 "eval_count":3,"eval_duration":22585000}
```

(De JSON staat in werkelijkheid op één regel; hier afgebroken voor de leesbaarheid.)

- **Statusregel:** `200 OK`. De **statuscode** zegt in één getal hoe het ging:
  - `2xx`: gelukt.
  - `4xx`: fout aan **jouw** kant. Bijvoorbeeld `404 Not Found` (model bestaat niet) of `400 Bad Request` (kapotte JSON).
  - `5xx`: fout aan de **serverkant**. Bijvoorbeeld een model dat niet in het geheugen past.
- **Headers:** de inhoud is JSON, 323 bytes.
- **Body:** het antwoord plus de meetgegevens uit les 01. Duren in **nanoseconden**: `total_duration` 88 002 519 ns = 0,088 s. `load_duration` is hier maar 0,5 ms, omdat het model al in de VRAM zat (warme start).

### Stap 4 — JSON en Python

JSON is een tekstformaat voor gestructureerde gegevens. Het lijkt sterk op Python:

| JSON | Python |
|---|---|
| `{"a": 1}` (object) | `dict` |
| `[1, 2]` (array) | `list` |
| `"tekst"` | `str` |
| `42`, `0.2` | `int`, `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

`httpx` doet de omzetting voor je:
- `httpx.post(url, json=payload)` zet je dict om naar JSON-tekst (`json.dumps`) en zet de header `Content-Type` goed.
- `response.json()` zet de JSON-tekst van het antwoord terug om naar een dict (`json.loads`).

Daarna is het gewoon Python: `data["message"]["content"]` geeft `"hallo"`.

### Stap 5 — Streaming

Standaard (`"stream": true`) stuurt Ollama het antwoord **token voor token** terug, elk als een losse regel JSON. Echte uitvoer van hetzelfde verzoek, nu zonder `"stream": false`:

```
{"model":"qwen3.5:9b",...,"message":{"role":"assistant","content":"hal"},"done":false}
{"model":"qwen3.5:9b",...,"message":{"role":"assistant","content":"lo"},"done":false}
{"model":"qwen3.5:9b",...,"message":{"role":"assistant","content":""},"done":true,"done_reason":"stop",...,"eval_count":3,...}
```

Hier zie je les 01 letterlijk gebeuren: `hallo` is twee tokens (`hal`, `lo`), en de laatste regel is het stop-token met de statistieken. Drie tokens, dus `eval_count: 3`.

Dit formaat heet **NDJSON** (newline-delimited JSON): meerdere JSON-objecten, één per regel. Het geheel is dus **geen** geldig JSON-document. `response.json()` faalt erop.

Waarom streaming bestaat: in een chat-app zie je de eerste woorden na een fractie van een seconde, in plaats van te wachten op het hele antwoord. Wij verwerken de antwoorden in een script en loggen ze, dus kiezen we `"stream": false`: één compleet JSON-object.

### Stap 6 — Timeouts

Een **timeout** is hoe lang de client maximaal wacht voordat hij opgeeft. Zonder timeout kan een script eeuwig blijven hangen.

- `httpx` heeft standaard een timeout van **5 seconden**.
- Een koude start van het 9b-model kostte in les 01 al **3,75 s** laden. Daar komt de tijd voor het antwoord nog bij.
- Bij ongeveer 105 tokens/s (les 01) kost een antwoord van 1000 tokens zo'n 10 s. Een groter model, of een model dat niet helemaal op de GPU past, kan vele malen trager zijn.

Daarom gebruikt `chat()` standaard **120 seconden**. De afweging:
- **te kort** geeft vals alarm bij een gezonde maar trage aanroep;
- **te lang** betekent dat je bij een echt probleem lang wacht voordat je het merkt.

### Stap 7 — Foutafhandeling: elke schakel zijn eigen melding

De keten heeft vijf schakels, en `chat()` vangt elk falen apart af en vertaalt het naar één eigen fouttype, `LLMError`:

| Schakel | Wat gaat mis | `httpx`-fout | Melding van `chat()` |
|---|---|---|---|
| 1. Verbinding | server draait niet, verkeerde poort | `ConnectError` | "Geen verbinding met Ollama op …; draait de server?" |
| 2. Wachten | koude start, te lang antwoord | `TimeoutException` | "Timeout na … s (koude start? model te groot?)" |
| 3. Status | model bestaat niet, kapot verzoek | `HTTPStatusError` (via `raise_for_status()`) | "HTTP 404: …" met de tekst van de server |
| 4. Formaat | geen geldige JSON (bijv. streaming aan) | `ValueError` | "Antwoord is geen geldige JSON (stream per ongeluk aan?)" |
| 5. Inhoud | geldige JSON, maar geen `message.content` | (eigen controle) | "Onverwacht antwoord, geen message.content: …" |

Echte uitvoer voor schakel 3 en 1:

```
LLMError -> HTTP 404: {"error":"model 'bestaatniet' not found"} | oorzaak: HTTPStatusError
LLMError -> Geen verbinding met Ollama op http://localhost:11999; draait de server? | oorzaak: ConnectError
```

Vier Python-constructies in `chat()` die nieuw kunnen zijn:

- **`raise LLMError(...) from e`**: gooit onze eigen fout, maar bewaart de originele `httpx`-fout als oorzaak (`e.__cause__`). Bovenaan staat de leesbare melding, en wie dieper wil debuggen, ziet ook de originele fout. Dat is de "oorzaak: ..." in de uitvoer hierboven.
- **`try / except / finally`**: `finally` draait altijd, ook als er een fout optrad. Daar sluiten we de verbinding (`http.close()`), zodat er niets blijft openstaan.
- **De `*` in de functiedefinitie**: alles ná de `*` moet je bij naam meegeven, dus `chat(..., timeout=30)` en niet als zoveelste losse waarde. Dat voorkomt verwisselingen en maakt een aanroep leesbaar.
- **`client or httpx.Client(...)`**: geef je zelf een client mee (in tests een nep-server), dan gebruikt `chat()` die. Anders maakt hij er zelf een.

## 5. Knoppen en keuzes

- **`stream`**: `true` voor een chat-UI (eerste woorden snel zichtbaar), `false` voor scripts en logging. Wij kiezen `false`.
- **`timeout`**: 120 s als standaard. Voor snelle tests met het 4b-model mag het korter; voor grote modellen of lange antwoorden langer.
- **Endpoint**: `/api/chat` (messages met rollen) in plaats van `/api/generate` (één losse prompt). Chat is de basis voor RAG en tool calling. In les 05 komt `/v1/chat/completions`, de OpenAI-compatibele variant waarmee we later ook vLLM aanspreken.
- **`base_url`**: instelbaar, zodat dezelfde code tegen een andere machine of poort kan.
- **Een nieuwe verbinding per aanroep of hergebruik**: `chat()` opent en sluit nu per aanroep een verbinding. Voor vijf of vijftig vragen maakt dat niets uit. Bij duizenden aanroepen of gelijktijdige verzoeken (Project 3) hergebruik je één client.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| `json.decoder.JSONDecodeError: Extra data: line 2 column 1` | `stream` niet op `false`: NDJSON, meerdere JSON-objecten |
| `ReadTimeout` bij de eerste aanroep, daarna niet | koude start langer dan de timeout |
| `ConnectError` / "Connection refused" | Ollama draait niet (bijv. na een herstart), of verkeerde poort |
| `404` met "model … not found" | typfout in de modelnaam, of model niet gepulld (`ollama list`) |
| Script hangt minutenlang zonder melding | geen timeout gezet (bijv. bij `requests`, dat standaard eeuwig wacht) |
| Fout verdwijnt "vanzelf", maar resultaten missen | te brede foutafvang (`except Exception: pass`) slikt fouten in |

**Uitgewerkt voorbeeld.** Iemand schrijft snel, zonder onze client:

```python
r = httpx.post("http://localhost:11434/api/chat",
               json={"model": "qwen3.5:9b", "messages": [{"role": "user", "content": "hoi"}]})
print(r.json())
```

Dit gaat drie keer mis:
1. `stream` staat niet op `false`, dus `r.json()` faalt met *Extra data*: Ollama stuurde NDJSON.
2. Na het toevoegen van `"stream": False` werkt het, totdat het model koud is. De standaard-timeout van 5 s is dan krap, met wisselend succes.
3. `think` staat niet uit, en bij dit model staat thinking standaard aan (les 01). Het antwoord duurt langer en kost meer tokens.

`chat()` vangt alle drie af.

## 7. Analogie

Heb je ooit een instrument via GPIB of LAN met **SCPI**-commando's aangestuurd (bijvoorbeeld vanuit een calibratieprocedure)? Dan ken je dit patroon al:

| SCPI / VISA | HTTP / Ollama |
|---|---|
| instrumentadres (`GPIB0::22::INSTR`) | `localhost:11434` |
| commando (`MEAS:VOLT:DC?`) | endpoint + JSON-body |
| meetwaarde terug | JSON-antwoord |
| foutcode uit de error queue (`-113, "Undefined header"`) | statuscode (`404`, `400`) |
| VISA-timeout bij een lange integratietijd | `ReadTimeout` bij een koude start |
| buffer per meting uitlezen vs. losse waarden terwijl ze binnenkomen | `stream: false` vs. `stream: true` |

**Waar de vergelijking ophoudt:**
- Een instrument onthoudt instellingen tussen commando's (`CONF`, daarna `READ?`). `/api/chat` onthoudt níets: elk verzoek bevat alles (les 01, stap 6).
- SCPI-syntaxis verschilt per instrument. HTTP en JSON zijn één wereldwijde standaard die elke webdienst gebruikt.

## 8. Samenvatting

**Kern:** Ollama is een server op `localhost:11434`. Python stuurt een `POST` met JSON naar `/api/chat` en krijgt JSON terug. Met `stream: false` is dat één compleet object; anders NDJSON, één regel per token. Elke schakel (verbinding, wachten, status, formaat, inhoud) kan falen, en `chat()` vertaalt elk falen naar een duidelijke `LLMError`.

**Begrippen:**
- **Server / client**: wie luistert en wie vraagt.
- **Poort**: het nummer waarop een server luistert.
- **Endpoint**: het pad dat bepaalt wat je vraagt.
- **Methode** (`GET`/`POST`), **headers**, **body**: de delen van een verzoek.
- **Statuscode**: `2xx` gelukt, `4xx` jouw fout, `5xx` serverfout.
- **JSON**: tekstformaat voor gegevens, vertaalt één-op-één naar dicts en lists.
- **NDJSON**: één JSON-object per regel; zo ziet streaming eruit.
- **Timeout**: maximale wachttijd van de client.
- **Exception chaining** (`raise ... from e`): eigen fout met de originele als oorzaak.

**Knoppen:** `stream` · `timeout` · endpoint · `base_url` · verbinding hergebruiken.

**Foutmodi:** *Extra data* door streaming · timeout bij koude start · geen verbinding · 404 door een verkeerde modelnaam · hangen zonder timeout · fouten die worden ingeslikt.

## 9. Wat we hiermee gaan bouwen

De tabel in stap 7 is meteen ons testplan. In de volgende bouwstap schrijven we `tests/test_llm_client.py`: met een **nep-server** (`httpx.MockTransport`) laten we elke schakel bewust falen en controleren we dat `chat()` de juiste `LLMError` geeft. Ook het geslaagde pad en `done_reason: "length"` testen we. Dat werkt zonder dat Ollama draait, zodat de tests later ook in CI kunnen draaien (Project 3).
