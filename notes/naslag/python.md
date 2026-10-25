# Python — spiekbriefje

Constructies die we in dit project gebruiken, met waar je ze tegenkomt. Groeit mee.

## Ik wil iets laten zien terwijl het programma draait: logging

```python
import logging
logger = logging.getLogger(__name__)   # naam = de module, bijv. src.llm_client

logger.info("gewone voortgang")         # standaard NIET zichtbaar
logger.warning("let op, maar gaat door")  # standaard wel zichtbaar
```

`info` ook zien? Bovenaan je script: `logging.basicConfig(level=logging.INFO)`.
In `src/` altijd logging, geen `print` (CLAUDE.md §6). *Zie: `src/llm_client.py` regel 9, 81, 86.*

## Ik wil code uit een ander bestand gebruiken: modules en packages

```
src/__init__.py        ← leeg bestand: maakt van src/ een package
src/llm_client.py      ← een module, naam: src.llm_client
```

```python
from src.llm_client import chat   # één onderdeel uit een module
import time                       # hele module; gebruik: time.perf_counter()
```

`__name__` = naam van de module (`src.llm_client`), of `"__main__"` als je het bestand rechtstreeks start.

## Ik wil dat een parameter bij naam wordt meegegeven: `*`

```python
def meet(kanaal, bereik=10, *, nplc=1): ...

meet(1)                  # ok: bereik=10, nplc=1
meet(1, 100, nplc=10)    # ok
meet(1, 100, 10)         # TypeError: na * alleen bij naam
```

*Zie: `chat()`, regel 34.*

## Ik wil een standaardwaarde als er niets is: `x or y`

```python
options or {}     # None → {}, {"temperature": 0.2} → blijft
0 or 120          # → 120  (!) 0 telt als "niets"
```

"Niets" = `None`, `0`, `""`, `{}`, `[]`, `False`. Niet gebruiken als 0 een geldige waarde is.
*Zie: `chat()`, regel 48 en 50.*

## Ik wil een dict of lijst als standaardwaarde

```python
def f(options: dict | None = None):   # goed
    options = options or {}

def f(options: dict = {}):            # valkuil: één dict, gedeeld door alle aanroepen
```

Waarom: de standaardwaarde wordt één keer gemaakt (bij het inlezen van `def`), niet per aanroep.

```python
def log_meting(waarde, log=[]): log.append(waarde); return log
log_meting(10.0)   # [10.0]
log_meting(9.9)    # [10.0, 9.9]   ← oude meting hangt er nog
```

Geldt voor lijst, dict en set. Getallen en teksten zijn veilig.
Bekijken wat er bewaard is: `log_meting.__defaults__`.

## Ik wil snappen wat `=` doet: naam versus ding

Een naam is een sticker op een ding. Twee soorten "wijzigen":

```python
log = []             # sticker op een ANDER ding plakken → alleen hier merkbaar
log.append(10.0)     # op het ding ZELF schrijven → iedereen met dezelfde sticker ziet het
```

Daarom werkt `log = log or []`: meegegeven logboek blijft, anders een nieuw lijstje.
`log = []` altijd: gooit ook een bewust meegegeven logboek weg.

## Beschrijving bij een bestand, class of functie: docstring

```python
def chat(...):
    """Wat deze functie doet, in één zin."""
```

VSCodium toont hem als je met de muis over de naam beweegt.
