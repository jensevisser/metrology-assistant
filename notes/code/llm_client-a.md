# Rondleiding `src/llm_client.py` — deel A: overzicht en het verzoek versturen

## 1. Inleiding

**Waar we zijn:** bij het stukje Python dat met Ollama praat.

```
  5 vragen ──▶ meetlat ──▶ [ chat() ] ──▶ Ollama ──▶ model
                               ▲
                    dit bestand: src/llm_client.py
```

**Wat je al weet:** wat een HTTP-verzoek en -antwoord zijn, en hoe JSON in Python een dict wordt (`../02a-vraag-en-antwoord-over-http.md`). Waarom we `"stream": false` sturen en een timeout zetten (`../02b-streaming-en-timeouts.md`). Welke fouten er kunnen optreden (`../02c-wat-er-mis-kan-gaan.md`).

**Waarom deze rondleiding:** dit bestand bestaat al sinds het begin, maar we hebben het samen nog nooit doorgelopen. Voordat we het testen of veranderen, moet je weten wat er staat. Zo kun je straks elke wijziging in de diff lezen.

**Na dit deel kun je:**
- aanwijzen waar in het bestand wat gebeurt;
- uitleggen hoe `chat()` het verzoek uit les 02a opbouwt en verstuurt;
- de drie Python-constructies hieronder lezen en zelf gebruiken.

**Python-constructies in dit deel (3):** logging · een functie met standaardwaarden en `*` · `x or y`.

Open het bestand ernaast in VSCodium, zodat je de regelnummers kunt volgen.

## 2. Het bestand in vogelvlucht

Van boven naar beneden staan er vijf onderdelen:

| Regels | Wat | In welk deel |
|---|---|---|
| 1 | een korte beschrijving van het bestand | A |
| 3–11 | voorbereiding: imports, de logger en het standaardadres van Ollama | A |
| 14–15 | `LLMError`: ons eigen fouttype (les 02c) | B |
| 18–27 | `ChatResult`: het resultaat dat `chat()` teruggeeft | B |
| 30–89 | de functie `chat()` zelf | A (begin) en B (rest) |

De functie `chat()` doet op hoofdlijnen vier dingen na elkaar:

```
  1. verzoek opbouwen          (regels 43–49)   ← deel A
  2. verzoek versturen         (regels 50–55)   ← deel A
  3. fouten opvangen           (regels 56–71)   ← deel B
  4. resultaat teruggeven      (regels 73–89)   ← deel B
```

## 3. Blok voor blok

### Regel 1 — Wat dit bestand is

```python
"""Minimale client voor de Ollama HTTP API (/api/chat), zonder streaming."""
```

Tekst tussen drie aanhalingstekens bovenaan een bestand, class of functie heet een **docstring**: een beschrijving voor mensen. Python doet er niets mee bij het draaien. Je ziet hetzelfde bij `LLMError` (regel 15), `ChatResult` (regel 20) en `chat()` (regels 39–42). VSCodium toont de docstring als je met je muis over de naam beweegt.

### Regels 3–7 — Wat we nodig hebben

```python
import logging
import time
from dataclasses import dataclass

import httpx
```

- `import logging` en `import time` halen een module uit de standaardbibliotheek van Python binnen. Daarna gebruik je onderdelen met een punt ervoor: `time.perf_counter()`.
- `from dataclasses import dataclass` haalt één onderdeel uit een module, zodat je het direct kunt gebruiken: `@dataclass` in plaats van `@dataclasses.dataclass`.
- `import httpx` komt na een lege regel. Dat is een afspraak: eerst de standaardbibliotheek, daarna pakketten die je zelf installeerde (`uv add httpx`). Python maakt het niet uit; het is voor de lezer.

### Regel 9 — De logger *(nieuwe constructie: logging)*

```python
logger = logging.getLogger(__name__)
```

**Wat logging is.** In plaats van `print()` gebruikt code in `src/` een **logger** (CLAUDE.md §6). Een logger is een `print` met extra's: elk bericht krijgt een **niveau** (hoe belangrijk is het?) en een **naam** (waar komt het vandaan?). Wie het programma draait, bepaalt welke niveaus zichtbaar zijn. Zo hoef je de code niet aan te passen om meer of minder te zien.

De niveaus die wij gebruiken, van minst tot meest belangrijk:

| Niveau | Wanneer | In `chat()` |
|---|---|---|
| `info` | gewone voortgang | "model=... tokens_in=... duur=..." (regel 81) |
| `warning` | iets is niet zoals verwacht, maar het programma gaat door | "Antwoord afgekapt" (regel 86) |

**Klein los voorbeeld** (echt gedraaid):

```python
import logging
logger = logging.getLogger("demo")
logger.info("dit is info")
logger.warning("dit is een waarschuwing")
```

```
dit is een waarschuwing
```

Alleen de waarschuwing verschijnt. Standaard laat Python alleen `warning` en erger zien. Zet je er `logging.basicConfig(level=logging.INFO)` bovenaan, dan verschijnt ook `info`, met niveau en naam ervoor:

```
INFO:demo:dit is info
WARNING:demo:dit is een waarschuwing
```

Daarom staat `logging.basicConfig(level=logging.INFO)` straks vooraan in het commando waarmee je `chat()` uitprobeert (na deel B).

**Wat een module is.** In Python is elk `.py`-bestand een **module**: code die je vanuit ander Python-code kunt importeren. Bij `from src.llm_client import chat` laadt Python het bestand `src/llm_client.py`, en geeft het de naam `src.llm_client`: de `/` wordt een punt en `.py` valt weg. Dat het pad met `src.` kan beginnen, komt door het lege bestand `src/__init__.py`. Dat maakt van de map een **package**: een map met modules die bij elkaar horen.

**Wat `__name__` is.** Een speciale variabele die Python vult met de naam van de module. Voor dit bestand is dat `src.llm_client` (echt gecontroleerd). Daarom begint de logregel van `chat()` met `INFO:src.llm_client:...`, en weet je meteen uit welk bestand een bericht komt. (Uitzondering: start je een bestand rechtstreeks met `uv run python bestand.py`, dan is `__name__` gelijk aan `"__main__"`. Dat gebruiken we in bouwstap 4.)

### Regel 11 — Het standaardadres

```python
OLLAMA_URL = "http://localhost:11434"
```

Het adres uit les 02a. Een naam in HOOFDLETTERS is een afspraak voor "dit is een vaste waarde, verander hem niet tijdens het draaien". Hij staat bovenaan, zodat je hem op één plek vindt en aanpast.

### Regels 30–38 — De ingang van `chat()` *(nieuwe constructie: standaardwaarden en `*`)*

```python
def chat(
    model: str,
    messages: list[dict[str, str]],
    options: dict | None = None,
    *,
    timeout: float = 120.0,
    base_url: str = OLLAMA_URL,
    client: httpx.Client | None = None,
) -> ChatResult:
```

Dit is de "ingang" van de functie: welke gegevens je meegeeft. Elke parameter heeft een type hint (die ken je), en het pijltje `-> ChatResult` zegt wat de functie teruggeeft.

| Parameter | Betekenis | Verplicht? |
|---|---|---|
| `model` | welk model, bijv. `"qwen3.5:9b"` | ja |
| `messages` | de berichten met rollen (les 01b): een lijst van dicts | ja |
| `options` | de knoppen voor het model, bijv. `{"temperature": 0.2}` (les 03) | nee, standaard `None` |
| `timeout` | hoe lang we wachten (les 02b) | nee, standaard 120 s |
| `base_url` | het adres van Ollama | nee, standaard `OLLAMA_URL` |
| `client` | een eigen verbinding, alleen voor tests | nee, standaard `None` |

**Standaardwaarden.** `= 120.0` achter een parameter is de waarde die geldt als je niets meegeeft. Je kent dit misschien al.

**De `*` op regel 34** is waarschijnlijk nieuw. Hij betekent: alles ná de `*` moet je **bij naam** meegeven. Dus `chat(..., timeout=30)`, en niet als derde of vierde losse waarde.

**Klein los voorbeeld** (echt gedraaid):

```python
def meet(kanaal, bereik=10, *, nplc=1):
    return f"kanaal={kanaal} bereik={bereik} nplc={nplc}"

print(meet(1))
print(meet(1, 100, nplc=10))
meet(1, 100, 10)
```

```
kanaal=1 bereik=10 nplc=1
kanaal=1 bereik=100 nplc=10
TypeError -> meet() takes from 1 to 2 positional arguments but 3 were given
```

De derde aanroep faalt: zonder naam weet Python niet dat `10` voor `nplc` bedoeld was, en de `*` verbiedt raden.

**Waarom zo in `chat()`?** Bij `chat("qwen3.5:9b", berichten, None, 30, "http://...")` moet je onthouden welke positie wat betekent, en een verwisseling valt niet op. Met de `*` staat er `timeout=30`, en dat leest iedereen direct.

**Waarom `options: dict | None = None` en niet `options: dict = {}`?** Een voorbeeld (echt gedraaid): een functie die een meting aan een logboek toevoegt, en een nieuw logboek moet beginnen als je er geen meegeeft.

```python
def log_meting(waarde, log=[]):
    log.append(waarde)
    return log

print(log_meting(10.0))
print(log_meting(9.9))
print(log_meting(10.1))
```

```
[10.0]
[10.0, 9.9]
[10.0, 9.9, 10.1]
```

De metingen stapelen zich op. Python maakt de standaardwaarde `[]` **één keer**, bij het inlezen van de `def`-regel, en geeft daarna bij elke aanroep zonder logboek **datzelfde ene lijstje**. Het is als één meetformulier op de werkbank dat iedereen gebruikt en niemand weggooit.

De oplossing: `None` als standaard, en binnen de functie een nieuw lijstje maken. Die regel draait bij elke aanroep opnieuw:

```python
def log_meting2(waarde, log=None):
    log = log or []
    log.append(waarde)
    return log

print(log_meting2(10.0))
print(log_meting2(9.9))
```

```
[10.0]
[9.9]
```

Waarom werkt dit wel? De `def`-regel draait maar één keer, en bewaart `None` als standaard; daarop kun je niets schrijven. De regel `log = log or []` plakt de naam `log` bij elke aanroep op een **nieuw** lijstje, en de bewaarde `None` blijft `None`. Het verschil tussen een naam op een ander ding plakken (`log = ...`) en op het ding zelf schrijven (`log.append(...)`) staat uitgelegd in `../naslag/python.md`, bij "naam versus ding".

Dit geldt voor alles wat je achteraf kunt veranderen: lijstjes, dicts en sets. Getallen en teksten zijn veilig als standaardwaarde (`timeout=120.0`). In `chat()` zou `options: dict = {}` nu toevallig goed gaan, omdat `chat()` `options` alleen leest. Maar voegt iemand later een regel toe als "zet altijd een seed in `options`", dan blijft die seed hangen voor alle volgende aanroepen. `None` als standaard voorkomt dat. Het nieuwe dict wordt gemaakt op regel 48.

### Regels 43–49 — Het verzoek opbouwen *(nieuwe constructie: `x or y`)*

```python
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": options or {},
    }
```

Dit is precies de body uit het `curl`-voorbeeld van les 02a, maar nu als Python-dict:
- `"stream": False` staat er altijd, dus nooit NDJSON (les 02b);
- `"think": False` staat er altijd: bij jouw model staat denken standaard aan, en dat willen we niet in de meting.

`payload` is het gebruikelijke woord voor "de inhoud die we versturen".

**`options or {}`.** De `or` doet hier iets anders dan "of". In Python geeft `x or y` de waarde `x` terug als die "iets" bevat, en anders `y`. "Niets" is onder andere `None`, een leeg dict `{}`, een lege tekst `""` en het getal `0`.

**Klein los voorbeeld** (echt gedraaid):

```python
print(None or {})
print({'temperature': 0.2} or {})
print({} or 'leeg')
print(0 or 120)
```

```
{}
{'temperature': 0.2}
leeg
120
```

Dus: geef je geen `options` mee (`None`), dan wordt het een leeg dict `{}`. Geef je ze wel mee, dan blijven ze zoals ze zijn.

**Valkuil:** de laatste regel. `0 or 120` geeft `120`, omdat `0` als "niets" telt. Gebruik `or` daarom niet voor getallen waarbij 0 een geldige waarde is.

### Regel 50 — Een verbinding klaarzetten

```python
    http = client or httpx.Client(base_url=base_url, timeout=timeout)
```

Weer de `or`:
- **normaal** is `client` leeg (`None`), en maakt `chat()` zelf een `httpx.Client`;
- **in tests** geven we een eigen client mee die zich voordoet als Ollama (bouwstap 2), en dan wordt die gebruikt.

Een **`httpx.Client`** is een verbinding met vaste instellingen. In les 02a gebruikten we `httpx.post(...)`, en daar moest je elke keer het volledige adres en de timeout opgeven. Een `Client` onthoudt ze:
- met `base_url` hoef je daarna alleen nog het endpoint op te geven, `"/api/chat"`, en plakt httpx het adres ervoor;
- de `timeout` geldt voor elk verzoek via deze client.

Een client moet je na gebruik sluiten. Dat gebeurt op regel 66, in deel B.

### Regels 53 en 55 — Versturen en uitpakken

```python
        response = http.post("/api/chat", json=payload)
        ...
        data = response.json()
```

Dit ken je uit les 02a:
- `http.post("/api/chat", json=payload)` stuurt de `POST` naar `http://localhost:11434/api/chat`, met de payload als JSON-body;
- `response.json()` maakt van de JSON-body een dict, `data`.

Regel 54, `response.raise_for_status()`, en de regels eromheen (`try:` en `except`) zijn de foutafhandeling uit les 02c. Die zijn voor deel B.

## 4. Zelf proberen

Je hoeft hiervoor niets aan het project te veranderen. Draai in een terminal in de projectmap:

```bash
uv run python -c "
from src.llm_client import chat
import inspect
print(inspect.signature(chat))
"
```

`inspect.signature` laat de ingang van een functie zien, precies zoals in regels 30–38. Let op waar de `*` staat in de uitvoer.

Wil je het voorbeeld met `meet()` of `or` uitproberen: kopieer het in een bestand in je scratchpad, of start `uv run python` en typ het regel voor regel in. Afsluiten doe je met `exit()`.

## 5. Samenvatting

- **Het bestand** heeft vijf onderdelen: beschrijving, voorbereiding (imports, logger, adres), `LLMError`, `ChatResult` en `chat()`.
- **`chat()`** bouwt de body uit les 02a op als dict (`payload`), met altijd `stream` en `think` uit, en verstuurt hem met een `httpx.Client` naar `/api/chat`.
- **Logging:** een `print` met niveau en naam; standaard alleen `warning` en erger zichtbaar, met `basicConfig(level=logging.INFO)` ook `info`.
- **`*` in de parameters:** alles erna moet je bij naam meegeven; dat voorkomt verwisselingen.
- **`x or y`:** geeft `x` als die iets bevat, anders `y`. Valkuil: `0` telt als niets.
- **`None` als standaard voor een dict**, en binnen de functie een nieuw dict maken.

## 6. Wat komt in deel B

Regels 52–89: wat er gebeurt als het misgaat (`try`, `except`, `finally`, `raise ... from e` en ons eigen `LLMError`), en hoe het antwoord wordt omgezet naar een `ChatResult` (de `@dataclass`). Dat is precies de foutketen uit les 02c, nu in code.
