# Markdown — spiekbriefje

Opzoeken, niet uit het hoofd leren. Links staat wat je typt, met `←` wat het doet.

**Resultaat bekijken in VSCodium:** `Ctrl+Shift+V` (voorbeeld in een nieuw tabblad) · `Ctrl+K` en dan `V` (voorbeeld naast je tekst).

## Ik wil tekst opmaken

```
# Titel            ← kop 1: titel van het bestand, maar 1× per bestand
## Kop             ← kop 2
### Subkop         ← kop 3

**vet**   *cursief*   ***vet en cursief***   ~~doorgehaald~~

Een lege regel     ← begint een nieuwe alinea
regel één\         ← \ aan het eind: nieuwe regel binnen dezelfde alinea
regel twee

---                ← horizontale lijn (lege regel erboven!)

> Opmerking of citaat, als ingesprongen blok
```

## Ik wil code tonen

Een naam of commando midden in een zin: enkele backticks.

```
Draai `uv sync` om te installeren.
```

Een heel codeblok: drie backticks erboven en eronder. Het woord erachter (`python`, `bash`, `json`, `markdown`) bepaalt de kleuren.

````
```python
print("hallo")
```
````

Backticks tónen in je tekst: zet er méér backticks omheen dan erin staan. Zo staat het voorbeeld hierboven tussen vier backticks.

## Ik wil een lijst

```
- punt                ← ongeordend
- punt
  - subpunt           ← 2 spaties inspringen

1. stap               ← genummerd
2. stap
   - subpunt          ← 3 spaties inspringen bij genummerd

- [x] gedaan          ← checklist (GitHub toont aanvinkvakjes)
- [ ] nog doen
```

## Ik wil een link of afbeelding

```
[zichtbare tekst](https://voorbeeld.nl)
[ander bestand](../01a-tokens-en-genereren.md)    ← pad vanaf DIT bestand
[naar een kop](#ik-wil-een-tabel)                  ← kleine letters, spaties → -
![beschrijving](pad/naar/plaatje.png)              ← beschrijving altijd invullen
```

`..` betekent "één map omhoog". Vanuit `notes/naslag/` is `../` dus `notes/`, en `../../` de hoofdmap van het project.

## Ik wil een tabel

```
| Veld            | Betekenis                 |
|-----------------|---------------------------|
| `eval_count`    | tokens uit                |
| `load_duration` | laadtijd in nanoseconden  |
```

De streepjesregel is verplicht. Uitlijnen hoeft niet; GitHub maakt het zelf netjes. Getallen rechts uitlijnen: `|---:|`.

## Ik wil iets extra's (alleen GitHub)

```
> [!NOTE]
> Handig om te weten.          ← blauw infoblok; ook [!TIP], [!WARNING]

<details>
<summary>Klik om uit te klappen</summary>

Verborgen tekst, bijv. een lange foutmelding.

</details>

![Python](https://img.shields.io/badge/python-3.12-blue)   ← badge
```

## Valkuilen: het ziet er niet uit zoals bedoeld

| Wat je ziet | Oorzaak → oplossing |
|---|---|
| lijst of tabel wordt gewone tekst | geen lege regel ervóór → lege regel toevoegen |
| tabel wordt niet getoond | streepjesregel `\|---\|---\|` ontbreekt |
| subpunt staat niet ingesprongen | te weinig spaties → 2 (bij genummerd: 3) |
| de rest van het bestand is één codeblok | sluitende ` ``` ` vergeten |
| een `\|` in een tabelcel breekt de tabel | schrijf `\|` |
| link naar een bestand doet niets | pad klopt niet vanaf het bestand waar de link in staat |
| `---` wordt een dikke kop | er staat tekst direct boven → lege regel ertussen |
| twee regels plakken aan elkaar | één Enter is geen nieuwe regel → lege regel of `\` aan het eind |
