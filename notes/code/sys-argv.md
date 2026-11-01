# Zijpad: woorden meegeven op de opdrachtregel (`sys.argv`)

## 1. Inleiding

**Waar dit vandaan komt:** uit regel 30 van [`voorbeelden/raise_demo.py`](voorbeelden/raise_demo.py). Dat is geen projectcode, maar het keuzeknopje van een demobestand. Toch kom je `sys.argv` overal tegen, dus hier de rustige versie.

**Wat je al weet:** dat een functie pas iets doet als je hem aanroept, en dat de waarde tussen de haakjes naar binnen gaat (`hoe_komt_er_iets_in.py`). Dit is hetzelfde idee, maar dan voor een heel bestand in plaats van één functie.

**Na dit stuk kun je:**
- uitleggen wat `sys.argv` is en waarom `[0]` het bestand zelf is;
- een script schrijven dat met een ander woord erachter iets anders doet;
- de twee valkuilen herkennen: alles is tekst, en spaties splitsen.

**Nieuwe begrippen (2):** argument op de opdrachtregel · `sys.argv`.

## 2. Het probleem

Je hebt een scriptje dat een vraag naar het model stuurt:

```python
vraag = "Wat is vLLM?"
```

Wil je een andere vraag stellen, dan open je het bestand, verandert die regel, slaat op, en draait opnieuw. Bij drie vragen is dat vervelend. Bij twintig ga je fouten maken, en je weet achteraf niet meer welke versie van het bestand welke uitvoer gaf.

Wat je wilt is: het bestand blijft zoals het is, en je zegt bij het starten wat er anders moet.

## 3. Het idee in het kort

Alles wat je achter de bestandsnaam typt, geeft Python aan je programma door als een lijst met woorden. Die lijst heet `sys.argv`. Je programma kan hem uitlezen en zich erop aanpassen. Zo wordt één bestand bruikbaar voor veel gevallen, zonder het te wijzigen.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — de lijst bekijken

Het hele bestand [`voorbeelden/argumenten.py`](voorbeelden/argumenten.py):

```python
import sys

print(f"aantal:  {len(sys.argv)}")
for i, woord in enumerate(sys.argv):
    print(f"  argv[{i}] = {woord!r}")
```

`enumerate` geeft bij elk element ook het nummer, zodat je `argv[0]`, `argv[1]` ... kunt tonen. De `!r` in de f-string zet aanhalingstekens om de waarde, zodat je ziet dat het tekst is.

Draai hem zonder iets erachter (echt gedraaid):

```
$ uv run python argumenten.py
aantal:  1
  argv[0] = 'argumenten.py'
```

Eén element. **`sys.argv[0]` is altijd het bestand zelf**, ook als je verder niets typt. De lijst is dus nooit leeg.

### Stap 2 — woorden toevoegen

```
$ uv run python argumenten.py qwen3.5:9b 0.2
aantal:  3
  argv[0] = 'argumenten.py'
  argv[1] = 'qwen3.5:9b'
  argv[2] = '0.2'
```

Elk woord dat je typt, wordt een volgend element. Jouw eerste woord is dus altijd `sys.argv[1]`, niet `[0]`.

Let op `'0.2'` met aanhalingstekens: het is **tekst**, geen getal. Daarover meer in sectie 6.

### Stap 3 — spaties splitsen, aanhalingstekens plakken

```
$ uv run python argumenten.py Wat is vLLM?
aantal:  4
  argv[1] = 'Wat'
  argv[2] = 'is'
  argv[3] = 'vLLM?'
```

Drie losse woorden. De shell knipt op spaties, nog voordat Python iets ziet. Wil je één zin doorgeven, zet er dan aanhalingstekens omheen:

```
$ uv run python argumenten.py "Wat is vLLM?"
aantal:  2
  argv[1] = 'Wat is vLLM?'
```

### Stap 4 — ermee kiezen

Nu de regel uit `raise_demo.py`:

```python
keuze = sys.argv[1] if len(sys.argv) > 1 else "from"
```

- `len(sys.argv) > 1` betekent: staat er meer in de lijst dan alleen de bestandsnaam? Oftewel: heb ik iets getypt?
- Zo ja, neem dat woord. Zo nee, neem de standaardwaarde `"from"`.

Daarom kreeg je de `from`-variant toen je niets typte. Zie ook *Keuze op één regel* op het [Python-spiekbriefje](../naslag/python-spiekbriefje.md).

## 5. Knoppen en keuzes

**Eén of twee knopjes:** `sys.argv` rechtstreeks uitlezen is prima. Kort, geen extra pakket.

**Meer dan dat:** dan wil je `--model qwen3.5:4b --temperature 0.2`, met een `--help` die uitlegt wat er kan, en een nette foutmelding bij een typefout. Dat ga je niet zelf bouwen. Python heeft daar `argparse` voor, in de standaardbibliotheek. Zonder hulp ziet een streepje er voor `sys.argv` namelijk uit als zomaar een woord:

```
$ uv run python argumenten.py --model qwen3.5:4b
aantal:  3
  argv[1] = '--model'
  argv[2] = 'qwen3.5:4b'
```

Twee losse woorden; dat `--model` bij `qwen3.5:4b` hoort, moet je zelf uitzoeken. `argparse` doet dat voor je.

**Wat wij doen:** in `src/` komt `sys.argv` niet voor. Daar gaan waarden via parameters (`chat(model, messages, ...)`) en straks via config naar binnen. De opdrachtregel is iets voor scripts die je aanroept, niet voor code die door andere code wordt gebruikt. Bij bouwstap 4 (`src/run_baseline.py`) komt deze vraag terug: dat is wél een script, en dan kiezen we tussen `sys.argv`, `argparse` en alles in een configbestand.

## 6. Waar het misgaat

**Symptoom:** `IndexError: list index out of range`

```
$ uv run python -c "import sys; print(sys.argv[1])"
Traceback (most recent call last):
  File "<string>", line 3, in <module>
IndexError: list index out of range
```

**Oorzaak:** je vroeg om `[1]`, maar er is alleen `[0]`. Je typte geen argument.
**Voorkomen:** eerst `len(sys.argv) > 1` controleren, zoals in stap 4. Dat is precies waarom die regel in `raise_demo.py` zo omslachtig lijkt.

**Symptoom:** `TypeError: '>' not supported between instances of 'str' and 'int'`, of een vergelijking die onzin oplevert.
**Oorzaak:** alles uit `sys.argv` is tekst. `"1500" > 1000` is geen geldige vergelijking, en `"0.2" * 2` geeft `'0.20.2'` in plaats van `0.4`.
**Voorkomen:** zelf omzetten: `float(sys.argv[1])` of `int(sys.argv[1])`. Zie `hoe_komt_er_iets_in.py`, waar `float(getypt)` staat.

**Symptoom:** je zin komt als losse woorden binnen.
**Oorzaak:** de shell splitst op spaties (stap 3).
**Voorkomen:** aanhalingstekens om de zin.

## 7. Zelf proberen

```bash
cd notes/code/voorbeelden
uv run python argumenten.py
uv run python argumenten.py qwen3.5:9b 0.2
uv run python argumenten.py "Wat is vLLM?"
```

De uitvoer staat in sectie 4. Daarna de foutmodus uitlokken:

```bash
uv run python -c "import sys; print(sys.argv[1])"
```

## 8. Analogie

Een meetprogramma waarin het kanaalnummer vast in de code staat, is als een testopstelling waarbij je de bedrading moet omsolderen voor een ander kanaal. `sys.argv` is het frontpaneel: dezelfde kast, maar je stelt bij het starten in wat er moet gebeuren.

Waar de vergelijking ophoudt: een frontpaneel kun je tijdens het meten nog verdraaien. `sys.argv` lees je één keer bij de start; daarna ligt het vast tot je het programma opnieuw draait.

## 9. Samenvatting

- **Kern:** `sys.argv` is de lijst woorden die je op de opdrachtregel typte. `[0]` is het bestand zelf, `[1]` is jouw eerste woord. Zo past één script zich aan zonder dat je hem openmaakt.
- **Begrippen:** *argument* = een woord dat je bij het starten meegeeft · *`sys.argv`* = de lijst waarin ze terechtkomen.
- **Knoppen:** zelf uitlezen bij één of twee waarden; `argparse` zodra je `--opties` en een `--help` wilt.
- **Foutmodi:** `IndexError` als je niets typte · alles is tekst, dus zelf omzetten · spaties splitsen, tenzij je aanhalingstekens gebruikt.
