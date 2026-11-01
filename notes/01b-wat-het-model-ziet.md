# Les 01b — Wat het model ziet en wat het weet

## 1. Inleiding

**Waar we zijn:** nog steeds bij het model zelf, rechts op de kaart.

```
  5 vragen ──▶ meetlat ──▶ chat() ──▶ Ollama ──▶ [ MODEL ]  ◀── deze les
```

**Wat je al weet:** het model knipt tekst in tokens, berekent een kansverdeling over het volgende token, en bouwt zo token voor token een antwoord op (`01a-tokens-en-genereren.md`).

**Waarom dit nu:** in les 01a keken we naar *hoe* het model schrijft. Nu kijken we naar *waar het mee werkt*: wat ziet het precies op het moment dat je een vraag stelt, en wat niet? Dat is de kern van alles wat met RAG te maken heeft. RAG draait er straks om dat je de juiste tekst in beeld van het model brengt.

**Na deze les kun je:**
- uitleggen hoe een gesprek met rollen (gebruiker, assistent) voor het model één doorlopende tekst wordt;
- uitleggen waarom het model niets onthoudt tussen twee vragen;
- uitleggen wat het context window is, en waarom Ollama er standaard maar een klein deel van gebruikt;
- uitleggen waarom het model over nieuwe dingen zelfverzekerd fout kan zijn.

**Nieuwe begrippen (4):** chat template · geen geheugen tussen aanroepen · context window · knowledge cutoff.

## 2. Het probleem

Drie dingen die we zagen en die nog niet verklaard zijn:

1. Onze vraag van 7 woorden telde **24 tokens**. Les 01a verklaarde een deel: woorden worden soms in meerdere stukjes geknipt. Maar 7 woorden worden geen 24 tokens alleen door knippen.
2. `ollama show qwen3.5:9b` meldt **context length 262144**, maar direct na een aanroep meldt `ollama ps` **CONTEXT 4096**. Wat betekenen die getallen, en welke geldt?
3. Het model gaf een vloeiend antwoord over vLLM. Maar hoe weet het iets over vLLM, en wat gebeurt er als je vraagt naar iets dat het niet weet?

## 3. Het idee in het kort

Het model ziet bij elke vraag precies één ding: één rij tokens. Je gesprek wordt, met speciale markeringen erin, omgezet in die ene rij. Wat niet in die rij staat, bestaat voor het model niet. Dat geldt ook voor je vorige vraag, tenzij je die opnieuw meestuurt. De rij heeft een maximale lengte, het context window. En naast die rij heeft het model alleen wat het tijdens de training heeft opgepikt, en dat stopt op een datum.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Van gesprek naar één rij tokens

Als je Ollama een vraag stuurt, stuur je geen losse tekst, maar een lijstje berichten, elk met een rol:
- `system`: algemene instructies, bijvoorbeeld "antwoord kort en in het Nederlands";
- `user`: wat jij vraagt;
- `assistant`: wat het model eerder antwoordde.

Het model zelf kent geen rollen en geen lijstjes. Het kent alleen een rij tokens (les 01a). Daarom zet Ollama je berichten om in één doorlopende tekst, met speciale markeringen ertussen die zeggen "hier begint een bericht van de gebruiker", "hier eindigt het" en "hier begint het antwoord van de assistent".

Schematisch (de echte markeringen zien er per model anders uit):

```
<begin gebruiker> Wat is vLLM? Antwoord in één zin. <einde> <begin assistent>
```

Het model doet daarna wat het altijd doet: de rij voortzetten. Omdat de rij eindigt met "begin assistent", is de meest plausibele voortzetting een antwoord.

Het recept dat bepaalt hoe berichten in zo'n rij worden omgezet, heet een **chat template**. Elk model heeft zijn eigen template, omdat het is getraind met zijn eigen markeringen.

Dat verklaart raadsel 1: de 7 woorden zijn misschien 10 à 12 tokens (schatting), en de rest van de 24 zijn markeringen uit het chat template. Chat templates komen uitgebreid terug in Sprint 2. Daar worden ze belangrijk, omdat vLLM en Ollama ze elk op hun eigen manier toepassen.

### Stap 2 — Geen geheugen tussen aanroepen

Elke aanroep begint blanco. Het model onthoudt niets van een vorige vraag. De vaste getallen van het model (de 9 miljard uit les 01a) veranderen ook niet door jouw gesprek; het model leert er niets van.

Hoe kan een chatprogramma dan een gesprek voeren? Doordat het bij elke nieuwe vraag **de hele geschiedenis opnieuw meestuurt**:

| Aanroep | Wat er wordt meegestuurd |
|---|---|
| 1 | gebruiker: "Wat is vLLM?" |
| 2 | gebruiker: "Wat is vLLM?" · assistent: (antwoord 1) · gebruiker: "En hoe installeer ik het?" |
| 3 | alles van aanroep 2 · assistent: (antwoord 2) · gebruiker: "Werkt dat ook zonder GPU?" |

De rij wordt dus bij elke vraag langer. Het "geheugen" van een chat zit volledig in wat jij meestuurt.

Voor onze meetlat is dit juist handig: elke vraag wordt los gesteld, zonder geschiedenis. Vraag 3 wordt dus niet beïnvloed door het antwoord op vraag 2. Zo blijven de metingen onafhankelijk van elkaar.

### Stap 3 — Het context window: hoeveel past er in de rij

De rij tokens kan niet onbeperkt lang zijn. Het maximale aantal tokens dat het model in één keer kan bekijken heet het **context window**. Het geldt voor **vraag en antwoord samen**: elk token van het antwoord wordt immers ook achter de rij geplakt (les 01a).

Nu raadsel 2:
- **262.144** (`ollama show`) is wat het model maximaal *kán*. Daarvoor is het getraind.
- **4096** (`ollama ps`) is wat Ollama bij onze aanroep werkelijk *gebruikte*.

Waarom zo weinig? Tijdens het genereren houdt het model voor elk token in de rij tussenresultaten bij in het geheugen van je videokaart (VRAM). Hoe langer de rij mag worden, hoe meer VRAM Ollama vooraf moet reserveren. Ollama kiest daarom een zuinige standaard. Je kunt die per aanroep verhogen; die knop heet `num_ctx`. Hoe die tussenresultaten precies werken, komt in Sprint 2. Voor nu is genoeg: **een groter venster kost meer videogeheugen.**

Wat gebeurt er als de rij te lang is? Dan kort Ollama hem in, **zonder foutmelding**. Een deel van je tekst valt gewoon weg. Welk deel precies, gaan we later bewust uitproberen en meten.

Een rekenvoorbeeld uit de toekomst, voor de RAG van Sprint 1. Stel, we geven het model 5 passages uit de documentatie mee:
- 5 passages van elk 400 tokens = 2000 tokens;
- instructie en vraag = 200 tokens;
- ruimte voor het antwoord = 500 tokens;
- totaal: **2700 tokens**. Dat past in 4096.

Met 10 passages wordt het 4000 + 200 + 500 = **4700 tokens**. Dat past niet, en Ollama kort stilzwijgend in.

### Stap 4 — Wat het model weet: de knowledge cutoff

Buiten de rij tokens heeft het model maar één bron: wat het tijdens de training heeft opgepikt, vastgelegd in die 9 miljard getallen. De training gebruikte tekst tot een bepaalde datum. Alles daarna kent het model niet. Die datum heet de **knowledge cutoff**.

Dat verklaart raadsel 3. Het model weet iets over vLLM, omdat er vóór de cutoff veel over vLLM geschreven is. Maar vLLM verandert snel: nieuwe opties, hernoemde instellingen, nieuwe functies. Die kent het model niet.

En hier zit het gevaar: het model wéét niet dat het iets niet weet. Het doet wat het altijd doet: een plausibele voortzetting schrijven (les 01a). Vraag je naar een optie die na de cutoff is toegevoegd, dan krijg je een vloeiend antwoord, mogelijk met een verzonnen of verouderde optienaam. Zo'n zelfverzekerd fout antwoord heet een **hallucinatie**.

Dit is precies wat we in de nulmeting van Sprint 0 willen zien: bij welke vragen over vLLM gaat het model de mist in? En het is precies wat RAG oplost: de juiste passage uit de documentatie komt ín de rij tokens, dus in beeld van het model.

## 5. Knoppen en keuzes

- **`num_ctx` (grootte van het context window).** Groter betekent dat er meer tekst past, maar het kost meer videogeheugen en elk rondje wordt iets trager. Voor de vijf korte vragen van Sprint 0 is 4096 ruim genoeg. In Sprint 1 rekenen we het per prompt uit, zoals in het rekenvoorbeeld.
- **Geschiedenis meesturen of niet.** Voor een chat stuur je de geschiedenis mee; voor een meting juist niet, zodat elke vraag op zichzelf staat.
- **Een system-bericht.** Daarmee kun je algemene instructies geven ("antwoord kort", "zeg het als je het niet weet"). Of dat helpt, meten we later; aannemen doen we het niet.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| Model "vergeet" wat je net vroeg | geschiedenis niet meegestuurd; elke aanroep begint blanco |
| Model negeert een instructie die vooraan een lange tekst stond | context window vol; Ollama heeft ingekort |
| Zelfverzekerd antwoord met een optie die niet bestaat | knowledge cutoff; het model schrijft plausibel, niet per se waar |
| Meer tokens dan je zou verwachten uit het aantal woorden | markeringen uit het chat template tellen mee |

**Uitgewerkt voorbeeld.** In Sprint 1 bouwen we een prompt met 10 passages uit de documentatie: ongeveer 4700 tokens. `num_ctx` staat nog op de standaard 4096. Bovenaan staat de instructie: *"Beantwoord de vraag alleen met de passages hieronder."* Ollama kort de rij in, en als juist die instructie of de beste passage wegvalt, antwoordt het model uit zijn eigen, mogelijk verouderde kennis. Het antwoord klinkt net zo overtuigend. Er komt geen foutmelding. Je herkent het aan het aantal tokens dat Ollama als invoer meldt: dat is **veel lager dan je verwachtte**.

Dat hebben we gemeten (1 november 2026, `qwen3.5:9b`). Dezelfde prompt, drie keer:

| `num_ctx` | HTTP | tokens erin | antwoord |
|---|---|---|---|
| 16384 | 200 | 6968 | volgt de instructie |
| 4096 | 200 | **2050** | negeert de instructie, verzint iets |
| 4096 + `"truncate": false` | **400** | — | `request (6968 tokens) exceeds the available context size (4096 tokens), try increasing it` |

Let op de middelste regel: van 6968 tokens bleven er 2050 over, dus ongeveer de helft van het venster, niet "net onder de 4096". Ollama gooide dus niet een stukje weg maar het overgrote deel, inclusief de instructie — en meldde dat met een nette `200 OK`.

De derde regel is de les: **stuur `"truncate": false` mee**, dan wordt stil inkorten een luide `400` met beide getallen erin. Dat is het verschil tussen een meetfout die je ziet en een meetfout die je niet ziet. Zie [FM-001](../FAILURE_MODES.md). Daarom slaat de meetlat het aantal tokens erin bij elke aanroep op.

## 7. Analogie

**Het context window lijkt op de geheugendiepte (record length) van een digitale oscilloscoop.** De scope legt een vast aantal samples vast; wat buiten dat venster valt, bestaat niet voor de meting. Meer geheugendiepte kost geheugen. Ollama's 4096 tegenover de 262.144 van het model is als een scope die maar een deel van zijn maximale geheugendiepte gebruikt, omdat de rest geld kost, hier in videogeheugen.

**Waar de vergelijking ophoudt:**
- Een scope behandelt elk sample gelijk. Een taalmodel let niet gelijkmatig op alles in het venster. Informatie midden in een heel lange tekst wordt vaker over het hoofd gezien dan informatie aan het begin of het eind.
- Een scope laat zien wat er wás. Een taalmodel maakt iets nieuws op basis van wat het ziet, en dat nieuwe kan onjuist zijn.

## 8. Samenvatting

**Kern:** het model ziet per aanroep precies één rij tokens. Je berichten worden via een chat template in die rij omgezet. Wat er niet in staat, inclusief eerdere vragen, bestaat voor het model niet. De rij mag niet langer zijn dan het context window, vraag en antwoord samen; is hij te lang, dan kort Ollama stilzwijgend in. Daarbuiten kent het model alleen zijn training, tot de knowledge cutoff.

**Begrippen:**
- **Chat template**: het recept dat berichten met rollen omzet in één rij tokens met markeringen.
- **Geen geheugen tussen aanroepen**: elke aanroep begint blanco; een gesprek bestaat doordat je de geschiedenis meestuurt.
- **Context window**: het maximale aantal tokens dat het model in één keer ziet, vraag en antwoord samen.
- **Knowledge cutoff**: de datum tot waar de trainingstekst loopt.
- (ook genoemd) **Hallucinatie**: een zelfverzekerd, plausibel klinkend, maar onjuist antwoord.

**Knoppen:** `num_ctx` · geschiedenis meesturen of niet · system-bericht.

**Foutmodi:** vergeten geschiedenis · stilzwijgend ingekorte invoer · hallucinatie na de cutoff · meer tokens door het template.

## 9. Wat we hiermee gaan bouwen

De meetlat stelt elke vraag los, zonder geschiedenis, zodat de metingen onafhankelijk zijn. En hij slaat bij elke aanroep het aantal tokens erin op, zodat ingekorte invoer opvalt. Met les 01a en 01b weet je nu wat er bínnen het model gebeurt. In les 02a stappen we één plek naar links op de kaart: hoe komt je vraag eigenlijk bij Ollama, en hoe komt het antwoord terug?
