# Rondleiding `src/llm_client.py` — deel C: fouten gooien en vertalen

## 1. Inleiding

**Waar we zijn:** in de `except`-regels van `chat()`, en bij ons eigen fouttype bovenaan het bestand.

```
  chat():
  3. fouten opvangen           (regels 52–66)   ← deel B
     fouten vertalen           (regels 56–63, en LLMError op regel 14)   ← dit deel (C)
  4. resultaat teruggeven      (regels 67–89)   ← deel D
```

**Wat je al weet:** hoe je met `try / except / finally` een fout opvangt, en dat een fout die niemand opvangt "naar boven" gaat, naar de aanroeper (`llm_client-b.md`). Waarom `chat()` elke fout vertaalt naar één eigen soort fout met een leesbare melding, en hoe je een gelaagde foutmelding leest (`../02c-wat-er-mis-kan-gaan.md`).

**Waarom dit deel:** in deel B zag je dát `chat()` fouten opvangt. Maar opvangen alleen is niet genoeg: de meetlat moet straks óók weten dat het misging. Daarom gooit `chat()` in elke `except` zelf een nieuwe fout, `LLMError`. Hoe dat werkt, is dit deel.

**Na dit deel kun je:**
- zelf een fout gooien met `raise`, en uitleggen hoe dat verschilt van `return`;
- een eigen soort fout maken, en uitleggen waarom de ouder ertoe doet;
- een fout vertalen met `raise ... from e`, en uitleggen wat er gebeurt zonder `from e`;
- één gat in de foutafhandeling van `chat()` aanwijzen.

**Python-constructies in dit deel (3):** `raise` · een eigen fouttype (`class ... (Exception)`) · `raise ... from e`.

Open [`src/llm_client.py`](../../src/llm_client.py) er weer naast. Op je spiekbriefje: `../naslag/python-fouten-spiekbriefje.md`.

## 2. Zelf een fout gooien: `raise` *(nieuwe constructie)*

`raise` betekent: **gooi deze fout**. Het werkt precies zoals de fouten van Python zelf: binnenin `float("OVLD")` doet Python ook een `raise ValueError(...)`.

**Klein los voorbeeld** (echt gedraaid):

```python
def controleer_bereik(waarde):
    if waarde > 1000:
        raise ValueError(f"Waarde {waarde} V buiten bereik (max 1000 V)")
    return waarde

print(controleer_bereik(230))
print(controleer_bereik(1500))
```

```
230
Traceback (most recent call last):
  ...
ValueError: Waarde 1500 V buiten bereik (max 1000 V)
```

Bij 230 komt de functie bij `return` en geeft de waarde terug. Bij 1500 komt hij nooit bij `return`.

De regel met `raise` doet twee dingen:
1. `ValueError("...")` **maakt** een fout-object, net zoals `Meting(...)` een meting maakt. Er gebeurt nog niets.
2. `raise` **gooit** het. Vanaf dat moment stopt de functie direct op die regel, en gaat de fout naar boven (deel B), tot iemand hem opvangt.

**`return` tegenover `raise`:**

| | `return waarde` | `raise Fout(...)` |
|---|---|---|
| betekenis | "klaar, hier is het resultaat" | "het lukt niet, iemand moet dit afhandelen" |
| gaat naar | de aanroeper, als gewone waarde | naar boven, op zoek naar een passende `except` |
| de aanroeper | rekent verder met de waarde | stopt ook, tenzij hij een passende `except` heeft |

Als vergelijking: `return` is afmelden met de meetwaarde. `raise` is de noodstop: alles stopt, tot iemand verantwoordelijkheid neemt.

## 3. Een eigen soort fout maken *(nieuwe constructie)*

Python heeft zelf al veel soorten fouten: `ValueError`, `ZeroDivisionError`, `KeyError`. Je kunt er ook zelf één maken, met een naam die zegt waar het over gaat:

```python
class MeetFout(Exception):
    """Fout bij het uitlezen van een instrument."""
```

Je kent classes uit je intro OOP. Nieuw is waarschijnlijk **`(Exception)`** achter de naam. Dat is **overerving**: `MeetFout` is een *soort* `Exception`, en erft alles wat een fout in Python kan. Je kunt hem gooien met `raise`, opvangen met `except`, een melding meegeven en een oorzaak eraan hangen (sectie 4). Daar hoef je niets voor te schrijven. Daarom bestaat de class alleen uit een docstring.

### De ouder bepaalt wie hem opvangt

Wat je tussen de haakjes zet, maakt uit: **een `except` vangt de soort die erachter staat, en ook alle soorten die daarvan erven.** Echte uitkomsten (`voorbeelden/erven.py`):

| Definitie | Gevolg |
|---|---|
| `class LLMError(Exception)` | alleen `except LLMError` (of het brede `except Exception`) vangt hem. Zo staat het nu in `chat()`. |
| `class LLMError(ConnectionError)` | dan vangt ook `except ConnectionError` hem. Verkeerd voor ons: een 404 is geen verbindingsprobleem. |
| `class LLMTimeoutError(LLMError)` | een **familie**: `except LLMError` vangt alle leden, `except LLMTimeoutError` alleen de timeouts. |
| `class X(LLMError, TimeoutError)` | twee ouders tegelijk: beide `except`-regels vangen hem. Kan, maar spaarzaam gebruiken. |

Dit verklaart iets uit deel B: één `except httpx.TimeoutException` vangt zowel `ReadTimeout` als `ConnectTimeout` op, omdat httpx ze allebei laat erven van `TimeoutException` (gecontroleerd). httpx heeft dus zelf zo'n familie van fouten.

Een familie is ook de knop uit les 02c ("één soort of één per schakel"), maar dan zonder te hoeven kiezen. Voor nu is één `LLMError` genoeg. Willen we later bijvoorbeeld bij een timeout opnieuw proberen, dan maken we er een familie van, en blijft `except LLMError` gewoon werken.

### Twee grenzen

- **Een fout moet afstammen van `BaseException`**, de stamvader van alle fouten. Via `Exception` zit je goed. Een gewone class gooien geeft `TypeError: exceptions must derive from BaseException` (echt gedraaid).
- **Nooit een kale `except:`**. Onder `BaseException` staan, naast `Exception`, ook stopsignalen, zoals `KeyboardInterrupt` (Ctrl+C) en `SystemExit` (`sys.exit()`). Een kale `except:` vangt die ook, en dan stopt je programma niet meer als je dat wilt. Wil je alle gewone fouten opvangen, schrijf dan `except Exception:`. De stamboom staat op je spiekbriefje.

## 4. Een fout vertalen: `raise ... from e` *(nieuwe constructie)*

Nu komen sectie 2 en 3 samen. In een `except` vang je een technische fout op, en gooi je een eigen fout met een melding die zegt wat er in de praktijk aan de hand is.

### Een `raise` ín een `except`: waar gaat die heen?

Een `except` vangt alleen fouten op die ontstaan **in zijn eigen `try`-deel**. Een `raise` in een `except`-deel verlaat daarom het hele `try/except`-blok. De andere `except`-regels van datzelfde blok kijken er niet naar. Wel draait `finally` nog, vlak voordat de fout de functie verlaat. Echt gedraaid (`voorbeelden/raise_in_except.py`):

```python
def lees(tekst):
    try:
        return float(tekst)
    except ValueError as e:
        raise MeetFout(f"Geen getal: '{tekst}'") from e   # verlaat het blok
    except MeetFout:
        print("except MeetFout: ben ik hier?")              # wordt NIET bereikt
    finally:
        print("finally: ik draai nog ...")                  # wordt WEL bereikt

def meetlat():
    try:
        lees("OVLD")
    except MeetFout as e:
        print("meetlat: MeetFout opgevangen ->", e)
```

```
try: ik probeer om te zetten
except ValueError: ik gooi een MeetFout
finally: ik draai nog, vlak voordat de fout lees() verlaat
meetlat: MeetFout opgevangen -> Geen getal: 'OVLD'
```

De `MeetFout` gaat naar de aanroeper, `meetlat()`, en die vangt hem op. Zo werkt `chat()` ook: **`chat()` vertaalt, de aanroeper beslist.**

### Wat `from e` doet

Met `from e` hang je de originele fout aan de nieuwe, als **oorzaak**. Echte uitvoer (`voorbeelden/raise_demo.py from`):

```
Traceback (most recent call last):
  ...
ValueError: could not convert string to float: 'OVLD'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...
MeetFout: Geen getal: 'OVLD'
```

Onderaan staat de leesbare melding. Erboven staat de technische oorzaak, met de zin *"The above exception was the direct cause of the following exception"*: de fout hierboven was de directe oorzaak van de fout hieronder. Dat is precies de gelaagde foutmelding uit les 02c.

### Wat er gebeurt zonder `from e`

De originele fout verdwijnt **niet**: Python onthoudt vanzelf dat je in een `except` zat. Het verschil zit in de zin tussen de twee fouten. Echte uitkomsten van de drie varianten:

| Variant | Zin tussen de fouten | Betekenis |
|---|---|---|
| `raise ... from e` | *The above exception was the direct cause of the following exception* | de eerste fout was de **oorzaak**: een bewuste vertaling |
| `raise ...` (zonder `from`) | *During handling of the above exception, another exception occurred* | **tijdens** het afhandelen ging er nóg iets mis: suggereert een tweede, los probleem |
| `raise ... from None` | (geen: de originele fout wordt niet getoond) | oorzaak weg |

Als storingsrapport: met `from e` staat er "geen meetwaarde, oorzaak: instrument gaf OVLD". Zonder `from` staat er "storing 1: OVLD; tijdens het verhelpen trad storing 2 op". Wie dat leest, gaat een tweede probleem zoeken dat er niet is. En met `from None` staat de oorzaak er helemaal niet bij.

**Ezelsbruggetje:** lees `from e` als **"komt door e"**. Vertaal je in een `except` een fout naar een eigen fout, dan altijd `from e`.

## 5. In onze code

### Regels 14–15 — Ons eigen fouttype

```python
class LLMError(Exception):
    """Fout bij het aanroepen van het LLM: timeout, geen verbinding, HTTP-fout of onverwacht antwoord."""
```

Precies zoals `MeetFout` in sectie 3: een eigen soort fout, die erft van `Exception`.

**Waarom een eigen soort, en niet gewoon `Exception`?** Les 02c, stap 3: de meetlat hoeft straks maar één soort te kennen. Met `except LLMError` vangt hij precies de fouten uit `chat()`, en niet per ongeluk een tikfout ergens anders in zijn eigen code.

### Regels 56–63 — De vertalingen

```python
    except httpx.TimeoutException as e:
        raise LLMError(f"Timeout na {timeout} s (koude start? model te groot?)") from e
    except httpx.ConnectError as e:
        raise LLMError(f"Geen verbinding met Ollama op {base_url}; draait de server?") from e
    except httpx.HTTPStatusError as e:
        raise LLMError(f"HTTP {e.response.status_code}: {e.response.text}") from e
    except ValueError as e:
        raise LLMError("Antwoord is geen geldige JSON (stream per ongeluk aan?)") from e
```

Elke regel is nu te lezen:
- **`except ... as e`** vangt één soort fout (deel B) en noemt hem `e`;
- **`raise LLMError(...)`** gooit ons eigen fouttype, met een melding die per schakel zegt wat er waarschijnlijk mis is;
- **`from e`** hangt de originele httpx-fout eraan als oorzaak.

Twee details:
- **`f"..."`** is een f-string: `{timeout}` wordt vervangen door de waarde van `timeout`. Zo komt "Timeout na 120.0 s" in de melding.
- **`e.response.status_code`** en **`e.response.text`**: bij een statusfout zit het antwoord van de server in de fout zelf. Zo komen de statuscode en de tekst van Ollama (bijv. `{"error":"model 'qwen3.5:8b' not found"}`) in onze melding.

## 6. Wat `chat()` nog níet opvangt

Bij het schrijven van deze rondleiding heb ik nagekeken welke fouten van httpx precies worden opgevangen. Twee soorten vallen ertussendoor (gecontroleerd):

| Fout | Wanneer | Wordt opgevangen? |
|---|---|---|
| `ReadError` | de verbinding valt weg terwijl het antwoord onderweg is | **nee** |
| `RemoteProtocolError` | de server breekt het antwoord halverwege af | **nee** |

Dat gebeurt bijvoorbeeld als Ollama herstart terwijl het een antwoord maakt. Geen van de vier `except`-regels past, dus de fout gaat langs `chat()` naar boven (deel B). Je krijgt dan geen `LLMError`, maar een kale httpx-fout. Erger: de meetlat vangt straks `LLMError` op, en deze fout gaat daar ook langs. De hele run stopt, in plaats van dat de fout bij die ene vraag wordt genoteerd.

Met sectie 3 is te zien hoe dat komt, en hoe het op te lossen is. Allebei erven ze van `httpx.TransportError`, de familie "er ging iets mis met de verbinding", waar ook `ConnectError` en de timeouts bij horen. De oplossing is een extra `except httpx.TransportError` ná de specifieke regels, als vangnet voor de rest van die familie. Omdat Python de `except`-regels van boven naar beneden langsloopt (deel B), krijgen timeouts en `ConnectError` dan nog steeds hun eigen, specifieke melding.

Dat doen we in bouwstap 2, samen met een test die het gat eerst laat zien. Dit is precies waarom we testen: het gat zat er vanaf het begin in, en viel pas op toen we gericht gingen kijken.

## 7. Zelf proberen

De voorbeelden staan in [`voorbeelden/`](voorbeelden/). Draai ze in de projectmap:

```bash
uv run python notes/code/voorbeelden/raise_demo.py bereik
uv run python notes/code/voorbeelden/raise_demo.py from
uv run python notes/code/voorbeelden/raise_demo.py zonder
uv run python notes/code/voorbeelden/raise_demo.py none
uv run python notes/code/voorbeelden/raise_in_except.py
uv run python notes/code/voorbeelden/erven.py
```

Bij `raise_demo.py`: vergelijk vooral de zin tussen de twee fouten.

**Een fout uitlokken in `chat()`:**

```bash
uv run python -c "
from src.llm_client import chat
chat('qwen3.5:8b', [{'role': 'user', 'content': 'hoi'}])
"
```

Lees de foutmelding van onderen. De onderste regel hoort te zijn: `src.llm_client.LLMError: HTTP 404: {"error":"model 'qwen3.5:8b' not found"}`. Zoek erboven de zin die zegt dat de httpx-fout de oorzaak was.

## 8. Samenvatting

- **`raise`:** gooi een fout. De functie stopt direct, en de fout gaat naar boven. (`return` = klaar, hier is de waarde.)
- **Eigen fouttype:** `class LLMError(Exception)` erft alles wat een fout kan. De ouder bepaalt wie hem opvangt: een `except` vangt de soort én alles wat ervan erft. Nooit een kale `except:`.
- **`raise ... from e`:** vertaal een technische fout naar een leesbare, en bewaar de originele als oorzaak ("komt door e"). Zonder `from` lijkt het op een tweede, los probleem.
- **Een `raise` in een `except`** verlaat het hele blok en gaat naar de aanroeper; `finally` draait nog.
- **Gat:** `ReadError` en `RemoteProtocolError` worden nog niet opgevangen. Oplossing in bouwstap 2: een vangnet `except httpx.TransportError`.

## 9. Wat komt in deel D

De laatste regels van `chat()`: de inhoud van het antwoord controleren (schakel 5), en het antwoord omzetten naar een `ChatResult`, met `@dataclass`. Daarna ken je het hele bestand, en draai je `chat()` zelf.
