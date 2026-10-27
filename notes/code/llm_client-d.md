# Rondleiding `src/llm_client.py` — deel D: het resultaat

## 1. Inleiding

**Waar we zijn:** het laatste stuk van `chat()`, en de class `ChatResult` bovenaan het bestand.

```
  chat():
  3. fouten opvangen en vertalen   (regels 52–66)                        ← deel B en C
  4. resultaat teruggeven          (regels 67–89, en ChatResult op 18)   ← dit deel (D)
```

**Wat je al weet:** hoe `chat()` het verzoek verstuurt (`llm_client-a.md`) en fouten opvangt en vertaalt (`llm_client-b.md`, `llm_client-c.md`). Uit les 02a weet je dat `response.json()` het antwoord van Ollama omzet naar een dict, `data`.

**Waarom dit deel:** als alles goed ging, heeft `chat()` nu een dict van Ollama. Dat wordt niet zomaar doorgegeven, maar omgezet naar een eigen, klein object: `ChatResult`. Waarom, en hoe, is dit deel. Daarna ken je het hele bestand, en draai je het zelf.

**Na dit deel kun je:**
- uitleggen hoe `chat()` de duur van een aanroep meet;
- schakel 5 uit les 02c in de code aanwijzen;
- een `@dataclass` lezen en zelf maken;
- uitleggen waarom `chat()` een `ChatResult` teruggeeft en niet de dict van Ollama.

**Python-constructies in dit deel (1):** `@dataclass`.

Open [`src/llm_client.py`](../../src/llm_client.py) er weer naast.

## 2. De stopwatch: regels 51 en 67

```python
    start = time.perf_counter()          # regel 51, vóór het versturen
    ...
    seconds = time.perf_counter() - start   # regel 67, ná het try-blok
```

`time.perf_counter()` is een nauwkeurige stopwatch: hij geeft een tijd in seconden. Je leest hem af vóór het verzoek en erna, en het verschil is de verstreken tijd. Daar zit dus alles in: het versturen, eventueel een koude start (les 02b), het genereren en het terugsturen.

Regel 67 staat ná het hele `try / except / finally`-blok. Je komt er alleen als er geen fout was: bij een fout is `chat()` al gestopt met een `LLMError` (deel C). Een mislukte aanroep krijgt dus geen tijd.

**Waarom zelf meten, als Ollama zelf `total_duration` meestuurt?** Aan het eind van Sprint 0 (les 05) praten we ook via de OpenAI-compatibele route, en die stuurt geen duur mee. Met een eigen stopwatch meten we op beide routes op dezelfde manier. Ollama's eigen tijden, zoals `load_duration`, gooien we niet weg; zie sectie 4.

## 3. Schakel 5: de inhoud controleren (regels 69–71)

```python
    message = data.get("message")
    if not isinstance(message, dict) or "content" not in message:
        raise LLMError(f"Onverwacht antwoord, geen message.content: {data}")
```

Dit is de laatste schakel uit les 02c: het antwoord is geldige JSON, maar staat het verwachte veld er ook in?

- **`data.get("message")`** haalt het veld `message` op. Bestaat het niet, dan krijg je `None` in plaats van een fout. Met `data["message"]` zou je een `KeyError` krijgen, de fout uit les 02a.
- **`isinstance(message, dict)`** vraagt: is `message` een dict? Bij een vreemd antwoord kan het `None` zijn, of iets anders.
- **`"content" not in message`** vraagt: ontbreekt het veld `content` in dat dict?
- Klopt één van beide niet, dan gooit `chat()` een `LLMError` (deel C), met het hele antwoord in de melding, zodat je kunt zien wat er wél kwam.

Deze controle staat niet in het `try`-blok, omdat het hier geen fout van httpx is die vertaald moet worden. Het is onze eigen controle, en die gooit meteen zelf een `LLMError`.

## 4. Een eigen resultaat: `@dataclass` *(nieuwe constructie)*

### Het idee, los van ons project

Een **dataclass** is een class die je gebruikt om een paar gegevens bij elkaar te houden. Je schrijft alleen op welke velden er zijn en van welk type. Python maakt de rest zelf: een `__init__` om het object te maken, en een nette weergave bij `print`.

**Klein los voorbeeld** (echt gedraaid, `voorbeelden/meting_dataclass.py`):

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Meting:
    waarde: float
    eenheid: str

m = Meting(waarde=10.0003, eenheid="V")
print(m)
print(m.waarde, m.eenheid)
m.waarde = 9.9
```

```
Meting(waarde=10.0003, eenheid='V')
10.0003 V
Traceback (most recent call last):
  ...
dataclasses.FrozenInstanceError: cannot assign to field 'waarde'
```

- **`@dataclass`** boven de class zegt: "dit is een dataclass, maak de rest zelf". Zonder dataclass had je zelf een `__init__` moeten schrijven, met `self.waarde = waarde` en `self.eenheid = eenheid`.
- **`waarde: float`** en **`eenheid: str`** zijn de velden, met hun type.
- **`frozen=True`** betekent: na het maken kun je de velden niet meer veranderen. Daarom faalt de laatste regel. Een meetresultaat pas je achteraf niet aan.

### Regels 18–27: `ChatResult`

```python
@dataclass(frozen=True)
class ChatResult:
    """Resultaat van één aanroep, onafhankelijk van de backend."""

    content: str
    done_reason: str | None  # "stop" = klaar, "length" = afgekapt
    tokens_in: int | None
    tokens_out: int | None
    seconds: float  # gemeten door de client, van verzoek tot antwoord
    raw: dict  # het volledige antwoord van de backend, voor logging
```

| Veld | Wat | Uit welke les |
|---|---|---|
| `content` | de tekst van het antwoord | 02a |
| `done_reason` | `"stop"` of `"length"` | 01a |
| `tokens_in`, `tokens_out` | tokens erin en eruit | 01a, 01b |
| `seconds` | duur, met onze eigen stopwatch | 02b, sectie 2 |
| `raw` | het complete, onvertaalde antwoord, bijv. voor `load_duration` | 02b |

`str | None` betekent "een tekst, óf niets": niet elke backend stuurt elk veld mee, en dan wordt het `None` in plaats van dat het programma vastloopt.

**Waarom een eigen resultaat, en niet gewoon de dict van Ollama?** Op de OpenAI-compatibele route (les 05) heten dezelfde dingen anders: `usage.completion_tokens` in plaats van `eval_count`, `choices[0].message.content` in plaats van `message.content`. Als de meetlat Ollama's namen gebruikt, moet hij bij die overstap op elke plek worden aangepast. Met `ChatResult` kent de meetlat alleen ónze namen, en maakt het niet uit welke backend erachter zit.

### Regels 73–80: op één plek vertalen

```python
    result = ChatResult(
        content=message["content"],
        done_reason=data.get("done_reason"),
        tokens_in=data.get("prompt_eval_count"),
        tokens_out=data.get("eval_count"),
        seconds=seconds,
        raw=data,
    )
```

Links staan onze namen, rechts die van Ollama. Dit is de **enige plek** in het project die Ollama's veldnamen kent. Hier mag `message["content"]` met vierkante haken, omdat schakel 5 (sectie 3) net heeft gecontroleerd dat `content` er is.

## 5. Loggen en teruggeven (regels 81–89)

```python
    logger.info(
        "model=%s tokens_in=%s tokens_uit=%s duur=%.2fs done_reason=%s",
        model, result.tokens_in, result.tokens_out, result.seconds, result.done_reason,
    )
    if result.done_reason == "length":
        logger.warning("Antwoord afgekapt door num_predict (done_reason=length)")
    if message.get("thinking"):
        logger.warning("Model heeft gedacht ondanks think=false")
    return result
```

- **`logger.info(...)`** (deel A) schrijft één regel per aanroep. Er staan `%s` en `%.2f` in plaats van een f-string met `{...}`. Dat is een afspraak bij logging: de logger vult de plekken zelf in, met de waarden die erachter staan, en alleen als het bericht ook echt getoond wordt. `%s` betekent "vul hier een waarde in", `%.2f` "een getal met 2 decimalen".
- **Twee waarschuwingen:** bij een afgekapt antwoord (les 01a), en als het model toch heeft gedacht, wat niet zou mogen omdat we `think: false` sturen (les 01b).
- **`return result`** geeft het `ChatResult` terug aan wie `chat()` aanriep.

## 6. Zelf proberen: `chat()` draaien

Je kent nu het hele bestand. Tijd om het te draaien. Dit is **bouwstap 1** uit het bouwplan. Ollama moet draaien:

```bash
uv run python -c "
import logging; logging.basicConfig(level=logging.INFO)
from src.llm_client import chat
r = chat('qwen3.5:9b', [{'role': 'user', 'content': 'Wat is vLLM? Eén zin.'}], {'temperature': 0.2, 'seed': 42})
print(r.content)
print(r.tokens_in, r.tokens_out, round(r.seconds, 2), r.done_reason)
"
```

**Wat je hoort te zien:**
1. een regel van httpx: `INFO:httpx:HTTP Request: POST http://localhost:11434/api/chat "HTTP/1.1 200 OK"`;
2. een regel van `chat()`: `INFO:src.llm_client:model=qwen3.5:9b tokens_in=... tokens_uit=... duur=...s done_reason=stop`;
3. een antwoord van één zin over vLLM;
4. een regel met vier waarden: tokens in, tokens uit, de duur in seconden, en `stop`.

De precieze getallen en de tekst staan pas vast als je het draait. Bij een test op 25 oktober kwam er `22 53 4.28 stop` uit; die 4,28 s was een koude start. Draai je het twee keer kort na elkaar, dan is de tweede keer veel sneller (les 02b).

**Speelopdracht (optioneel):** zet aan het eind van het commando, vóór het laatste aanhalingsteken, de regel `r.content = 'iets anders'`. Draai het opnieuw. Let op welke foutmelding je onderaan krijgt, en vergelijk die met het `Meting`-voorbeeld in sectie 4.

## 7. Samenvatting

- **Stopwatch:** `time.perf_counter()` vóór en na; alleen een geslaagde aanroep krijgt een duur. Zelf gemeten, zodat het op elke backend hetzelfde werkt.
- **Schakel 5:** met `.get`, `isinstance` en `not in` controleren dat `message.content` er is; zo niet, een `LLMError`.
- **`@dataclass(frozen=True)`:** een class met alleen velden, waarvan Python de rest maakt; `frozen` maakt hem onveranderbaar.
- **`ChatResult`:** het antwoord in onze eigen namen, op één plek vertaald uit Ollama's namen. Het ruwe antwoord blijft bewaard in `raw`.
- **Logging:** `%s`-plekken in plaats van een f-string; een waarschuwing bij een afgekapt antwoord en bij onverwacht denken.

## 8. Wat nu

Na het draaien is bouwstap 1 klaar. Daarna volgt **bouwstap 2**: tests voor `chat()` met een nep-server. Die bootsen de vijf schakels uit les 02c na, en dichten het gat uit deel C.
