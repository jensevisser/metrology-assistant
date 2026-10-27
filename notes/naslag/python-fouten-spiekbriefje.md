# Python fouten — spiekbriefje

Fouten opvangen, gooien en vertalen. De rest van Python staat op [python-spiekbriefje.md](python-spiekbriefje.md).

**Inhoud**
- [Een fout opvangen met try, except en finally](#een-fout-opvangen-met-try-except-en-finally)
- [Waar een fout naartoe gaat (naar boven)](#waar-een-fout-naartoe-gaat-naar-boven)
- [Zelf een fout gooien met raise](#zelf-een-fout-gooien-met-raise)
- [Een eigen soort fout maken](#een-eigen-soort-fout-maken)
- [De stamboom van fouten en waarom nooit een kale except](#de-stamboom-van-fouten-en-waarom-nooit-een-kale-except)
- [Een fout vertalen met raise from](#een-fout-vertalen-met-raise-from)

## Een fout opvangen met try, except en finally

```python
try:
    uitkomst = a / b              # probeer dit
except ZeroDivisionError as e:    # alleen DEZE soort fout; e = de fout
    uitkomst = None
finally:
    opruimen()                    # draait altijd, ook na een fout
```

Meerdere `except`-regels: Python kijkt ze van boven naar beneden langs; de eerste die past, wint.
*Zie: `chat()`, regels 52–66 · rondleiding deel B.*

## Waar een fout naartoe gaat (naar boven)

```
  script            ← bovenste laag
    └─ niveau1()    ← riep niveau2 aan
         └─ niveau2()
              └─ niveau3()   ← hier gaat het mis
```

Een fout zonder passende `except` gaat terug naar de aanroeper, laag voor laag, tot een passende `except`. Elke laag zonder `except` stopt meteen. Nergens gevonden → het programma stopt met een traceback: bovenste laag eerst, waar het misging onderaan. Lees een traceback dus van onderen.
*Zie: rondleiding deel B · `../code/voorbeelden/naar_boven.py`.*

## Zelf een fout gooien met raise

```python
if waarde > 1000:
    raise ValueError(f"Waarde {waarde} V buiten bereik")   # maak een fout-object en gooi het
```

| | `return waarde` | `raise Fout(...)` |
|---|---|---|
| betekenis | klaar, hier is het resultaat | het lukt niet, iemand moet dit afhandelen |
| gaat naar | de aanroeper, als gewone waarde | naar boven, op zoek naar een `except` |

De functie stopt direct op de regel met `raise`.
*Zie: rondleiding deel C · `../code/voorbeelden/raise_demo.py bereik`.*

## Een eigen soort fout maken

```python
class LLMError(Exception):              # erft alles wat een fout kan
    """Fout bij het aanroepen van het LLM."""

class LLMTimeoutError(LLMError): ...    # familie: except LLMError vangt deze ook
class X(LLMError, TimeoutError): ...    # twee ouders: beide except-regels vangen hem (spaarzaam)
```

**De ouder bepaalt wie hem opvangt:** een `except` vangt de soort die erachter staat, én alles wat daarvan erft. Kies een ouder die past bij wat de fout ís.
*Zie: `LLMError`, regel 14 · rondleiding deel C · `../code/voorbeelden/erven.py`.*

## De stamboom van fouten en waarom nooit een kale except

```
BaseException             ← stamvader: een fout moet hiervan afstammen, anders TypeError
 ├─ Exception             ← alle gewone fouten: ValueError, KeyError, OSError (→ TimeoutError, ConnectionError), ...
 ├─ KeyboardInterrupt     ← Ctrl+C
 ├─ SystemExit            ← sys.exit()
 ├─ GeneratorExit         ← intern signaal
 └─ BaseExceptionGroup    ← meerdere fouten tegelijk (async)
```

Alles naast `Exception` zijn stopsignalen, geen fouten. **Nooit** een kale `except:` of `except BaseException:`: die vangt ook Ctrl+C en `sys.exit()`, en dan stopt je programma niet meer. Alle gewone fouten opvangen = `except Exception:`.

## Een fout vertalen met raise from

```python
try:
    float("OVLD")
except ValueError as e:
    raise MeetFout("Instrument gaf geen getal terug") from e   # "komt door e"
```

Een `raise` ín een `except` verlaat het hele `try/except`-blok: de andere `except`-regels van dat blok vangen hem niet; `finally` draait nog wel. De fout gaat naar de aanroeper.

| In een `except` | Traceback zegt | Gebruik |
|---|---|---|
| `raise X(...) from e` | "...was the direct cause of..." | **standaard**: bewuste vertaling |
| `raise X(...)` | "During handling ... another exception occurred" | vermijden: lijkt op een tweede, los probleem |
| `raise X(...) from None` | alleen de nieuwe fout | zelden: als de oorzaak niets toevoegt |

*Zie: `chat()`, regels 56–63 · rondleiding deel C · `../code/voorbeelden/raise_demo.py` en `raise_in_except.py`.*
