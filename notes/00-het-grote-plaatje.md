# Les 00 — Het grote plaatje

## 1. Inleiding

**Waar we zijn:** aan het begin. Deze les heeft geen code. Het is de kaart waarop je straks bij elke volgende les kunt zien waar je bent.

**Waarom deze les eerst:** in de komende weken bouwen we een systeem uit losse onderdelen. Zonder kaart voelt elk onderdeel als een los trucje. Met kaart weet je bij elke stap waarvóór hij dient.

**Na deze les kun je:**
- in je eigen woorden uitleggen wat we in Project 1 bouwen en waarom;
- uitleggen waarom we beginnen met één losse aanroep van een model, zonder zoeken in documenten;
- de onderdelen van Sprint 0 aanwijzen op de kaart.

**Nieuwe begrippen (3):** LLM · RAG · evaluatieset.

## 2. Het probleem

Stel: over een paar maanden werk je met vLLM, het programma dat taalmodellen snel draait. Je wilt weten hoe je de maximale lengte van de invoer instelt. Je vraagt het aan een taalmodel.

Je krijgt een vloeiend, zelfverzekerd antwoord met een optienaam erin. Misschien klopt die. Maar misschien komt hij uit een oudere versie en bestaat hij niet meer, of is hij net verkeerd gespeld. Aan de tekst zelf zie je het verschil niet. Pas als vLLM een foutmelding geeft, of de optie stilletjes negeert, merk je dat het mis was.

Het juiste antwoord staat wél in de officiële documentatie. Maar die is honderden pagina's groot, en zoeken kost tijd.

Dus:
- het **model** is snel en vloeiend, maar niet betrouwbaar bij specifieke, recente feiten;
- de **documentatie** is betrouwbaar, maar moeilijk doorzoekbaar.

## 3. Het idee in het kort

We combineren die twee. Een programma zoekt eerst de passages in de documentatie die bij de vraag horen, en geeft die passages samen met de vraag aan het model: "beantwoord de vraag met deze tekst". Het model doet waar het goed in is: een helder antwoord formuleren. De feiten komen uit de documentatie. Bij elk antwoord laten we zien uit welke passages het kwam, zodat jij kunt controleren.

En we **meten** of het werkt, met een vaste lijst vragen waarvan we het juiste antwoord kennen. Net als een calibratie: meten tegen bekende referentiewaarden, niet op gevoel.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Wat een taalmodel is

Een taalmodel is een programma dat enorm veel tekst heeft gelezen en daardoor heel goed is in één ding: tekst op een plausibele manier voortzetten. Je geeft het een begin (je vraag), en het schrijft woord voor woord verder wat er waarschijnlijk volgt.

Zo'n groot taalmodel heet een **LLM** (*Large Language Model*). In dit project draait het op je eigen computer, via Ollama. Hoe dat voortzetten precies werkt, is les 01a.

Twee dingen zijn belangrijk om nu al te weten:
- **Het zoekt niets op.** Het is geen database en geen zoekmachine. Alles wat het "weet", heeft het opgepikt tijdens het lezen.
- **Dat lezen stopte op een bepaalde datum.** Wat daarna gebeurde, bijvoorbeeld een nieuwe versie van vLLM, kent het niet.

### Stap 2 — Waarom dat bij specifieke vragen misgaat

Een LLM is gemaakt om *plausibele* tekst te schrijven, niet per se *ware* tekst. Meestal valt dat samen, maar niet altijd. Uit zichzelf zegt het bijna nooit "dat weet ik niet". Het schrijft gewoon iets dat er goed uitziet.

Een echt voorbeeld uit onze eerste test. Op de vraag "Wat is vLLM?" antwoordde het model:

> *"vLLM is een open-source systeem dat grote taalmodellen (LLMs) aanzienlijk sneller en efficiënter maakt door geavanceerde technieken zoals PagedAttention toe te passen voor het optimaliseren van geheugenbesturing."*

Dat klopt grotendeels. Maar "geheugenbesturing" is een vreemd woord; het bedoelt waarschijnlijk "geheugenbeheer". Bij een algemene vraag is zo'n slordigheid onschuldig. Bij een specifieke vraag, zoals de naam van een optie, levert dezelfde slordigheid een commando op dat niet werkt.

### Stap 3 — RAG: eerst zoeken, dan antwoorden

De oplossing uit "Het idee in het kort" heet **RAG**: *Retrieval-Augmented Generation*. Letterlijk: generatie (het model schrijft een antwoord), aangevuld (augmented) met wat er is opgehaald (retrieval). In een schema:

```
                    ┌───────────────────────┐
  jouw vraag ──────▶│ 1. ZOEKEN in de docs  │──▶ de beste passages
                    └───────────────────────┘          │
                                                       ▼
                    ┌───────────────────────┐
  vraag + passages ▶│ 2. LLM schrijft       │──▶ antwoord + bronnen
                    │    het antwoord       │
                    └───────────────────────┘
```

- **Zoeken:** hoe een programma bepaalt welke passages "bij de vraag horen", leren we in Sprint 1. Dat is een vak apart.
- **Antwoorden:** het model krijgt de passages mee in de vraag en wordt gevraagd zich daaraan te houden.
- **Bronnen tonen:** bij elk antwoord laten we zien welke passages gebruikt zijn. Dan kun je controleren, in plaats van te moeten vertrouwen.

### Stap 4 — Meten met een evaluatieset

Hoe weet je of het systeem goed werkt, of beter is geworden na een aanpassing? Niet door een paar vragen te proberen en "het lijkt beter" te denken.

We maken een **evaluatieset**: een vaste lijst vragen, elk met het juiste antwoord en de passage in de documentatie waar dat antwoord staat. Na elke aanpassing laten we het systeem alle vragen opnieuw beantwoorden en vergelijken we met de juiste antwoorden. Dat levert een score op: vóór en na de aanpassing, met dezelfde vragen.

De allereerste meting is de **nulmeting**: het model alléén, zonder zoeken in de documentatie. Die heb je nodig om later te kunnen laten zien hoeveel RAG oplevert.

### Stap 5 — De route door Project 1

| Sprint | Wat we bouwen | Wat je daarna kunt |
|---|---|---|
| **0 (nu)** | het model aanroepen vanuit Python, een meetlat, en de nulmeting met 5 vragen | een model betrouwbaar aanspreken en reproduceerbaar meten |
| 1 | een eerste, simpele RAG: documentatie ophalen, zoeken, passages meegeven | laten zien hoeveel beter RAG is dan de nulmeting |
| 2 | vLLM als tweede "motor" naast Ollama | hetzelfde systeem op een andere backend draaien en de verschillen verklaren |
| daarna | verbeteren waar de meting zegt dat het misgaat | keuzes onderbouwen met meetresultaten |
| afronding | Docker en een README met scores | het systeem overdragen aan een andere engineer |

Daarna, kort: in Project 2 maken we er een **agent** van (het model mag zelf hulpmiddelen inzetten). In Project 3 maken we het **productieklaar** (een echte service, onder belasting gemeten). Project 4 is **fine-tuning** (het model zelf bijtrainen).

### Stap 6 — Sprint 0 van dichtbij

In Sprint 0 is er nog geen zoeken in documenten. De keten is:

```
  5 vragen          meetlat-          chat()         Ollama-        model
  (eval/)    ──▶    script     ──▶   (Python)  ──▶   server    ──▶ (qwen3.5:9b)
                       │
                       ▼
                 resultaten
                 (data/runs/)
```

- **5 vragen:** over de vLLM-documentatie, met het juiste antwoord erbij.
- **meetlat-script:** stuurt de vragen één voor één, steeds met dezelfde instellingen, en schrijft alles weg.
- **`chat()`:** het stukje Python dat met Ollama praat. Dat bestaat al.
- **resultaten:** per run een bestand met de vragen, de antwoorden en alle instellingen. Zo kun je later precies terugzien hoe een uitkomst tot stand kwam.

Waarom eerst zonder RAG?
1. Je moet eerst betrouwbaar met het model kunnen praten. Alles daarna bouwt op `chat()`.
2. Zonder nulmeting kun je later niet laten zien wat RAG oplevert.
3. De meetlat gebruiken we het hele project. Hij moet vanaf het begin goed zijn.

De lessen van Sprint 0:
- **01a / 01b:** wat een LLM doet bij één aanroep, en wat het wel en niet ziet;
- **02a / 02b / 02c:** hoe je vraag via het netwerk bij Ollama komt, en wat daarbij mis kan gaan;
- **03:** de knoppen die bepalen hoe het model zijn woorden kiest;
- **04:** hoe je reproduceerbaar meet met een vaste set vragen;
- **05:** een tweede, algemene manier om modellen aan te spreken, zodat we later van motor kunnen wisselen.

## 5. Knoppen en keuzes

De grote keuzes zijn al gemaakt. Kort waarom:

- **Lokaal in plaats van in de cloud:** geen kosten per vraag, geen data die je computer verlaat, en je ziet zelf wat er onder de motorkap gebeurt (geheugen, snelheid).
- **De vLLM-documentatie als onderwerp:** recent genoeg dat het model niet alles weet, dus het verschil dat RAG maakt is meetbaar. En je leert vLLM onderweg.
- **Eerst zelf bouwen, daarna pas kant-en-klare bibliotheken:** dan weet je bij een fout waar je moet zoeken.
- **Eerst meten, dan verbeteren:** anders weet je niet of een aanpassing helpt.

## 6. Waar het misgaat

Typische fouten bij het bouwen van zo'n systeem:

| Symptoom | Oorzaak |
|---|---|
| Iets werkt niet en je weet niet waar je moet zoeken | meteen een groot framework gebruikt zonder te weten wat het doet |
| "Het lijkt beter", maar je kunt het niet laten zien | geen vaste evaluatieset en geen nulmeting |
| Je verbetert het model, maar de antwoorden blijven fout | het zoeken vond de verkeerde passages, dus het lag niet aan het model |
| Na drie aanpassingen tegelijk weet je niet welke hielp | meer dan één ding per keer veranderd |

**Uitgewerkt voorbeeld.** Je leest dat "reranking" (een extra sorteerstap na het zoeken) RAG beter maakt, en voegt het toe. De antwoorden voelen beter. Maar er is geen nulmeting en geen vaste vragenlijst. Je kunt niet laten zien dat het echt beter is, en je ziet ook niet dat het systeem nu misschien twee keer zo traag is voor een verschil dat er mogelijk niet is. Met een evaluatieset had je binnen een paar minuten geweten: helpt het, hoeveel, en wat kost het?

## 7. Analogie

Je kent dit uit het calibratielab:

| Calibratielab | Dit project |
|---|---|
| referentiestandaarden met bekende waarden | de evaluatieset met bekende juiste antwoorden |
| *as found*: meting vóór je iets aanpast | de nulmeting |
| justeren, daarna *as left* meten | een verbetering doorvoeren, daarna opnieuw meten met dezelfde set |
| de technicus pakt de handleiding van de fabrikant erbij in plaats van uit het hoofd te werken | RAG: het model krijgt de juiste passages mee in plaats van uit zijn geheugen te antwoorden |

**Waar de vergelijking ophoudt:**
- Een referentiestandaard is herleidbaar en heeft een bekende onzekerheid. Onze "referentie" is wat er in de documentatie staat. Staat daar een fout, dan is ook onze referentie fout.
- Een meting levert een getal met een onzekerheid op. Een antwoord van een model beoordelen vraagt vaak een oordeel (goed, half goed, fout), en dat is minder hard.

## 8. Samenvatting

**Kern:** een LLM schrijft vloeiende tekst, maar is niet betrouwbaar bij specifieke, recente feiten. RAG laat een programma eerst de juiste passages in de documentatie zoeken en geeft die mee aan het model, met bronvermelding. Met een vaste evaluatieset meten we of het werkt, beginnend met een nulmeting zonder RAG.

**Begrippen:**
- **LLM**: groot taalmodel; zet tekst plausibel voort, zoekt niets op, kennis stopt op een datum.
- **RAG**: eerst relevante passages ophalen, dan het model laten antwoorden met die passages.
- **Evaluatieset**: vaste lijst vragen met juiste antwoorden en bronpassages; de meetlat.
- (ook genoemd) **Nulmeting**: de eerste meting, met het model alleen.

**Keuzes:** lokaal · vLLM-documentatie · eerst zelf bouwen · eerst meten.

**Foutmodi:** niet weten waar te zoeken · verbeteren zonder meting · het model de schuld geven van slecht zoeken · meerdere dingen tegelijk veranderen.

## 9. Wat we hiermee gaan bouwen

In Sprint 0 bouwen we het onderste deel van de kaart: de lijn van vragenlijst via `chat()` naar het model, en terug naar een resultatenbestand. Les 01a begint bij het model zelf: wat gebeurt er precies als je het een vraag stelt?
