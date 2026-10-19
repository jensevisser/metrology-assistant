# Les 02a — Je vraag naar Ollama en het antwoord terug

## 1. Inleiding

**Waar we zijn:** één plek naar links op de kaart. In les 01a en 01b keken we ín het model. Nu kijken we naar de pijlen tussen jouw Python-code en Ollama.

```
  5 vragen ──▶ meetlat ──▶ chat() ══▶ Ollama ──▶ model
                                  ◀══
                            deze les: de dubbele pijlen
```

**Wat je al weet:** wat het model doet met een vraag (`01a-tokens-en-genereren.md`) en wat het daarbij ziet (`01b-wat-het-model-ziet.md`). Je hebt Ollama via de CLI gebruikt, en de Python-library `requests` eerder gezien.

**Waarom dit nu:** de meetlat moet vijf vragen automatisch kunnen stellen, met vaste instellingen, en alles kunnen vastleggen. Typen in de CLI kan dat niet. Daarvoor moet je programma zelf met Ollama praten. Hoe dat gesprek eruitziet, is deze les.

**Na deze les kun je:**
- uitleggen wat een server en een client zijn, en waar Ollama luistert;
- met één commando zelf een vraag naar Ollama sturen en het antwoord lezen;
- de onderdelen van een verzoek en een antwoord aanwijzen, inclusief de statuscode;
- JSON lezen en uitleggen hoe het in Python een dict wordt.

**Nieuwe begrippen (3):** server en client · HTTP-verzoek en HTTP-antwoord · JSON.

## 2. Het probleem

In de CLI typ je `ollama run qwen3.5:9b`, stel je een vraag en lees je het antwoord op je scherm. Voor de meetlat werkt dat niet:
- je wilt vijf (later vijftig) vragen achter elkaar stellen zonder te typen;
- je wilt bij elke vraag precies dezelfde instellingen;
- je wilt het antwoord én de meetgegevens (tokens, tijden, `done_reason`) in een bestand opslaan.

Daarvoor moet een programma de vraag stellen, niet jij. Maar hoe "praat" een Python-programma met een ander programma dat op je computer draait?

## 3. Het idee in het kort

Ollama draait op de achtergrond als **server**: een programma dat wacht tot iemand iets vraagt. Jouw Python-programma is de **client**: het stelt de vraag. Ze praten met elkaar in een afgesproken taal, HTTP, dezelfde taal waarmee je browser met websites praat. De client stuurt een **verzoek**, de server stuurt een **antwoord**. De inhoud van beide, de vraag en het antwoord, is opgeschreven in **JSON**: een eenvoudig tekstformaat dat Python één-op-één kan omzetten naar een dict.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Server en client

Een **server** is een programma dat wacht op vragen en ze beantwoordt. Een **client** is een programma dat vragen stelt. Dat zegt niets over hoe groot of krachtig ze zijn; het gaat alleen om de rol.

- Ollama is de server. Het start op de achtergrond en blijft draaien, ook als je geen vraag stelt.
- Het `ollama`-commando in je terminal is een client. Als je `ollama run` typt, stuurt het commando zelf een vraag naar de server.
- Onze `chat()`-functie in Python wordt ook een client, net als `ollama run`, maar dan aangestuurd door code in plaats van door jou.

Om de server te vinden, heeft de client een **adres** nodig. Voor Ollama is dat `http://localhost:11434`:
- `localhost` betekent "deze computer". De server draait op je eigen machine.
- `11434` is het **poortnummer**. Op één computer kunnen veel servers tegelijk draaien; elk luistert op zijn eigen nummer. Ollama luistert standaard op 11434.

Achter het adres komt nog een pad, dat zegt wát je wilt. Zo'n pad heet een **endpoint**:

| Endpoint | Betekenis |
|---|---|
| `/api/chat` | "beantwoord dit gesprek" |
| `/api/tags` | "welke modellen heb je?" |
| `/api/version` | "welke versie ben je?" |

### Stap 2 — Het verzoek

De client stuurt een **HTTP-verzoek**. Dat bestaat uit vier delen. Ze staan hier met hun waarde voor onze vraag:

| Deel | Bij ons | Betekenis |
|---|---|---|
| **methode** | `POST` | "ik stuur je gegevens mee" (`GET` zou betekenen: "geef me iets", zonder gegevens) |
| **adres + endpoint** | `http://localhost:11434/api/chat` | naar wie en waarvoor |
| **headers** | `Content-Type: application/json` | etiketten: "de inhoud is JSON" |
| **body** | het model, de berichten, de instellingen | de eigenlijke vraag |

Je kunt dit zelf proberen zonder Python, met het programma `curl`. Dat stuurt een HTTP-verzoek vanaf de commandoregel:

```bash
curl -s -i http://localhost:11434/api/chat -d '{"model":"qwen3.5:9b","messages":[{"role":"user","content":"Zeg alleen: hallo"}],"stream":false,"think":false,"options":{"seed":42,"temperature":0.2}}'
```

- `-d '...'` geeft de body mee, en maakt er automatisch een `POST` van;
- `-i` laat ook de kop van het antwoord zien, niet alleen de inhoud;
- `-s` houdt `curl` zelf stil (geen voortgangsbalk).

`"stream":false` en `"think":false` laten we nu even voor wat ze zijn. Die komen in les 02b en 03.

### Stap 3 — Het antwoord

De server stuurt een **HTTP-antwoord** terug. Dit kwam er echt terug op het commando hierboven (14 oktober 2026):

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 323

{"model":"qwen3.5:9b","created_at":"2026-10-14T19:05:44.849813077Z","message":{"role":"assistant","content":"hallo"},"done":true,"done_reason":"stop","total_duration":88002519,"load_duration":529552,"prompt_eval_count":18,"prompt_eval_cached_count":0,"prompt_eval_duration":34645000,"eval_count":3,"eval_duration":22585000}
```

Het antwoord heeft drie delen:

**1. De statusregel: `200 OK`.** Het getal heet de **statuscode** en zegt in één keer hoe het ging. Het eerste cijfer is het belangrijkst:

| Begint met | Betekenis | Voorbeeld |
|---|---|---|
| 2 | gelukt | `200 OK` |
| 4 | fout aan **jouw** kant | `404 Not Found`: het model bestaat niet |
| 5 | fout aan de **serverkant** | `500`: er ging iets mis in Ollama zelf |

**2. De headers:** etiketten over het antwoord, hier "de inhoud is JSON, 323 tekens lang".

**3. De body:** het eigenlijke antwoord. Daarin vind je terug wat je uit les 01a kent:
- `"content":"hallo"`: het antwoord zelf;
- `"done_reason":"stop"`: het model was klaar, niet afgekapt;
- `"eval_count":3`: drie tokens uit (`hal`, `lo`, het klaar-token);
- `"prompt_eval_count":18`: 18 tokens in, de vraag plus de markeringen van het chat template (les 01b).

De tijden staan in **nanoseconden**: miljardsten van een seconde. `"total_duration":88002519` is dus 0,088 seconde. Dat is zo snel, omdat het model al in het videogeheugen zat. Bij de eerste aanroep van de dag duurt het langer.

### Stap 4 — JSON: de taal van de inhoud

Zowel de body van het verzoek als die van het antwoord is **JSON**. JSON is een tekstformaat om gegevens met structuur op te schrijven: namen met waarden, lijstjes, en lijstjes binnen lijstjes. Het lijkt sterk op hoe je in Python een dict of list opschrijft:

| JSON | Python | Voorbeeld |
|---|---|---|
| `{ ... }` (object) | `dict` | `{"role": "user"}` |
| `[ ... ]` (array) | `list` | `[1, 2, 3]` |
| `"tekst"` | `str` | `"hallo"` |
| `42`, `0.2` | `int`, `float` | `3` |
| `true` / `false` | `True` / `False` | `true` |
| `null` | `None` | `null` |

Twee verschillen om op te letten: JSON schrijft `true`, `false` en `null` met kleine letters, en tekst staat altijd tussen dubbele aanhalingstekens.

**Let op het woord "object".** Een *JSON-object* is alleen tekst in de vorm `{"naam": waarde}`, zonder gedrag of methodes. De naam komt van *JavaScript Object Notation*. In Python heet hetzelfde een dict. Een *Python-object* is iets anders: een waarde die in je programma leeft, met een type en vaak met methodes. Het `response` hieronder is zo'n Python-object, en `response.json()` vertaalt de JSON-tekst naar een Python-dict.

Waarom JSON? Omdat elke programmeertaal het kan lezen en schrijven. Ollama is in de taal Go geschreven, onze code in Python. JSON is de gemeenschappelijke taal ertussen.

In Python hoef je JSON niet zelf om te zetten; de library `httpx` doet dat. Het hele verzoek uit stap 2, maar nu in Python:

```python
import httpx

response = httpx.post(
    "http://localhost:11434/api/chat",
    json={"model": "qwen3.5:9b",
          "messages": [{"role": "user", "content": "Zeg alleen: hallo"}],
          "stream": False, "think": False},
)
data = response.json()
print(data["message"]["content"])
```

```
hallo
```

Wat hier gebeurt:
1. `httpx.post(...)` verstuurt het verzoek. Met `json=` geef je de body mee als gewone Python-dict; httpx zet die om naar JSON-tekst en zet de header `Content-Type` goed.
2. httpx geeft het antwoord terug als een Python-object, dat we `response` noemen. Dat object ís het HTTP-antwoord uit stap 3.
3. `response.json()` is een methode van dat object, net zoals `"hallo".upper()` een methode van een tekst is. Hij zet de JSON-body om naar een dict.
4. `data["message"]` geeft `{"role":"assistant","content":"hallo"}`, en daarvan pak je `["content"]`.

Het antwoord-object heeft voor elk deel uit stap 3 een eigen onderdeel:

| In Python | Deel van het antwoord | Echte waarde |
|---|---|---|
| `response.status_code` | statuscode | `200` |
| `response.headers["content-type"]` | een header | `application/json; charset=utf-8` |
| `response.text` | body als ruwe tekst (`str`) | `{"model":"qwen3.5:9b",...}` |
| `response.json()` | body omgezet naar een `dict` | `{'model': 'qwen3.5:9b', ...}` |

`.text` en `.json()` bevatten dezelfde inhoud: de eerste als één lange tekst, de tweede als dict waaruit je velden kunt pakken.

## 5. Knoppen en keuzes

- **Endpoint `/api/chat` of `/api/generate`.** Ollama heeft ook `/api/generate`, dat één losse tekst aanneemt zonder rollen. Wij kiezen `/api/chat`: met berichten en rollen kun je een system-bericht meegeven (les 01b), en straks passages uit de documentatie (Sprint 1) en tool calls (Project 2).
- **Het adres instelbaar houden.** `localhost:11434` is de standaard, maar Ollama kan ook op een andere computer of poort draaien. Daarom heeft `chat()` een parameter `base_url`, zodat je het adres kunt veranderen zonder de code aan te passen.
- **`curl` naast Python.** Doet iets raars in Python, probeer dan hetzelfde verzoek met `curl`. Werkt het daar wel, dan zit het probleem in je Python-code. Werkt het daar ook niet, dan zit het in Ollama of in het verzoek zelf. Zo halveer je het zoekgebied.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| `Connection refused` | Ollama draait niet, of je gebruikt een verkeerd poortnummer |
| statuscode `404` met "model not found" | typfout in de modelnaam, of het model is niet gedownload (`ollama list`) |
| statuscode `400` | de body is geen geldige JSON, bijvoorbeeld een vergeten `}` of aanhalingsteken |
| `KeyError: 'message'` in Python | je leest een veld dat niet in het antwoord staat; bekijk eerst het hele antwoord |

**Uitgewerkt voorbeeld.** Je tikt `8b` in plaats van `9b`: `"model":"qwen3.5:8b"`. Met `curl -i` zie je meteen wat er gebeurt (echte uitvoer, 17 oktober 2026):

```
HTTP/1.1 404 Not Found
...
{"error":"model 'qwen3.5:8b' not found"}
```

De statusregel is geen `200 OK` maar `404`, en de body bevat geen `message` maar een `error`. Zonder naar de statuscode te kijken, zou je in Python alleen een `KeyError` krijgen bij `data["message"]`, en dan zoek je op de verkeerde plek. Les: **kijk eerst naar de statuscode, dan pas naar de inhoud.**

(Een hoofdletter, `qwen3.5:9B`, is trouwens géén probleem: dat leverde gewoon `200 OK` op. En een body met een vergeten `}` aan het eind gaf `400 Bad Request` met `{"error":"unexpected EOF"}`: de server zat nog op de rest van de tekst te wachten.)

## 7. Analogie

Als je ooit een meetinstrument via een netwerk- of GPIB-aansluiting hebt aangestuurd met **SCPI**-commando's, bijvoorbeeld vanuit een geautomatiseerde calibratieprocedure, dan ken je dit patroon al:

| Instrument aansturen | Ollama aansturen |
|---|---|
| instrumentadres (`GPIB0::22::INSTR` of een IP-adres) | `localhost:11434` |
| commando `MEAS:VOLT:DC?` | endpoint `/api/chat` + JSON-body |
| meetwaarde terug | JSON-antwoord |
| foutcode uit het instrument (`-113, "Undefined header"`) | statuscode (`404`, `400`) |

**Waar de vergelijking ophoudt:**
- Een instrument onthoudt instellingen tussen commando's: eerst `CONF:VOLT:DC 10`, daarna `READ?`. Ollama onthoudt niets tussen twee verzoeken (les 01b). Elk verzoek moet alles bevatten: model, berichten en instellingen.
- SCPI-commando's verschillen per merk en type instrument. HTTP en JSON zijn één wereldwijde standaard; dezelfde kennis werkt voor Ollama, voor vLLM en voor vrijwel elke webdienst.

## 8. Samenvatting

**Kern:** Ollama is een server die op je eigen computer luistert op `localhost:11434`. Een client (de CLI, `curl` of onze Python-code) stuurt een HTTP-verzoek naar een endpoint, met de vraag als JSON in de body. De server stuurt een HTTP-antwoord met een statuscode en het antwoord als JSON. Python zet die JSON om naar een gewone dict.

**Begrippen:**
- **Server / client**: wie wacht en antwoordt, en wie vraagt.
- **Poort**: het nummer waarop een server luistert (Ollama: 11434).
- **Endpoint**: het pad achter het adres dat zegt wat je wilt (`/api/chat`).
- **HTTP-verzoek**: methode, adres, headers en body.
- **HTTP-antwoord**: statuscode, headers en body.
- **Statuscode**: `2xx` gelukt, `4xx` fout aan jouw kant, `5xx` fout aan de serverkant.
- **JSON**: tekstformaat voor gegevens met structuur; wordt in Python een dict of list.

**Knoppen:** `/api/chat` of `/api/generate` · instelbaar adres (`base_url`) · `curl` om het zoekgebied te halveren.

**Foutmodi:** geen verbinding · 404 door een verkeerde modelnaam · 400 door ongeldige JSON · een `KeyError` doordat je de statuscode niet bekeek.

## 9. Wat we hiermee gaan bouwen

Dit is precies wat `chat()` in `src/llm_client.py` doet: een `POST` naar `/api/chat` met een JSON-body, en het JSON-antwoord terug als dict. In les 02b kijken we naar twee dingen die we in het `curl`-commando nog even negeerden: waarom we `"stream": false` meesturen, en hoe lang de client mag wachten op een antwoord.
