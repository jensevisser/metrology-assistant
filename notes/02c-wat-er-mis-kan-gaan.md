# Les 02c — Wat er mis kan gaan, en hoe `chat()` het meldt

## 1. Inleiding

**Waar we zijn:** het laatste deel over de pijlen tussen `chat()` en Ollama.

```
  5 vragen ──▶ meetlat ──▶ chat() ══▶ Ollama ──▶ model
                                  ◀══
                       deze les: wat er onderweg mis kan gaan
```

**Wat je al weet:** hoe een verzoek en een antwoord eruitzien, met de statuscode (`02a-vraag-en-antwoord-over-http.md`), waarom we `"stream": false` sturen en wat een timeout en een koude start zijn (`02b-streaming-en-timeouts.md`).

**Waarom dit nu:** de meetlat gaat straks tientallen vragen achter elkaar stellen. Gaat er bij vraag 17 iets mis, dan wil je in één oogopslag weten wát, en niet een halfuur in een foutmelding van zestig regels zoeken. Bovendien is deze les het testplan voor de eerstvolgende bouwstap.

**Na deze les kun je:**
- de vijf plekken noemen waar het mis kan gaan tussen `chat()` en Ollama;
- uitleggen waarom `chat()` alle fouten vertaalt naar één eigen soort fout, met een leesbare melding;
- een lange Python-foutmelding lezen: van onderen, laag voor laag.

**Nieuwe begrippen (3):** de foutketen · een eigen fouttype · de oorzaak bewaren.

## 2. Het probleem

Een echte meting (19 oktober 2026). We stuurden een verzoek naar een poort waar niets luistert, zoals wanneer Ollama niet draait. Eén keer rechtstreeks met `httpx`, één keer via `chat()`.

**Rechtstreeks met httpx** krijg je 61 regels, die eindigen met:

```
httpx.ConnectError: [Errno 111] Connection refused
```

**Via `chat()`** krijg je 68 regels, die eindigen met:

```
src.llm_client.LLMError: Geen verbinding met Ollama op http://localhost:11999; draait de server?
```

Twee dingen vallen op:
1. De eerste melding is technisch juist, maar zegt niet wat je moet doen. "Errno 111"? "Connection refused" door wie?
   (*Errno* is *error number*: een foutnummer dat Linux zelf teruggeeft. 111 betekent op Linux "verbinding geweigerd": op die poort luistert niets. Python geeft het nummer door zoals het binnenkomt.)
2. De tweede melding is in gewone taal en wijst de waarschijnlijke oorzaak aan. Maar ze is **langer**, niet korter.

Waarom is dat langer, en waarom is dat juist goed? En wat kan er nog meer misgaan?

## 3. Het idee in het kort

Tussen `chat()` en een bruikbaar antwoord zitten vijf schakels, en elke schakel kan op zijn eigen manier falen. `chat()` vangt elke fout op, en geeft in plaats daarvan één eigen soort fout, `LLMError`, met een melding die zegt wat er waarschijnlijk aan de hand is. De originele, technische fout gooit hij niet weg, maar bewaart hij als oorzaak. Je krijgt beide op je scherm, in deze volgorde: **bovenaan de technische oorzaak, onderaan de leesbare melding.** Een foutmelding lees je dus van onder naar boven; in stap 4 staat hoe.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Wat een fout in Python is

Als er in Python iets misgaat dat het programma niet zelf kan oplossen, stopt het met een **foutmelding**. De vakterm is *exception*. Zo'n fout heeft twee dingen:
- een **soort** (type), bijvoorbeeld `ConnectError` of `ReadTimeout`;
- een **tekst** met details, bijvoorbeeld `Connection refused`.

Code kan een fout ook **opvangen**: "als hier een fout van soort X optreedt, doe dan dit in plaats van te stoppen". Hoe je dat in Python schrijft, komt in de bouwstap. Voor nu is het idee genoeg.

### Stap 2 — De foutketen: vijf schakels

Van het versturen van de vraag tot een bruikbaar antwoord gaat het door vijf schakels. Elke schakel kan falen:

| # | Schakel | Wat gaat er mis | Soort fout van httpx |
|---|---|---|---|
| 1 | **verbinding maken** | Ollama draait niet, of verkeerd poortnummer | `ConnectError` |
| 2 | **wachten op het antwoord** | koude start of lang antwoord duurt langer dan de timeout (les 02b) | `ReadTimeout` |
| 3 | **statuscode controleren** | model bestaat niet (`404`), kapot verzoek (`400`), fout in Ollama (`5xx`) (les 02a) | `HTTPStatusError` |
| 4 | **JSON lezen** | de body is geen geldig JSON, bijvoorbeeld door streaming (les 02b) | `JSONDecodeError` |
| 5 | **inhoud controleren** | geldig JSON, maar het verwachte veld `message.content` ontbreekt | geen: dit controleert `chat()` zelf |

Die volgorde is niet toevallig. Elke schakel kan pas als de vorige gelukt is: zonder verbinding geen antwoord, zonder antwoord geen statuscode, enzovoort. Faalt schakel 1, dan kom je nooit bij schakel 4.

Let op schakel 3: httpx vindt een `404` uit zichzelf géén fout. Er kwam immers netjes een antwoord terug. Pas als je httpx expliciet vraagt de statuscode te controleren, maakt het er een fout van. `chat()` doet dat met `response.raise_for_status()`: "is de statuscode geen 2xx, maak er dan een fout van". Zonder die regel zou een `404` pas bij schakel 5 opvallen, als `message` ontbreekt, en dan wijst de melding naar de verkeerde schakel.

### Stap 3 — Eén eigen soort fout: `LLMError`

`chat()` vangt de fouten van alle vijf schakels op, en gooit in plaats daarvan steeds dezelfde soort fout: **`LLMError`**. Die soort hebben we zelf gemaakt, in `src/llm_client.py`. De tekst verschilt per schakel en zegt wat er waarschijnlijk aan de hand is.

Echte meldingen van `chat()`:

| Schakel | Melding |
|---|---|
| 1 verbinding | `Geen verbinding met Ollama op http://localhost:11999; draait de server?` |
| 2 wachten | `Timeout na 1 s (koude start? model te groot?)` |
| 3 status | `HTTP 404: {"error":"model 'bestaatniet' not found"}` |
| 4 JSON | `Antwoord is geen geldige JSON (stream per ongeluk aan?)` |
| 5 inhoud | `Onverwacht antwoord, geen message.content: {...}` |

De meldingen voor schakel 1, 2 en 3 zijn echt gemeten. Die voor 4 en 5 zijn de teksten uit de code: met de echte Ollama krijg je die fouten bijna niet voor elkaar, omdat `chat()` zelf `"stream": false` meestuurt en Ollama altijd een `message` teruggeeft. Juist daarom gaan we ze straks nabootsen in tests.

**Waarom één eigen soort, en niet gewoon de fouten van httpx doorlaten?** Om twee redenen:
1. **Leesbaarheid.** "Geen verbinding met Ollama; draait de server?" zegt wat je moet controleren. "Errno 111" niet.
2. **Eén plek om op te vangen.** De meetlat hoeft straks maar één soort fout te kennen. Gaat er bij vraag 17 iets mis, dan vangt hij een `LLMError`, noteert hij de melding in de resultaten en gaat hij door met vraag 18. Zonder eigen soort zou de meetlat vijf verschillende httpx-fouten moeten kennen, en bij het overstappen naar de OpenAI-route (les 05) misschien weer andere.

### Stap 4 — De oorzaak bewaren, en een foutmelding van onderen lezen

Nu het raadsel uit het begin: waarom is de melding van `chat()` langer?

Omdat `chat()` de originele fout niet weggooit, maar meegeeft als **oorzaak** van de `LLMError`. Python toont dan alle lagen onder elkaar. De echte melding van 68 regels heeft deze opbouw:

```
Traceback (most recent call last):
  ...                                            ← laag 1: diep in de netwerkcode
httpcore.ConnectError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...                                            ← laag 2: httpx vertaalt het
httpx.ConnectError: [Errno 111] Connection refused

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...                                            ← laag 3: chat() vertaalt het
src.llm_client.LLMError: Geen verbinding met Ollama op http://localhost:11999; draait de server?
```

*"The above exception was the direct cause of the following exception"* betekent: "de fout hierboven was de oorzaak van de fout hieronder".

Zo lees je zo'n melding:
1. **Begin onderaan.** De laatste regel is de fout zoals hij uiteindelijk bovenkwam. Bij `chat()` is dat de leesbare melding. Vaak weet je hiermee al genoeg.
2. **Heb je meer nodig, ga dan een laag omhoog.** Daar staat de technische oorzaak, hier `httpx.ConnectError`.
3. **Pas als je echt diep moet zoeken,** bijvoorbeeld bij een fout in httpx zelf, lees je de regels met bestandsnamen en regelnummers erboven.

Bewaren kost dus wat extra regels, maar je verliest niets: **onderaan** staat het antwoord voor de gebruiker, **erboven** het bewijs voor wie wil debuggen. Python zet het zo omdat de oudste fout als eerste gebeurde; hij vertelt het verhaal op volgorde van de tijd, niet op volgorde van belang.

### Stap 5 — Luid falen, nooit stil

Er is ook een verkeerde manier om fouten op te vangen: ze **inslikken**. Bijvoorbeeld: "als er een fout is, doe dan niets en ga door". Het script crasht niet meer, en dat voelt als een oplossing.

Maar de fout is niet weg, alleen onzichtbaar. Vraag 17 heeft dan geen antwoord, en de meetlat telt dat misschien als "model wist het niet", terwijl Ollama even niet bereikbaar was. Je meetresultaat klopt dan niet, en je weet het niet eens.

`chat()` doet daarom het omgekeerde: elke fout komt **luid** naar boven, als `LLMError` met een duidelijke melding. Wat ermee moet gebeuren (stoppen, of noteren en doorgaan), beslist de code die `chat()` aanroept, zoals straks de meetlat. Maar nooit stilletjes.

## 5. Knoppen en keuzes

- **Hoe specifiek moet de melding zijn?** Specifiek genoeg om te weten waar je moet kijken ("draait de server?"), maar zonder te doen alsof je het zeker weet. Daarom staan er vraagtekens in: "koude start? model te groot?". Het zijn waarschijnlijke oorzaken, geen diagnoses.
- **Eén eigen soort fout, of één per schakel?** Je zou ook `LLMConnectError`, `LLMTimeoutError` enzovoort kunnen maken. Dat is nuttig als de code die `chat()` aanroept per soort iets anders moet doen, bijvoorbeeld bij een timeout nog één keer opnieuw proberen. Voor de meetlat is één soort genoeg. Hebben we later meer nodig, dan splitsen we.
- **Vangen of doorlaten in de meetlat?** Voor de nulmeting kiezen we: vangen, de melding noteren bij die vraag, en doorgaan. Zo verlies je bij één haperende vraag niet de hele run. Die keuze maken we definitief in les 04.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| Een `404` valt pas op als `KeyError: 'message'` | `raise_for_status()` vergeten; schakel 3 overgeslagen |
| Script loopt door, maar antwoorden ontbreken in de resultaten | fouten ingeslikt in plaats van gemeld |
| Melding zegt "geen geldige JSON", maar de echte oorzaak is een timeout | opvangen in de verkeerde volgorde, of één brede vangst voor alles |
| Alleen "Errno 111" en je weet niet wat te doen | technische fout niet vertaald naar een leesbare melding |
| Leesbare melding, maar de technische oorzaak is weg | eigen fout gemaakt zonder de originele als oorzaak te bewaren |

**Uitgewerkt voorbeeld.** Stel, iemand schrijft de foutafhandeling zo: "bij elke fout: geef een lege tekst terug". De meetlat draait vijf vragen. Bij vraag 3 is Ollama net aan het herstarten, en `chat()` geeft een lege tekst terug in plaats van een fout. In de resultaten staat bij vraag 3 een leeg antwoord. Bij het beoordelen schrijf je "fout: model gaf geen antwoord" en tel je het mee in de nulmeting. Die is nu te slecht, door een netwerkhapering die niets met het model te maken heeft. En niemand ziet het, want er was geen foutmelding. Met `LLMError` had in de resultaten gestaan: *"Geen verbinding met Ollama; draait de server?"*, en had je vraag 3 opnieuw gedraaid in plaats van hem fout te rekenen.

## 7. Analogie

**De foutketen lijkt op storingzoeken in een meetopstelling.** Bron, kabel, connector, instrument, uitlezing: geeft het display niets, dan loop je de keten af, en elke schakel kan pas werken als de vorige werkt. `chat()` doet dat zoeken voor je en meldt bij welke schakel het stokte.

**Het eigen fouttype lijkt op een foutcode op het display van een instrument**, zoals `OVLD` of `Err 21: reference unstable`. Die zegt de gebruiker wat er aan de hand is, zonder de interne schakeling te tonen. De oorzaak bewaren lijkt op de servicehandleiding: daarin vindt de technicus welke component erachter zit.

**Waar de vergelijking ophoudt:**
- De foutcodes van een instrument zijn vast door de fabrikant bepaald. Onze meldingen schrijven we zelf, en we moeten ze bijwerken als er nieuwe manieren van falen bijkomen.
- Een instrument toont alleen de code. Een Python-foutmelding met bewaarde oorzaak bevat het complete pad tot op de regel code. Dat is meer dan een servicehandleiding je meestal geeft.

## 8. Samenvatting

**Kern:** tussen `chat()` en een bruikbaar antwoord zitten vijf schakels: verbinding, wachten, statuscode, JSON lezen en inhoud. Elke schakel kan op zijn eigen manier falen. `chat()` vertaalt elke fout naar één eigen soort fout, `LLMError`, met een leesbare melding, en bewaart de originele fout als oorzaak. Een foutmelding lees je van onderen. Fouten worden altijd luid gemeld, nooit ingeslikt.

**Begrippen:**
- **Foutmelding** (*exception*): een fout met een soort en een tekst, die het programma stopt tenzij code hem opvangt.
- **Foutketen**: de vijf schakels waar het mis kan gaan, elk afhankelijk van de vorige.
- **Eigen fouttype** (`LLMError`): één soort fout voor alle schakels, met een melding in gewone taal.
- **Oorzaak bewaren**: de originele fout meegeven, zodat Python alle lagen toont ("direct cause").

**Knoppen:** hoe specifiek de melding is · één eigen soort of één per schakel · vangen of doorlaten in de meetlat.

**Foutmodi:** `raise_for_status()` vergeten · fouten inslikken · één brede vangst · onvertaalde technische fout · oorzaak weggegooid.

## 9. Wat we hiermee gaan bouwen

De tabel in stap 2 is ons testplan. In bouwstap 2 schrijven we tests met een **nep-server**: een stukje code dat zich voordoet als Ollama, maar precies het antwoord geeft dat wij willen, ook een kapot antwoord. Zo bootsen we alle vijf schakels na, ook schakel 4 en 5 die de echte Ollama bijna nooit laat zien, en controleren we dat `chat()` telkens een `LLMError` met de juiste melding geeft. Zo'n test werkt zonder dat Ollama draait. Eerst gaan we terug naar bouwstap 1: jij draait de `ChatResult`-versie van `chat()`, en ik leg de code rustig uit.
