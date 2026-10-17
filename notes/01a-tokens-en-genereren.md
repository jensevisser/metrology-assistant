# Les 01a — Van vraag naar antwoord: tokens en token voor token

## 1. Inleiding

**Waar we zijn:** op de kaart van les 00 (`00-het-grote-plaatje.md`) zitten we helemaal rechts, bij het model zelf.

```
  5 vragen ──▶ meetlat ──▶ chat() ──▶ Ollama ──▶ [ MODEL ]  ◀── deze les
```

**Wat je al weet:** een LLM zet tekst plausibel voort, zoekt niets op, en zijn kennis stopt op een datum (les 00).

**Waarom dit nu:** alles wat we straks meten (hoeveel tokens erin en eruit, hoe lang een antwoord duurt, waarom een antwoord wordt afgekapt) volgt uit hoe het model een antwoord maakt. Zonder dat beeld zijn de getallen in de meetlat alleen maar getallen.

**Na deze les kun je:**
- uitleggen wat een token is, en waarom een woord soms uit meerdere tokens bestaat;
- uitleggen hoe een model woord voor woord, eigenlijk token voor token, een antwoord opbouwt;
- verklaren waarom een lang antwoord veel meer tijd kost dan een lange vraag.

**Nieuwe begrippen (3):** token · kansverdeling over het volgende token · token voor token genereren.

## 2. Het probleem

Bij onze eerste echte aanroep stelden we `qwen3.5:9b` de vraag *"Wat is vLLM? Antwoord in één zin."* Ollama gaf naast het antwoord deze getallen terug:

| Wat | Waarde |
|---|---|
| tokens in de vraag | 24 |
| tokens in het antwoord | 52 |
| tijd om de vraag te verwerken | 0,055 s |
| tijd om het antwoord te maken | 0,50 s |

Hier zitten twee raadsels in:
1. De vraag heeft 7 woorden. Waar komen 24 "tokens" vandaan, en wat is een token eigenlijk?
2. De vraag (24 tokens) was in 0,055 s verwerkt. Het antwoord (52 tokens) kostte 0,50 s: per token ongeveer vier keer zo lang. Waarom is uitvoer zoveel trager dan invoer?

Na deze les kun je beide verklaren. Het eerste raadsel lossen we voor een deel op; de rest van de 24 komt in les 01b.

## 3. Het idee in het kort

Een model werkt niet met letters of woorden, maar met **tokens**: genummerde stukjes tekst. Bij elke stap kijkt het naar alle tokens tot nu toe en berekent het voor elk mogelijk volgend token hoe waarschijnlijk dat is. Daaruit wordt er één gekozen, dat token wordt achter de tekst geplakt, en dan begint dezelfde stap opnieuw. Zo groeit het antwoord, één token per stap, tot het model aangeeft dat het klaar is.

## 4. Hoe het werkt, stap voor stap

### Stap 1 — Tekst wordt geknipt in stukjes

Een computer rekent met getallen, niet met letters. Daarom wordt tekst eerst in stukjes geknipt, en krijgt elk stukje een nummer.

Die stukjes komen uit een vaste lijst die bij het model hoort, zoiets als een woordenboek met ruim honderdduizend vermeldingen. Daarin staan:
- veelvoorkomende woorden in hun geheel, zoals `the` of `model`;
- losse woorddelen, zoals `kal`, `ib` en `ratie`;
- losse letters, cijfers en leestekens, als vangnet.

Een veelvoorkomend woord is vaak één stukje. Een zeldzaam woord wordt uit meerdere stukjes opgebouwd. Ter illustratie (de echte knippen verschillen per model): `kalibratie` → `kal` · `ib` · `ratie`.

Zo'n stukje heet een **token**.

**Een echte meting.** We vroegen het model om alleen "hallo" te zeggen, en lieten het antwoord binnenkomen terwijl het gemaakt werd. Het kwam in twee delen binnen: eerst `hal`, dan `lo`. "Hallo" is voor dit model dus twee tokens.

Waarom stukjes en geen hele woorden? Met een vaste lijst stukjes kun je élk woord bouwen, ook een woord dat het model nooit eerder zag, zoals een nieuwe optienaam uit de vLLM-documentatie. Een lijst met alleen hele woorden zou altijd woorden missen.

**Vuistregel:** in Engelse tekst is een token gemiddeld ongeveer 4 letters, of driekwart woord. Nederlands en programmacode kosten doorgaans meer tokens per woord, omdat het model minder Nederlandse en minder "codewoorden" als geheel kent. Dat is een vuistregel, geen meting. Echt tellen doet Ollama voor ons: het vertelt bij elke aanroep hoeveel tokens erin en eruit gingen.

### Stap 2 — Het model berekent kansen voor het volgende token

Nu staat de vraag als een rij tokens klaar. Het model is in wezen één grote berekening: miljarden vaste getallen die tijdens de training zijn afgesteld. Bij ons model zijn het er 9 miljard; daar staat de "9b" in `qwen3.5:9b` voor.

Die berekening krijgt de hele rij tokens als invoer, en geeft als uitvoer **voor elk token uit de lijst een kans**: hoe waarschijnlijk is het dat dít token nu volgt? Alle kansen samen tellen op tot 1, dus 100%.

Een voorbeeld. Stel, het antwoord is tot nu toe *"vLLM is een open-source"*. De kansen voor het volgende token kunnen er zo uitzien (getallen verzonnen ter illustratie):

| Volgend token | Kans |
|---|---|
| `systeem` | 35% |
| `bibliotheek` | 30% |
| `inference` | 20% |
| `project` | 10% |
| alle andere tokens samen | 5% |

Zo'n lijst van mogelijkheden met hun kansen heet een **kansverdeling**. Het model "weet" dus nooit één antwoord. Het geeft bij elke stap een verdeling over mogelijke volgende stukjes.

### Stap 3 — Eén token kiezen

Uit die kansverdeling wordt één token gekozen. Dat hoeft niet altijd het meest waarschijnlijke te zijn; er zit een gecontroleerde portie toeval in. In ons echte antwoord werd het `systeem`.

Hoe dat kiezen precies gaat, en met welke knoppen je het toeval regelt, is les 03. Voor nu is genoeg: uit de verdeling komt één token.

### Stap 4 — Erachter plakken en opnieuw

Het gekozen token wordt achter de rij geplakt. De rij is nu één token langer: *"vLLM is een open-source systeem"*. Daarna gebeurt stap 2 opnieuw, met de langere rij als invoer, en dan stap 3, en weer stap 4.

```
 rij tokens ──▶ [ berekening ] ──▶ kansen ──▶ kies 1 token ──┐
     ▲                                                       │
     └───────────── plak het achter de rij ◀─────────────────┘
```

Dit rondje heet **token voor token genereren**. De vakterm is *autoregressief*: elk nieuw token hangt af van alle tokens ervóór, ook van die het model zelf net heeft gemaakt.

Er zijn twee manieren waarop het rondje stopt:
- **Het model kiest een speciaal "ik ben klaar"-token.** Dat zit ook in de lijst. Ollama meldt dan `done_reason: "stop"`.
- **Een ingestelde limiet is bereikt**, bijvoorbeeld "maximaal 500 tokens". Ollama meldt dan `done_reason: "length"`: het antwoord is afgekapt, misschien midden in een zin.

In de "hallo"-meting zag je dit letterlijk: `hal`, dan `lo`, dan het klaar-token. Drie rondjes, en Ollama telde 3 tokens uit.

### Stap 5 — Waarom uitvoer trager is dan invoer

Nu is het tweede raadsel uit het begin te verklaren.

- **De vraag** is vooraf bekend. Alle 24 tokens kunnen in één keer door de berekening, tegelijk. Daarom 0,055 s.
- **Het antwoord** kan niet in één keer. Token 2 kan pas berekend worden als token 1 gekozen is, token 3 pas na token 2, enzovoort. 52 tokens zijn dus 52 rondjes na elkaar.

Rekenen met de echte meting: 0,50 s gedeeld door 52 tokens is ongeveer 0,0095 s, dus 9,5 milliseconde per token. Dat is ruwweg **105 tokens per seconde** op jouw RTX 3080. Dat is één meting met één korte vraag; we meten het later vaker.

Wat dit in de praktijk betekent:
- een **lang antwoord** kost veel tijd, want elk token is een rondje;
- een **lange vraag** kost relatief weinig, maar is niet gratis;
- wie snelheid wil, beperkt eerst de lengte van het antwoord.

## 5. Knoppen en keuzes

Twee knoppen hangen direct aan deze les:

- **Maximaal aantal tokens in het antwoord** (bij Ollama heet die `num_predict`). Een limiet beschermt tegen eindeloze antwoorden en lange wachttijden. Te krap gezet krijg je afgekapte antwoorden. In de praktijk kies je een ruime limiet en controleer je `done_reason`: staat daar `length`, dan weet je dat het antwoord niet af is.
- **Modelgrootte** (`qwen3.5:4b` of `qwen3.5:9b`). Minder vaste getallen betekent een kleinere berekening per rondje, dus sneller en minder geheugen. Meestal weet een groter model meer en formuleert het beter. Voor de meetlat gebruiken we 9b; voor snel uitproberen mag 4b.

## 6. Waar het misgaat

| Symptoom | Oorzaak |
|---|---|
| Antwoord stopt midden in een zin | limiet voor het aantal tokens bereikt (`done_reason: "length"`) |
| Een kort lijkend Nederlands antwoord telt veel tokens | Nederlands kost meer tokens per woord dan Engels |
| Lange wachttijd bij een korte vraag | het antwoord is lang: elk token is een rondje |
| Dezelfde vraag geeft niet steeds hetzelfde antwoord | bij het kiezen zit toeval (les 03) |

**Uitgewerkt voorbeeld.** Je zet de limiet op 30 tokens om de meetlat snel te maken, en vraagt: *"Welke opties heeft vLLM om het geheugengebruik te beperken? Noem ze allemaal."* Het antwoord begint keurig met twee opties en stopt dan halverwege een woord. Wie alleen naar de tekst kijkt, denkt misschien dat het model maar twee opties kent. Maar in de meetgegevens staat `done_reason: "length"`. Het model was nog niet klaar; de limiet greep in. In je evaluatie zou je dit antwoord onterecht als "onvolledig, model weet het niet" beoordelen. Daarom slaat de meetlat `done_reason` bij elk antwoord op.

## 7. Analogie

**Token voor token genereren lijkt op een successieve-benaderings-ADC (SAR-ADC).** Zo'n ADC bepaalt de digitale waarde bit voor bit, en elke beslissing hangt af van de bits die al vastliggen. Je kunt bit 3 niet bepalen voordat bit 1 en 2 bekend zijn. Daarom kost een conversie met meer bits meer klokslagen. Net zo kost een antwoord met meer tokens meer rondjes.

**Waar de vergelijking ophoudt:**
- Een SAR-ADC zoekt één juiste waarde, en elke stap brengt hem dichter bij die waarde. Een taalmodel heeft geen "juiste waarde" om naartoe te werken. Elke stap kiest een waarschijnlijk vervolg, en als een vroege keuze verkeerd was, bouwt het model daar vrolijk op verder.
- Een ADC is deterministisch: dezelfde ingangsspanning geeft dezelfde code. Een taalmodel kiest met een portie toeval, tenzij je dat uitzet (les 03).

## 8. Samenvatting

**Kern:** een model knipt tekst in tokens, genummerde stukjes uit een vaste lijst. Bij elke stap berekent het een kansverdeling over het volgende token, kiest er één, plakt dat achter de rij en herhaalt dat, tot een klaar-token of een limiet. Omdat elk antwoord-token een eigen rondje is, kost uitvoer veel meer tijd dan invoer.

**Begrippen:**
- **Token**: stukje tekst uit de vaste lijst van het model; een woord kan uit één of meer tokens bestaan.
- **Kansverdeling**: de lijst van alle mogelijke volgende tokens met elk hun kans; samen 100%.
- **Token voor token genereren** (autoregressief): kiezen, erachter plakken, opnieuw berekenen.
- (ook genoemd) **klaar-token**: speciaal token waarmee het model aangeeft dat het antwoord af is.

**Knoppen:** maximaal aantal tokens in het antwoord (`num_predict`) · modelgrootte.

**Foutmodi:** afgekapt antwoord door de limiet · onverwacht veel tokens bij Nederlands · lange wachttijd door een lang antwoord.

## 9. Wat we hiermee gaan bouwen

Dit verklaart drie velden die de meetlat straks bij elk antwoord opslaat: het aantal tokens erin, het aantal tokens eruit, en `done_reason`. Daarmee zie je achteraf of een slecht antwoord echt slecht was of gewoon afgekapt. In les 01b kijken we naar wat het model ziet en wat niet: waar de rest van die 24 tokens vandaan komt, waarom het model niets onthoudt tussen twee vragen, en hoeveel tekst er maximaal in past.
