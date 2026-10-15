# Les 01 — Wat een LLM doet bij één aanroep

## 1. Wat je al weet

Dit is de eerste les. Je hebt Ollama via de CLI gebruikt, en we hebben vanuit Python al één aanroep gedaan met `chat()` uit `src/llm_client.py`. Deze les legt uit wat er bínnen die ene aanroep gebeurt.

## 2. Het probleem

We stuurden `qwen3.5:9b` de vraag *"Wat is vLLM? Antwoord in één zin."* Ollama gaf dit terug (echte meting, 14 oktober 2026):

| Veld | Waarde |
|---|---|
| `prompt_eval_count` (tokens in) | 24 |
| `eval_count` (tokens uit) | 52 |
| `load_duration` | 3,75 s |
| `prompt_eval_duration` | 0,055 s |
| `eval_duration` | 0,50 s |
| `total_duration` | 4,30 s |

En `ollama show qwen3.5:9b` meldt *context length 262144*, terwijl `ollama ps` direct daarna *CONTEXT 4096* laat zien.

Zonder een beeld van wat een LLM doet, zijn dit raadsels:
- Waarom 24 tokens in, terwijl de vraag 7 woorden heeft?
- Waarom duurt laden 7× langer dan antwoorden?
- Waarom gaat de invoer (24 tokens in 0,055 s) zoveel sneller per token dan de uitvoer (52 tokens in 0,50 s)?
- Welk context window geldt nu: 262.144 of 4096?
- En: het antwoord klinkt overtuigend, maar hoe weet het model het? Wat als het het níet weet?

Elke latere stap hangt hieraan. RAG bijvoorbeeld draait om de vraag hoeveel tekst je in het venster kwijt kunt en waarom het model zonder bronnen dingen verzint.

## 3. Het idee in het kort

Een LLM is een functie: er gaat een rij **tokens** in, en er komt een **kansverdeling** uit over welk token er nu volgt. Kies één token, plak het achter de rij en vraag opnieuw: zo ontstaat tekst, token voor token. Alles wat het model over jouw gesprek "weet", zit in die ene rij tokens, en die rij heeft een maximale lengte: het **context window**. Het model zoekt niets op. Het voorspelt een waarschijnlijke voortzetting op basis van wat het tijdens de training heeft gezien.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Van tekst naar tokens

Het model rekent met getallen, niet met letters. Een **tokenizer** knipt tekst daarom in stukjes uit een vaste lijst, de **vocabulaire**. Elk stukje (token) heeft een nummer (token-ID). Voor Qwen-modellen bevat die lijst ruim honderdduizend stukjes.

- Veelvoorkomende Engelse woorden zijn vaak één token: `the`, `model`.
- Zeldzame woorden, Nederlands, code en getallen worden in meer stukjes geknipt. Ter illustratie (de precieze knippen verschillen per tokenizer): `kalibratie` → `kal` · `ib` · `ratie`.
- Echte meting met `qwen3.5:9b`: het antwoord `hallo` kwam gestreamd binnen als `hal` + `lo`, plus het stop-token: `eval_count: 3` (zie les 02).
- Spaties en leestekens tellen mee, vaak als deel van een token.

Vuistregel voor Engels: één token ≈ 4 tekens ≈ ¾ woord. Nederlands kost doorgaans meer tokens per woord. Dat is een vuistregel, geen meting; tellen doe je met `prompt_eval_count`.

Waarom stukjes en geen hele woorden? Met een vaste lijst stukjes kun je élk woord maken, ook woorden die nooit in de training voorkwamen.

### Stap 2 — Van messages naar één rij tokens

Je stuurt een lijst `messages` met rollen (`system`, `user`, `assistant`). Het model zelf kent geen rollen; het ziet alleen één doorlopende rij tokens. Ollama zet de messages daarom met een **chat template** om in één tekst met speciale markeringen, zoals "hier begint een bericht van de gebruiker" en "hier begint het antwoord".

Dat verklaart de 24: zeven woorden zijn ongeveer 10–12 tokens (schatting), de rest zijn markeringen uit het template. Chat templates komen uitgebreid terug in Sprint 2.

### Stap 3 — Eén rekenronde geeft een kansverdeling

Het model bestaat uit **parameters**: 9 miljard getallen (`parameters 9.0B`) die tijdens de training zijn afgesteld. Met die getallen rekent het over de hele rij tokens en geeft het voor élk token uit de vocabulaire een score. Die scores worden omgezet naar kansen die samen optellen tot 1.

Na de tokens voor *"vLLM is een open-source"* zou het er zo uit kunnen zien (getallen verzonnen ter illustratie):

| Volgend token | Kans |
|---|---|
| `systeem` | 0,35 |
| `bibliotheek` | 0,30 |
| `inference` | 0,20 |
| `project` | 0,10 |
| (alle andere samen) | 0,05 |

### Stap 4 — Eén token kiezen

Uit die verdeling wordt één token gekozen. Dat kiezen heet **sampling**, en de knoppen daarvoor (temperature, top_k, top_p, seed) zijn les 03. Voor nu: het model kiest niet altijd het meest waarschijnlijke token. Er zit een gecontroleerde portie toeval in.

### Stap 5 — Erachter plakken en herhalen

Het gekozen token wordt achter de rij geplakt, en stap 3 begint opnieuw met een rij die één token langer is. Dit heet **autoregressief** genereren. Het stopt als:
- het model een speciaal **stop-token** kiest ("ik ben klaar") → `done_reason: "stop"`;
- of de limiet `num_predict` is bereikt → `done_reason: "length"`.

Nu zijn de tijden te verklaren:
- **52 tokens uit = 52 rondes.** 0,50 s / 52 ≈ 9,5 ms per token, dus ongeveer **105 tokens per seconde** op jouw RTX 3080 (één meting, één korte prompt).
- **24 tokens in in 0,055 s.** De invoer is al bekend, dus die verwerkt het model in één keer, parallel. De uitvoer moet stuk voor stuk, want elk token hangt af van het vorige. Daarom zijn lange antwoorden duur en lange prompts relatief goedkoop, maar niet gratis.
- **3,75 s laden** is de koude start: 5,6 GB aan gewichten gaat van de schijf naar de VRAM. Een tweede aanroep binnen een paar minuten slaat dit over (`ollama ps`: *UNTIL 4 minutes from now*).

### Stap 6 — Geen geheugen tussen aanroepen

Elke aanroep begint blanco. Een "gesprek" bestaat alleen doordat jij bij elke aanroep de hele geschiedenis opnieuw meestuurt in `messages`. Het model leert ook niets van jouw gesprek; de parameters veranderen niet. Wat niet in de rij tokens staat, bestaat voor het model niet.

### Stap 7 — Het context window

Het **context window** is het maximale aantal tokens dat het model in één keer kan bekijken: **invoer + antwoord samen**.

- Het model kán 262.144 tokens aan (`ollama show`: *context length*).
- Ollama gebruikte hier **4096** (`ollama ps`: *CONTEXT*).

Waarom zo zuinig? Voor elk token in het venster houdt het model tussenresultaten bij in de VRAM (de **KV-cache**, uitgebreid in Sprint 2). Een groter venster kost dus meer VRAM. Ollama kiest een bescheiden standaard; je zet het per aanroep hoger met de option `num_ctx`.

Is de invoer langer dan het venster, dan kort Ollama haar in, **zonder foutmelding**. Welk deel precies wegvalt, laten we later bewust gebeuren en meten.

### Stap 8 — Waar komt de kennis vandaan?

Alles wat het model "weet", zit in de parameters, vastgelegd tijdens de training. Die kennis is bevroren op een datum, de **knowledge cutoff**. Het model weet niet wat het niet weet. Het voorspelt áltijd een plausibele voortzetting, ook als de feiten ontbreken. Dan krijg je een **hallucinatie**: vloeiend, zelfverzekerd en fout.

Voor ons domein betekent dit: functies die vLLM na de cutoff heeft gekregen, kent het model niet, maar het antwoordt er even overtuigend over. Precies dat gaan we meten in de baseline.

## 5. Knoppen en keuzes

- **`num_ctx`** (context window): groter = meer tekst past, maar meer VRAM en trager. Voor RAG reken je het uit: instructie + gevonden passages + vraag + ruimte voor het antwoord moeten erin passen. Zie het rekenvoorbeeld hieronder.
- **`num_predict`** (maximum aantal tokens uit): beschermt tegen eindeloze antwoorden, maar te laag geeft een afgekapt antwoord.
- **`think`**: bij jouw model staat denken **standaard aan** (`ollama show`: *thinking default true*). Denktokens kosten tijd en ruimte in het venster. Voor de meetlat zetten we het uit; `chat()` stuurt `think: false` mee.
- **Modelgrootte** (`qwen3.5:4b` of `9b`): kleiner is sneller en zuiniger met VRAM, groter weet en redeneert meestal beter.
- **Standaardwaarden van het model:** wat je niet instelt, is niet "niets". Het model komt met eigen standaarden (`ollama show`: temperature 1, top_k 20, top_p 0,95, presence_penalty 1,5). Leg daarom altijd vast wat er werkelijk gold. Zie les 03.

**Rekenvoorbeeld context:** 5 passages × 400 tokens = 2000, instructie + vraag = 200, ruimte voor het antwoord = 500. Totaal 2700, dat past in 4096. Met 10 passages: 4000 + 200 + 500 = 4700, dat past níet, en Ollama kort stilzwijgend in.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| Model negeert een instructie die vooraan een lange prompt stond | Context window overschreden; invoer ingekort |
| Eerste aanroep traag, daarna snel | Koude start; te zien aan `load_duration` |
| Model "vergeet" de vorige vraag | Geschiedenis niet meegestuurd in `messages` |
| Zelfverzekerd fout over een nieuwe functie | Knowledge cutoff; hallucinatie |
| Lang wachten, of een leeg antwoord bij een krappe `num_predict` | Thinking staat aan; denktokens gaan voor |
| `done_reason: "length"` | `num_predict` te laag |

**Uitgewerkt voorbeeld.** Een RAG-prompt van ongeveer 5000 tokens, met `num_ctx` op de standaard 4096. Vooraan staat de instructie *"Antwoord alleen op basis van de bronnen hieronder."* Ollama kort de invoer in, en als die instructie wegvalt, antwoordt het model uit eigen kennis: vloeiend, overtuigend en mogelijk verouderd. Er is geen foutmelding. Je herkent het aan `prompt_eval_count`: dat ligt dan tegen de limiet aan in plaats van rond de 5000 die je verwachtte. Dat is een verwachting die we later bewust gaan testen. Daarom loggen we `prompt_eval_count` bij elke aanroep.

## 7. Analogie

**Context window ≈ geheugendiepte (record length) van een digitale oscilloscoop.** De scope legt een vast aantal samples vast; wat daarbuiten valt, bestaat niet voor de meting. Meer geheugendiepte kost geheugen. Ollama's 4096 tegenover de 262.144 van het model lijkt op een scope die maar een deel van zijn maximale geheugendiepte gebruikt, omdat de rest geld kost, in dit geval VRAM.

**Waar de vergelijking ophoudt:**
- Een scope behandelt elk sample gelijk. Een LLM let niet gelijkmatig op alles in het venster; informatie midden in een lange context wordt vaker gemist.
- Het rekenwerk per nieuw token groeit met hoeveel er in het venster staat.
- Een scope toont wat er wás. Een LLM maakt iets nieuws, en dat kan niet kloppen.

## 8. Samenvatting

**Kern:** een LLM voorspelt steeds één volgend token uit een kansverdeling, berekend over de hele rij tokens tot nu toe, en herhaalt dat tot een stop-token of limiet. Het heeft geen geheugen tussen aanroepen en geen toegang tot feiten buiten zijn training en jouw prompt. Alles moet binnen het context window passen; wat erbuiten valt, ziet het model niet.

**Begrippen:**
- **Token**: stukje tekst uit de vaste vocabulaire, met een nummer.
- **Tokenizer**: knipt tekst in tokens.
- **Chat template**: zet messages met rollen om in één rij tokens.
- **Parameters**: de geleerde getallen van het model (hier 9 miljard).
- **Autoregressief**: elk nieuw token wordt achter de invoer geplakt voor de volgende ronde.
- **Stop-token**: speciaal token waarmee het model aangeeft dat het klaar is.
- **Context window**: maximum aantal tokens in + uit samen.
- **KV-cache**: tussenresultaten per token in de VRAM; de reden dat een groter venster meer geheugen kost.
- **Knowledge cutoff**: datum tot waar de trainingsdata loopt.
- **Hallucinatie**: plausibel klinkend, maar onjuist antwoord.

**Knoppen:** `num_ctx` · `num_predict` · `think` · modelgrootte · standaardwaarden van het model.

**Foutmodi:** stil ingekorte invoer · koude start · vergeten geschiedenis · hallucinatie na de cutoff · thinking dat tijd en tokens opeet.

## 9. Wat we hiermee gaan bouwen

`chat()` doet al één aanroep. Door deze les weet je waarom de meetlat straks per vraag `prompt_eval_count`, `eval_count`, de duren, `done_reason` en de werkelijk gebruikte instellingen vastlegt: daarmee zie je achteraf of een antwoord is ingekort, afgekapt of vertraagd door een koude start. In les 02 kijken we naar het transport zelf, het HTTP-verzoek en -antwoord, JSON en timeouts, en daarna testen we `chat()`. Het rekenvoorbeeld over het context window komt terug in Sprint 1, als we passages in de prompt zetten.
