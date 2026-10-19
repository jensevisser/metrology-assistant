# Les 02b — Streaming, wachten en de koude start

## 1. Inleiding

**Waar we zijn:** nog steeds bij de pijlen tussen `chat()` en Ollama.

```
  5 vragen ──▶ meetlat ──▶ chat() ══▶ Ollama ──▶ model
                                  ◀══
                       deze les: hóé het antwoord terugkomt,
                       en hoe lang we erop wachten
```

**Wat je al weet:** een verzoek en een antwoord bestaan uit een statuscode, headers en een body met JSON, en `response.json()` maakt van de body een dict (`02a-vraag-en-antwoord-over-http.md`). Het model maakt zijn antwoord token voor token (`01a-tokens-en-genereren.md`).

**Waarom dit nu:** in het `curl`-commando van les 02a stond `"stream": false`, en die regel hebben we toen genegeerd. Laat je hem weg, dan breekt `response.json()`. En de meetlat moet weten hoe lang hij op een antwoord mag wachten, anders hangt hij of geeft hij vals alarm.

**Na deze les kun je:**
- uitleggen wat streaming is en waarom `response.json()` erop vastloopt;
- uitleggen wat een timeout is en een redelijke waarde kiezen;
- uitleggen waarom de eerste vraag na een pauze langzamer is dan de volgende.

**Nieuwe begrippen (3):** streaming · timeout · koude start.

## 2. Het probleem

Twee dingen die we echt zagen (19 oktober 2026):

1. Hetzelfde verzoek als in les 02a, maar zonder `"stream": false`. Daarna `response.json()`:
   ```
   JSONDecodeError -> Extra data: line 2 column 1 (char 128)
   ```
   Het antwoord kwam binnen, statuscode `200`, en toch kan Python het niet lezen.

2. Het model uit het videogeheugen gehaald, en daarna dezelfde vraag gesteld met de instructie "wacht maximaal 1 seconde":
   ```
   ReadTimeout -> timed out (na 1.01 s)
   ```
   Een paar seconden later, met het model weer geladen, duurde dezelfde vraag **0,04 seconde**.

Wat is "Extra data"? En waarom is dezelfde vraag het ene moment te traag voor 1 seconde en het andere moment binnen een twintigste seconde klaar?

## 3. Het idee in het kort

Ollama kan een antwoord op twee manieren terugsturen: in één keer als het helemaal klaar is, of in stukjes terwijl het gemaakt wordt. Dat tweede heet **streaming**, en dan is het antwoord geen enkel JSON-object meer maar een reeks. Daarom kiezen we voor de meetlat "in één keer". Daarnaast wacht de client nooit eindeloos, maar hooguit een ingestelde tijd, de **timeout**. Die tijd moet ruim genoeg zijn voor de **koude start**: de eerste vraag na een pauze, waarbij het model eerst in het videogeheugen geladen moet worden.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Twee manieren om een antwoord terug te sturen

Uit les 01a weet je dat het model zijn antwoord token voor token maakt. Ollama kan daar op twee manieren mee omgaan:

- **Wachten tot het klaar is, en dan alles in één keer sturen.** Je krijgt één JSON-object met het hele antwoord en alle meetgegevens. Dit is `"stream": false`.
- **Elk token meteen doorsturen zodra het er is.** Je krijgt een reeks kleine berichtjes. Dit is `"stream": true`, en dat is Ollama's **standaard**: als je niets zegt, krijg je dit.

Dat doorsturen-terwijl-het-gemaakt-wordt heet **streaming**.

### Stap 2 — Hoe een gestreamd antwoord eruitziet

Dit kwam er echt terug op "Zeg alleen: hallo", zonder `"stream": false`. Ingekort tot de belangrijkste velden:

```
{"model":"qwen3.5:9b", ... ,"message":{"role":"assistant","content":"hal"},"done":false}
{"model":"qwen3.5:9b", ... ,"message":{"role":"assistant","content":"lo"},"done":false}
{"model":"qwen3.5:9b", ... ,"message":{"role":"assistant","content":""},"done":true,"done_reason":"stop", ... ,"eval_count":3, ...}
```

Drie regels, drie losse JSON-objecten:
- regel 1: het eerste token, `hal`, met `"done":false` ("er komt nog meer");
- regel 2: het tweede token, `lo`;
- regel 3: het klaar-token. Lege inhoud, maar `"done":true`, en hier staan de meetgegevens die je uit les 02a kent.

Dit is les 01a letterlijk zichtbaar: elk rondje van het model wordt een eigen regel.

Zo'n tekst met één JSON-object per regel heeft een eigen naam: **NDJSON** (*newline-delimited JSON*, JSON gescheiden door nieuwe regels).

### Stap 3 — Waarom `response.json()` erop vastloopt

`response.json()` verwacht **één** JSON-object in de body. Het begint te lezen, vindt netjes het eerste object `{...}`, en dan staat er nóg iets: een nieuwe regel met een tweede object. Dat mag niet in één JSON-document. Vandaar de melding:

```
Extra data: line 2 column 1 (char 128)
```

In gewone taal: "op regel 2, positie 1 staat extra tekst die er niet hoort". Het eerste object was precies 128 tekens lang; daarna begon regel 2.

Let op: de statuscode was gewoon `200`. Het verzoek ging goed, Ollama deed wat het moest doen. Het probleem zit alleen in hoe wij de body lezen.

**Waarom bestaat streaming dan?** Voor een chatprogramma. Bij een antwoord van 500 tokens wacht je bij ongeveer 105 tokens per seconde (les 01a) zo'n 5 seconden. Met streaming zie je de eerste woorden na een fractie van een seconde verschijnen, en lees je mee terwijl de rest komt. Dat voelt veel sneller, ook al duurt het totaal even lang.

**Waarom wij het niet gebruiken:** de meetlat leest het antwoord niet mee, maar slaat het op. Eén compleet object met alle meetgegevens is dan veel eenvoudiger. Daarom zet `chat()` altijd `"stream": False` in het verzoek.

### Stap 4 — Hoe lang wacht de client? De timeout

Na het versturen wacht de client op het antwoord. Maar hoe lang? Als Ollama vastloopt of de verbinding wegvalt, wil je niet dat je script eeuwig blijft hangen. Daarom stel je een maximale wachttijd in: de **timeout**. Is die verstreken zonder antwoord, dan geeft de client op met een foutmelding.

- `httpx` heeft standaard een timeout van **5 seconden**. Zet je zelf niets, dan geldt die.
- Je stelt hem zelf in met `timeout=`, bijvoorbeeld `httpx.post(..., timeout=120)` voor 120 seconden.
- Verloopt de tijd terwijl de client op het antwoord wacht, dan krijg je een `ReadTimeout`. Dat zag je in het probleem: na 1,01 seconde gaf de client op.

Belangrijk: een timeout betekent "**ik** wacht niet langer", niet "het ging mis". Ollama was in dat voorbeeld gewoon gezond bezig met laden.

### Stap 5 — De koude start

Waarom duurde dezelfde vraag het ene moment te lang voor 1 seconde, en het andere moment maar 0,04 seconde?

Om te kunnen rekenen, moet het model, alle 9 miljard vaste getallen (les 01a), in het videogeheugen van je RTX 3080 staan. Bij `qwen3.5:9b` is dat 5,6 GB. Zit het model daar niet, dan laadt Ollama het eerst van de schijf. Dat laden heet de **koude start**. Ollama meldt de duur ervan in het veld `load_duration`.

Echte metingen:

| Moment | `load_duration` | totale tijd voor "hallo" |
|---|---|---|
| koud, 19 oktober | 2,55 s | 2,62 s |
| warm, direct daarna | 0,0005 s | 0,04 s |
| koud, 14 oktober (eerste meting) | 3,75 s | 4,30 s* |

\* Een andere, langere vraag (52 tokens antwoord), dus de totale tijd is niet één-op-één te vergelijken. De laadtijd wel.

Twee dingen vallen op:
- **Het laden kost bijna alle tijd.** Het antwoord zelf is in een paar honderdsten van een seconde klaar.
- **De laadtijd varieert:** 3,75 s tegenover 2,55 s. Een waarschijnlijke verklaring (niet gemeten): op 14 oktober kwam het model echt van de schijf, op 19 oktober stond het bestand nog in het werkgeheugen (RAM) van Linux, die recent gebruikte bestanden bewaart. Laden uit RAM is sneller dan van de schijf.

**Wanneer is het model koud?** Ollama haalt een model zelf weer uit het videogeheugen als het een tijdje niet gebruikt wordt, standaard na 5 minuten. Dat was te zien bij onze eerste aanroep op 14 oktober: `ollama ps` meldde toen *UNTIL 4 minutes from now*, de resterende tijd tot het model weer wordt weggehaald. Na een koffiepauze is je eerste vraag dus weer een koude start.

### Stap 6 — Een timeout kiezen

Nu kun je een redelijke timeout uitrekenen. Hij moet ruim genoeg zijn voor het slechtste normale geval: een koude start plus een lang antwoord.

- koude start: tot ongeveer 4 s (gemeten);
- een lang antwoord van 1000 tokens bij ongeveer 105 tokens per seconde: zo'n 10 s;
- samen ongeveer 14 s, en dan nog een flinke marge, want andere modellen of drukte op de GPU kunnen veel trager zijn.

`chat()` gebruikt daarom standaard **120 seconden**. Ruim, maar niet eindeloos.

## 5. Knoppen en keuzes

- **`stream`**: `true` voor een chatprogramma waarin je meeleest, `false` voor scripts en metingen. Wij: `false`.
- **`timeout`**:
  - **te kort** geeft vals alarm bij een gezonde maar trage aanroep, zoals een koude start;
  - **te lang** betekent dat je bij een echt probleem lang wacht voordat je het merkt.

  Wij: 120 s.
- **`keep_alive`**: een Ollama-instelling die bepaalt hoe lang een model na gebruik geladen blijft (standaard 5 minuten). Langer voorkomt koude starten, maar houdt videogeheugen bezet dat een ander programma misschien nodig heeft. Dat wordt belangrijk in Sprint 2, als vLLM en Ollama hetzelfde videogeheugen delen.
- **De koude start bij het meten.** Meet je snelheid, dan moet je weten of een aanroep koud of warm was, anders vergelijk je appels met peren. Daarom slaat de meetlat `load_duration` op. Een gangbare aanpak is één "opwarm"-aanroep vóór de eigenlijke meting; die keuze maken we in les 04.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| `JSONDecodeError: Extra data: line 2 column 1` | `stream` niet op `false`; de body is NDJSON |
| `ReadTimeout` bij de eerste vraag, daarna niet meer | koude start langer dan de timeout |
| Script hangt minutenlang zonder melding | geen timeout gezet in een library die standaard eeuwig wacht (zoals `requests`), of een veel te lange timeout |
| Eerste meting van een reeks veel trager dan de rest | koude start; zichtbaar aan `load_duration` |

**Uitgewerkt voorbeeld.** Je draait de meetlat 's ochtends, met de standaard-timeout van httpx (5 s) omdat je vergat er zelf een te zetten. De eerste vraag is een koude start van ongeveer 3 s, plus een antwoord van 300 tokens (bijna 3 s): totaal zo'n 6 s. `ReadTimeout`. Je denkt: "Ollama is kapot." Je draait het script meteen opnieuw, en nu werkt alles: het model was intussen geladen. Het probleem lijkt "vanzelf opgelost", maar komt morgenochtend terug. De echte oorzaak, een te korte timeout, zie je alleen als je weet dat de eerste aanroep koud was. Daarom: zelf een timeout zetten, en `load_duration` vastleggen.

## 7. Analogie

| Instrument | Ollama |
|---|---|
| een scope in **roll mode**: de samples verschijnen terwijl ze binnenkomen | `stream: true`: tokens verschijnen terwijl ze gemaakt worden |
| een **single shot**: na de acquisitie het hele record in één keer | `stream: false`: het hele antwoord in één keer |
| een VISA-**timeout** bij een multimeter op een lange integratietijd: het instrument is gezond, alleen je wachttijd is te kort | `ReadTimeout` bij een koude start |
| **opwarmtijd** van een instrument na inschakelen | koude start: het model moet eerst geladen worden |

**Waar de vergelijking ophoudt:**
- De opwarmtijd van een instrument gaat om **stabiliteit**: een koud instrument meet minder nauwkeurig, door drift. Een koud model geeft precies hetzelfde antwoord als een warm model, alleen later. Het gaat puur om tijd.
- Een instrument blijft warm zolang het aan staat. Ollama "zet het model uit" na 5 minuten niets doen, en dan begint de koude start opnieuw.

## 8. Samenvatting

**Kern:** zonder `"stream": false` stuurt Ollama elk token als een losse regel JSON (NDJSON), en `response.json()` kan dat niet lezen. Met `false` krijg je één compleet object, wat de meetlat nodig heeft. De client wacht hooguit de timeout; die moet ruim genoeg zijn voor een koude start, waarbij het model eerst in het videogeheugen wordt geladen (gemeten: 2,5 tot 3,8 s). Na 5 minuten niets doen is het model weer koud.

**Begrippen:**
- **Streaming**: het antwoord token voor token doorsturen terwijl het gemaakt wordt.
- **NDJSON**: één JSON-object per regel; zo ziet een gestreamd antwoord eruit.
- **Timeout**: de maximale tijd dat de client op een antwoord wacht.
- **Koude start**: het model moet eerst in het videogeheugen geladen worden; te zien aan `load_duration`.

**Knoppen:** `stream` · `timeout` · `keep_alive` · opwarmen vóór een snelheidsmeting.

**Foutmodi:** *Extra data* door streaming · `ReadTimeout` door een koude start · hangen zonder timeout · een vertekende eerste meting.

## 9. Wat we hiermee gaan bouwen

`chat()` zet al `"stream": False` en een timeout van 120 s, en dat begrijp je nu. In les 02c kijken we naar alles wat er mis kan gaan tussen `chat()` en Ollama: geen verbinding, een timeout, een foutcode, een onleesbaar antwoord. We zien hoe `chat()` elk van die fouten vertaalt naar een melding die zegt wat er aan de hand is. Daarna gaan we bouwen: tests die al die fouten bewust nabootsen.
