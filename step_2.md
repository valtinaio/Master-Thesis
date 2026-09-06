# Schritt 2: Betriebliche Aufwendungen prognostizieren

> Erklaerungsdokument zu `fsap_guide.md`, Abschnitt "Schritt 2".
> Quelle: FSAP 7-Step Forecasting Framework, PDF S. 12-21.
> Dieses Dokument enthaelt **keinen fertigen Code** — aber zu jedem fachlichen Teil
> einen Block **"In Python"**, der sagt, *was konkret gebaut wird*, *mit welcher
> Formel* und *aus welchen Daten*. Wer alle "In Python"-Bloecke der Reihe nach
> abarbeitet, hat Schritt 2 des Guides vollstaendig umgesetzt.

**Lesehilfe:** Jeder Abschnitt hat zwei Teile.
`Theorie` = was das PDF sagt. `In Python` = was daraus im Code wird.
Abschnitte ohne "In Python"-Block sind reines Hintergrundwissen und erzeugen keinen Code.

---

## Teil 0: Die Grundidee in einem Satz

Schritt 1 hat den Umsatz prognostiziert. Schritt 2 leitet aus diesem Umsatz alle
betrieblichen Aufwendungen ab und endet beim **Betriebsergebnis**.

Der Umsatz ist also der Motor. Fast alles in Schritt 2 haengt an ihm.

**Der Datenfluss von Schritt 2 als Ganzes:**

```
Umsatzprognose (aus Schritt 1)
   |
   +--> Gruppe A: Aufwandsquote x Umsatz          -> Aufwandsposten
   +--> Gruppe B: Investitionsquote x Umsatz      -> Investitionen
   |                  -> Abschreibungsschichten   -> Abschreibungen
   |                  -> Sachanlagen brutto/netto (Input fuer Schritt 3)
   +--> Gruppe C: Beteiligungsergebnis, Einmaleffekte = 0
                          |
                          v
                  Betriebsergebnis (2.3)
```

---

## Teil 1: Warum es 2.1 *und* 2.2 gibt — und warum wir nur 2.2 nehmen

### Theorie

Das ist der Punkt, an dem der Guide beim ersten Lesen verwirrt. Deshalb zuerst
die Aufloesung.

**2.1 und 2.2 sind keine Kette, sondern zwei Alternativen.** Es ist **nicht** so,
dass 2.1 die Kostensaetze berechnet und 2.2 diese dann weiterverarbeitet. Es sind
zwei *konkurrierende* Methoden fuer dieselbe Aufgabe:

| | Methode 2.1 | Methode 2.2 |
|---|---|---|
| Name | Fix-/Variabel-Trennung | Common-Size-Prognose |
| Idee | Aufwand hat einen fixen und einen variablen Teil | Aufwand ist zu 100 % umsatzabhaengig |
| Aufwand | hoch | niedrig |
| Im PDF fuer Starbucks verwendet? | **nein** | **ja, ueberall** |

Das PDF erklaert 2.1 mit einem Zahlenbeispiel (Umsatz 10 -> 12 Mio., Wareneinsatz
7 -> 8 Mio.) und wendet es dann **nie an**. Alle Starbucks-Zahlen im PDF entstehen
aus 2.2.

**Warum wir 2.1 weglassen — drei Gruende:**

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

### In Python

**Nichts.** Fuer 2.1 entsteht kein Code. Dieser Teil legt nur fest, dass der ganze
Rest von Schritt 2 auf einer einzigen Formel aufbaut — der aus Teil 2.

---

## Teil 2: Common-Size — das eine Werkzeug fuer fast alles

### Theorie

Zwei Zeilen, mehr ist es nicht:

```
Schritt A (Historie):  Quote(t)    = Aufwand(t) / Umsatz(t)
Schritt B (Prognose):  Aufwand(+n) = Umsatz(+n) x Quote(+n)
```

Schritt A ist reine Arithmetik aus dem Abschluss. Schritt B braucht eine
*gesetzte* Quote — und genau da liegt die ganze Denkarbeit.

**Ein durchgerechnetes Beispiel (Wareneinsatz, PDF S. 13).** Historie:

| Jahr | Umsatz | Wareneinsatz | Quote |
|---|---|---|---|
| 2013 | 14.866,8 | 5.486,9 | 36,9 % |
| 2014 | 16.447,8 | 5.865,0 | 35,7 % |
| 2015 | 19.162,7 | 6.648,4 | 34,7 % |

Die Reihe **faellt**. Das PDF schreibt sie deshalb weiter fallend fort:

| Jahr | +1 | +2 | +3 | +4 | +5 |
|---|---|---|---|---|---|
| gesetzte Quote | 34,0 % | 33,8 % | 33,6 % | 33,4 % | 33,2 % |

Prognose Year +1 bei einem prognostizierten Umsatz von z. B. 21.755:

```
6.596,5  =  21.755  x  0,340
```

**Der entscheidende Punkt:** Die **Formel ist immer dieselbe**. Was sich unterscheidet,
ist nur die Zahl, die man fuer `Quote(+n)` einsetzt. Es gibt genau drei Moeglichkeiten:

| Variante | Regel | Charakter |
|---|---|---|
| Rueckfall | letzte historische Quote, konstant | konservativ, immer verfuegbar |
| Durchschnitt | Mittel der historischen Quoten | glaettet Ausreisser |
| Trend | Quote sinkt/steigt weiter | braucht eine Begruendung |

Der Guide warnt ausdruecklich: **Eine fallend fortgeschriebene Quote ist eine starke
Annahme.** Sie unterstellt anhaltenden Effizienzgewinn und hebt die Marge. Wer das
nicht begruenden kann, nimmt den Rueckfall.

**Warum die Quote nicht konstant bleiben muss (PDF S. 12-13)** — vier Faelle:

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

### In Python

Das sind **zwei getrennte Bausteine**, weil Schritt A auf der Historie arbeitet und
Schritt B auf der Prognose.

**Baustein A — Quotenreihe aus der Historie. Existiert bereits.**

`services/calculus.py` hat `Calculus.get_cost_quota(columns_costs: list)`. Die
Methode rechnet genau `Aufwand(t) / Umsatz(t)` fuer jede uebergebene Spalte und
haengt sie als `<spalte>_quota` an.

| | |
|---|---|
| Eingang | DataFrame mit `date`, `revenue` und den Aufwandsspalten |
| Formel | `df[spalte] / df["revenue"]` |
| Ausgang | derselbe DataFrame plus eine `_quota`-Spalte je Aufwandsposten |

Hier ist **nichts neu zu bauen** — nur aufzurufen.

**Baustein B — Fortschreibung. Muss neu gebaut werden.**

Gebraucht wird eine Rechenmethode, die eine Umsatzprognose und eine Quote je
Prognosejahr nimmt und daraus den Aufwand je Prognosejahr macht.

| | |
|---|---|
| Eingang | Umsatzprognose je Jahr (aus Schritt 1: `get_CAGR_prediction_plus_one`), eine Quote je Prognosejahr |
| Formel | `Aufwand(+n) = Umsatz(+n) * Quote(+n)` |
| Ausgang | ein Aufwandswert je Prognosejahr |
| Ort | `services/calculus.py` — reine Arithmetik auf einer Zeitreihe, wie `get_growth_rate` und `get_CAGR` |

Diese eine Methode deckt **alle vier Aufwandsposten der Gruppe A und zusaetzlich die
Investitionen aus Gruppe B** ab. Sie wird also fuenfmal aufgerufen und nur einmal
geschrieben — das ist die DRY-Stelle von Schritt 2.

**Wichtig fuer die Signatur:** Die Quote muss **je Jahr** uebergeben werden koennen,
nicht als ein einzelner Wert. Sonst laesst sich der fallende Verlauf des PDFs
(34,0 % -> 33,2 %) gar nicht abbilden, und die spaetere LLM-Anbindung (Teil 6)
waere blockiert. Eine konstante Quote ist dann einfach die Liste `[q, q, q, q, q, q]`.

> **Offene Entscheidung (Teil 8, Nr. 6):** Wie diese Methode genau heisst, welche
> Argumente sie nimmt und ob die Quote als Liste, Series oder Spalte kommt — das
> legst du fest, nicht dieses Dokument.

---

## Teil 3: Die Positionen — drei Rechenlogiken, nicht eine

### Theorie

Schritt 2 sieht im Guide aus wie eine lange Liste. Tatsaechlich fallen alle Positionen
in nur drei Gruppen:

```
Gruppe A — Common-Size          (4 Positionen)  -> Teil 2, fertig
Gruppe B — Sachanlagen/AfA      (1 Block)       -> eigene Mechanik, der grosse Brocken
Gruppe C — Sonderfaelle         (2 Positionen)  -> je eine kleine Extraregel
```

**Gruppe A: Common-Size.** Betrifft Wareneinsatz, Filialbetriebskosten, sonstige
betriebliche Aufwendungen und Verwaltungsaufwand. Alle vier laufen ueber exakt
dieselbe Formel aus Teil 2. Kein Unterschied in der Rechenlogik — nur andere
Eingangsspalten.

**Wichtige Abweichung gegenueber dem PDF:** Das PDF misst Filialbetriebskosten am
*Umsatz der firmeneigenen Filialen* und sonstige Aufwendungen am *Lizenz-/CPG-Umsatz*.
Diese Segmentaufteilung liefert keine API. **Bezugsgroesse ist bei uns immer der
Gesamtumsatz.** Das ist die allgemeine Regel des PDFs (S. 12) und methodisch sauber —
nur eben groeber.

Ebenso: Das PDF trennt Wareneinsatz und Mietkosten (Miete pro Filiale x Filialanzahl).
Beides steht nur im MD&A und in "Note 10: Leases". **Wir prognostizieren den
Gesamtposten `costOfRevenue` als eine Zahl.**

**Gruppe B: Sachanlagen und Abschreibungen.** Der aufwendigste Teil, folgt **nicht**
der Common-Size-Logik. Details in Teil 4. Der einzige Beruehrungspunkt: die
**Investitionsquote** (`capitalExpenditure / Umsatz`) wird genau wie eine Kostenquote
gesetzt. Alles danach ist reine Arithmetik.

**Gruppe C: Sonderfaelle.**

*Beteiligungsergebnis* — Treiber ist nicht der Umsatz, sondern der Buchwert der
Beteiligung:

```
Durchschnittlicher Buchwert = (Buchwert Anfang + Buchwert Ende) / 2
Beteiligungsergebnis        = Durchschnittlicher Buchwert x Renditeannahme
```

Das PDF nimmt fuer Starbucks 50 % Rendite und 5 % Wachstum des Buchwerts. 50 % ist
ungewoehnlich hoch — in dieser Zeile werden neben dem anteiligen Gewinn auch
Bruttomargen aus Warenlieferungen und Lizenzgebuehren ausgewiesen. Das ist
**Starbucks-spezifisch und nicht uebertragbar.**

*Einmalige Ertraege und Aufwendungen* — Regel des PDFs: pruefen, ob sie wiederkehren.
Wenn nicht: **auf null setzen.** Das ist der Normalfall und wird uebernommen.

### In Python

Diese Gruppierung ist die **Bauanleitung fuer die Reihenfolge**, nicht selbst Code:

| Gruppe | Baut auf | Neuer Code noetig? |
|---|---|---|
| A | Baustein A + B aus Teil 2 | nein — nur Aufrufe mit anderen Spalten |
| B | eigene Mechanik | ja — der groesste Block, Teil 4 |
| C | zwei kleine Extraregeln | ja — klein, Teil 4 Ende |

Konkret fuer Gruppe A: **kein neuer Rechencode.** Es wird nur `get_cost_quota()` mit
der Liste der Aufwandsspalten aufgerufen und danach der Fortschreibungs-Baustein je
Spalte. Die einzige Arbeit ist, **welche FMP-Spalten** in diese Liste gehoeren — das
ist offene Entscheidung Nr. 1 in Teil 8 und muss vor Stufe 1 geklaert sein.

Gruppe C ist erst am Ende dran (Stufe 4).

---

## Teil 4: Sachanlagen und Abschreibungen — der grosse Brocken

Hier lohnt sich Genauigkeit, weil dieser Teil den groessten Code-Anteil hat.

### Die Grundidee

> "forecast capital expenditures that lead projected future sales, and forecast
> depreciation expense amounts that lag capital expenditures" [PDF S. 15]

Uebersetzt:
- **Investitionen kommen vor dem Umsatz** — man baut die Filiale, bevor sie Umsatz macht.
- **Abschreibungen kommen nach der Investition** — man schreibt ab, was man gekauft hat.

Der ganze Block ist eine Kette von vier Rechnungen, die **in dieser Reihenfolge**
laufen muessen, weil jede das Ergebnis der vorigen braucht:

```
4.1 Nutzungsdauer  ->  4.2 Investitionen  ->  4.3 Abschreibungen  ->  4.4 Sachanlagen
```

---

### 4.1 Nutzungsdauer schaetzen

#### Theorie

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

#### In Python

Eine Rechenmethode, die aus zwei Zeitreihen eine einzige Zahl macht.

| | |
|---|---|
| Eingang | Sachanlagen **brutto** je Jahr, Abschreibungsaufwand je Jahr |
| Formel | `((brutto(t-1) + brutto(t)) / 2) / afa(t)` |
| Ausgang | eine Zahl (Jahre) |
| Ort | `services/calculus.py` |

**Datenherkunft — das ist der kritische Punkt:** Die Formel braucht Sachanlagen zu
*Anschaffungskosten* (brutto). FMP liefert nur `propertyPlantEquipmentNet` (netto).
Der Bruttowert kommt aus
`SEC.get_concept("PropertyPlantAndEquipmentGross")`. **Das ist der einzige Grund,
warum in Schritt 2 ueberhaupt die SEC-API gebraucht wird.**

`SEC.get_concept()` gibt eine Liste von dicts zurueck (`start`, `end`, `value`, ...),
sortiert nach `end`. Der FMP-DataFrame ist nach `date` sortiert. Beide muessen ueber
das Jahr zusammengefuehrt werden, bevor die Formel rechnen kann.

**Achtung Jahresbedarf:** Der Durchschnittsbestand kostet ein Jahr (Guide, Regel 2).
Aus 6 Jahren brutto entstehen nur **5** Nutzungsdauer-Werte.

> **Offene Entscheidung (Teil 8, Nr. 4):** Wird 10,3 auf 10 gerundet wie im PDF, oder
> exakt weitergerechnet? Und: ein Wert je Jahr oder ein Durchschnitt ueber alle Jahre?

---

### 4.2 Investitionen fortschreiben

#### Theorie

```
Investitionsquote = Investitionen(t) / Umsatz(t)
Prognose          = Umsatz(prognostiziert) x Investitionsquote
```

Das ist wieder Common-Size — angewandt auf `capitalExpenditure` aus dem Cash Flow.

#### In Python

**Kein neuer Rechencode.** Das sind exakt die beiden Bausteine aus Teil 2, nur mit
`capitalExpenditure` statt einer Aufwandsspalte:

```
get_cost_quota(["capitalExpenditure"])   ->  Quotenreihe
Fortschreibungs-Baustein                 ->  Investitionen je Prognosejahr
```

**Eine Vorzeichen-Falle:** FMP gibt `capitalExpenditure` im Cash Flow als **negative**
Zahl aus (Mittelabfluss). Die Abschreibungsrechnung in 4.3 braucht sie **positiv**.
Wo das Vorzeichen gedreht wird, muss festgelegt und im Code sichtbar sein — sonst
sinkt der Sachanlagenbestand statt zu steigen, und der Fehler faellt erst in Schritt 3
auf.

**Vorbedingung:** `FMP` hat aktuell nur `get_income_statement()`. Fuer diesen Teil
werden `get_balance_sheet()` und `get_cash_flow()` gebraucht. Beide Endpunkte stehen
schon in `FMP._endpoints` (Index 1 und 2) — die Methoden fehlen. Sie sind baugleich
zu `get_income_statement()`, also derselbe Aufbau mit anderem Endpunkt.

---

### 4.3 Abschreibungen schichtweise berechnen

#### Theorie

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

#### In Python

Die aufwendigste Methode von Schritt 2 — und die einzige mit einer Schleife ueber
zwei Dimensionen (Schicht x Jahr).

| | |
|---|---|
| Eingang | Restbuchwert Altbestand (= Sachanlagen netto des letzten Ist-Jahres), Investitionen je Prognosejahr (aus 4.2), Nutzungsdauer (aus 4.1) |
| Ausgang | Gesamtabschreibung je Prognosejahr; die Schichtentabelle selbst als nachvollziehbares Zwischenergebnis |
| Ort | `services/calculus.py` — reine Arithmetik, wiederverwendbar |

**Die Rechenlogik in Worten:**

1. Jede Schicht hat zwei Merkmale: einen **Jahresbetrag** (`Basis / Nutzungsdauer`)
   und einen **Restbuchwert**, der mit der Basis startet.
2. Schicht 0 ist der Altbestand, Basis = Restbuchwert des letzten Ist-Jahres.
   Schicht n ist die Investition des Prognosejahres n, Basis = diese Investition.
3. Fuer jedes Prognosejahr: ueber alle bis dahin existierenden Schichten laufen und
   je Schicht `min(Jahresbetrag, verbleibender Restbuchwert)` abschreiben. Dieses
   `min()` **ist** die Deckelung.
4. Restbuchwert der Schicht um den abgeschriebenen Betrag verringern.
5. Summe ueber alle Schichten = Gesamtabschreibung des Jahres.

**Der Testfall steht schon fertig in der PDF-Tabelle oben.** Mit Restbuchwert 4.088,3,
Nutzungsdauer 10 und den Investitionen 1.400 / 1.500 / 1.800 / 2.100 / 2.400 muss
Jahr +1 die Summe 1.104,2 und Jahr +5 fuer den Altbestand **231,6** statt 964,2
ergeben. Ergibt Jahr +5 noch 964,2, fehlt die Deckelung.

> **Offene Entscheidung (Teil 8, Nr. 3):** Welche Datenstruktur die Schichtentabelle
> hat — DataFrame, dict, Liste von Listen. Diese Entscheidung bestimmt den gesamten
> Aufbau dieser Methode und sollte vor Stufe 3 stehen.

---

### 4.4 Sachanlagen fortschreiben

#### Theorie

```
Sachanlagen zu AK (Ende)   = Sachanlagen zu AK (Anfang) + Investitionen
Kumulierte AfA (Ende)      = Kumulierte AfA (Anfang) + Abschreibung des Jahres
Sachanlagen netto          = Sachanlagen zu AK - Kumulierte AfA
```

#### In Python

Eine kleine Fortschreibungsmethode: drei Zeitreihen, die sich Jahr fuer Jahr aus
dem Vorjahr plus einer Bewegung ergeben.

| | |
|---|---|
| Eingang | Sachanlagen brutto und kumulierte AfA des letzten Ist-Jahres, Investitionen je Prognosejahr (4.2), Abschreibung je Prognosejahr (4.3) |
| Formel | die drei Zeilen oben, je Prognosejahr |
| Ausgang | brutto, kumulierte AfA und netto je Prognosejahr |
| Ort | `services/calculus.py` |

**Warum das nicht weggelassen werden darf, obwohl Schritt 2 nur das Betriebsergebnis
sucht:** Die Sachanlagen netto sind ein Bilanzposten und gehen direkt in **Schritt 3**
ein. Wer sie hier nicht mitfuehrt, muss die ganze Schichtenrechnung dort wiederholen.

**Plausibilitaets-Check:** Sachanlagen netto duerfen nie negativ werden. Passiert das,
fehlt die Deckelung aus 4.3.

---

### Was in Teil 4 NICHT uebernommen wird

Das PDF setzt fuer Starbucks feste Investitionsbetraege (1.400 / 1.500 / 1.800 /
2.100 / 2.400 Mio.) aus dem MD&A. Die haben wir nicht — deshalb 4.2.

Ebenso Starbucks-spezifisch: die Aufteilung der Abschreibung in 95 % eigene Zeile /
5 % im Wareneinsatz. Das ist eine Ausweisbesonderheit und wird nicht uebernommen.

---

### Gruppe C in Python

**Beteiligungsergebnis:**

| | |
|---|---|
| Eingang | Beteiligungsbuchwert je Jahr aus der Bilanz, eine Renditeannahme |
| Formel | `((buchwert(t-1) + buchwert(t)) / 2) * rendite` |
| Ausgang | ein Wert je Prognosejahr |

Der Buchwert muss dafuer selbst erst in die Zukunft fortgeschrieben werden (das PDF
nimmt 5 % Wachstum p. a.). Auch hier kostet der Durchschnitt ein Jahr.

> **Offene Entscheidung (Teil 8, Nr. 5):** Woher die Renditeannahme kommt — fester
> Wert, Parameter oder aus der Historie abgeleitet. Die 50 % des PDFs sind
> Starbucks-spezifisch und duerfen nicht fest verdrahtet werden.

**Einmaleffekte:** kein Code. Sie werden schlicht nicht in die Summe von 2.3
aufgenommen — das ist gleichbedeutend mit "auf null gesetzt".

---

## Teil 5: Rechenschritt 2.3 — das Betriebsergebnis

### Theorie

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

**Interpretation — was danach zu pruefen ist.** Operative Marge =
Betriebsergebnis / Umsatz. Im PDF steigt sie fuer Starbucks von 18,8 % (2015) auf
23,1 % (Year +5).

Eine **steigende Marge** bedeutet: die Kostenquoten sinken schneller, als der Umsatz
waechst — der Skaleneffekt.

**Warnung:** Steigende Margen in einer Prognose sind eine starke Annahme. Wenn nicht
begruendet ist, warum die Kostenquote weiter faellt, gehoert die Quote des letzten
Jahres konstant fortgeschrieben. Die Margenreihe ist damit der beste **Plausibilitaets-
Check** fuer den ganzen Schritt 2: springt sie unrealistisch hoch, stimmt eine Quote
nicht.

### In Python

Eine Subtraktion ueber die bereits berechneten Prognosereihen — und danach die
Margenreihe als Kontrollgroesse.

| | |
|---|---|
| Eingang | Umsatzprognose, alle Aufwandsprognosen der Gruppe A, Abschreibungen aus 4.3, Beteiligungsergebnis aus Gruppe C |
| Formel | `Umsatz - Summe(Aufwendungen) + Beteiligungsergebnis`, danach `Betriebsergebnis / Umsatz` |
| Ausgang | Betriebsergebnis und operative Marge je Prognosejahr |
| Ort | die Zusammenfuehrung gehoert in `sub_graphs/fsap.py` — dort laufen die Service-Ergebnisse zusammen (Architekturregel 3) |

**Die Doppelzaehlungs-Falle — hier schlaegt sie zu.** Bei FMP enthaelt
`operatingExpenses` je nach Anbieter bereits `sellingGeneralAndAdministrativeExpenses`
und `depreciationAndAmortization`. Werden alle drei subtrahiert, ist das
Betriebsergebnis zu niedrig und die Marge bricht ein.

**So wird es geprueft — an den Ist-Daten, nicht an der Prognose:** Man rechnet die
Summenformel fuer ein historisches Jahr durch und vergleicht sie mit dem von FMP
gelieferten `operatingIncome` desselben Jahres. Stimmen beide ueberein, ist die
Spaltenauswahl richtig. Weichen sie ab, wird doppelt gezaehlt oder ein Posten fehlt.
**Dieser Abgleich sollte laufen, bevor die erste Prognosezahl entsteht** — er
beantwortet die offene Entscheidung Nr. 1 aus Teil 8 empirisch statt durch Raten.

---

## Teil 6: Wo genau ein LLM entscheidet

### Theorie

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

**Die Entscheidungstabelle:**

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

**Was das LLM darf:**

- Einen erkennbaren **Trend fortschreiben** statt einer Durchschnittsquote — das PDF
  tut bei Starbucks genau das (34,0 % -> 33,2 %).
- Ein **Ausreisserjahr ausschliessen** und das begruenden.
- Bei zu starker Schwankung **`konfidenz = niedrig`** melden.

**Was das LLM niemals darf:**

- **Die Abschreibungsschichten-Tabelle berechnen.** Der Guide sagt das ausdruecklich:
  reine Arithmetik gehoert nicht an ein LLM. Ein LLM rechnet unzuverlaessig, und der
  Fehler waere hier still — die Bilanz stimmt einfach nicht mehr.
- Die Nutzungsdauer schaetzen — das ist eine Formel.
- Das Betriebsergebnis bilden.

**Idealer Input je Aufruf:**

- Der Aufwandsposten und der Umsatz je Jahr fuer **alle** verfuegbaren Jahre
- Die daraus berechnete Quotenreihe
- Branche der Firma
- Bei der Investitionsquote zusaetzlich der **Anlagenalter-Indikator**:

```
Anlagenalter = Kumulierte Abschreibungen / Sachanlagen zu Anschaffungskosten
```

Ein hoher Wert heisst: der Bestand ist weitgehend abgeschrieben, Ersatzinvestitionen
stehen an — die Investitionsquote sollte steigen. Genau damit begruendet das PDF die
steigenden Starbucks-Investitionen (S. 15-16). Das klingt nach MD&A-Wissen, ist aber
aus der Bilanz ablesbar. **Das ist die interessanteste LLM-Stelle in Schritt 2**,
weil hier eine scheinbar unerreichbare Information doch aus dem Abschluss
rekonstruiert wird.

### In Python

Drei Teile — und **keiner davon aendert eine bestehende Rechenmethode**. Die
LLM-Quote wird lediglich anstelle der Rueckfall-Quote in den Fortschreibungs-Baustein
aus Teil 2 gegeben.

**1. Der Aufruf. Existiert bereits.**
`services/llm_call.py` mit `LLMCall(model).llm_call(context, system_prompt, prompt)`.
Rueckgabe ist `response.content` — Index 0 ein ThinkingBlock, Index 1 ein TextBlock
mit dem eigentlichen Antworttext.

**2. Ein Antwortmodell.** Der Guide legt drei Felder fest, einheitlich fuer alle
LLM-Stellen des gesamten FSAP:

| Feld | Inhalt |
|---|---|
| `wert` | die Quote bzw. die Quotenreihe |
| `begruendung` | ein bis zwei Saetze, warum genau dieser Wert |
| `konfidenz` | hoch / mittel / niedrig |

Ort: `pydantic_models/pydantic_models.py` (Architekturregel 4). Weil `llm_call()`
Text zurueckgibt, muss dieser Text in das Modell ueberfuehrt werden — der Weg dorthin
(JSON im Prompt anfordern und parsen, oder ein anderer) ist offen.

**3. Ein Prompt, nicht vier.** Alle vier Stellen fragen dasselbe. Gebraucht wird ein
**generischer Prompt mit Parametern**: Name des Postens, Quotenreihe, Branche,
Anzahl Prognosejahre — bei der Investitionsquote zusaetzlich das Anlagenalter.

**4. Der Rueckfall bleibt bestehen.** Bei fehlender Antwort, Parse-Fehler oder
`konfidenz = niedrig` greift die Regel aus der Tabelle oben.
**Schritt 2 muss ohne LLM vollstaendig durchlaufen** — nur eben konservativ. Genau
deshalb kommt das LLM in der Baureihenfolge zuletzt (Teil 7, Stufe 5).

> **Offene Entscheidung (Teil 8, Nr. 7):** ein generischer Prompt oder vier eigene.
> Teil 6 empfiehlt einen generischen (DRY).

---

## Teil 7: Was du wann in Python baust

Die Reihenfolge folgt nicht der Nummerierung des Guides, sondern der Schwierigkeit.
**Nach jeder Stufe laeuft etwas Lauffaehiges.**

### Stufe 0 — Datenbeschaffung

| Quelle | Felder | Status |
|---|---|---|
| `FMP.get_income_statement()` | `revenue`, `costOfRevenue`, `sellingGeneralAndAdministrativeExpenses`, `operatingExpenses`, `depreciationAndAmortization`, `operatingIncome` | **da** |
| `FMP.get_balance_sheet()` | `propertyPlantEquipmentNet`, Beteiligungsbuchwert | **fehlt** |
| `FMP.get_cash_flow()` | `capitalExpenditure` | **fehlt** |
| `SEC.get_concept("PropertyPlantAndEquipmentGross")` | Sachanlagen brutto | **da** |

**Was gebaut wird:** `get_balance_sheet()` und `get_cash_flow()` in
`services/fmp_api.py`. Beide Endpunkte stehen bereits in `FMP._endpoints`
(Index 1 und 2). Der Aufbau ist identisch zu `get_income_statement()`: gleiche
Parameter (`period`, `limit`), gleiche Datumsumwandlung, gleiche aufsteigende
Sortierung.

> **Hier ist die DRY-Frage zu stellen:** Drei fast identische Methoden sind eine
> Wiederholung. Ob daraus eine gemeinsame Hilfsmethode mit dem Endpunkt als Argument
> wird, ist deine Entscheidung — sinnvoll waere sie.

**Noetige Jahre: 6.** Kostenquoten und Investitionsquote brauchen je ein Jahr und
ergeben 6 Werte. Nutzungsdauer und Beteiligungsrendite brauchen einen
Durchschnittsbestand und ergeben deshalb nur 5 Werte.

---

### Stufe 1 — Quotenreihen aus der Historie

**Was:** `Aufwand(t) / Umsatz(t)` ueber alle Jahre, angewandt auf jede Aufwandsspalte.

**Zu bauen:** nichts — `Calculus.get_cost_quota()` existiert. Es wird nur die
**Spaltenliste** festgelegt und der Aufruf gemacht.

**Warum zuerst:** Es ist die kleinste sinnvolle Einheit, und du siehst sofort echte
Zahlen — steigen die Quoten, fallen sie, schwanken sie? Diese Anschauung brauchst du
fuer jede weitere Entscheidung.

**Hier gehoert der Doppelzaehlungs-Test aus Teil 5 hin:** Summenformel gegen
`operatingIncome` eines Ist-Jahres pruefen, bevor weitergebaut wird.

**Ergebnis:** Eine Quotentabelle. Noch keine Prognose.

---

### Stufe 2 — Aufwandsposten fortschreiben (ohne LLM)

**Was:** `Umsatz(+n) x Quote` mit der **Rueckfall-Regel** — letzte historische Quote,
konstant.

**Zu bauen:** der Fortschreibungs-Baustein aus Teil 2 (Baustein B) in
`services/calculus.py`. Eingang: Umsatzprognose aus `get_CAGR_prediction_plus_one()`
und eine Quote je Prognosejahr.

**Warum jetzt:** Damit ist Gruppe A komplett und Schritt 2 laeuft zum ersten Mal
durch. Kein LLM, keine Sonderfaelle, keine SEC-API. Alles Weitere ist Verfeinerung.

**Ergebnis:** Prognostizierte Aufwandsposten fuer Year +1 bis +6.

---

### Stufe 3 — Sachanlagen und Abschreibungen

Der groesste Block. In dieser Reihenfolge:

| # | Was | Neu zu bauen |
|---|---|---|
| 1 | `get_balance_sheet()` / `get_cash_flow()` (Stufe 0) | ja |
| 2 | Sachanlagen brutto von der SEC holen und mit FMP zusammenfuehren | ja |
| 3 | Nutzungsdauer schaetzen (4.1) | ja |
| 4 | Investitionen fortschreiben (4.2) | nein — Bausteine aus Teil 2 |
| 5 | Abschreibungsschichten **mit Deckelung** (4.3) | ja — der Kern |
| 6 | Sachanlagen brutto / kumulierte AfA / netto (4.4) | ja |

**Der kritische Punkt ist 5.** Bau die Deckelung sofort mit ein, nicht nachtraeglich.
Teste sie an der PDF-Tabelle: Wenn dein Jahr +5 fuer den Altbestand 231,6 statt 964,2
ergibt, stimmt die Logik.

---

### Stufe 4 — Sonderfaelle und Abschluss

1. Beteiligungsergebnis (Durchschnittsbuchwert x Rendite) — neue kleine Methode
2. Einmaleffekte = 0 — kein Code
3. Betriebsergebnis bilden — Subtraktion in `sub_graphs/fsap.py`
4. Operative Marge als Plausibilitaets-Check ausgeben

**Nach dieser Stufe ist Schritt 2 fachlich vollstaendig** — deterministisch,
nachvollziehbar, ohne LLM.

---

### Stufe 5 — Das LLM einsetzen

**Erst jetzt.** Du ersetzt an den vier Stellen aus Teil 6 die Rueckfall-Quote durch
eine LLM-gesetzte Quote. Der Rueckfall bleibt bestehen und greift bei fehlender oder
niedrig-konfidenter Antwort.

**Zu bauen:** das Antwortmodell in `pydantic_models.py`, der generische Prompt, und
die Uebergabe der LLM-Quote an den Fortschreibungs-Baustein. `services/llm_call.py`
steht bereits.

**Warum zuletzt:** Du hast dann eine deterministische Vergleichsbasis. Du siehst genau,
was das LLM an der Prognose veraendert — und das ist fuer die Thesis ein starkes
Argument, weil du den Beitrag des LLM messen kannst statt ihn zu behaupten.

---

### Architektur-Einordnung

| Was | Wohin | Warum |
|---|---|---|
| `get_balance_sheet()`, `get_cash_flow()` | `services/fmp_api.py` | Datenimport |
| Quotenberechnung, Fortschreibung, Nutzungsdauer, Abschreibungsschichten, Sachanlagen | `services/calculus.py` | Reine Rechenlogik, wiederverwendbar |
| Orchestrierung von Schritt 2, Betriebsergebnis | `sub_graphs/fsap.py` | Sub-Graph konsumiert Services |
| LLM-Antwortmodell, Ein- und Ausgaben | `pydantic_models/pydantic_models.py` | Architekturregel 4 |

Sub-Graphs konsumieren Services und niemals andere Sub-Graphs (Architekturregel 3).

---

## Teil 8: Was du entscheiden musst, bevor Code entsteht

Diese Punkte kann kein Dokument fuer dich beantworten — sie legen den Umfang fest.

### Bereits entschieden

- **2.1 wird nicht implementiert.** Nur Common-Size (Teil 1).

### Noch offen

| Nr. | Frage | Blockiert |
|---|---|---|
| 1 | Welche Aufwandsposten einzeln, welche zusammengefasst? | Stufe 1 |
| 2 | Rueckfall-Regel: letzte Quote, Durchschnitt oder Trend? | Stufe 2 |
| 3 | Datenstruktur der Abschreibungsschichten-Tabelle | Stufe 3 |
| 4 | Nutzungsdauer runden oder exakt? | Stufe 3 |
| 5 | Renditeannahme fuer Beteiligungen: fest, Parameter oder aus Historie? | Stufe 4 |
| 6 | Klasse oder Funktionen? Bei Klasse: welche Attribute? | alle |
| 7 | Ein generischer LLM-Prompt fuer alle vier Quoten, oder vier eigene? | Stufe 5 |
| 8 | Prognosehorizont und Anzahl historischer Jahre: Parameter oder fest? | alle |

**Zu Nr. 1:** FMP liefert `costOfRevenue`, `sellingGeneralAndAdministrativeExpenses`,
`operatingExpenses`, `depreciationAndAmortization`. Die PDF-Aufteilung
(Filialbetriebskosten vs. sonstige betriebliche Aufwendungen) existiert in FMP nicht.
*Achtung Doppelzaehlung:* `operatingExpenses` enthaelt je nach Anbieter bereits die
SG&A- und AfA-Zeilen. Der Abgleich gegen `operatingIncome` aus Teil 5 beantwortet
das empirisch.

**Zu Nr. 2:** Der Guide nennt fuer Kostenquoten "letzte Quote", fuer die
Investitionsquote "Durchschnitt". Uebernehmen oder vereinheitlichen?

Punkt 1 und 3 legen den groessten Teil des Umfangs fest. Alles Weitere kann
schrittweise entschieden werden.

---

## Anhang: Alle "In Python"-Bloecke auf einen Blick

| Teil | Was | Zu bauen |
|---|---|---|
| 1 | Fix-/Variabel-Trennung | nichts |
| 2 A | Quotenreihe `Aufwand/Umsatz` | nichts — `get_cost_quota()` existiert |
| 2 B | Fortschreibung `Umsatz x Quote` | **neu** — deckt 5 Anwendungsfaelle ab |
| 3 | Gruppierung A/B/C | nichts — Bauanleitung |
| 4.0 | `get_balance_sheet()`, `get_cash_flow()` | **neu** |
| 4.1 | Nutzungsdauer | **neu** — braucht SEC-Bruttowert |
| 4.2 | Investitionen | nichts — Bausteine aus Teil 2 (Vorzeichen beachten) |
| 4.3 | Abschreibungsschichten mit Deckelung | **neu** — der Kern |
| 4.4 | Sachanlagen brutto/AfA/netto | **neu** |
| 4 C | Beteiligungsergebnis | **neu**, klein |
| 5 | Betriebsergebnis + Marge | **neu**, im Sub-Graph |
| 6 | LLM-Antwortmodell + generischer Prompt | **neu** — `llm_call()` existiert |
