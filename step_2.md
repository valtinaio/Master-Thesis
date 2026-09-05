# Schritt 2: Betriebliche Aufwendungen prognostizieren

> Erklaerungsdokument zu `fsap_guide.md`, Abschnitt "Schritt 2".
> Quelle: FSAP 7-Step Forecasting Framework, PDF S. 12-21.
> Dieses Dokument enthaelt **keinen Code** — es erklaert, *was* zu bauen ist,
> *in welcher Reihenfolge*, und *wo ein LLM entscheidet*.

---

## Teil 0: Die Grundidee in einem Satz

Schritt 1 hat den Umsatz prognostiziert. Schritt 2 leitet aus diesem Umsatz alle
betrieblichen Aufwendungen ab und endet beim **Betriebsergebnis**.

Der Umsatz ist also der Motor. Fast alles in Schritt 2 haengt an ihm.

---

## Teil 1: Warum es 2.1 *und* 2.2 gibt — und warum wir nur 2.2 nehmen

Das ist der Punkt, an dem der Guide beim ersten Lesen verwirrt. Deshalb zuerst
die Aufloesung.

### 2.1 und 2.2 sind keine Kette, sondern zwei Alternativen

Es ist **nicht** so, dass 2.1 die Kostensaetze berechnet und 2.2 diese dann
weiterverarbeitet. Es sind zwei *konkurrierende* Methoden fuer dieselbe Aufgabe:

| | Methode 2.1 | Methode 2.2 |
|---|---|---|
| Name | Fix-/Variabel-Trennung | Common-Size-Prognose |
| Idee | Aufwand hat einen fixen und einen variablen Teil | Aufwand ist zu 100 % umsatzabhaengig |
| Aufwand | hoch | niedrig |
| Im PDF fuer Starbucks verwendet? | **nein** | **ja, ueberall** |

Das PDF erklaert 2.1 mit einem Zahlenbeispiel (Umsatz 10 -> 12 Mio., Wareneinsatz
7 -> 8 Mio.) und wendet es dann **nie an**. Alle Starbucks-Zahlen im PDF entstehen
aus 2.2.

### Warum wir 2.1 weglassen

Drei Gruende:

1. Das PDF selbst nutzt es nicht.
2. Die Formel `Variabler Kostensatz = Delta Aufwand / Delta Umsatz` braucht nur zwei
   Jahre und ist damit extrem anfaellig — ein einziges Sonderjahr kippt das Ergebnis.
   Wenn der Umsatz zwischen zwei Jahren kaum schwankt, wird der Nenner winzig und
   der Kostensatz explodiert.
3. Es verdoppelt den Code, ohne die Prognose besser zu machen.

**Entscheidung fuer dieses Projekt: Nur Common-Size (2.2).**

Was von 2.1 trotzdem bleibt, ist die *Intuition* dahinter: wenn der Umsatz schneller
waechst als die Kosten, gibt es einen Skaleneffekt, und die Kostenquote sinkt. Diese
Beobachtung brauchen wir spaeter — nicht als Formel, sondern als Begruendung dafuer,
warum eine Quote fallend fortgeschrieben werden darf.

---

## Teil 2: Common-Size — das eine Werkzeug fuer fast alles

### Die Formel

Zwei Zeilen, mehr ist es nicht:

```
Schritt A (Historie):  Quote(t) = Aufwand(t) / Umsatz(t)
Schritt B (Prognose):  Aufwand(+n) = Umsatz(+n) x Quote(+n)
```

Schritt A ist reine Arithmetik aus dem Abschluss. Schritt B braucht eine
*gesetzte* Quote — und genau da liegt die ganze Denkarbeit.

### Ein durchgerechnetes Beispiel (Wareneinsatz, PDF S. 13)

Historie:

| Jahr | Umsatz | Wareneinsatz | Quote |
|---|---|---|---|
| 2013 | 14.866,8 | 5.486,9 | 36,9 % |
| 2014 | 16.447,8 | 5.865,0 | 35,7 % |
| 2015 | 19.162,7 | 6.648,4 | 34,7 % |

Die Reihe **faellt**. Das PDF schreibt sie deshalb weiter fallend fort:

| Jahr | gesetzte Quote |
|---|---|
| +1 | 34,0 % |
| +2 | 33,8 % |
| +3 | 33,6 % |
| +4 | 33,4 % |
| +5 | 33,2 % |

Prognose Year +1 bei einem prognostizierten Umsatz von z. B. 21.755:

```
6.596,5  =  21.755  x  0,340
```

### Der entscheidende Punkt

Die **Formel ist immer dieselbe**. Was sich unterscheidet, ist nur die Zahl, die man
fuer `Quote(+n)` einsetzt. Es gibt genau drei Moeglichkeiten:

| Variante | Regel | Charakter |
|---|---|---|
| Rueckfall | letzte historische Quote, konstant | konservativ, immer verfuegbar |
| Durchschnitt | Mittel der historischen Quoten | glaettet Ausreisser |
| Trend | Quote sinkt/steigt weiter | braucht eine Begruendung |

Der Guide warnt ausdruecklich: **Eine fallend fortgeschriebene Quote ist eine starke
Annahme.** Sie unterstellt anhaltenden Effizienzgewinn und hebt die Marge. Wer das
nicht begruenden kann, nimmt den Rueckfall.

### Warum die Quote nicht konstant bleiben muss (PDF S. 12-13)

Vier Faelle, die eine Quote verschieben:

1. **Aufwand aendert sich, Umsatz nicht** — Effizienzgewinne senken die Quote,
   steigende Einkaufspreise heben sie.
2. **Umsatz aendert sich, Aufwand nicht** — Preissenkungen im Wettbewerb heben die
   Quote bei gleichen Kosten.
3. **Beide gleichgerichtet** — es haengt davon ab, was staerker waechst.
4. **Beide gegenlaeufig** — typisch beim Uebergang Start-up -> Wachstum, oder in
   der Krise.

Praktische Konsequenz: **Der Trend ueber mehrere Jahre ist aussagekraeftiger als der
letzte Einzelwert.** Faellt die Quote drei Jahre in Folge, ist die konstante
Fortschreibung des letzten Werts eigentlich schon zu pessimistisch.

---

## Teil 3: Die Positionen — drei Rechenlogiken, nicht eine

Schritt 2 sieht im Guide aus wie eine lange Liste. Tatsaechlich fallen alle Positionen
in nur drei Gruppen:

```
Gruppe A — Common-Size          (4 Positionen)  -> Teil 2, fertig
Gruppe B — Sachanlagen/AfA      (1 Block)       -> eigene Mechanik, der grosse Brocken
Gruppe C — Sonderfaelle         (2 Positionen)  -> je eine kleine Extraregel
```

### Gruppe A: Common-Size

Betrifft Wareneinsatz, Filialbetriebskosten, sonstige betriebliche Aufwendungen und
Verwaltungsaufwand. Alle vier laufen ueber exakt dieselbe Formel aus Teil 2. Kein
Unterschied in der Rechenlogik — nur andere Eingangsspalten.

**Wichtige Abweichung gegenueber dem PDF:** Das PDF misst Filialbetriebskosten am
*Umsatz der firmeneigenen Filialen* und sonstige Aufwendungen am *Lizenz-/CPG-Umsatz*.
Diese Segmentaufteilung liefert keine API. **Bezugsgroesse ist bei uns immer der
Gesamtumsatz.** Das ist die allgemeine Regel des PDFs (S. 12) und methodisch sauber —
nur eben groeber.

Ebenso: Das PDF trennt Wareneinsatz und Mietkosten (Miete pro Filiale x Filialanzahl).
Beides steht nur im MD&A und in "Note 10: Leases". **Wir prognostizieren den
Gesamtposten `costOfRevenue` als eine Zahl.**

### Gruppe B: Sachanlagen und Abschreibungen

Das ist der aufwendigste Teil und folgt **nicht** der Common-Size-Logik. Details in
Teil 4.

Der einzige Beruehrungspunkt mit Common-Size: die **Investitionsquote**
(`capitalExpenditure / Umsatz`) wird genau wie eine Kostenquote gesetzt. Alles
danach ist reine Arithmetik.

### Gruppe C: Sonderfaelle

**Beteiligungsergebnis** — Treiber ist nicht der Umsatz, sondern der Buchwert der
Beteiligung:

```
Durchschnittlicher Buchwert = (Buchwert Anfang + Buchwert Ende) / 2
Beteiligungsergebnis        = Durchschnittlicher Buchwert x Renditeannahme
```

Das PDF nimmt fuer Starbucks 50 % Rendite und 5 % Wachstum des Buchwerts. 50 % ist
ungewoehnlich hoch — in dieser Zeile werden neben dem anteiligen Gewinn auch
Bruttomargen aus Warenlieferungen und Lizenzgebuehren ausgewiesen. Das ist
**Starbucks-spezifisch und nicht uebertragbar.**

**Einmalige Ertraege und Aufwendungen** — Regel des PDFs: pruefen, ob sie
wiederkehren. Wenn nicht: **auf null setzen.** Das ist der Normalfall und wird
uebernommen.

---

## Teil 4: Sachanlagen und Abschreibungen — der grosse Brocken

Hier lohnt sich Genauigkeit, weil dieser Teil den groessten Code-Anteil hat.

### Die Grundidee

> "forecast capital expenditures that lead projected future sales, and forecast
> depreciation expense amounts that lag capital expenditures" [PDF S. 15]

Uebersetzt:
- **Investitionen kommen vor dem Umsatz** — man baut die Filiale, bevor sie Umsatz macht.
- **Abschreibungen kommen nach der Investition** — man schreibt ab, was man gekauft hat.

### 4.1 Nutzungsdauer schaetzen

```
Nutzungsdauer = Durchschnittliche Sachanlagen zu Anschaffungskosten
                / Abschreibungsaufwand des Jahres
```

PDF-Beispiel:

```
((9.641,8 + 8.581,1) / 2) / 883,8  =  9.111,45 / 883,8  =  10,3 Jahre
```

Das PDF rundet auf **10 Jahre**. Dahinter steckt die Annahme: lineare Abschreibung
auf einen Restwert von null.

**Achtung — Datenherkunft:** Diese Formel braucht Sachanlagen zu *Anschaffungskosten*
(brutto). FMP liefert nur `propertyPlantEquipmentNet`. Der Bruttowert kommt aus
`SEC.get_concept("PropertyPlantAndEquipmentGross")`. Das ist der Grund, warum in
Schritt 2 ueberhaupt die SEC-API gebraucht wird.

### 4.2 Investitionen fortschreiben

```
Investitionsquote = Investitionen(t) / Umsatz(t)
Prognose          = Umsatz(prognostiziert) x Investitionsquote
```

Das ist wieder Common-Size — angewandt auf `capitalExpenditure` aus dem Cash Flow.

### 4.3 Abschreibungen schichtweise berechnen

**Das ist der zentrale Rechenschritt.** Jede Investition erzeugt eine eigene,
dauerhafte Abschreibungsschicht, die in allen Folgejahren bestehen bleibt.

```
Abschreibung auf Altbestand    = Sachanlagen zu AK / Nutzungsdauer
Abschreibung auf Investition n = Investition(Jahr n) / Nutzungsdauer
                                 (ab Jahr n, in jedem Folgejahr erneut)

Gesamtabschreibung(t) = Altbestand + Summe aller Schichten der Jahre 1..t
```

PDF-Tabelle (S. 16):

| Jahr | Altbestand | Inv +1 | Inv +2 | Inv +3 | Inv +4 | Inv +5 | Summe |
|---|---|---|---|---|---|---|---|
| +1 | 964,2 | 140,0 | | | | | 1.104,2 |
| +2 | 964,2 | 140,0 | 150,0 | | | | 1.254,2 |
| +3 | 964,2 | 140,0 | 150,0 | 180,0 | | | 1.434,2 |
| +4 | 964,2 | 140,0 | 150,0 | 180,0 | 210,0 | | 1.644,2 |
| +5 | **231,6** | 140,0 | 150,0 | 180,0 | 210,0 | 240,0 | 1.151,6 |

Zwei Dinge, die man hier sehen muss:

1. **Die Abschreibungen wachsen kumulativ** — jede Schicht bleibt liegen. Deshalb
   steigt die Summe von 1.104,2 auf 1.644,2.
2. **Die Deckelung.** Im Jahr +5 faellt der Altbestand von 964,2 auf 231,6. Grund:
   Restbuchwert war 4.088,3, nach vier Jahren zu je 964,2 sind nur noch 231,6 uebrig.
   **Eine Schicht darf nie mehr abschreiben, als noch an Buchwert vorhanden ist.**

Punkt 2 ist der haeufigste Implementierungsfehler. Ohne Deckelung wird der Buchwert
negativ und die ganze Bilanz kippt.

### 4.4 Sachanlagen fortschreiben

```
Sachanlagen zu AK (Ende)   = Sachanlagen zu AK (Anfang) + Investitionen
Kumulierte AfA (Ende)      = Kumulierte AfA (Anfang) + Abschreibung des Jahres
Sachanlagen netto          = Sachanlagen zu AK - Kumulierte AfA
```

### Was hier NICHT uebernommen wird

Das PDF setzt fuer Starbucks feste Investitionsbetraege (1.400 / 1.500 / 1.800 /
2.100 / 2.400 Mio.) aus dem MD&A. Die haben wir nicht — deshalb 4.2.

Ebenso Starbucks-spezifisch: die Aufteilung der Abschreibung in 95 % eigene Zeile /
5 % im Wareneinsatz. Das ist eine Ausweisbesonderheit und wird nicht uebernommen.

---

## Teil 5: Rechenschritt 2.3 — das Betriebsergebnis

Das Ziel von Schritt 2. Reine Subtraktion:

```
Betriebsergebnis = Umsatz
                   - Wareneinsatz (und Mietkosten)
                   - Filialbetriebskosten
                   - Sonstige betriebliche Aufwendungen
                   - Abschreibungen
                   - Verwaltungsaufwand
                   + Beteiligungsergebnis
```

### Interpretation — was danach zu pruefen ist

**Operative Marge = Betriebsergebnis / Umsatz.** Im PDF steigt sie fuer Starbucks von
18,8 % (2015) auf 23,1 % (Year +5).

Eine **steigende Marge** bedeutet: die Kostenquoten sinken schneller, als der Umsatz
waechst — der Skaleneffekt.

**Warnung:** Steigende Margen in einer Prognose sind eine starke Annahme. Wenn nicht
begruendet ist, warum die Kostenquote weiter faellt, gehoert die Quote des letzten
Jahres konstant fortgeschrieben. Die Margenreihe ist damit der beste **Plausibilitaets-
Check** fuer den ganzen Schritt 2: springt sie unrealistisch hoch, stimmt eine Quote
nicht.

---

## Teil 6: Wo genau ein LLM entscheidet

### Das Prinzip

```
Aufwand(+n) = Umsatz(+n) x Quote(+n)
                            ^^^^^^^^
                            nur das setzt das LLM
```

**Das LLM ersetzt niemals die Formel. Es liefert eine einzelne Zahl hinein.**

Der Grund: Die Quote ist **kein Rechenergebnis, sondern ein Urteil**. Ob eine seit
drei Jahren fallende Wareneinsatzquote weiterfaellt oder sich stabilisiert, laesst
sich aus den Zahlen nicht ableiten. Beide Fortschreibungen sind arithmetisch korrekt.
Es gibt keine Formel, die sagt, welche richtig ist.

Merksatz: **Das LLM setzt Quoten. Python rechnet.**

### Die Entscheidungstabelle

| Nr. | Entscheidung | Wer | Rueckfall ohne LLM |
|---|---|---|---|
| 1 | Wareneinsatzquote je Prognosejahr | **LLM** | letzte historische Quote konstant |
| 2 | Quote der uebrigen Aufwandsposten je Jahr | **LLM** | letzte historische Quote konstant |
| 3 | Verwaltungsaufwandsquote | **LLM** | letzte historische Quote konstant |
| 4 | Investitionsquote je Prognosejahr | **LLM** | durchschnittliche historische Quote |
| 5 | Nutzungsdauer | Python | — (Formel, kein Urteil) |
| 6 | Abschreibungsschichten inkl. Deckelung | **Python, niemals LLM** | — |
| 7 | Sachanlagen-Fortschreibung | Python | — |
| 8 | Renditeannahme Beteiligungen | offen (siehe Teil 8) | — |
| 9 | Einmaleffekte = 0 | feste Annahme | — |
| 10 | Betriebsergebnis | Python | — |

Vier LLM-Aufrufe also — und alle vier haben dieselbe Struktur: *"Hier ist eine
Quotenreihe. Setze die Quote fuer die naechsten Jahre und begruende es."*

**Das ist ein DRY-Hinweis:** Es braucht nicht vier Prompts, sondern **einen
generischen Prompt mit Parametern** (Name des Postens, Quotenreihe, Branche).

### Was das LLM darf

- Einen erkennbaren **Trend fortschreiben** statt einer Durchschnittsquote — das PDF
  tut bei Starbucks genau das (34,0 % -> 33,2 %).
- Ein **Ausreisserjahr ausschliessen** und das begruenden.
- Bei zu starker Schwankung **`konfidenz = niedrig`** melden.

### Was das LLM niemals darf

- **Die Abschreibungsschichten-Tabelle berechnen.** Der Guide sagt das ausdruecklich:
  reine Arithmetik gehoert nicht an ein LLM. Ein LLM rechnet unzuverlaessig, und der
  Fehler waere hier still — die Bilanz stimmt einfach nicht mehr.
- Die Nutzungsdauer schaetzen — das ist eine Formel.
- Das Betriebsergebnis bilden.

### Was das LLM zurueckgeben muss

Dieselbe Struktur wie in Schritt 1:

```
wert         -> die Quote(n)
begruendung  -> warum
konfidenz    -> hoch / mittel / niedrig
```

Bei fehlender Antwort oder `konfidenz = niedrig` greift der Rueckfall aus der Tabelle.
**Schritt 2 muss ohne LLM vollstaendig durchlaufen** — nur eben konservativ. Das ist
auch die Reihenfolge fuer die Umsetzung (Teil 7).

### Idealer Input je LLM-Aufruf

- Der Aufwandsposten und der Umsatz je Jahr fuer **alle** verfuegbaren Jahre
- Die daraus berechnete Quotenreihe
- Branche der Firma
- Bei der Investitionsquote zusaetzlich: der **Anlagenalter-Indikator**

```
Anlagenalter = Kumulierte Abschreibungen / Sachanlagen zu Anschaffungskosten
```

Ein hoher Wert heisst: der Bestand ist weitgehend abgeschrieben, Ersatzinvestitionen
stehen an — die Investitionsquote sollte steigen. Genau damit begruendet das PDF die
steigenden Starbucks-Investitionen (S. 15-16). Das klingt nach MD&A-Wissen, ist aber
aus der Bilanz ablesbar. **Das ist die interessanteste LLM-Stelle in Schritt 2**,
weil hier eine scheinbar unerreichbare Information doch aus dem Abschluss
rekonstruiert wird.

---

## Teil 7: Was du wann in Python baust

Die Reihenfolge folgt nicht der Nummerierung des Guides, sondern der Schwierigkeit.
**Nach jeder Stufe laeuft etwas Lauffaehiges.**

### Datenbeschaffung (vor Stufe 1)

| Quelle | Felder |
|---|---|
| `FMP.get_income_statement()` | `revenue`, `costOfRevenue`, `sellingGeneralAndAdministrativeExpenses`, `operatingExpenses`, `depreciationAndAmortization` |
| `FMP.get_balance_sheet()` | `propertyPlantEquipmentNet` |
| `FMP.get_cash_flow()` | `capitalExpenditure` |
| `SEC.get_concept("PropertyPlantAndEquipmentGross")` | Sachanlagen brutto |

**Noetige Jahre: 6.** Kostenquoten und Investitionsquote brauchen je ein Jahr und
ergeben 6 Werte. Nutzungsdauer und Beteiligungsrendite brauchen einen
Durchschnittsbestand und ergeben deshalb nur 5 Werte.

`FMP` hat aktuell nur `get_income_statement()`. `get_balance_sheet()` und
`get_cash_flow()` fehlen noch — das ist Voraussetzung fuer Stufe 3, nicht fuer
Stufe 1 und 2.

---

### Stufe 1 — Quotenreihen aus der Historie

**Was:** Eine einzige, wiederverwendbare Berechnung `Aufwand(t) / Umsatz(t)` ueber
alle Jahre, angewandt auf jede Aufwandsspalte.

**Warum zuerst:** Es ist die kleinste sinnvolle Einheit, und du siehst sofort echte
Zahlen — steigen die Quoten, fallen sie, schwanken sie? Diese Anschauung brauchst du
fuer jede weitere Entscheidung.

**Wo:** Diese Berechnung ist reine Arithmetik auf einer Zeitreihe. Sie gehoert
inhaltlich zu `services/calculus.py`, wo `get_growth_rate` und `get_CAGR` schon
denselben Charakter haben.

**Ergebnis:** Eine Quotentabelle. Noch keine Prognose.

---

### Stufe 2 — Aufwandsposten fortschreiben (ohne LLM)

**Was:** `Umsatz(+n) x Quote` mit der **Rueckfall-Regel** — letzte historische Quote,
konstant.

**Warum jetzt:** Damit ist Gruppe A komplett und Schritt 2 laeuft zum ersten Mal
durch. Kein LLM, keine Sonderfaelle, keine SEC-API. Alles Weitere ist Verfeinerung.

**Ergebnis:** Prognostizierte Aufwandsposten fuer Year +1 bis +6.

---

### Stufe 3 — Sachanlagen und Abschreibungen

Der groesste Block. In dieser Reihenfolge:

1. Sachanlagen brutto von der SEC holen
2. Nutzungsdauer schaetzen (Teil 4.1)
3. Investitionen fortschreiben (Teil 4.2, Quote vom Umsatz)
4. Abschreibungsschichten aufbauen — **mit Deckelung** (Teil 4.3)
5. Sachanlagen brutto / kumulierte AfA / netto fortschreiben (Teil 4.4)

**Der kritische Punkt ist 4.** Bau die Deckelung sofort mit ein, nicht nachtraeglich.
Teste sie an der PDF-Tabelle: Wenn dein Jahr +5 fuer den Altbestand 231,6 statt 964,2
ergibt, stimmt die Logik.

---

### Stufe 4 — Sonderfaelle und Abschluss

1. Beteiligungsergebnis (Durchschnittsbuchwert x Rendite)
2. Einmaleffekte = 0
3. Betriebsergebnis bilden
4. Operative Marge als Plausibilitaets-Check ausgeben

**Nach dieser Stufe ist Schritt 2 fachlich vollstaendig** — deterministisch,
nachvollziehbar, ohne LLM.

---

### Stufe 5 — Das LLM einsetzen

**Erst jetzt.** Du ersetzt an den vier Stellen aus Teil 6 die Rueckfall-Quote durch
eine LLM-gesetzte Quote. Der Rueckfall bleibt bestehen und greift bei fehlender oder
niedrig-konfidenter Antwort.

**Warum zuletzt:** Du hast dann eine deterministische Vergleichsbasis. Du siehst genau,
was das LLM an der Prognose veraendert — und das ist fuer die Thesis ein starkes
Argument, weil du den Beitrag des LLM messen kannst statt ihn zu behaupten.

`services/llm_call.py` mit `llm_call(context, system_prompt, prompt)` steht bereits.

---

### Architektur-Einordnung

| Was | Wohin | Warum |
|---|---|---|
| Quotenberechnung, Fortschreibung, Abschreibungsschichten | `services/` | Reine Rechenlogik, wiederverwendbar |
| Orchestrierung von Schritt 2 | `sub_graphs/fsap.py` | Sub-Graph konsumiert Services |
| Ein- und Ausgaben | `pydantic_models/pydantic_models.py` | Architekturregel 4 |

Sub-Graphs konsumieren Services und niemals andere Sub-Graphs (Architekturregel 3).

---

## Teil 8: Was du entscheiden musst, bevor Code entsteht

Diese Punkte kann kein Dokument fuer dich beantworten — sie legen den Umfang fest.

### Bereits entschieden

- **2.1 wird nicht implementiert.** Nur Common-Size (Teil 1).

### Noch offen

1. **Welche Aufwandsposten einzeln, welche zusammengefasst?**
   FMP liefert `costOfRevenue`, `sellingGeneralAndAdministrativeExpenses`,
   `operatingExpenses`, `depreciationAndAmortization`. Die PDF-Aufteilung
   (Filialbetriebskosten vs. sonstige betriebliche Aufwendungen) existiert in FMP
   nicht. Frage: Welche Posten prognostizierst du getrennt?
   *Achtung Doppelzaehlung:* `operatingExpenses` enthaelt je nach Anbieter bereits
   die SG&A- und AfA-Zeilen. Das muss geklaert sein, bevor summiert wird.

2. **Rueckfall-Regel: letzte Quote, Durchschnitt oder Trend?**
   Der Guide nennt fuer Kostenquoten "letzte Quote", fuer die Investitionsquote
   "Durchschnitt". Willst du das so uebernehmen oder vereinheitlichen?

3. **Datenstruktur der Abschreibungsschichten-Tabelle.**
   DataFrame, dict, Liste von Listen? Das bestimmt die gesamte Stufe 3.

4. **Nutzungsdauer runden oder exakt?** (10,3 -> 10 wie im PDF, oder 10,3 rechnen)

5. **Renditeannahme fuer Beteiligungen: fest, Parameter oder aus Historie?**
   Die 50 % des PDFs sind Starbucks-spezifisch und nicht uebertragbar.

6. **Klasse oder Funktionen?** Bei Klasse: welche Attribute?

7. **Ein generischer LLM-Prompt fuer alle vier Quoten, oder vier eigene?**
   (Teil 6 empfiehlt einen generischen — DRY.)

8. **Prognosehorizont und Anzahl historischer Jahre: Parameter oder fest?**

Punkt 1 und 3 legen den groessten Teil des Umfangs fest. Alles Weitere kann
schrittweise entschieden werden.
