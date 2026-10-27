# Rondleiding `src/llm_client.py` — deel B: fouten opvangen

## 1. Inleiding

**Waar we zijn:** in de tweede helft van `chat()`. Die is te groot voor één keer, dus hij is verdeeld over drie delen:

```
  chat():
  1. verzoek opbouwen          (regels 43–49)   ← deel A
  2. verzoek versturen         (regels 50–55)   ← deel A
  3. fouten opvangen           (regels 52–66)   ← dit deel (B)
     fouten vertalen           (regels 56–63, en LLMError op regel 14)   ← deel C
  4. resultaat teruggeven      (regels 67–89, en ChatResult op regel 18)  ← deel D
```

**Wat je al weet:** hoe `chat()` het verzoek opbouwt en verstuurt (`llm_client-a.md`). De foutketen van vijf schakels uit les 02c (`../02c-wat-er-mis-kan-gaan.md`): verbinding, wachten, statuscode, JSON lezen en inhoud.

**Waarom dit deel:** les 02c vertelde wát `chat()` doet als het misgaat. Nu zie je hóé het opvangen van een fout in Python werkt, en waar dat in `chat()` staat.

**Na dit deel kun je:**
- `try / except / finally` lezen en zelf gebruiken;
- uitleggen waar een fout naartoe gaat als niemand hem opvangt;
- aanwijzen welke `except` in `chat()` bij welke schakel uit les 02c hoort.

**Python-constructies in dit deel (1):** `try / except / finally`, met als vervolg: waar een fout heen gaat ("naar boven").

Open [`src/llm_client.py`](../../src/llm_client.py) er weer naast. Op je spiekbriefje: `../naslag/python-fouten-spiekbriefje.md`.

## 2. Een fout opvangen: `try / except / finally` *(nieuwe constructie)*

Als er in Python iets misgaat, stopt het programma met een foutmelding (les 02c). Met `try` kun je dat voorkomen:
- **`try`**: "probeer dit stuk";
- **`except`**: "gaat het mis met deze soort fout, doe dan dit in plaats van te stoppen";
- **`finally`**: "en dit doe je **altijd** aan het eind, of het nu goed ging of niet".

**Klein los voorbeeld** (echt gedraaid):

```python
def deel(a, b):
    try:
        uitkomst = a / b
    except ZeroDivisionError:
        print("delen door nul")
        uitkomst = None
    finally:
        print("finally draait altijd")
    return uitkomst

print(deel(10, 2))
print(deel(10, 0))
```

```
finally draait altijd
5.0
delen door nul
finally draait altijd
None
```

- `deel(10, 2)`: het `try`-deel lukt, `except` wordt overgeslagen, `finally` draait.
- `deel(10, 0)`: delen door nul geeft een fout van de soort `ZeroDivisionError`. Python springt naar het `except` voor die soort, en daarna draait `finally` ook.

Twee dingen om te onthouden:
1. Achter `except` staat **welke soort** fout je opvangt. Een andere soort wordt níet opgevangen.
2. Met **`except ZeroDivisionError as e`** geef je de opgevangen fout een naam, `e`, zodat je er daarna iets mee kunt, bijvoorbeeld de melding uitlezen.

## 3. Waar een fout naartoe gaat: "naar boven"

Wat gebeurt er met een fout die níet wordt opgevangen?

Binnen een functie loopt de code van boven naar beneden. Maar functies roepen elkaar aan, en dat vormt een keten van lagen:

```
  het script zelf                ← bovenste laag: hier begon het
    └─ niveau1()                 ← riep niveau2 aan
         └─ niveau2()            ← riep niveau3 aan
              └─ niveau3()       ← onderste laag: hier gaat het mis
```

Gaat het mis in `niveau3()`, dan zoekt Python een passende `except`: eerst in `niveau3()` zelf, dan bij wie hem aanriep (`niveau2()`), dan `niveau1()`, enzovoort. **"Naar boven" betekent: terug naar de aanroeper**, niet omhoog in het bestand.

- Elke laag zonder passende `except` stopt meteen; de regels daarna worden niet meer uitgevoerd.
- Vindt de fout in een laag wél een passende `except`, dan wordt hij daar opgevangen, en loopt het programma vanaf daar verder.
- Vindt de fout nergens een passende `except`, dan stopt het hele programma met een traceback.

Die traceback is de keten op papier: de bovenste laag eerst, en waar het misging onderaan (*"most recent call last"*). Echte uitvoer van een voorbeeld met deze drie functies, zonder `try`:

```
Traceback (most recent call last):
  File "naar_boven.py", line 20, in <module>   ← het script
  File "naar_boven.py", line 7, in niveau2     ← riep niveau3 aan
  File "naar_boven.py", line 3, in niveau3     ← hier ging het mis
ZeroDivisionError: division by zero
```

Daarom lees je een traceback van onderen (les 02c): daar staat wat er misging.

In ons project ziet de keten er straks zo uit:

```
  meetlat (straks)          ← vangt LLMError op, noteert, gaat door
    └─ chat()               ← vangt httpx-fouten op (dit deel)
         └─ http.post()
              └─ netwerkcode  ← hier gaat het mis (bijv. ConnectError)
```

**Vergelijking:** een storingsmelding gaat omhoog, van monteur naar teamleider naar afdelingshoofd, tot iemand hem kan afhandelen. Kan niemand dat, dan gaat de lijn stil. Waar de vergelijking ophoudt: in een bedrijf kan iedereen de melding even bekijken. In Python slaat een laag zonder passende `except` de fout gewoon over; die laag stopt alleen zelf ook.

## 4. In onze code: regels 52–66

```python
    try:
        response = http.post("/api/chat", json=payload)    # schakel 1 en 2
        response.raise_for_status()                          # schakel 3
        data = response.json()                               # schakel 4
    except httpx.TimeoutException as e:
        ...
    except httpx.ConnectError as e:
        ...
    except httpx.HTTPStatusError as e:
        ...
    except ValueError as e:
        ...
    finally:
        if client is None:
            http.close()
```

Wat er bij de `...` staat, is voor deel C. Nu gaat het om de vorm.

**Het `try`-deel** bevat de drie regels uit deel A, plus `raise_for_status()`. Samen zijn dat de schakels 1 tot en met 4 uit les 02c. `raise_for_status()` maakt van een statuscode die geen 2xx is (bijv. een `404`) een fout; zonder die regel zou httpx een `404` gewoon als antwoord teruggeven (les 02c, stap 2).

**Er zijn vier `except`-regels**, één per schakel. Python kijkt ze van boven naar beneden langs, en de eerste die past, wordt uitgevoerd:

| `except` | Schakel uit les 02c |
|---|---|
| `httpx.TimeoutException` | 2: wachten duurde langer dan de timeout |
| `httpx.ConnectError` | 1: geen verbinding |
| `httpx.HTTPStatusError` | 3: statuscode is geen 2xx |
| `ValueError` | 4: geen geldige JSON. De JSON-fout uit les 02b (`JSONDecodeError`) is een soort `ValueError` (gecontroleerd) |

Hoe het kan dat één `except` meerdere fouten opvangt (`TimeoutException` vangt zowel `ReadTimeout` als `ConnectTimeout`), zie je in deel C.

**Het `finally`-deel** sluit de verbinding. Een `httpx.Client` moet je sluiten als je klaar bent (deel A). Omdat het in `finally` staat, gebeurt dat **ook** als er een fout optrad. Anders bleef er bij elke mislukte aanroep een verbinding openstaan.

Waarom `if client is None`? Alleen een client die `chat()` **zelf** heeft gemaakt, sluit `chat()` ook zelf. Een client die je meegeeft (in de tests) is van jou, en die sluit je zelf. Het principe: wie hem opent, sluit hem.

## 5. Zelf proberen

Het voorbeeld met de drie lagen staat in [`voorbeelden/naar_boven.py`](voorbeelden/naar_boven.py). Draai het in de projectmap:

```bash
uv run python notes/code/voorbeelden/naar_boven.py
```

Let op welke `print`-regels wél en níet verschijnen, en vergelijk de traceback met het lagenschema in sectie 3.

## 6. Samenvatting

- **`try / except / finally`:** probeer iets; vang een bepaalde soort fout op; ruim altijd op.
- **`except Soort as e`:** vang alleen deze soort op, en geef hem de naam `e`.
- **"Naar boven":** een fout die niet wordt opgevangen, gaat terug naar de aanroeper, laag voor laag, tot een passende `except`. Vindt hij er geen, dan stopt het programma met een traceback: bovenste laag eerst, waar het misging onderaan.
- **In `chat()`:** het `try`-deel bevat de schakels 1–4, er is één `except` per schakel, en `finally` sluit altijd de verbinding die `chat()` zelf opende.

## 7. Wat komt in deel C

Wat er bij de `...` in de `except`-regels staat: daar gooit `chat()` zelf een nieuwe fout, `LLMError`. In deel C zie je hoe je zelf een fout gooit (`raise`), hoe je een eigen soort fout maakt, en hoe je een fout vertaalt naar een leesbare melding zonder de oorzaak kwijt te raken (`raise ... from e`).
