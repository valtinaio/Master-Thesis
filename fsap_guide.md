# FSAP: 7-Schritte-Forecasting und Bewertung -- Ablauf, Rechenschritte, Interpretation

Diese Datei erklaert den kompletten FSAP-Prozess in nicht-technischer Sprache. Fuer
jeden Schritt steht am Ende, was in Python dafuer gebaut werden muss.

Sie hat zwei Teile mit **zwei verschiedenen Quellen**:

| Teil | Inhalt | Quelle |
|---|---|---|
| **Schritte 1-7** | Prognose der drei Jahresabschluesse | das Quell-PDF (Buchkapitel 10) |
| **Kapitel 8** | Bewertung und Kaufentscheidung | Blatt `Valuation` aus `fsap/FSAP - Starbucks.xlsx` |

---

## Quelle und Zitierweise

Das Quell-PDF ist `FSAP 7-Step Forecasting Framework for Starbucks_.pdf` (55 Seiten).
Es ist **Kapitel 10 "Forecasting Financial Statements"** aus:

> Wahlen, J. M., Baginski, S. P., & Bradshaw, M. T.: *Financial Reporting, Financial
> Statement Analysis, and Valuation: A Strategic Perspective*. Cengage Learning.

"FSAP" = **Financial Statement Analysis Package**, das Excel-Werkzeug, das dem Buch
beiliegt. FSAP ist kein akademisches Framework mit einem eigenen Ursprungspaper,
sondern das Begleittool zu diesem Lehrbuch. Das vorliegende PDF **ist** deshalb die
Primaerquelle; es kann nicht "vom Original abweichen".

**Zitierweise in dieser Datei:** `[PDF S. n, "Abschnittsueberschrift"]`. Die
Seitenzahl ist die PDF-Seite (1-55). Wo das PDF selbst eine Buchseite nennt, steht
sie zusaetzlich dabei.

**Wichtiger Hinweis zur Bewertung:** Das PDF endet nach Schritt 7. Die eigentliche
Bewertung (DCF, Residual Income, Kaufentscheidung) ist Kapitel 11-14 desselben Buchs
und **nicht** Teil dieses Auszugs. Die 7 Schritte liefern die *Prognosen*, die
der Input der Bewertung sind.

Die Bewertung ist trotzdem dokumentiert -- siehe **Kapitel 8** dieser Datei. Quelle
dort ist nicht das PDF, sondern das Blatt `Valuation` der Datei
`fsap/FSAP - Starbucks.xlsx`, also die rechnende Referenzimplementierung von FSAP
selbst.

---

## Kennzeichnung der Abweichungen

Das PDF formuliert fast ueberall zuerst eine **allgemeine Regel** und wendet sie dann
auf Starbucks an. Nur die allgemeine Regel darf generisch implementiert werden.
Drei Markierungen kommen in dieser Datei vor:

| Markierung | Bedeutung |
|---|---|
| **[ALLGEMEIN]** | Die Regel, die das PDF selbst als allgemein gueltig formuliert. Das ist die Regel, die implementiert wird. |
| **[SBUX-SPEZIFISCH]** | Eine Annahme, die nur fuer Starbucks gilt (Filialzahlen, Guthabenkarten, 53. Woche, konkrete Prozentsaetze). Wird **nicht** generisch implementiert. Fundstelle ist genannt. |
| **[ABWEICHUNG]** | Hier weicht die geplante Implementierung bewusst vom PDF ab, weil FMP/SEC die noetigen Daten nicht liefern. Die PDF-Variante ist jeweils zitiert, damit die Abweichung in der Thesis begruendbar ist. |
| **[LLM-LOESBAR]** | Eine Abweichung, bei der die fehlende Groesse **keine fehlende Zahl, sondern ein fehlendes Urteil** ist. Ein LLM, das den Jahresabschluss liest, kann dieses Urteil bilden. Steht immer direkt bei der betroffenen [ABWEICHUNG] und nennt Aufgabe, Idealdaten und Rueckfall. |

---

## Der Ueberblick: worum es ueberhaupt geht

Ziel des Prozesses ist: aus den **vergangenen** Jahresabschluessen einer Firma die
**zukuenftigen** Jahresabschluesse zu prognostizieren -- typischerweise fuer die
naechsten fuenf Jahre ("Year +1" bis "Year +5") plus ein Jahr fuer den langfristigen
Zustand ("Year +6").

Prognostiziert werden alle drei Abschluesse:

1. **Gewinn- und Verlustrechnung** (Income Statement): Was verdient die Firma?
2. **Bilanz** (Balance Sheet): Was besitzt und schuldet die Firma?
3. **Kapitalflussrechnung** (Statement of Cash Flows): Wohin fliesst das Geld?

Die Reihenfolge der 7 Schritte ist nicht beliebig. Sie folgt einer Kette: Der Umsatz
treibt die Aufwendungen, Umsatz und Aufwendungen treiben die Bilanzposten, die Bilanz
bestimmt den Finanzierungsbedarf, der Finanzierungsbedarf bestimmt Zinsen, Zinsen
bestimmen den Gewinn, und der Gewinn fliesst zurueck in die Bilanz.

```
Schritt 1: Umsatz
    v
Schritt 2: Betriebliche Aufwendungen  ->  vorlaeufiges Betriebsergebnis
    v
Schritt 3: Betriebliche Vermoegenswerte und Schulden (Bilanz)
    v
Schritt 4: Finanzierung (Schulden, Eigenkapital) + Zinsertrag/Zinsaufwand
    v
Schritt 5: Steuern, Nettogewinn, Dividenden, Aktienrueckkaeufe, Gewinnruecklagen
    v
Schritt 6: Bilanz zum Ausgleich bringen (Aktiva = Passiva)
    v
Schritt 7: Kapitalflussrechnung ableiten
```

Der Prozess enthaelt eine eingebaute **Zirkularitaet**: Zinsen haengen von den Schulden
ab, die Schulden haengen vom Finanzierungsbedarf ab, der Finanzierungsbedarf haengt vom
Gewinn ab, der Gewinn haengt von den Zinsen ab. Wie damit umzugehen ist, steht in
Schritt 6.

### Die zwei Kernideen, die alles tragen

Fast jeder Rechenschritt ist eine Variante einer dieser beiden Ideen:

**Idee 1 -- Common-Size (Prozent vom Umsatz).**
Ein Posten wird als fester Prozentsatz des Umsatzes fortgeschrieben.

```
Prognose(Posten) = Prognose(Umsatz) x Prozentsatz
```

Beispiel: Verwaltungsaufwand war historisch stabil bei 6 % des Umsatzes, also wird er
mit 6 % des prognostizierten Umsatzes angesetzt.

**Idee 2 -- Turnover / Umschlagsdauer (Anzahl Tage).**
Ein Bilanzposten wird ueber die Zahl der Tage bestimmt, die er "vorhaelt".

```
Prognose(Bestand) = (Prognose(Bezugsgroesse) / 365) x Anzahl Tage
```

Beispiel: Das Lager reicht historisch fuer 56 Tage Warenverkauf, also ist der
Lagerbestand 56/365 des prognostizierten Wareneinsatzes.

Wer diese zwei Formeln verstanden hat, versteht rund 80 % des gesamten Verfahrens.

### Interpretation: warum ueberhaupt so aufwaendig?

Das PDF stellt am Ende die "Shortcut"-Methode gegenueber: Umsatz einfach mit der
historischen Wachstumsrate fortschreiben und die historische Nettomarge anwenden
[PDF S. 54, "Shortcut Approaches to Forecasting"]. Fuer Starbucks liefert das einen
deutlich hoeheren Umsatz und einen deutlich niedrigeren Gewinn als die detaillierte
Methode. Die Autoren begruenden ihre Praeferenz so:

> "Given that forecast errors can be very costly if they lead to bad investment
> decisions, we strongly advocate the careful, detailed approach"
> [PDF S. 55, "Shortcut Approaches to Forecasting"].

Der Shortcut unterstellt, dass alle bestehenden Verhaeltnisse linear in die Zukunft
gelten. Die detaillierte Methode erlaubt, einzelne Posten unterschiedlich zu behandeln
-- z. B. sinkende Kostenquoten bei steigenden Filialkosten.

---

## Ein Hinweis vorweg: Was der Datenbestand hergibt

Zwei Datenquellen stehen zur Verfuegung: `services/fmp_api.py` (Financial Modeling
Prep) und `services/sec_api.py` (SEC XBRL). Beide liefern **strukturierte
Abschlussdaten**.

Das PDF stuetzt sich an vielen Stellen zusaetzlich auf den **MD&A-Fliesstext** des
Geschaeftsberichts ("Fiscal 2016 -- The View Ahead"), auf **Anhangsangaben** (Notes)
und auf **Segmentberichte**. Diese Angaben sind Prosa und ueber die APIs nicht
maschinell verwertbar.

Daraus folgt der grundlegende Unterschied zwischen PDF und Implementierung:

> Das PDF forecastet **wissensbasiert**: der Analyst liest den Geschaeftsbericht und
> bildet Annahmen. Die Implementierung forecastet **datenbasiert**: sie leitet
> Annahmen aus der historischen Zeitreihe ab.

Jede **[ABWEICHUNG]** in dieser Datei ist eine Auspraegung dieses einen Unterschieds.
Fuer die Thesis laesst sich das als eine einzige, begruendete Designentscheidung
formulieren -- nicht als Sammlung von Einzelkompromissen.

---

## Zwei Arten von Abweichung: fehlende Zahl vs. fehlendes Urteil

Die Abweichungen sind nicht alle gleich. Sieht man genau hin, zerfallen sie in zwei
Gruppen, und nur eine davon ist wirklich ein Datenproblem.

**Gruppe 1 -- fehlende Zahl.** Das PDF benutzt eine Groesse, die in *keinem*
Jahresabschluss steht: Filialzahlen, Umsatz pro Filiale, Mietaufwand je Filiale, die
Faelligkeitstermine einzelner Anleihen, die Aufteilung des Umsatzes auf Segmente. Wer
den Abschluss liest, findet diese Zahlen dort nicht. Ein LLM auch nicht -- es koennte
sie nur erfinden. Diese Abweichungen bleiben Abweichungen.

**Gruppe 2 -- fehlendes Urteil.** Hier fehlt keine Zahl, sondern eine *Entscheidung*.
Die Zahlen liegen vollstaendig im Abschluss; das PDF laesst einen Menschen daraus
etwas ableiten:

- Welche Quote wird fortgeschrieben -- die des letzten Jahres, ein Durchschnitt, oder
  ein erkennbarer Trend?
- Ist ein Ausreisserjahr ein Ausreisser oder der neue Normalzustand?
- Welcher Bilanzposten eignet sich als Ausgleichsposten fuer *diese* Firma?
- Ist die Fortschreibung einer Kennzahl hier ueberhaupt zulaessig, oder schwankt sie
  zu stark?

Genau das sind Aufgaben, die ein LLM uebernehmen kann: Es bekommt die historischen
Werte aus dem Abschluss, urteilt darueber und liefert **eine Zahl plus eine
schriftliche Begruendung**. Solche Stellen sind mit **[LLM-LOESBAR]** gekennzeichnet.

### Warum ein LLM und nicht einfach eine Formel?

Eine Formel muss sich fuer *alle* Firmen fuer denselben Weg entscheiden -- z. B.
"immer den Dreijahresdurchschnitt". Das ist bei einer stabilen Firma richtig und bei
einer Firma mit einem Sondereffekt im mittleren Jahr falsch. Das LLM darf pro Firma
unterschiedlich entscheiden, so wie der Analyst im PDF es tut. Der Preis dafuer ist,
dass die Entscheidung nicht mehr reproduzierbar-deterministisch ist -- deshalb gilt:

> **Jede [LLM-LOESBAR]-Stelle hat einen deterministischen Rueckfall.** Faellt der
> LLM-Aufruf aus, liefert er einen unplausiblen Wert oder fehlt die Datenbasis, greift
> die einfache Regel, die ohnehin schon in dieser Datei beschrieben ist. Das LLM
> *verbessert* die Annahme, es ist nie die einzige Quelle dafuer.

### Was das LLM ausgibt

Einheitlich fuer alle [LLM-LOESBAR]-Stellen, damit nur **ein** Prompt-Muster und
**ein** Pydantic-Modell noetig sind (DRY):

| Feld | Inhalt |
|---|---|
| `wert` | die gesetzte Annahme (Quote, Wachstumsrate, Tage, Steuersatz, ...) |
| `begruendung` | ein bis zwei Saetze, warum genau dieser Wert |
| `konfidenz` | hoch / mittel / niedrig -- bei "niedrig" wird der Rueckfall verwendet |

Die `begruendung` ist fuer die Thesis wertvoll: Sie macht die Prognose erklaerbar und
ist genau das, was das PDF als Fliesstext des Analysten liefert.

### Was das LLM idealerweise braucht

Bei jeder [LLM-LOESBAR]-Stelle steht unter **"Idealer Input"**, welche Angaben das
LLM haben muesste, um so gut zu urteilen wie der Analyst im PDF. Das ist bewusst als
*Wunschliste* formuliert und noch nicht als Umsetzungsplan -- welche dieser Angaben
FMP und SEC tatsaechlich liefern, ist getrennt davon zu pruefen. Ein Muster wiederholt
sich in fast allen Faellen:

1. die betroffene Kennzahl als **Zeitreihe** ueber alle verfuegbaren Jahre
2. die **Bezugsgroesse** derselben Jahre (meist der Umsatz), damit Quoten bildbar sind
3. **Branche und Groesse** der Firma als Kontext
4. wo vorhanden: **erlaeuternder Text** des Geschaeftsberichts (MD&A, Anhang)

Punkt 4 ist der einzige, der ueber die reinen Zahlen hinausgeht -- und zugleich der,
der aus einigen Gruppe-1-Faellen Gruppe-2-Faelle machen wuerde.

---
---

# Schritt 1: Umsatz prognostizieren

> Fundstelle: [PDF S. 1-12, "Step 1: Project Revenues"]

## Warum zuerst der Umsatz?

Der Umsatz ist die Grundlage fuer fast alles Weitere. Das PDF:

> "Analysts frequently use the expected future level of revenues as a basis for
> deriving many other amounts in the financial statement forecasts. Therefore,
> analysts typically begin the forecasting process by projecting revenues."
> [PDF S. 1]

## Die allgemeine Regel

**[ALLGEMEIN]** Umsatz wird zerlegt in **Menge x Preis** [PDF S. 1]:

```
Umsatz = Absatzmenge x Preis pro Einheit
```

Was als "Menge" dient, haengt von der Branche ab. Das PDF nennt: Fahrzeugstueckzahlen
(Automobilhersteller), verkaufte Gallonen (Getraenke), Filialanzahl (Handel,
Restaurantketten), Passagiermeilen (Airlines) [PDF S. 1].

**[ALLGEMEIN]** Faktoren, die die Mengenprognose beeinflussen [PDF S. 1]:
- Branchenwachstum insgesamt
- Marktanteilsveraenderungen der Firma
- Kapazitaetsausweitungen der Firma
- Bevoelkerungswachstum in den Absatzmaerkten

**[ALLGEMEIN]** Faktoren, die die Preisprognose beeinflussen [PDF S. 1]:
- Ueberkapazitaet oder Kapazitaetsknappheit in der Branche
- Rohstoffpreise
- Substitutionsprodukte
- technologischer Wandel
- Markenstaerke (Marken koennen Preise besser halten als Generika)
- Inflation und Wechselkurse
- Akquisitionen (erhoehen Umsatz) und Verkaeufe von Geschaeftsteilen (senken ihn)

**[ALLGEMEIN] Der entscheidende Fallback -- die Regel, die implementiert wird:**

> "If revenues have grown at a reasonably steady rate in prior periods and you expect
> that economic, industry, and firm-specific factors will remain stable, you can
> project that the historical growth rate will persist into the future."
> [PDF S. 2, "Step 1: Project Revenues"]

Das ist der Kern dessen, was mit FMP/SEC-Daten umsetzbar ist.

**[ALLGEMEIN]** Das PDF nennt zwei Faelle, in denen die Fortschreibung *nicht*
funktioniert [PDF S. 2]:
- **Zyklische Firmen** (Maschinenbau, Versicherer, Investmentbanken): Wachstumsraten
  schwanken stark mit dem Konjunkturzyklus.
- **Firmen mit Produktpipeline** (Pharma, Technologie, Oel & Gas): Wachstum haengt an
  Forschungserfolgen, die man nicht aus der Historie ablesen kann.

## Wie Starbucks im PDF gerechnet wird

**[SBUX-SPEZIFISCH]** Das PDF forecastet Starbucks in fuenf Segmenten (Americas,
CAP, EMEA, Other Stores, CPG/Foodservice) und je Segment getrennt nach
firmeneigenen und lizenzierten Filialen [PDF S. 2-12, "Projecting Revenues for
Starbucks"].

Die Kernformel dabei [PDF S. 6, "Americas Revenue Growth"]:

```
Durchschnittliche Filialen im Jahr = (Filialen Jahresanfang + Filialen Jahresende) / 2
Umsatz pro Filiale (neu)           = Umsatz pro Filiale (alt) x (1 + Wachstumsrate)
Segmentumsatz                      = Durchschnittliche Filialen x Umsatz pro Filiale
```

Die Halbierung unterstellt, dass neue Filialen im Schnitt ein halbes Jahr geoeffnet
sind [PDF S. 6].

**[SBUX-SPEZIFISCH]** Die einzelnen Annahmen (je 350 neue Filialen in Americas,
6 % Umsatzwachstum je Filiale; 300/600 neue Filialen in CAP, 7 %; 200 neue lizenzierte
Filialen in EMEA, 2 %; 3 % in Other Stores; 10 % in CPG) stammen aus dem MD&A-Abschnitt
"Fiscal 2016 -- The View Ahead" des Geschaeftsberichts [PDF S. 5-11].

**[SBUX-SPEZIFISCH]** Die **53. Woche**: Starbucks' Geschaeftsjahr endet am Sonntag,
der dem 30. September am naechsten liegt. Alle sechs bis sieben Jahre hat das
Geschaeftsjahr deshalb 53 statt 52 Wochen. Das PDF multipliziert den Umsatz von
Year +1 mit 53/52 = 1,019 [PDF S. 11-12, "Starbucks' Combined Revenue Growth
Forecasts, Including the 53rd-Week Effect"].

**[SBUX-SPEZIFISCH]** Fuer Year +6 und danach: 3,0 % nominales Wachstum, begruendet
als langfristiges reales Wirtschaftswachstum plus langfristige Inflation
[PDF S. 12, Fussnote 7].

## [ABWEICHUNG] Was stattdessen implementiert wird

**Nicht umsetzbar:** Segmentweise Prognose ueber Filialzahlen. Weder FMP noch SEC
liefern Filialzahlen oder Umsatz pro Filiale. Diese stehen ausschliesslich im
MD&A-Fliesstext.

**Umgesetzt wird die allgemeine Fallback-Regel des PDFs** [PDF S. 2]: Fortschreibung
der historischen Wachstumsrate auf den Gesamtumsatz.

Die Rechenschritte:

**1.1 Historische Wachstumsraten** -- fuer jedes Paar aufeinanderfolgender Jahre:

```
Wachstumsrate(t) = Umsatz(t) / Umsatz(t-1) - 1
```

**1.2 Die Basis-Wachstumsrate** -- das PDF verwendet an mehreren Stellen die
zusammengesetzte jaehrliche Wachstumsrate (CAGR), z. B. "a compounded annual growth
rate of 13.5% from 2013 to 2015" [PDF S. 2] und "a compound annual growth rate in
revenues of 12.3%" [PDF S. 54]:

```
CAGR = (Umsatz(letztes Jahr) / Umsatz(erstes Jahr))^(1 / Anzahl Jahre) - 1
```

Beispiel mit Zahlen aus dem PDF [PDF S. 3, Exhibit 10.2]:
Umsatz 2013 = 14.866,8; Umsatz 2015 = 19.162,7; Anzahl Jahre = 2.

```
CAGR = (19.162,7 / 14.866,8)^(1/2) - 1 = 1,2889^0,5 - 1 = 1,1353 - 1 = 13,53 %
```

Das deckt sich mit den 13,5 %, die das PDF nennt.

**1.3 Prognose Year +1 bis +5:**

```
Umsatz(+1) = Umsatz(letztes Ist-Jahr) x (1 + g)
Umsatz(+n) = Umsatz(+n-1) x (1 + g)
```

**1.4 Prognose Year +6** (langfristiger Zustand, PDF-Annahme uebernommen,
[PDF S. 12, Fussnote 7]):

```
Umsatz(+6) = Umsatz(+5) x (1 + 0,03)
```

### [LLM-LOESBAR] Die Wahl der Wachstumsrate

Die Zahlen fehlen hier nicht -- die Umsatzreihe steht vollstaendig im Abschluss.
Was fehlt, ist das Urteil darueber. Die CAGR ueber den gesamten Zeitraum ist nur
*eine* moegliche Lesart, und der Abschnitt "Interpretation" unten nennt selbst den
Fall, in dem sie in die Irre fuehrt (Raten +40 %, -20 %, +30 %).

**Aufgabe fuer das LLM:** aus der historischen Umsatzreihe die Wachstumsrate `g` fuer
Year +1 bis +5 setzen und begruenden. Es darf dabei

- ein erkennbares Ausreisserjahr ausschliessen und das begruenden,
- einen fallenden Trend fortschreiben statt eine Durchschnittsrate zu verwenden
  (das PDF tut genau das bei Starbucks: sinkende Raten ueber die Jahre),
- bei zu starker Schwankung `konfidenz = niedrig` melden.

**Idealer Input:** Umsatz je Jahr fuer alle verfuegbaren Jahre (je mehr, desto besser);
die daraus berechneten Einzeljahresraten und die CAGR; Branche der Firma. Ideal
zusaetzlich, aber nicht aus Zahlen ableitbar: der Ausblicksteil des Geschaeftsberichts.

**Rueckfall:** die CAGR-Fortschreibung wie oben beschrieben.

Die langfristige Rate fuer Year +6 bleibt eine feste Annahme (3 %) und wird **nicht**
vom LLM gesetzt -- sie ist eine gesamtwirtschaftliche Groesse, keine Eigenschaft der
Firma [PDF S. 12, Fussnote 7].

## Interpretation: was die Zahlen bedeuten

- **Hohe, stabile Wachstumsrate** (z. B. 10-15 %): Firma in der Wachstumsphase. Die
  Fortschreibung ist plausibel, aber riskant -- kein Unternehmen waechst ewig
  zweistellig.
- **Niedrige Wachstumsrate (2-4 %)**: reifes Unternehmen, Wachstum entspricht etwa
  Inflation plus Bevoelkerungswachstum. Fortschreibung ist hier am sichersten.
- **Stark schwankende Raten**: Warnsignal. Die Fortschreibung ist dann methodisch
  fragwuerdig -- das PDF nennt genau diesen Fall bei zyklischen Firmen [PDF S. 2].
- **Negative Rate**: schrumpfendes Geschaeft. Eine unbesehene Fortschreibung
  prognostiziert das Unternehmen ins Nichts und ist praktisch immer falsch.

**Typischer Fallstrick:** Die CAGR glaettet und verbirgt Schwankungen. Eine Firma mit
den Raten +40 %, -20 %, +30 % hat eine ordentliche CAGR, aber die Fortschreibung ist
wertlos. Die Streuung der Einzeljahresraten sollte deshalb immer mitbetrachtet werden.

## Was in Python zu bauen ist

**Input:** Umsatzreihe (`revenue`) aus `FMP.get_income_statement()`, mindestens
3 Jahre, besser 5.

**Zu implementierende Rechenlogik:**
1. Umsatzreihe aus den Rohdaten extrahieren, chronologisch sortieren
2. Jahres-Wachstumsraten berechnen
3. CAGR ueber den gesamten Zeitraum berechnen
4. Umsatz fuer Year +1 bis +5 mit der CAGR fortschreiben
5. Umsatz fuer Year +6 mit der langfristigen Rate fortschreiben

**Output:** Umsatzprognose fuer 6 Jahre.

**Zusaetzlich, wenn die Wachstumsrate per LLM gesetzt wird** (siehe [LLM-LOESBAR]
oben): Das LLM liefert `wert`, `begruendung` und `konfidenz`; die Fortschreibung selbst
bleibt unveraendert. Bei fehlender oder niedrig-konfidenter Antwort greift die CAGR.

**Vom Nutzer zu entscheiden, bevor Code entsteht:**
- Klasse oder Funktion? Bei Klasse: welche Attribute?
- Wird die Wachstumsrate deterministisch (CAGR) oder per LLM gesetzt -- oder beides
  mit Rueckfall?
- Welche Datenstruktur fuer die Zeitreihen (Liste, dict, DataFrame)?
- Anzahl historischer Jahre als Parameter oder fest?
- Langfristige Wachstumsrate (3 %) als Parameter oder fest?
- Prognosehorizont (5+1 Jahre) als Parameter oder fest?
- Umgang mit fehlenden Jahren in der Zeitreihe

---
---

# Schritt 2: Betriebliche Aufwendungen prognostizieren

> Fundstelle: [PDF S. 12-21, "Step 2: Project Operating Expenses"]

## Die Grundidee

Aufwendungen werden danach unterschieden, ob sie **fix** oder **variabel** sind:

> "The procedure for projecting operating expenses depends on the degree to which they
> have fixed or variable components." [PDF S. 12]

- **Variable Aufwendungen** steigen mit dem Umsatz (Wareneinsatz, Provisionen).
  Prognose ueber Prozent vom Umsatz.
- **Fixe Aufwendungen** bleiben konstant (Miete, Gehaelter, Versicherungen).
  Prognose ueber eigene Treiber.
- **Gemischte Aufwendungen** haben beides (Vertriebs- und Verwaltungsaufwand).

## Rechenschritt 2.1: Fix- und Variablekosten trennen

**[ALLGEMEIN]** Das PDF beschreibt die Trennung so [PDF S. 12]:

```
Variabler Kostensatz = Veraenderung des Aufwands / Veraenderung des Umsatzes
Variable Kosten      = Umsatz x Variabler Kostensatz
Fixe Kosten          = Gesamtaufwand - Variable Kosten
```

Das PDF-Zahlenbeispiel [PDF S. 12]: Umsatz steigt von 10 auf 12 Mio., Wareneinsatz
von 7 auf 8 Mio.

```
Variabler Kostensatz = (8 - 7) / (12 - 10) = 1 / 2 = 50 %
Variable Kosten      = 12 x 0,50 = 6 Mio.
Fixe Kosten          = 8 - 6 = 2 Mio.
```

Interpretation: Von den 8 Mio. Wareneinsatz sind 6 Mio. umsatzabhaengig, 2 Mio. fallen
unabhaengig vom Umsatz an.

**[ALLGEMEIN]** Ein Hinweis auf Fixkosten ist, wenn der Umsatz schneller waechst als
die Kosten [PDF S. 12]. Das ist der Skaleneffekt.

## Rechenschritt 2.2: Common-Size-Prognose

**[ALLGEMEIN]** Die einfachere Standardmethode [PDF S. 12]:

```
Prozentsatz    = Aufwand(historisch) / Umsatz(historisch)
Prognose       = Umsatz(prognostiziert) x Prozentsatz
```

**[ALLGEMEIN]** Das PDF warnt ausdruecklich, dass dieser Prozentsatz nicht konstant
bleiben muss. Vier Faelle [PDF S. 12-13]:

1. **Aufwand aendert sich, Umsatz nicht** -- z. B. Effizienzgewinne senken die Quote,
   oder steigende Einkaufspreise erhoehen sie.
2. **Umsatz aendert sich, Aufwand nicht** -- z. B. Preissenkungen im Wettbewerb
   erhoehen die Quote bei gleichbleibenden Kosten.
3. **Beide aendern sich gleichgerichtet** -- die Quote haengt davon ab, was staerker
   waechst.
4. **Beide aendern sich gegenlaeufig** -- typisch fuer Firmen im Uebergang von der
   Start-up- zur Wachstumsphase (Umsatz hoch, Kosten runter) oder in der Krise.

**Praktische Konsequenz:** Der Trend der Quote ueber mehrere Jahre ist aussagekraeftiger
als ihr letzter Wert. Sinkt die Quote drei Jahre in Folge, ist die Fortschreibung des
letzten Werts zu pessimistisch.

## Die einzelnen Aufwandsarten im PDF

### Wareneinsatz und Mietkosten

**[SBUX-SPEZIFISCH]** Starbucks berichtet "Cost of sales including occupancy costs" --
Wareneinsatz und Miete in einer Zeile. Das PDF trennt beide, weil sie
unterschiedlichen Treibern folgen [PDF S. 13-14, "Projecting Cost of Sales Including
Occupancy Costs"]:

- Wareneinsatz (ohne Miete): sinkende Quote, 36,9 % (2013) -> 34,7 % (2015),
  fortgeschrieben mit 34,0 % in Year +1, weiter sinkend bis 33,2 % in Year +5
- Miete: eigener Treiber -- Miete pro Filiale x durchschnittliche Filialanzahl,
  Miete pro Filiale steigt mit 3 % Inflation

Die Mietformel [PDF S. 14]:

```
Miete pro Filiale (neu) = Miete pro Filiale (alt) x (1 + Inflation)
Mietaufwand             = Miete pro Filiale x Durchschnittliche Filialanzahl
```

**[ABWEICHUNG]** Die Mietangabe stammt aus "Note 10: Leases" des Geschaeftsberichts
[PDF S. 13] und die Filialanzahl aus dem MD&A -- beides ueber die APIs nicht
verfuegbar. Implementiert wird stattdessen die allgemeine Common-Size-Regel
[PDF S. 12] auf den Gesamtposten `costOfRevenue`:

```
Quote      = Wareneinsatz(t) / Umsatz(t)
Prognose   = Umsatz(prognostiziert) x Quote
```

**[LLM-LOESBAR]** Der *getrennte* Mietaufwand bleibt unerreichbar -- er steht in keinem
Abschluss. Die **Hoehe der Quote** ist dagegen ein Urteil: Das PDF haelt sie nicht
konstant, sondern schreibt sie fallend fort (34,0 % -> 33,2 %), weil die historische
Reihe faellt [PDF S. 13]. Genau diese Reihe steht im Abschluss.

- **Aufgabe:** je Prognosejahr eine Wareneinsatzquote setzen -- konstant, oder mit
  einem aus der Historie belegten Trend.
- **Idealer Input:** Wareneinsatz und Umsatz je Jahr fuer alle verfuegbaren Jahre;
  daraus die Quotenreihe. Ideal zusaetzlich: Hinweise des Geschaeftsberichts auf
  Rohstoffpreise oder Preiserhoehungen.
- **Rueckfall:** letzte historische Quote konstant fortschreiben.

### Filialbetriebskosten und sonstige betriebliche Aufwendungen

**[SBUX-SPEZIFISCH]** Filialbetriebskosten werden im PDF nicht am Gesamtumsatz
gemessen, sondern **am Umsatz der firmeneigenen Filialen** -- 36,3 % (2013) auf
35,6 % (2015), fortgeschrieben von 35,0 % auf 34,2 % [PDF S. 14-15, "Projecting Store
Operating Expenses and Other Operating Expenses"].

Sonstige betriebliche Aufwendungen werden am Umsatz aus Lizenz-, CPG- und
Foodservice-Geschaeft gemessen (13,2 %, fortgeschrieben mit 13,0 %) [PDF S. 15].

**[ABWEICHUNG]** Diese Bezugsgroessen setzen die Segmentaufteilung voraus. Ohne sie
wird der Gesamtumsatz als Bezug verwendet -- die allgemeine Regel [PDF S. 12].

**[LLM-LOESBAR]** Die *Bezugsgroesse* bleibt der Gesamtumsatz -- die Segmentaufteilung
ist eine fehlende Zahl. Die **Quote darauf** ist wieder ein Urteil, wie beim
Wareneinsatz: konstant oder mit belegtem Trend.

- **Aufgabe:** Quote je Prognosejahr fuer die uebrigen betrieblichen Aufwandsposten.
- **Idealer Input:** die jeweilige Aufwandszeile und der Umsatz je Jahr ueber alle
  verfuegbaren Jahre.
- **Rueckfall:** letzte historische Quote konstant.

### Sachanlagen und Abschreibungen

Das ist der aufwaendigste Teil von Schritt 2 und zugleich einer der wenigen, die sich
gut umsetzen lassen.

**[ALLGEMEIN]** Das Grundprinzip [PDF S. 15]:

> "you should create a separate schedule to forecast capital expenditures that lead
> projected future sales, and to forecast depreciation expense amounts that lag capital
> expenditures on property, plant, and equipment"

Uebersetzt: Investitionen kommen **vor** dem Umsatz (man baut die Filiale, bevor sie
Umsatz macht), Abschreibungen kommen **nach** der Investition (man schreibt ab, was
man gekauft hat).

**[ALLGEMEIN] Die Nutzungsdauer schaetzen** [PDF S. 16]:

```
Nutzungsdauer = Durchschnittliche Sachanlagen zu Anschaffungskosten
                / Abschreibungsaufwand des Jahres
```

PDF-Beispiel [PDF S. 16]:
```
Nutzungsdauer = ((9.641,8 + 8.581,1) / 2) / 883,8 = 9.111,45 / 883,8 = 10,3 Jahre
```
Das PDF rundet auf 10 Jahre. Die Annahme dahinter: lineare Abschreibung auf einen
Restwert von null [PDF S. 16].

**[ALLGEMEIN] Abschreibungen schichtweise berechnen.** Das ist der zentrale
Rechenschritt. Jede Investition erzeugt eine eigene, dauerhafte
Abschreibungsschicht [PDF S. 16]:

```
Abschreibung auf Altbestand    = Sachanlagen zu Anschaffungskosten / Nutzungsdauer
Abschreibung auf Investition n = Investition(Jahr n) / Nutzungsdauer
                                 (ab Jahr n, jedes Folgejahr erneut)

Gesamtabschreibung(Jahr t) = Abschreibung Altbestand
                             + Summe aller Abschreibungsschichten
                               aus Investitionen der Jahre 1 bis t
```

PDF-Beispiel [PDF S. 16, "Capital Expenditures and Depreciation Expense Forecasts"]:

| Jahr | Altbestand | Invest +1 | Invest +2 | Invest +3 | Invest +4 | Invest +5 | Summe |
|---|---|---|---|---|---|---|---|
| +1 | 964,2 | 140,0 | | | | | 1.104,2 |
| +2 | 964,2 | 140,0 | 150,0 | | | | 1.254,2 |
| +3 | 964,2 | 140,0 | 150,0 | 180,0 | | | 1.434,2 |
| +4 | 964,2 | 140,0 | 150,0 | 180,0 | 210,0 | | 1.644,2 |
| +5 | 231,6 | 140,0 | 150,0 | 180,0 | 210,0 | 240,0 | 1.151,6 |

Zwei Dinge sind hier zu sehen:
- Jede Schicht bleibt in allen Folgejahren bestehen -- die Abschreibungen wachsen
  kumulativ.
- Im Jahr +5 faellt der Altbestand von 964,2 auf 231,6, weil der Restbuchwert
  aufgebraucht ist. **Eine Schicht darf nie mehr abschreiben, als noch an Buchwert
  vorhanden ist.** Im PDF: Restbuchwert 4.088,3 zu Beginn, nach vier Jahren a 964,2
  bleiben 231,6 uebrig [PDF S. 16].

**[ALLGEMEIN] Fortschreibung der Sachanlagen** [PDF S. 17]:

```
Sachanlagen zu AK (Ende)      = Sachanlagen zu AK (Anfang) + Investitionen
Kumulierte Abschr. (Ende)     = Kumulierte Abschr. (Anfang) + Abschreibung des Jahres
Sachanlagen netto             = Sachanlagen zu AK - Kumulierte Abschreibungen
```

**[SBUX-SPEZIFISCH]** Die Investitionsbetraege (1.400 / 1.500 / 1.800 / 2.100 / 2.400
Mio.) stammen aus dem MD&A und einer Einschaetzung des Analysten zum Alter des
Filialbestands [PDF S. 15-16].

**[SBUX-SPEZIFISCH]** Die Aufteilung 95 % / 5 % der Abschreibung (95 % als eigene
Zeile, 5 % im Wareneinsatz) ist eine Starbucks-Ausweisbesonderheit [PDF S. 17].

**[ABWEICHUNG]** Fuer die Investitionen wird eine Fortschreibung als Prozentsatz vom
Umsatz verwendet -- die Common-Size-Regel [PDF S. 12] angewandt auf
`capitalExpenditure`:

```
Investitionsquote = Investitionen(t) / Umsatz(t)
Prognose          = Umsatz(prognostiziert) x Investitionsquote
```

**[LLM-LOESBAR]** Diese Stelle ist die interessanteste in Schritt 2. Das PDF setzt die
Investitionen nicht als feste Quote an, sondern *steigend* (1.400 -> 2.400 Mio.), und
begruendet das mit dem **Alter des Filialbestands** [PDF S. 15-16] -- das klingt nach
MD&A-Wissen, ist aber zu einem grossen Teil aus dem Abschluss ablesbar:

```
Anlagenalter (Indikator) = Kumulierte Abschreibungen / Sachanlagen zu Anschaffungskosten
```

Ein hoher Wert bedeutet: der Bestand ist weitgehend abgeschrieben, Ersatzinvestitionen
stehen an. Diese beiden Groessen stehen in der Bilanz bzw. im Anlagenspiegel.

- **Aufgabe:** Investitionsquote je Prognosejahr setzen -- konstant oder steigend --
  und begruenden.
- **Idealer Input:** Investitionen, Umsatz, Sachanlagen brutto, kumulierte
  Abschreibungen und Abschreibungsaufwand je Jahr ueber alle verfuegbaren Jahre; die
  geschaetzte Nutzungsdauer aus der Formel oben. Ideal zusaetzlich: die
  Investitionsankuendigung aus dem MD&A.
- **Rueckfall:** durchschnittliche historische Investitionsquote, konstant.

Wichtig: Das LLM setzt hier **nur die Quote**. Die schichtweise Abschreibungsrechnung
bleibt vollstaendig deterministisch -- sie ist reine Arithmetik und darf nicht an ein
LLM abgegeben werden.

Die Nutzungsdauer-Schaetzung und die schichtweise Abschreibungsrechnung bleiben
dagegen unveraendert wie im PDF -- die dafuer noetigen Daten (Sachanlagen brutto,
Abschreibungsaufwand) sind verfuegbar.

### Verwaltungsaufwand

**[ALLGEMEIN]** Reine Common-Size-Prognose. Das PDF: Quote schwankte in engem Band
zwischen 6,0 % und 6,3 %, fortgeschrieben mit 6,0 % [PDF S. 17-18, "Projecting General
and Administrative Expenses"]. Diese Regel ist ohne Anpassung uebernehmbar.

### Ergebnis aus Beteiligungen

**[ALLGEMEIN]** Zwei Wege werden genannt [PDF S. 18]:
1. Eine normale Rendite auf den Beteiligungsbuchwert annehmen (einfach)
2. Vollstaendige Abschluesse fuer die Beteiligungen prognostizieren (aufwaendig,
   genauer -- lohnt nur bei sehr grossen Beteiligungen)

Weg 1 als Formel [PDF S. 19]:

```
Durchschnittlicher Buchwert = (Buchwert Anfang + Buchwert Ende) / 2
Beteiligungsergebnis        = Durchschnittlicher Buchwert x Renditeannahme
```

**[SBUX-SPEZIFISCH]** Starbucks' Renditeannahme von 50 % und das Wachstum der
Beteiligungen von 5 % p. a. [PDF S. 19]. 50 % ist ungewoehnlich hoch; das PDF
begruendet es damit, dass Starbucks neben dem anteiligen Gewinn auch Bruttomargen aus
Warenlieferungen und Lizenzgebuehren in dieser Zeile ausweist [PDF S. 18].

### Einmalige Ertraege und Aufwendungen

**[ALLGEMEIN]** Die Regel [PDF S. 19, "Projecting Nonrecurring Income Items"]:

> "you must determine whether items such as these are likely to be persistent in the
> future; if so, include them in the financial statement forecasts."

Fuer Starbucks werden sie auf null gesetzt, weil sie unregelmaessig auftreten
[PDF S. 19]. Diese Annahme (kuenftige Einmaleffekte = 0) ist die allgemein uebliche
und wird uebernommen.

## Rechenschritt 2.3: Betriebsergebnis

**[ALLGEMEIN]** Das Betriebsergebnis ergibt sich als Restgroesse
[PDF S. 21, "Operating Income Projections"]:

```
Betriebsergebnis = Umsatz
                   - Wareneinsatz und Mietkosten
                   - Filialbetriebskosten
                   - Sonstige betriebliche Aufwendungen
                   - Abschreibungen
                   - Verwaltungsaufwand
                   + Beteiligungsergebnis
```

## Interpretation

- **Operative Marge** = Betriebsergebnis / Umsatz. Im PDF steigt sie fuer Starbucks
  von 18,8 % (2015) auf 23,1 % (Year +5) [PDF S. 21].
- **Steigende Marge** bedeutet, dass die Kostenquoten schneller sinken als der Umsatz
  waechst -- der Skaleneffekt aus Rechenschritt 2.1.
- **Warnung:** Steigende Margen in einer Prognose sind eine starke Annahme. Sie
  unterstellen anhaltenden Effizienzgewinn. Wenn die Prognose ueberzeugen soll, muss
  begruendet sein, warum die Kostenquote weiter sinkt. Andernfalls ist die Quote des
  letzten Jahres konstant fortzuschreiben -- die konservative Variante.

## Was in Python zu bauen ist

**Input:**
- `FMP.get_income_statement()` -- `costOfRevenue`, `sellingGeneralAndAdministrativeExpenses`,
  `depreciationAndAmortization`, `operatingExpenses`
- `FMP.get_balance_sheet()` -- `propertyPlantEquipmentNet`
- `FMP.get_cash_flow()` -- `capitalExpenditure`
- `SEC.get_concept("PropertyPlantAndEquipmentGross")` -- Sachanlagen zu Anschaffungs-
  kosten; FMP liefert nur den Nettowert, die Nutzungsdauer-Formel braucht aber brutto

**Zu implementierende Rechenlogik:**
1. Kostenquoten (Aufwand / Umsatz) je historischem Jahr berechnen
2. Aufwandsposten als Umsatz x Quote fortschreiben
3. Nutzungsdauer schaetzen (Formel oben)
4. Investitionen fortschreiben (Quote vom Umsatz)
5. Abschreibungsschichten aufbauen, mit Deckelung auf den Restbuchwert
6. Sachanlagen brutto, kumulierte Abschreibung, Sachanlagen netto fortschreiben
7. Beteiligungsergebnis aus durchschnittlichem Buchwert und Renditeannahme
8. Betriebsergebnis als Differenz

**Output:** Prognostizierte Aufwandsposten, Abschreibungsplan, Sachanlagenplan,
Betriebsergebnis.

**Vom Nutzer zu entscheiden:**
- Welche Aufwandsposten einzeln, welche zusammengefasst?
- Quote des letzten Jahres, Durchschnitt oder Trendfortschreibung?
- Wie wird die Abschreibungsschichten-Tabelle datenstrukturell abgebildet?
- Nutzungsdauer runden (10,3 -> 10) oder exakt?
- Renditeannahme fuer Beteiligungen: fest, Parameter oder aus Historie?
- Fix-/Variabel-Trennung (2.1) ueberhaupt implementieren, oder nur Common-Size?

---
---

# Schritt 3: Betriebliche Vermoegenswerte und Schulden

> Fundstelle: [PDF S. 21-38, "Step 3: Project Operating Assets and Liabilities on the
> Balance Sheet"]

## Die Grundidee

Der prognostizierte Geschaeftsbetrieb erzeugt Bilanzposten. Mehr Umsatz bedeutet mehr
Forderungen, mehr Lagerbestand, mehr Verbindlichkeiten.

**[ALLGEMEIN]** Das PDF unterscheidet den zeitlichen Zusammenhang [PDF S. 21]:

> "For some types of assets, such as inventory and property, plant, and equipment,
> asset growth typically **leads** future sales growth. Growth for other types of
> assets, such as accounts receivable, typically **lags** sales growth."

Uebersetzt:
- **Vorlaufend (leads):** Lager und Sachanlagen muessen *vorher* da sein. Man baut die
  Filiale, bevor sie Umsatz macht.
- **Nachlaufend (lags):** Forderungen entstehen *nachdem* verkauft wurde.

## Die vier Prognosetechniken

**[ALLGEMEIN]** Das PDF nennt vier Techniken [PDF S. 21-22]:

**Technik A -- Wachstumsrate:** Der Posten waechst mit einer Rate (haeufig der
Umsatzwachstumsrate).
```
Prognose = Bestand(Vorjahr) x (1 + Wachstumsrate)
```

**Technik B -- Common-Size vom Umsatz:**
```
Prognose = Umsatz(prognostiziert) x Quote
```

**Technik C -- Prozent der Bilanzsumme:** Fuer Firmen mit stabiler Vermoegensstruktur
[PDF S. 22].
```
Prognose = Bilanzsumme(prognostiziert) x Quote
```

**Technik D -- Umschlagsdauer in Tagen:** Die genaueste Methode fuer Working-Capital-
Posten [PDF S. 22].
```
Prognose = (Bezugsgroesse(prognostiziert) / 365) x Umschlagsdauer in Tagen
```

**[ALLGEMEIN] Wann Technik D nicht verwendet werden darf** [PDF S. 22]:

> "you should not use a turnover-based forecast if the firm will experience
> substantially different future growth rates in revenues and the forecasted account,
> or if the turnover rate varies unpredictably over time."

**[LLM-LOESBAR] Technikwahl und Umschlagsdauer.** Dieses Zitat ist woertlich eine
Urteilsaufgabe: Es verlangt zu pruefen, ob eine Kennzahl "unvorhersehbar schwankt".
Das laesst sich nur beurteilen, wenn man die Reihe ansieht -- und die steht im
Abschluss. Dasselbe gilt fuer die Frage, welche der vier Techniken je Posten passt und
welche Umschlagsdauer angesetzt wird (letztes Jahr, Durchschnitt, gerundet oder exakt
-- das PDF rundet 30,8 auf 30 Tage [PDF S. 23], ohne die Rundung zu begruenden).

- **Aufgabe:** je Bilanzposten die Technik (A-D) und den zugehoerigen Parameter
  (Umschlagsdauer in Tagen, Quote oder Wachstumsrate) setzen.
- **Idealer Input:** der Bilanzposten und seine Bezugsgroesse je Jahr ueber alle
  verfuegbaren Jahre; die daraus berechnete Umschlagsdauer je Jahr; Branche.
- **Rueckfall:** Technik D mit dem Durchschnitt der historischen Umschlagsdauern; wo
  keine sinnvolle Bezugsgroesse existiert, Technik A mit der Umsatzwachstumsrate.

## Das Saegezahn-Problem

**[ALLGEMEIN]** Das PDF beschreibt einen wichtigen Fallstrick [PDF S. 22]. Wenn die
Umschlagsdauer den **Durchschnittsbestand** liefert, muss daraus der **Endbestand**
abgeleitet werden:

```
Endbestand = (Durchschnittsbestand x 2) - Anfangsbestand
```

Das PDF-Beispiel [PDF S. 22]: Umsatz konstant 12.167, Ziel 30 Tage Kasse, also
Durchschnittsbestand 1.000. Anfangsbestand 800.

| Jahr | Durchschnitt | Anfang | Ende |
|---|---|---|---|
| +1 | 1.000 | 800 | 1.200 |
| +2 | 1.000 | 1.200 | 800 |
| +3 | 1.000 | 800 | 1.200 |
| +4 | 1.000 | 1.200 | 800 |

Der Bestand oszilliert dauerhaft, obwohl sich real nichts aendert. Das PDF nennt das
"sawtooth pattern" [PDF S. 22].

**[ALLGEMEIN] Die Loesung** [PDF S. 23]: Endbestand direkt = Durchschnittsbestand
setzen (Glaettung). Das PDF waehlt fuer Starbucks genau diesen Weg -- es rechnet die
Umschlagsdauer direkt auf den Endbestand.

Diese Glaettung wird in der Implementierung uebernommen, weil sie das Problem
vollstaendig vermeidet.

## Die einzelnen Bilanzposten

### Kasse

**[ALLGEMEIN]** Technik D mit Umsatz als Bezugsgroesse [PDF S. 23,
"Projecting Cash and Cash Equivalents"]:

```
Umschlagsdauer = 365 / (Umsatz / Durchschnittlicher Kassenbestand)
Umsatz pro Tag = Umsatz(prognostiziert) / 365
Kasse          = Umsatz pro Tag x Umschlagsdauer
```

PDF-Beispiel [PDF S. 23]:
```
Umschlagsdauer = 365 / (19.162,7 / ((1.530,1 + 1.708,4) / 2)) = 30,8 Tage
```
Gerundet auf 30 Tage. Prognose Year +1 [PDF S. 28]:
```
Umsatz pro Tag = 21.678,3 / 365 = 59,4
Kasse          = 59,4 x 30 = 1.781,8
```

### Forderungen

**[SBUX-SPEZIFISCH]** Das PDF verwendet nicht den Gesamtumsatz als Bezug, sondern nur
den Umsatz aus Lizenz-, CPG- und Foodservice-Geschaeft. Begruendung: In firmeneigenen
Filialen wird bar oder per Karte gezahlt, es entstehen keine Forderungen
[PDF S. 28, "Projecting Accounts Receivable"].

**[ABWEICHUNG]** Ohne Segmentdaten wird der Gesamtumsatz als Bezug verwendet, mit
Technik D -- die allgemeine Regel [PDF S. 22]:

```
Umschlagsdauer = 365 / (Umsatz / Durchschnittliche Forderungen)
Forderungen    = (Umsatz(prognostiziert) / 365) x Umschlagsdauer
```

### Vorraete

**[ALLGEMEIN]** Technik D, Bezugsgroesse ist **nicht** der Umsatz, sondern der
**Wareneinsatz** -- Vorraete werden zu Einstandspreisen bewertet
[PDF S. 29, "Projecting Inventories"]:

```
Umschlagsdauer = 365 / (Wareneinsatz / Durchschnittliche Vorraete)
Wareneinsatz pro Tag = Wareneinsatz(prognostiziert) / 365
Vorraete       = Wareneinsatz pro Tag x Umschlagsdauer
```

PDF-Beispiel Year +1 [PDF S. 29]:
```
Wareneinsatz pro Tag = 8.653,5 / 365 = 23,7
Vorraete             = 23,7 x 56,0 = 1.327,7
```

**[ALLGEMEIN]** Fuer Handelsketten weist das PDF darauf hin, dass Vorraete besser an
die Filialanzahl gekoppelt werden [PDF S. 29]. Das ist ohne Filialdaten nicht
umsetzbar; die Umschlagsdauer bleibt der Weg.

### Aktive Rechnungsabgrenzung

**[SBUX-SPEZIFISCH]** Waechst mit der Anzahl firmeneigener Filialen
[PDF S. 29, "Projecting Prepaid Expenses and Other Current Assets"].

**[ABWEICHUNG]** Ohne Filialdaten: Technik A mit der Umsatzwachstumsrate.

**[LLM-LOESBAR]** Ob dieser Posten eher mit dem Umsatz mitwaechst (Technik A) oder
sich stabiler als Quote verhaelt (Technik B), zeigt die historische Reihe. Aufgabe,
Input und Rueckfall wie im Abschnitt "Technikwahl und Umschlagsdauer" oben.

### Latente Steuern

**[SBUX-SPEZIFISCH]** Das PDF nennt seine eigene Annahme ausdruecklich willkuerlich
[PDF S. 30, "Projecting Current and Noncurrent Deferred Income Tax Assets"]:

> "we will make the (somewhat arbitrary) assumptions that the current deferred tax
> assets will be fully realized in Year +1 and that the noncurrent deferred tax assets
> will decline by 10.0% per year"

**[ALLGEMEIN]** Die allgemeine Aussage dazu: latente Steuern entstehen aus zeitlichen
Differenzen zwischen Steueraufwand und tatsaechlicher Steuerzahlung, sind komplex, und
das PDF verzichtet bewusst auf eine tiefere Behandlung [PDF S. 29-30].

**[ABWEICHUNG]** Empfehlung fuer die Implementierung: konstant halten. Das ist die
neutralste Annahme und vermeidet eine willkuerliche Setzung.

**[LLM-LOESBAR]** Hier gibt das PDF selbst zu, dass seine Annahme "somewhat arbitrary"
ist -- es ist also gar keine Datenfrage, sondern ausdruecklich ein Urteil. Wenn die
historische Reihe der latenten Steuern einen klaren Auf- oder Abbau zeigt, kann das
LLM diesen Trend fortschreiben statt konstant zu halten.

- **Aufgabe:** jaehrliche Veraenderungsrate der latenten Steuern setzen (0 % ist ein
  zulaessiges Ergebnis).
- **Idealer Input:** latente Steueransprueche und -schulden je Jahr ueber alle
  verfuegbaren Jahre. Ideal zusaetzlich: die Steuerangabe im Anhang.
- **Rueckfall:** konstant halten.

### Langfristige Finanzanlagen, Geschaefts- und Firmenwert, immaterielle Vermoegenswerte

**[ALLGEMEIN]** Technik A mit einer festen Wachstumsrate. Das PDF begruendet dies
damit, dass diese Posten hauptsaechlich durch Akquisitionen wachsen und Akquisitionen
ohne konkrete Ankuendigung nicht prognostizierbar sind
[PDF S. 31, "Projecting Other Long-Term Assets, Other Intangible Assets, and Goodwill"]:

> "Absent announcements or disclosures about pending acquisitions, these types of
> transactions are inherently hard to forecast."

**[SBUX-SPEZIFISCH]** Die konkreten Raten (3 % fuer Finanzanlagen, 5 % fuer Goodwill
und immaterielle Vermoegenswerte) [PDF S. 30-31].

**[ALLGEMEIN]** Ebenfalls die Annahme: keine kuenftigen Wertminderungen
[PDF S. 31].

**[LLM-LOESBAR]** Die konkreten Raten (3 % / 5 %) sind bei Starbucks gesetzt, nicht
berechnet. Aus der Historie dieser Posten laesst sich aber ablesen, ob die Firma
regelmaessig zukauft (Goodwill waechst stetig), einmalig zugekauft hat (ein Sprung in
einem Jahr) oder gar nicht akquiriert (Goodwill konstant). Nur der erste Fall
rechtfertigt eine positive Wachstumsrate.

- **Aufgabe:** Wachstumsrate je Posten (Goodwill, immaterielle Vermoegenswerte,
  langfristige Finanzanlagen) setzen.
- **Idealer Input:** die drei Posten je Jahr ueber alle verfuegbaren Jahre.
- **Rueckfall:** konstant halten (0 % Wachstum) -- das entspricht der PDF-Annahme
  "keine unangekuendigten Akquisitionen" am striktesten.

Die Annahme "keine kuenftigen Wertminderungen" bleibt fest und wird **nicht** vom LLM
gesetzt -- eine prognostizierte Wertminderung waere reine Spekulation.

### Verbindlichkeiten aus Lieferungen und Leistungen

**[ALLGEMEIN]** Technik D, aber die Bezugsgroesse ist **nicht** der Wareneinsatz,
sondern der **Wareneinkauf**. Das ist der subtilste Rechenschritt in Schritt 3
[PDF S. 33-34, "Projecting Accounts Payable"]:

```
Wareneinkauf   = Wareneinsatz + (Vorraete Ende - Vorraete Anfang)
Einkauf pro Tag = Wareneinkauf / 365
Verbindlichkeiten = Einkauf pro Tag x Umschlagsdauer
```

Der Grund fuer die Bestandsveraenderung: Wer sein Lager aufbaut, kauft mehr ein, als er
verkauft. Nur der Einkauf erzeugt Verbindlichkeiten, nicht der Verkauf.

PDF-Beispiel Year +1 [PDF S. 33-34]:
```
Wareneinkauf      = 8.653,5 + (1.327,7 - 1.306,4) = 8.653,5 + 21,3 = 8.674,8
Einkauf pro Tag   = 8.674,8 / 365 = 23,8
Verbindlichkeiten = 23,8 x 28,0 = 665,5
```

**Reihenfolgehinweis:** Die Vorraeteprognose muss vor der
Verbindlichkeitenprognose stehen, weil deren Veraenderung in die Formel eingeht.

### Sonstige Rueckstellungen und Verbindlichkeiten

**[ALLGEMEIN]** Technik A mit der Umsatzwachstumsrate. Begruendung: diese Posten sind
historisch etwa mit dem Umsatz gewachsen [PDF S. 34, "Projecting Accrued Liabilities"].

**[SBUX-SPEZIFISCH]** Zwei Posten existieren so nur bei Starbucks:
- **Insurance reserves** (Selbstversicherung), 3 % Wachstum [PDF S. 34]
- **Stored-value card liabilities** (Guthaben auf Kundenkarten), waechst mit Umsatz
  [PDF S. 34-35]

Die allgemeine Regel dahinter -- betriebliche Verbindlichkeiten wachsen mit dem
Umsatz -- ist uebertragbar und wird auf `otherCurrentLiabilities` angewandt.

## Interpretation

- **Steigende Forderungslaufzeit:** Kunden zahlen langsamer. Warnsignal fuer
  Zahlungsprobleme oder aggressive Umsatzrealisierung.
- **Steigende Lagerdauer:** Ware bleibt laenger liegen. Warnsignal fuer sinkende
  Nachfrage oder Fehldisposition.
- **Steigende Zahlungsziele bei Lieferanten:** Zunaechst positiv (kostenlose
  Finanzierung), bei starkem Anstieg aber Warnsignal fuer Liquiditaetsprobleme.
- **Der Working-Capital-Effekt beim Wachstum:** Waechst eine Firma, muessen Lager und
  Forderungen mitwachsen -- das bindet Kapital. Genau deshalb erhoeht Wachstum den
  Finanzierungsbedarf, und genau das faengt Schritt 6 auf.

## Was in Python zu bauen ist

**Input:**
- `FMP.get_balance_sheet()` -- `cashAndCashEquivalents`, `netReceivables`,
  `inventory`, `accountPayables`, `otherCurrentAssets`, `otherCurrentLiabilities`,
  `goodwill`, `intangibleAssets`, `longTermInvestments`, `otherNonCurrentAssets`,
  `otherNonCurrentLiabilities`
- Umsatzprognose aus Schritt 1
- Wareneinsatzprognose aus Schritt 2

**Zu implementierende Rechenlogik:**
1. Umschlagsdauern aus der Historie berechnen (Kasse, Forderungen, Vorraete,
   Verbindlichkeiten)
2. Kasse, Forderungen, Vorraete ueber Umschlagsdauer prognostizieren
3. Wareneinkauf berechnen (Wareneinsatz + Vorratsveraenderung)
4. Verbindlichkeiten ueber Umschlagsdauer auf den Wareneinkauf
5. Uebrige Posten mit Wachstumsrate fortschreiben
6. Vermoegenswerte und Schulden summieren

**Output:** Prognostizierte betriebliche Bilanzposten.

**Vom Nutzer zu entscheiden:**
- 365 oder 360 Tage?
- Umschlagsdauer aus letztem Jahr oder Durchschnitt mehrerer Jahre?
- Runden wie im PDF (30,8 -> 30) oder exakt?
- Latente Steuern: konstant, Trend, oder ganz weglassen?
- Wachstumsraten fuer Goodwill etc.: fest, Parameter oder aus Historie?
- Welche Bilanzposten werden ueberhaupt einzeln modelliert?

---
---

# Schritt 4: Finanzierung, Finanzanlagen, Eigenkapital, Zinsen

> Fundstelle: [PDF S. 35-42, "Step 4: Project Financial Leverage, Financial Assets,
> Common Equity Capital, and Financial Income and Expense Items"]

## Die Grundidee

Schritt 3 hat bestimmt, **was** die Firma braucht. Schritt 4 bestimmt, **womit** sie
es bezahlt -- Fremdkapital oder Eigenkapital -- und was diese Finanzierung kostet.

**[ALLGEMEIN]** Zwei Wege werden genannt [PDF S. 35]:

1. **Common-Size der Passivseite:** Wenn die Firma eine stabile Kapitalstruktur hat
   (z. B. dauerhaft 60 % Schulden / 40 % Eigenkapital), werden diese Prozentsaetze auf
   die prognostizierte Bilanzsumme angewandt.
2. **Explizite Modellierung der Finanzstrategie:** Faelligkeiten, Neuemissionen,
   Rueckkaeufe einzeln fortschreiben.

## Rechenschritt 4.1: Finanzanlagen

**[ALLGEMEIN]** Zuerst ist zu klaeren, wozu die Firma Finanzanlagen haelt
[PDF S. 36]:

> "manage seasonal swings in operating liquidity / provide a financial cushion for
> future uncertainties / have financial flexibility to take advantage of profitable
> opportunities"

Die Unterscheidung ist wichtig:
- **Betriebsnotwendige Liquiditaet** -> gehoert zu Schritt 3 (betrieblich)
- **Ueberschussliquiditaet** (z. B. Tilgungsfonds fuer Anleihen) -> gehoert zu
  Schritt 4 (finanziell)

Fuer Starbucks entscheidet das PDF, alle Finanzanlagen als betrieblich zu behandeln
[PDF S. 36].

## Rechenschritt 4.2: Fremdkapital

**[ALLGEMEIN]** Das Grundprinzip der Fortschreibung [PDF S. 37]:

```
Endbestand = Anfangsbestand + Neuemissionen - Faelligkeiten
```

Faellige Betraege wandern im Jahr vor der Faelligkeit von "langfristig" nach
"kurzfristig" [PDF S. 37]:

```
Kurzfr. Faelligkeiten (Ende) = Kurzfr. Faelligkeiten (Anfang)
                               + faellig werdende langfr. Schulden
                               - getilgte Betraege
```

**[SBUX-SPEZIFISCH]** Die konkreten Faelligkeiten (400 Mio. in Year +2, 350 Mio. in
Year +4) und die Neuemission von 1.000 Mio. in Year +1 stammen aus "Note 9: Debt" des
Geschaeftsberichts und aus Beobachtungen waehrend der Kapitelentstehung [PDF S. 36-37].

**[ABWEICHUNG]** Faelligkeitsprofile stehen nur im Anhang und sind ueber FMP/SEC nicht
strukturiert abrufbar. Umgesetzt wird die allgemeine Alternative des PDFs -- Technik C
aus Schritt 3, angewandt auf die Passivseite [PDF S. 35]:

```
Fremdkapitalquote = Fremdkapital(t) / Bilanzsumme(t)
Prognose          = Bilanzsumme(prognostiziert) x Fremdkapitalquote
```

**[LLM-LOESBAR]** Das *Faelligkeitsprofil* bleibt unerreichbar -- fehlende Zahl. Die
**Zielverschuldungsquote** ist dagegen ablesbar: Steigt die Quote historisch, baut die
Firma Verschuldung auf; ist sie stabil, verfolgt sie offenbar eine Zielstruktur.

- **Aufgabe:** Fremdkapitalquote je Prognosejahr setzen.
- **Idealer Input:** kurz- und langfristiges Fremdkapital, Bilanzsumme und
  Eigenkapital je Jahr ueber alle verfuegbaren Jahre; die daraus berechnete
  Quotenreihe. Ideal zusaetzlich: die Faelligkeitstabelle aus dem Anhang.
- **Rueckfall:** letzte historische Quote konstant.

**[LLM-LOESBAR] Zusatzpruefung.** Das LLM sollte melden, wenn die Fortschreibung zu
einer unplausiblen Kapitalstruktur fuehrt (z. B. negatives Eigenkapital oder eine
Verschuldung, die den Zinsaufwand ueber das Betriebsergebnis treibt). Das ist genau
die Plausibilitaetskontrolle, die im PDF der Analyst leistet.

## Rechenschritt 4.3: Zinsaufwand

**[ALLGEMEIN]** Der Zinsaufwand wird ueber einen gewichteten Durchschnittszinssatz
auf den durchschnittlichen Schuldenstand berechnet [PDF S. 38-39,
"Projecting Interest Expense"]:

```
Gewichteter Zinssatz = Summe ueber alle Emissionen von
                       (Nominalbetrag / Gesamtnominal) x Zinssatz

Durchschn. Schulden  = (Schulden Anfang + Schulden Ende) / 2
Zinsaufwand          = Durchschn. Schulden x Gewichteter Zinssatz
```

PDF-Beispiel [PDF S. 39]: Aus sieben Anleihen ergibt sich ein gewichteter Zinssatz
von 2,7067 %. Year +1:
```
Durchschn. Schulden = (2.347,5 + 3.347,5) / 2 = 2.847,5
Zinsaufwand         = 2.847,5 x 0,027067 = 77,1
```

**[ABWEICHUNG]** Die einzelnen Anleihen mit Nominalbetraegen und Kupons stehen in
"Note 9: Debt" [PDF S. 38] und sind ueber die APIs nicht verfuegbar. Der effektive
Zinssatz laesst sich stattdessen direkt aus der Historie ableiten:

```
Effektiver Zinssatz = Zinsaufwand(t) / Durchschn. Schulden(t)
Zinsaufwand         = Durchschn. Schulden(prognostiziert) x Effektiver Zinssatz
```

Das ist rechnerisch aequivalent, nur die Herleitung des Zinssatzes unterscheidet sich:
das PDF leitet ihn aus den Vertragsdaten ab, die Implementierung aus dem
tatsaechlich gezahlten Zins.

**[LLM-LOESBAR]** Offen bleibt, *welcher* effektive Zinssatz genommen wird: der des
letzten Jahres oder ein Mehrjahresdurchschnitt. Bei einer Firma, die im letzten Jahr
eine grosse Anleihe zu abweichendem Kupon begeben hat, ist der letzte Wert
irrefuehrend -- erkennbar an einem Sprung in der Reihe.

- **Aufgabe:** effektiven Zinssatz fuer die Prognosejahre setzen.
- **Idealer Input:** Zinsaufwand und Schuldenstand je Jahr ueber alle verfuegbaren
  Jahre; die daraus berechnete Zinssatzreihe. Ideal zusaetzlich: das aktuelle
  Marktzinsniveau und die Anleihetabelle aus dem Anhang.
- **Rueckfall:** Durchschnitt der historischen effektiven Zinssaetze.

Dasselbe gilt spiegelbildlich fuer die Verzinsung der Finanzanlagen in
Rechenschritt 4.4.

## Rechenschritt 4.4: Zinsertrag

**[ALLGEMEIN]** Spiegelbildlich [PDF S. 40, "Projecting Interest Income"]:

```
Verzinsliche Anlagen  = Kasse + kurzfr. Finanzanlagen + langfr. Finanzanlagen
Durchschnitt          = (Anfang + Ende) / 2
Zinsertrag            = Durchschnitt x Renditeannahme
```

PDF-Beispiel [PDF S. 40]:
```
Rendite     = 43,0 / 2.043,0 = 2,1 %
Zinsertrag(+1) = 2.055,65 x 0,021 = 43,2
```

**[SBUX-SPEZIFISCH]** Die 2,1 % Rendite spiegeln das Niedrigzinsumfeld 2015
[PDF S. 40]. Die Ableitung aus der Historie (Zinsertrag / durchschnittliche Anlagen)
ist die allgemeine Regel und wird uebernommen.

## Rechenschritt 4.5: Eigenkapitalposten

**[ALLGEMEIN]** Gezeichnetes Kapital und Kapitalruecklage aendern sich durch
Aktienausgaben, Aktienrueckkaeufe und aktienbasierte Verguetung [PDF S. 41].

**[SBUX-SPEZIFISCH]** Starbucks wird mit Technik C fortgeschrieben: konstant 0,342 %
der Bilanzsumme [PDF S. 41]. Die Begruendung -- keine wesentlichen Neuemissionen
erwartet -- ist allgemein uebertragbar.

**[ALLGEMEIN] Kumuliertes sonstiges Ergebnis (OCI):** Auf null setzen. Die Begruendung
ist ausdruecklich allgemein formuliert [PDF S. 42, "Projecting Accumulated Other
Comprehensive Income or Loss"]:

> "analysts commonly forecast gains or losses from other comprehensive income items to
> be zero, on average."

Der Gedanke: OCI besteht aus Waehrungsumrechnung, Marktwertaenderungen und
Pensionsanpassungen. Diese sind ebenso wahrscheinlich positiv wie negativ und mitteln
sich langfristig heraus.

**[ALLGEMEIN] Minderheitsanteile:** Sollten ueber die anteiligen Gewinne und
Dividenden fortgeschrieben werden [PDF S. 41]. Bei Starbucks werden sie
vereinfachend auf null gesetzt, weil sie nur 0,03 % des Eigenkapitals ausmachen
[PDF S. 41] -- eine Wesentlichkeitsentscheidung, die uebertragbar ist.

## Interpretation

- **Verschuldungsgrad** = Fremdkapital / Bilanzsumme. Im PDF steigt er fuer Starbucks
  von 53,2 % auf ca. 64 % [PDF S. 38].
- **Steigender Verschuldungsgrad** erhoeht die Eigenkapitalrendite, solange die
  Geschaeftsrendite ueber dem Zinssatz liegt -- und erhoeht zugleich das Risiko.
- **Zinsdeckungsgrad** = Betriebsergebnis / Zinsaufwand. Werte unter 3 gelten als
  kritisch. Fuer Starbucks Year +1: 4.267,7 / 77,1 = 55 -- sehr komfortabel.
- **Wichtig fuer Schritt 6:** Die hier prognostizierten Zinsen sind eine *erste
  Iteration*. Aendert Schritt 6 die Schulden, muessen die Zinsen neu gerechnet werden
  [PDF S. 39].

## Was in Python zu bauen ist

**Input:**
- `FMP.get_balance_sheet()` -- `totalDebt`, `shortTermDebt`, `longTermDebt`,
  `commonStock`, `totalStockholdersEquity`, `minorityInterest`
- `FMP.get_income_statement()` -- `interestExpense`, `interestIncome`
- Bilanzsummenprognose aus Schritt 3

**Zu implementierende Rechenlogik:**
1. Historische Fremdkapitalquote berechnen
2. Fremdkapital ueber die Quote fortschreiben
3. Effektiven Zinssatz aus der Historie ableiten
4. Zinsaufwand auf den Durchschnittsschuldenstand berechnen
5. Rendite auf Finanzanlagen aus der Historie ableiten
6. Zinsertrag auf die durchschnittlichen Finanzanlagen berechnen
7. Eigenkapitalposten als Prozent der Bilanzsumme fortschreiben
8. OCI konstant halten

**Output:** Prognostiziertes Fremdkapital, Zinsaufwand, Zinsertrag,
Eigenkapitalposten.

**Vom Nutzer zu entscheiden:**
- Fremdkapital gesamt oder kurz-/langfristig getrennt?
- Zinssatz aus letztem Jahr oder Mehrjahresdurchschnitt?
- Durchschnittlicher oder Endbestand als Zinsbasis?
- Minderheitsanteile modellieren oder als unwesentlich weglassen?
- Wie wird die Iteration mit Schritt 6 organisiert?

---
---

# Schritt 5: Steuern, Nettogewinn, Dividenden, Rueckkaeufe, Gewinnruecklagen

> Fundstelle: [PDF S. 42-46, "Step 5: Project Provisions for Taxes, Net Income,
> Dividends, Share Repurchases, and Retained Earnings"]

## Rechenschritt 5.1: Vorsteuerergebnis

```
Vorsteuerergebnis = Betriebsergebnis (Schritt 2)
                    + Zinsertrag (Schritt 4)
                    - Zinsaufwand (Schritt 4)
                    +/- Einmaleffekte (in der Regel 0)
```

## Rechenschritt 5.2: Steueraufwand

**[ALLGEMEIN]** Kern der Ueberlegung ist die Unterscheidung zweier Steuersaetze
[PDF S. 43, "Projecting Provisions for Income Taxes"]:

- **Gesetzlicher Steuersatz (statutory rate):** was das Gesetz vorschreibt
- **Effektiver Steuersatz (effective rate):** was die Firma tatsaechlich zahlt

Der effektive Satz weicht ab durch auslaendische Steuersaetze, Steuervorteile,
Abzugsmoeglichkeiten. Fuer Starbucks: gesetzlich 35,0 %, effektiv 29,3 % (2015) und
34,6 % (2014) [PDF S. 43].

```
Effektiver Steuersatz = Steueraufwand(t) / Vorsteuerergebnis(t)
Steueraufwand         = Vorsteuerergebnis(prognostiziert) x Effektiver Steuersatz
```

**[SBUX-SPEZIFISCH]** Der Satz von 34,0 % stammt aus dem MD&A -- Starbucks hatte ihn
selbst angekuendigt [PDF S. 43].

**[ABWEICHUNG]** Ohne MD&A wird der effektive Steuersatz aus der Historie abgeleitet
(Formel oben). Weil er stark schwanken kann -- bei Starbucks 29,3 % vs. 34,6 % in zwei
aufeinanderfolgenden Jahren -- ist ein Mehrjahresdurchschnitt stabiler als der letzte
Wert.

**[LLM-LOESBAR]** Der Durchschnitt ist nur die sichere Notloesung. Die eigentliche
Frage -- ist 29,3 % ein einmaliger Sondereffekt oder das neue Niveau? -- ist ein
Urteil ueber die Zeitreihe, und die Zeitreihe steht im Abschluss. Genau dieses Urteil
faellt der Analyst im PDF, wenn er 34,0 % ansetzt: Er verwirft den letzten Wert
bewusst.

- **Aufgabe:** effektiven Steuersatz fuer die Prognosejahre setzen; ein einzelner
  Ausreisser darf ausgeschlossen werden, wenn das begruendet wird.
- **Idealer Input:** Steueraufwand und Vorsteuerergebnis je Jahr ueber alle
  verfuegbaren Jahre; die daraus berechnete Steuersatzreihe; der gesetzliche
  Steuersatz des Sitzlandes als Obergrenzen-Anhalt. Ideal zusaetzlich: die
  Ueberleitungsrechnung gesetzlich -> effektiv aus dem Anhang, die genau erklaert,
  woher die Abweichung kommt.
- **Rueckfall:** Mehrjahresdurchschnitt des effektiven Steuersatzes.

## Rechenschritt 5.3: Nettogewinn

```
Nettogewinn = Vorsteuerergebnis - Steueraufwand
Nettogewinn den Aktionaeren zurechenbar
            = Nettogewinn - Anteil der Minderheitsgesellschafter
```

## Rechenschritt 5.4: Dividenden

**[ALLGEMEIN]** Ueber die Ausschuettungsquote [PDF S. 45,
"Projecting Dividends and Share Repurchases"]:

```
Ausschuettungsquote = Dividenden(t) / Nettogewinn(t)
Dividenden          = Nettogewinn(prognostiziert) x Ausschuettungsquote
```

**[SBUX-SPEZIFISCH]** Die 42,5 % ergeben sich aus einer angekuendigten Dividende von
0,80 USD je Aktie bei rund 1.485 Mio. Aktien [PDF S. 44]:
```
Dividendensumme = 0,80 x 1.485 = 1.188,0
Quote           = 1.188,0 / 2.794,3 = 42,5 %
```

## Rechenschritt 5.5: Aktienrueckkaeufe

**[SBUX-SPEZIFISCH]** Die Annahme von 1.500 Mio. pro Jahr beruht auf der
Rueckkaufhistorie und einer Programmankuendigung [PDF S. 44-45].

**[LLM-LOESBAR] Ausschuettungspolitik (gilt fuer 5.4 und 5.5).** Die
Programmankuendigung ist eine fehlende Zahl -- die **Rueckkaufhistorie** dagegen steht
in der Kapitalflussrechnung, ebenso die gezahlten Dividenden. Aus beidem laesst sich
das Ausschuettungsverhalten der Firma ablesen: zahlt sie ueberhaupt Dividende, ist die
Quote stabil oder steigend, kauft sie regelmaessig oder nur gelegentlich zurueck.

- **Aufgabe:** Ausschuettungsquote und jaehrlichen Rueckkaufbetrag setzen.
- **Idealer Input:** Nettogewinn, gezahlte Dividenden und Aktienrueckkaeufe je Jahr
  ueber alle verfuegbaren Jahre; Aktienanzahl je Jahr. Ideal zusaetzlich: die
  angekuendigte Dividende je Aktie und das laufende Rueckkaufprogramm.
- **Rueckfall:** durchschnittliche historische Ausschuettungsquote; Rueckkaeufe in
  Hoehe des historischen Durchschnitts.

Wenn in Schritt 6 die Rueckkaeufe als Ausgleichsposten dienen, ist dieser Betrag nur
der **Startwert**, der dort angepasst wird -- genau wie im PDF-Zitat unten.

**[ALLGEMEIN] Zwei buchhalterische Behandlungen** [PDF S. 44]:
- Ueber ein **Treasury-Stock-Konto** (negativer Eigenkapitalposten) -- der Normalfall
- **Direkt von den Gewinnruecklagen abgezogen** -- bei Starbucks, weil das Recht des
  Bundesstaats Washington das vorschreibt

**Wichtig fuer Schritt 6:** Das PDF kuendigt hier bereits an, dass die
Rueckkaufannahme spaeter angepasst wird [PDF S. 44]:

> "We may need to reduce the projected amount of share repurchases in particular years
> if we determine later in our analysis that Starbucks will not have sufficient cash
> flow for these repurchases"

## Rechenschritt 5.6: Gewinnruecklagen

**[ALLGEMEIN]** Die Fortschreibungsformel [PDF S. 45, "Retained Earnings"]:

```
Gewinnruecklagen (Ende) = Gewinnruecklagen (Anfang)
                          + Nettogewinn
                          - Dividenden
                          - Aktienrueckkaeufe   [nur wenn direkt abgezogen]
```

Dies ist die **Verbindung zwischen GuV und Bilanz**. Ohne sie waeren die beiden
Abschluesse nicht verknuepft.

## Interpretation

- **Effektiver Steuersatz deutlich unter dem gesetzlichen:** Die Firma nutzt
  Steuervorteile. Nachhaltig oder einmalig? Bei Starbucks war der niedrige Satz 2015
  teils auf einen einmaligen Effekt aus der Japan-Akquisition zurueckzufuehren
  [PDF S. 43] -- eine Fortschreibung waere zu optimistisch gewesen.
- **Nettomarge** = Nettogewinn / Umsatz. Fuer Starbucks 14,4 % (2015), im PDF
  zunaechst auf 12,9 % fallend (hoehere Steuerquote), dann auf 15,2 % steigend
  [PDF S. 43].
- **Ausschuettungsquote:** Junge Wachstumsfirmen bei 0 %, reife Firmen bei 40-60 %.
  Ueber 100 % bedeutet Substanzausschuettung -- nicht dauerhaft tragfaehig.
- **Rueckkaeufe plus Dividenden ueber 100 % des Gewinns:** Die Firma gibt mehr aus, als
  sie verdient. Bei Starbucks im PDF: 42,5 % Dividende plus rund 50 % Rueckkaeufe. Das
  geht nur bei starkem Cashflow oder wachsender Verschuldung.

## Was in Python zu bauen ist

**Input:**
- `FMP.get_income_statement()` -- `incomeTaxExpense`, `incomeBeforeTax`, `netIncome`
- `FMP.get_cash_flow()` -- `dividendsPaid`, `commonStockRepurchased`
- Ergebnisse aus Schritt 2 und 4

**Zu implementierende Rechenlogik:**
1. Vorsteuerergebnis zusammensetzen
2. Effektiven Steuersatz aus der Historie ableiten
3. Steueraufwand und Nettogewinn berechnen
4. Ausschuettungsquote ableiten, Dividenden berechnen
5. Aktienrueckkaeufe fortschreiben
6. Gewinnruecklagen fortschreiben

**Output:** Steueraufwand, Nettogewinn, Dividenden, Rueckkaeufe, Gewinnruecklagen.

**Vom Nutzer zu entscheiden:**
- Steuersatz aus letztem Jahr oder Durchschnitt? Ueber wie viele Jahre?
- Ausschuettungsquote analog?
- Rueckkaeufe: konstanter Betrag, Prozent vom Gewinn, oder aus Historie?
- Rueckkaeufe von Gewinnruecklagen abziehen oder Treasury-Stock-Konto fuehren?
- Wie wird die Anpassung durch Schritt 6 zurueckgespielt?

---
---

# Schritt 6: Die Bilanz zum Ausgleich bringen

> Fundstelle: [PDF S. 46-49, "Step 6: Balance the Balance Sheet"]

## Das Problem

Nach den Schritten 1-5 sind alle Posten prognostiziert -- **aber die Bilanz geht nicht
auf.** Das PDF:

> "Even though the first-pass forecasts of all amounts on the income statement and
> balance sheet are complete, the balance sheet does not balance because we have
> projected individual asset and liability accounts to capture their underlying
> business activities, which are not perfectly correlated." [PDF S. 46]

Jeder Posten wurde nach seinem eigenen Treiber prognostiziert. Dass die Summen dann
zufaellig uebereinstimmen, waere ein Wunder.

## Die Loesung: der Ausgleichsposten

**[ALLGEMEIN]** Ein Bilanzposten wird zum "flexiblen" Posten erklaert und uebernimmt
die Differenz [PDF S. 46]:

```
Differenz = Bilanzsumme (Aktiva)
            - Schulden (Passiva)
            - Eigenkapital (Passiva)
```

**Die Vorzeicheninterpretation** [PDF S. 46]:

| Vorzeichen | Bedeutung | Handlungsoptionen |
|---|---|---|
| **positiv** (Aktiva > Passiva) | Finanzierungsluecke | Schulden aufnehmen, Eigenkapital ausgeben, oder Investitionen kuerzen |
| **negativ** (Passiva > Aktiva) | Ueberschuss | Schulden tilgen, Dividenden erhoehen, Aktien zurueckkaufen, oder Finanzanlagen aufbauen |

**[ALLGEMEIN] Die vier moeglichen Ausgleichsposten** [PDF S. 47]:

1. Kurz- oder langfristige Finanzanlagen erhoehen
2. Kurz- oder langfristige Schulden reduzieren
3. Gewinnruecklagen reduzieren durch hoehere Dividenden
4. Gewinnruecklagen reduzieren durch hoehere Aktienrueckkaeufe

**[ALLGEMEIN] Wie waehlt man den richtigen?** [PDF S. 46]:

> "For some firms (for example, start-ups), financial flexibility may be in cash or
> marketable securities... For profitable growth firms that do not have large reserves
> of excess cash or marketable securities, financial flexibility may be exercised
> through short-term or long-term debt or equity."

Als Faustregel aus dem Text:
- **Start-ups und Firmen mit Liquiditaetspuffer:** Kasse/Wertpapiere
- **Wachsende Firmen ohne Puffer:** Fremdkapital
- **Reife, cash-starke Firmen:** Dividenden/Rueckkaeufe

**[SBUX-SPEZIFISCH]** Das PDF waehlt fuer Starbucks die Aktienrueckkaeufe, weil
Starbucks nachweislich bereit und faehig ist, Kapital an Aktionaere auszuschuetten
[PDF S. 47].

**[ABWEICHUNG]** Empfehlung fuer die Implementierung: das **Fremdkapital** als
Ausgleichsposten. Zwei Gruende: Es ist die vom PDF genannte Option fuer wachsende
Firmen [PDF S. 46], und es funktioniert in beide Richtungen (Aufnahme *und* Tilgung),
waehrend Rueckkaeufe bei einer Finanzierungsluecke nicht negativ werden koennen.

**[LLM-LOESBAR]** Dies ist die deutlichste LLM-Stelle des ganzen Verfahrens. Das PDF
formuliert die Wahl ausdruecklich als **Einordnung der Firma** -- Start-up,
wachsende Firma, reife cash-starke Firma -- und liefert die Faustregel gleich mit
(siehe Tabelle oben). Eine solche Einordnung ist genau das, was sich aus einem
Jahresabschluss lesen laesst: Liquiditaetspolster, Verschuldungsgrad, Umsatzwachstum,
Profitabilitaet, Ausschuettungshistorie.

Der obige Vorschlag "immer Fremdkapital" waere die Faustregel fuer *eine* der drei
Kategorien, angewandt auf alle Firmen.

- **Aufgabe:** einen der vier Ausgleichsposten waehlen und die Wahl mit der
  Einordnung der Firma begruenden.
- **Idealer Input:** Kasse und kurzfristige Finanzanlagen, Fremd- und Eigenkapital,
  Umsatzwachstum, Nettomarge, operativer Cashflow, Dividenden und Rueckkaeufe -- je
  Jahr ueber alle verfuegbaren Jahre.
- **Rueckfall:** Fremdkapital, aus den zwei oben genannten Gruenden.

**Grenze:** Das LLM waehlt nur den *Posten*. Die Ausgleichsrechnung selbst -- Differenz
bilden, Veraenderung anpassen, auf null bringen -- bleibt vollstaendig deterministisch
und wird nie an ein LLM abgegeben. Ebenso muss die Wahl fuer alle Prognosejahre
dieselbe bleiben, sonst laesst sich die Veraenderungslogik unten nicht anwenden.

## Der Rechenschritt

**[ALLGEMEIN]** Wichtig ist, dass nicht die Differenz selbst, sondern ihre
**Veraenderung** angepasst wird [PDF S. 46]:

> "The change in the difference represents the increment by which we must adjust the
> flexible financial account each year."

PDF-Beispiel [PDF S. 46-47]:

| | Year +1 | Year +2 | Year +3 | Year +4 | Year +5 |
|---|---|---|---|---|---|
| Differenz | (1.153,7) | (1.137,2) | (1.235,4) | (1.493,0) | (1.503,0) |
| Veraenderung | (1.153,7) | 16,5 | (98,2) | (257,6) | (9,9) |
| Rueckkauf urspruenglich | 1.500,0 | 1.500,0 | 1.500,0 | 1.500,0 | 1.500,0 |
| Anpassung | 1.153,7 | (16,5) | 98,2 | 257,6 | 9,9 |
| **Rueckkauf angepasst** | **2.653,7** | **1.483,5** | **1.598,2** | **1.757,6** | **1.509,9** |

Der Grund fuer die Veraenderungslogik: Eine Anpassung in Year +1 wirkt ueber die
Gewinnruecklagen auch in allen Folgejahren fort. Wuerde man in Year +2 erneut die
volle Differenz anpassen, korrigierte man doppelt.

Nach der Anpassung gilt in jedem Jahr [PDF S. 48]:
```
Differenz = 0,0
```

## Die Zirkularitaet

**[ALLGEMEIN]** Das PDF widmet dem einen eigenen Abschnitt [PDF S. 48,
"Closing the Loop: Solving for Codetermined Variables"]:

> "If we had added the excess capital to interest-earning asset accounts... or
> subtracted it from interest-bearing short-term or long-term debt, the projected
> amounts for interest income or interest expense would have to be adjusted on the
> income statement."

Die Kette:
```
Schulden -> Zinsaufwand -> Nettogewinn -> Gewinnruecklagen -> Bilanzsumme -> Schulden
```

**[ALLGEMEIN] Die Loesung** [PDF S. 48]: iteratives Rechnen. Excel loest das ueber
"Enable iterative calculation" mit bis zu 1.000 Iterationen. In Python entspricht das
einer Schleife:

```
Wiederhole:
    Berechne Schritte 4 bis 6 neu
    Bis: Differenz < Toleranz  ODER  maximale Iterationen erreicht
```

**Hinweis:** Diese Zirkularitaet entsteht nur, wenn der Ausgleichsposten
zinstragend ist -- also bei Fremdkapital oder Finanzanlagen. Waehlt man
Aktienrueckkaeufe wie das PDF, entfaellt sie. Das ist ein Argument fuer die
PDF-Variante und gegen die oben empfohlene; die Entscheidung liegt beim Nutzer.

## Interpretation

- **Dauerhaft positive Differenz (Luecke):** Die Firma waechst schneller, als sie sich
  selbst finanzieren kann. Sie braucht externes Kapital.
- **Dauerhaft negative Differenz (Ueberschuss):** Die Firma erwirtschaftet mehr, als
  sie investiert. Typisch fuer reife, profitable Firmen -- genau der Starbucks-Fall.
- **Grosse Differenz in Year +1, danach kleine:** Der Ausgangszustand war
  unausgeglichen; das Modell hat sich eingeschwungen. Normal.
- **Wachsende Differenz ueber die Jahre:** Warnsignal. Der Finanzierungsbedarf
  eskaliert. Die Wachstumsannahmen sollten geprueft werden.

## Was in Python zu bauen ist

**Input:** Alle Prognosen aus den Schritten 1-5.

**Zu implementierende Rechenlogik:**
1. Bilanzsumme, Schulden und Eigenkapital je Prognosejahr summieren
2. Differenz berechnen
3. Veraenderung der Differenz gegenueber dem Vorjahr berechnen
4. Ausgleichsposten um die Veraenderung anpassen
5. Bei zinstragendem Ausgleichsposten: Schritte 4-6 iterativ wiederholen, bis die
   Differenz unter der Toleranz liegt
6. Pruefen, dass die Differenz null ist

**Output:** Ausgeglichene Bilanz.

**Vom Nutzer zu entscheiden:**
- Welcher Ausgleichsposten?
- Iterativ rechnen oder Ausgleichsposten waehlen, der keine Iteration braucht?
- Bei Iteration: Toleranz und maximale Iterationszahl?
- Wie wird eine nicht konvergierende Iteration behandelt?

---
---

# Schritt 7: Die Kapitalflussrechnung ableiten

> Fundstelle: [PDF S. 49-54, "Step 7: Project the Statement of Cash Flows"]

## Die Grundidee

Die Kapitalflussrechnung wird **nicht prognostiziert**, sondern **abgeleitet**. Sie
enthaelt keine neue Information, sondern uebersetzt die Bilanzveraenderungen in
Zahlungsstroeme [PDF S. 49]:

> "the statement of cash flows simply characterizes all of the changes in the balance
> sheet in terms of the implications for cash"

**[ALLGEMEIN] Die vier Grundregeln** [PDF S. 50]:

| Veraenderung | Wirkung auf Cash |
|---|---|
| Vermoegenswert steigt | Mittelabfluss |
| Vermoegenswert sinkt | Mittelzufluss |
| Schuld oder Eigenkapital steigt | Mittelzufluss |
| Schuld oder Eigenkapital sinkt | Mittelabfluss |

Die Logik: Wer sein Lager aufstockt, hat Geld ausgegeben. Wer eine Verbindlichkeit
erhoeht, hat Geld behalten.

## [ALLGEMEIN] Die ausdrueckliche Warnung des PDFs

Ein zentraler methodischer Hinweis [PDF S. 50, "Tips for Forecasting Statements of
Cash Flows"]:

> "You should **not** attempt to project future statements of cash flows from
> historical statements of cash flows."

Begruendung: In der historischen Kapitalflussrechnung fasst der Bilanzierende Posten
zusammen oder trennt sie auf, ohne dass das von aussen nachvollziehbar ist. Eine
Akquisition erscheint als eine Zeile, veraendert aber Dutzende Bilanzposten.

Die Konsequenz [PDF S. 50]:

> "We strongly recommend simply following the steps below to compute the **implied
> statement of cash flows** from the projected balance sheets and income statements,
> which you can observe and verify."

Diese Regel ist vollstaendig allgemein und wird unveraendert umgesetzt.

## Die 30 Zeilen im Detail

Fundstelle fuer alle Zeilennummern: [PDF S. 50-53]; Zahlenbeispiel: [PDF S. 51-52,
Exhibit 10.5].

### Operativer Bereich (Zeilen 1-13)

```
(1)  Nettogewinn                                    aus der GuV
(2)  + Abschreibungen                               aus der GuV
(3)  + Amortisation                                 aus der GuV
(4)-(10) -/+ Veraenderung Working Capital           aus der Bilanz
(11)-(12) -/+ Veraenderung latente Steuern und
              langfristige Rueckstellungen          aus der Bilanz
--------------------------------------------------------------
(13) = Cashflow aus operativer Taetigkeit           Summe (1) bis (12)
```

**Warum werden Abschreibungen addiert?** Sie haben den Gewinn gemindert, aber kein Geld
gekostet -- das Geld floss beim Kauf der Anlage ab. Fuer die Cash-Betrachtung muss der
Buchungseffekt rueckgaengig gemacht werden [PDF S. 50, Zeile 2].

**Vorzeichen bei Working Capital** [PDF S. 53, Zeilen 4-10]:
- Forderungen **steigen** -> **negativ** (Umsatz gebucht, Geld noch nicht da)
- Vorraete **steigen** -> **negativ** (Geld in Ware gebunden)
- Verbindlichkeiten **steigen** -> **positiv** (Ware erhalten, noch nicht bezahlt)

### Investitionsbereich (Zeilen 14-20)

```
(14) - Investitionen in Sachanlagen
(15) -/+ Veraenderung kurzfristige Finanzanlagen
(16) -/+ Veraenderung langfristige Finanzanlagen
(17) -/+ Veraenderung abschreibbare immaterielle Vermoegenswerte
(18) -/+ Veraenderung Goodwill und nicht abschreibbare Immaterielle
(19) -/+ Veraenderung sonstige langfristige Vermoegenswerte
--------------------------------------------------------------
(20) = Cashflow aus Investitionstaetigkeit          Summe (14) bis (19)
```

**[ALLGEMEIN] Die Kontrollrechnung fuer Sachanlagen** [PDF S. 53, Zeile 14]:

```
Abschreibungen - Investitionen + Erloese aus Anlagenverkaeufen
= Veraenderung der Sachanlagen (netto)
```

Diese Gleichung ist ein wertvoller Selbsttest fuer die Implementierung: Wenn sie nicht
aufgeht, ist der Abschreibungsplan aus Schritt 2 fehlerhaft.

**[ALLGEMEIN] Der Sonderfall Amortisation** [PDF S. 53, Zeile 17]: Immaterielle
Vermoegenswerte stehen netto in der Bilanz. Ihre Veraenderung enthaelt deshalb zwei
Effekte gleichzeitig -- Zukaeufe und Amortisation. Um den Zahlungsstrom zu isolieren,
muss die Amortisation zurueckaddiert werden.

Das PDF nennt fuer kleine Betraege ausdruecklich eine Vereinfachung [PDF S. 53,
Zeile 3]: Amortisation gar nicht erst zurueckaddieren und die Nettoveraenderung
komplett im Investitionsbereich zeigen. Das verschiebt Betraege zwischen operativem
und Investitionsbereich, aber der Nettoeffekt auf die Kasse ist null.

### Finanzierungsbereich (Zeilen 21-27)

```
(21) -/+ Veraenderung kurzfristige Schulden
(22) -/+ Veraenderung langfristige Schulden
(23) -/+ Veraenderung gezeichnetes Kapital und Kapitalruecklage
(24) -/+ Veraenderung kumuliertes sonstiges Ergebnis (OCI)
(25) - Dividenden und Aktienrueckkaeufe
(26) -/+ Veraenderung Minderheitsanteile
--------------------------------------------------------------
(27) = Cashflow aus Finanzierungstaetigkeit         Summe (21) bis (26)
```

### Abstimmung (Zeilen 28-30)

```
(28) Veraenderung der Kasse = (13) + (20) + (27)
(29) Kasse Anfangsbestand
(30) Kasse Endbestand = (29) + (28)
```

**[ALLGEMEIN] Die entscheidende Kontrolle** [PDF S. 53, Zeilen 29-30]:

```
Kasse Endbestand (aus der Kapitalflussrechnung)
= Kasse Endbestand (aus der prognostizierten Bilanz)
```

In Exhibit 10.5 heisst diese Zeile "Check figure" und muss in jedem Jahr null sein
[PDF S. 52].

**[ALLGEMEIN]** Das PDF nennt die Voraussetzung dafuer ausdruecklich [PDF S. 50]:

> "The statement of cash flows will only reconcile with the projected income statement
> and balance sheets when the balance sheets balance and the income statement
> articulates with the balance sheets."

Uebersetzt: Wenn die Kontrolle nicht aufgeht, liegt der Fehler **nicht** in Schritt 7,
sondern in einem der vorherigen Schritte. Schritt 7 ist damit der Gesamttest fuer das
ganze Modell.

## Interpretation

- **Operativer Cashflow deutlich ueber dem Nettogewinn:** Gesund. Der Unterschied sind
  meist die Abschreibungen. Fuer Starbucks Year +1: 4.648,5 vs. 2.794,3 [PDF S. 51].
- **Operativer Cashflow unter dem Nettogewinn:** Warnsignal. Gewinne werden gebucht,
  aber nicht kassiert -- Forderungen und Vorraete binden das Geld.
- **Freier Cashflow** = operativer Cashflow - Investitionen. Fuer Starbucks Year +1:
  4.648,5 - 1.400,0 = 3.248,5. Das ist das Geld, das fuer Aktionaere und Glaeubiger
  uebrig bleibt -- und der zentrale Input jeder DCF-Bewertung.
- **Negativer Finanzierungs-Cashflow:** Die Firma gibt Geld an Kapitalgeber zurueck.
  Reifezeichen. Positiver Wert bedeutet Kapitalaufnahme -- Wachstums- oder
  Krisenzeichen.

## Was in Python zu bauen ist

**Input:** Die prognostizierte GuV und Bilanz aus den Schritten 1-6. Historische
Kapitalflussrechnungen werden **nicht** verwendet [PDF S. 50].

**Zu implementierende Rechenlogik:**
1. Fuer jedes Prognosejahr die Veraenderung jedes Bilanzpostens berechnen
2. Vorzeichen nach den vier Grundregeln setzen
3. Zeilen 1-13 zum operativen Cashflow summieren
4. Zeilen 14-20 zum Investitions-Cashflow summieren
5. Zeilen 21-27 zum Finanzierungs-Cashflow summieren
6. Veraenderung der Kasse als Summe der drei Bereiche
7. Kontrolle: berechneter Endbestand gegen Bilanzwert pruefen

**Output:** Prognostizierte Kapitalflussrechnung plus Kontrollergebnis.

**Vom Nutzer zu entscheiden:**
- Welche Detailtiefe -- alle 30 Zeilen oder zusammengefasst?
- Toleranz fuer die Kontrolle (exakt null oder Rundungsspielraum)?
- Verhalten bei fehlgeschlagener Kontrolle: Fehler werfen, warnen, oder nur melden?
- Amortisation getrennt behandeln oder vereinfachen [PDF S. 53, Zeile 3]?

---
---

# Zusammenfassung: die Rechenkette

| Schritt | Input | Output | Kernformel |
|---|---|---|---|
| 1 | Historischer Umsatz | Umsatzprognose | `Umsatz x (1 + g)` |
| 2 | Umsatzprognose, Kostenhistorie | Aufwendungen, Betriebsergebnis | `Umsatz x Quote` |
| 3 | Umsatz, Wareneinsatz | Betriebliche Bilanzposten | `(Bezug / 365) x Tage` |
| 4 | Bilanzsumme | Fremdkapital, Zinsen | `Ø Schulden x Zinssatz` |
| 5 | Betriebsergebnis, Zinsen | Nettogewinn, Gewinnruecklagen | `Vorsteuer x (1 - Steuersatz)` |
| 6 | Alles | Ausgeglichene Bilanz | `Aktiva - Passiva = 0` |
| 7 | GuV und Bilanz | Kapitalflussrechnung | `Δ Bilanzposten -> Cash` |

## Alle [ABWEICHUNG]-Stellen im Ueberblick

Die Spalte **LLM** sagt, ob die Abweichung ein fehlendes *Urteil* ist, das ein LLM aus
dem Jahresabschluss bilden kann (siehe "Zwei Arten von Abweichung" am Anfang der
Datei):

- **ja** -- vollstaendig durch ein LLM setzbar
- **teilweise** -- die fehlende Zahl bleibt fehlend, aber der zugehoerige Parameter
  (Quote, Rate, Tage) ist ein Urteil und damit LLM-setzbar
- **nein** -- die Groesse steht in keinem Abschluss, ein LLM koennte sie nur erfinden

| # | Schritt | PDF-Variante | Implementierte Variante | LLM | Fundstelle |
|---|---|---|---|---|---|
| 1 | 1 | Segmentweise Prognose ueber Filialzahlen und Umsatz pro Filiale | CAGR-Fortschreibung des Gesamtumsatzes (der vom PDF selbst genannte Fallback) | teilweise -- Segmentierung nein, Wahl der Wachstumsrate ja | [PDF S. 2-12] |
| 2 | 1 | 53-Wochen-Korrektur (Faktor 1,019) | entfaellt -- Starbucks-Kalenderbesonderheit | nein -- Kalenderfrage, keine Abschlussgroesse | [PDF S. 11-12] |
| 3 | 2 | Miete getrennt ueber Miete pro Filiale x Filialanzahl | Common-Size auf den Gesamtposten Wareneinsatz | teilweise -- Trennung nein, Hoehe der Quote ja | [PDF S. 13-14] |
| 4 | 2 | Filialbetriebskosten am Umsatz firmeneigener Filialen | Common-Size am Gesamtumsatz | teilweise -- Bezugsgroesse nein, Quote ja | [PDF S. 14-15] |
| 5 | 2 | Investitionen aus MD&A-Ankuendigung | Common-Size vom Umsatz | **ja** -- Anlagenalter ist aus Bilanz und Anlagenspiegel ablesbar | [PDF S. 15-16] |
| 6 | 3 | Forderungen am Segmentumsatz (Lizenz/CPG/Foodservice) | Umschlagsdauer am Gesamtumsatz | teilweise -- Bezugsgroesse nein, Umschlagsdauer ja | [PDF S. 28] |
| 7 | 3 | Rechnungsabgrenzung ueber Filialanzahl | Wachstum mit Umsatzwachstumsrate | teilweise -- Filialbezug nein, Technikwahl ja | [PDF S. 29] |
| 8 | 3 | Latente Steuern -100 % / -10 % p. a. (PDF nennt es selbst "arbitrary") | konstant halten | **ja** -- PDF nennt seine Annahme selbst willkuerlich | [PDF S. 30] |
| 8b | 3 | Wachstumsraten Goodwill / immaterielle / Finanzanlagen (3 % / 5 %, gesetzt) | konstant oder Parameter | **ja** -- Akquisitionsmuster ist aus der Historie ablesbar | [PDF S. 30-31] |
| 9 | 4 | Fremdkapital ueber Faelligkeitsprofil aus Note 9 | Prozent der Bilanzsumme (vom PDF als Alternative genannt) | teilweise -- Faelligkeiten nein, Zielquote ja | [PDF S. 36-37] |
| 10 | 4 | Gewichteter Zinssatz aus Einzelanleihen | Effektiver Zinssatz aus der Historie | **ja** -- welcher Jahreswert/Durchschnitt gilt, ist ein Urteil | [PDF S. 38-39] |
| 11 | 5 | Steuersatz 34 % aus MD&A-Ankuendigung | Effektiver Steuersatz aus der Historie | **ja** -- Ausreisser vs. neues Niveau ist ein Urteil | [PDF S. 43] |
| 11b | 5 | Dividende je Aktie und Rueckkaufprogramm aus Ankuendigung | historische Ausschuettungsquote | **ja** -- Ausschuettungshistorie steht in der Kapitalflussrechnung | [PDF S. 44-45] |
| 12 | 6 | Aktienrueckkaeufe als Ausgleichsposten | Fremdkapital (Empfehlung, Entscheidung offen) | **ja** -- PDF formuliert die Wahl selbst als Einordnung der Firma | [PDF S. 46-47] |

Die Stellen 1, 3-7, 9-11 haben alle dieselbe Ursache: Das PDF nutzt MD&A-Fliesstext,
Anhangsangaben und Segmentberichte, die ueber FMP und SEC-XBRL nicht maschinell
verfuegbar sind. In allen diesen Faellen wird die Regel verwendet, die das PDF selbst
als allgemeine Alternative formuliert.

**Das Bild, das die LLM-Spalte zeigt:** Nur zwei Zeilen sind ein echtes "nein". Bei
allen anderen bleibt zwar die *Struktur* der PDF-Rechnung unerreichbar (Segmente,
Filialen, Anleihen), aber der **Parameter**, mit dem die Ersatzrechnung arbeitet, ist
in jedem einzelnen Fall ein Urteil ueber eine Zeitreihe aus dem Jahresabschluss. Genau
dort setzt das LLM an.

Fuer die Thesis laesst sich das so formulieren: Die Implementierung ersetzt nicht die
*Daten* des Analysten -- die bleiben teilweise unerreichbar -- sondern sein
**Urteilsvermoegen**, und zwar an genau den Stellen, an denen das Urteil auf Zahlen
beruht, die maschinell vorliegen.

## Was bewusst NICHT an ein LLM gegeben wird

Diese Abgrenzung ist so wichtig wie die Liste oben:

| Bereich | Grund |
|---|---|
| Jede Arithmetik der 7 Schritte | Reine Rechnung. Ein LLM wuerde nur Fehler hinzufuegen. |
| Die schichtweise Abschreibungsrechnung | Deterministisch, im PDF vollstaendig spezifiziert. |
| Die Ausgleichsrechnung in Schritt 6 | Muss exakt auf null gehen. |
| Die Kapitalflussrechnung in Schritt 7 | Reine Differenzenbildung aus Bilanz und GuV. |
| Die Bewertungsmodelle in Kapitel 8 | Feste Formeln, muessen untereinander uebereinstimmen. |
| Langfristige Wachstumsrate (3 %) | Gesamtwirtschaftliche Groesse, keine Firmeneigenschaft. Zudem muss sie in Schritt 1 und im Fortfuehrungswert identisch sein. |
| Marktrisikopraemie | Marktgroesse, keine Abschlussgroesse. |
| Kuenftige Wertminderungen | Waere reine Spekulation. |

Kurz: **Das LLM setzt Annahmen, es rechnet nicht.**

## Reihenfolgeabhaengigkeiten

Diese Abhaengigkeiten muessen in der Implementierung eingehalten werden:

```
Umsatz                    -> alles Weitere
Wareneinsatz              -> Vorraete
Vorraete                  -> Wareneinkauf -> Verbindlichkeiten
Sachanlagen               -> Abschreibungen -> Betriebsergebnis
Bilanzsumme               -> Fremdkapital -> Zinsen
Zinsen                    -> Nettogewinn -> Gewinnruecklagen
Gewinnruecklagen          -> Bilanzsumme   [Zirkel, siehe Schritt 6]
Vollstaendige Bilanz      -> Kapitalflussrechnung
```

## Naechster Schritt nach Schritt 7

Die 7 Schritte liefern prognostizierte Abschluesse -- noch keine Kaufentscheidung.
Dafuer ist eine Bewertung noetig, die auf diesen Prognosen aufsetzt. Sie ist der
Gegenstand des folgenden Kapitels 8.

Die Bruecken-Werte von Schritt 7 in die Bewertung sind der operative Cashflow, der
Investitions-Cashflow und die Veraenderung des Kassenbestands.

---
---

# Kapitel 8: Die Bewertung -- von der Prognose zur Kaufentscheidung

> **Quelle dieses Kapitels:** Nicht das PDF, sondern das Blatt `Valuation` der Datei
> `fsap/FSAP - Starbucks.xlsx` (FSAP Version 9.0). Zitiert wird als
> `[Valuation!Zelle]`. Die Guide-Texte von FSAP stehen im Blatt in Spalte L und werden
> als `[Valuation!Ln]` zitiert.
>
> Die zugehoerigen Buchkapitel nennt FSAP selbst: Dividendenmodell = Kap. 11
> [Valuation!L68], Free-Cash-Flow-Modelle = Kap. 12 [Valuation!L95, L244],
> Residual Income = Kap. 13 [Valuation!L151], Market-to-Book = Kap. 14
> [Valuation!L208].

## Warum es ueberhaupt eine Bewertung braucht

Die Schritte 1-7 sagen, **was die Firma verdienen wird**. Sie sagen nicht, **was die
Aktie wert ist**. Dazwischen liegt eine eigene Rechnung: Zukuenftige Zahlungen sind
weniger wert als heutige Zahlungen -- wegen Zinsen und wegen Risiko.

Die Bewertung beantwortet daher zwei Fragen:
1. Welche Zahlungen fliessen den Aktionaeren zu? (kommt aus Schritt 1-7)
2. Was sind diese Zahlungen heute wert? (das ist Kapitel 8)

Am Ende steht ein **Wert je Aktie**. Dieser wird mit dem **Boersenkurs** verglichen.
Der Vergleich *ist* die Kaufentscheidung.

## Der Ablauf im Ueberblick

```
Prognosen aus Schritt 1-7
    v
8.1  Kapitalkosten bestimmen  (Diskontierungssatz)
    v
8.2  Zahlungsstrom je Modell ableiten  (Year +1 bis +5)
    v
8.3  Fortfuehrungswert berechnen  (Year +6 und danach)
    v
8.4  Alles auf heute abzinsen
    v
8.5  Mitteljahres-Korrektur
    v
8.6  Durch Aktienanzahl teilen  ->  Wert je Aktie
    v
8.7  Mit Boersenkurs vergleichen  ->  Kaufen oder Verkaufen
```

FSAP rechnet **fuenf Modelle parallel**. Vier davon muessen exakt denselben Wert
liefern; das fuenfte darf leicht abweichen. Das ist kein Zufall, sondern eine
eingebaute Kontrolle -- dazu Abschnitt 8.8.

---

## 8.1 Die Kapitalkosten

> Fundstelle: [Valuation!A22-F59]

Der Diskontierungssatz drueckt aus, welche Rendite ein Investor fuer das eingegangene
Risiko verlangt. Je riskanter, desto hoeher der Satz, desto niedriger der heutige Wert.

### 8.1.1 Eigenkapitalkosten (CAPM)

FSAP verwendet das Capital Asset Pricing Model [Valuation!L36]:

> "FSAP computes the expected rate of return on equity using the market model version
> of the CAPM."

```
Eigenkapitalkosten = Risikofreier Zins + Beta x Marktrisikopraemie
```

Formel im Blatt: `F36 = F34 + F33 * F35` [Valuation!F36]

Starbucks-Werte [Valuation!F33-F36]:
```
Beta                  = 0,75
Risikofreier Zins     = 2,7 %
Marktrisikopraemie    = 6,0 %

Eigenkapitalkosten    = 0,027 + 0,75 x 0,06 = 0,027 + 0,045 = 7,2 %
```

Die drei Bausteine:

- **Risikofreier Zins:** Rendite einer sicheren Staatsanleihe. FSAP empfiehlt
  3- bis 5-jaehrige US-Treasuries [Valuation!L34].
- **Beta:** Wie stark schwankt die Aktie gegenueber dem Gesamtmarkt? Beta = 1 bedeutet
  Gleichlauf, Beta = 0,75 bedeutet 25 % weniger Schwankung als der Markt -- Starbucks
  gilt also als defensiver als der Durchschnitt.
- **Marktrisikopraemie:** Aufschlag, den Aktien gegenueber sicheren Anlagen bieten
  muessen. FSAP nennt eine plausible Spanne [Valuation!L35]:

  > "Reasonable estimates commonly range from 3% to 9%."

### 8.1.2 Fremdkapitalkosten

```
Fremdkapitalkosten nach Steuern = Zinssatz vor Steuern x (1 - Steuersatz)
```

Formel im Blatt: `F42 = F40 * (1 + F41)` [Valuation!F42]

**Achtung Vorzeichen:** FSAP fuehrt den Steuersatz als negative Zahl (-0,34), weil
Aufwendungen im Blatt negativ dargestellt werden. `(1 + (-0,34))` ergibt daher `0,66`.
In einer Python-Umsetzung mit positivem Steuersatz lautet die Formel
`Zinssatz x (1 - Steuersatz)`.

Starbucks [Valuation!F40-F42]:
```
Zinssatz vor Steuern  = 2,7067 %
Steuersatz            = 34,0 %
Nach Steuern          = 0,027067 x (1 - 0,34) = 1,7864 %
```

**Warum nach Steuern?** Zinsen mindern den steuerpflichtigen Gewinn. Von 100 Euro
Zinsen traegt der Staat bei 34 % Steuersatz effektiv 34 Euro -- Fremdkapital kostet die
Firma real nur 66 % des Nominalzinses. Dieser Effekt heisst *tax shield*.

### 8.1.3 Gewichtete Kapitalkosten (WACC)

```
WACC = Gewicht(EK) x Eigenkapitalkosten
       + Gewicht(FK) x Fremdkapitalkosten nach Steuern
       + Gewicht(Vorzugsaktien) x deren Kosten
       + Gewicht(Minderheiten) x deren Kosten
```

Formel im Blatt: `F59 = (F55*F36) + (F56*F42) + (F57*F47) + (F58*F52)`
[Valuation!F59]

Die Gewichte [Valuation!F55-F58]:
```
Gewicht(EK) = Marktwert EK / (Marktwert EK + FK + Vorzugsaktien + Minderheiten)
```

**Wichtig:** Der Zaehler ist der **Marktwert**, nicht der Buchwert [Valuation!F26]:
```
Marktwert Eigenkapital = Aktienkurs x Anzahl Aktien
                       = 56,84 x 1.485,1 = 84.413,1 Mio.
```

Starbucks [Valuation!F55-F59]:
```
Gewicht(EK)  = 84.413,1 / (84.413,1 + 2.402) = 97,23 %
Gewicht(FK)  = 2.402 / 86.815,1              =  2,77 %

WACC = 0,9723 x 0,072 + 0,0277 x 0,017864 = 0,07001 + 0,00049 = 7,050 %
```

Der WACC liegt hier nur knapp unter den Eigenkapitalkosten, weil Starbucks -- gemessen
zu Marktwerten -- fast ausschliesslich eigenkapitalfinanziert ist.

### Interpretation der Kapitalkosten

- **Hoehere Kapitalkosten -> niedrigerer Unternehmenswert.** Der Zusammenhang ist
  stark. Die Sensitivitaetstabelle [Valuation!B185-J198] zeigt es drastisch: bei 6 %
  Diskontsatz und 3 % Wachstum ergeben sich 93,09 USD je Aktie, bei 12 % nur noch
  30,31 USD -- derselbe Zahlungsstrom, dreifacher Wertunterschied.
- **Beta ist der subjektivste Baustein.** Es wird aus historischen Kursdaten
  geschaetzt und variiert je nach Zeitfenster erheblich.
- **Der WACC ist zirkulaer.** Er braucht den Marktwert des Eigenkapitals als Gewicht --
  aber genau den will man erst berechnen. Mehr dazu in Abschnitt 8.8.

### Was in Python zu bauen ist

**Input:**
- Beta: `FMP.get_profile()` -> Feld `beta`
- Risikofreier Zins: `FMP.get_treasury_rates()` (3- oder 5-Jahres-Satz)
- Marktrisikopraemie: **kein API-Wert** -- muss gesetzt werden
- Aktienkurs: `FMP.get_quote()` -> `price`
- Aktienanzahl: `FMP.get_shares_float()` -> `outstandingShares`
- Fremdkapital: `FMP.get_balance_sheet()` -> `totalDebt`
- Zinssatz und Steuersatz: aus Schritt 4 und 5

**Rechenlogik:**
1. Eigenkapitalkosten nach CAPM
2. Fremdkapitalkosten nach Steuern
3. Marktwert des Eigenkapitals
4. Gewichte berechnen
5. WACC als gewichtete Summe

**Vom Nutzer zu entscheiden:**
- Marktrisikopraemie: welcher Wert? (FSAP nutzt 6,0 %, Spanne 3-9 % [Valuation!L35])
- Risikofreier Zins: welche Laufzeit? Tagesaktuell oder Durchschnitt?
- Beta aus FMP uebernehmen oder selbst aus Kursdaten schaetzen?
- Vorzugsaktien und Minderheiten modellieren oder als null annehmen?

---

## 8.2 Die fuenf Bewertungsmodelle

Alle fuenf folgen demselben Muster: Zahlungsstrom bestimmen, abzinsen, summieren,
Fortfuehrungswert addieren, durch Aktienanzahl teilen. Sie unterscheiden sich nur
darin, **welchen** Zahlungsstrom sie betrachten.

### Modell 1: Dividendenmodell

> Fundstelle: [Valuation!A68-E86], Buch Kap. 11 [Valuation!L68]

Die Grundidee: Ein Aktionaer erhaelt Dividenden und Geld aus Aktienrueckkaeufen. Der
Wert der Aktie ist der Barwert dieser Zahlungen.

```
Netto-Dividende = Dividenden an Aktionaere
                  - Erloese aus Aktienausgaben
                  + Aktienrueckkaeufe
```

Formeln im Blatt [Valuation!E70-E73]:
```
E70 = Dividendenzahlungen                     (aus Forecasts)
E71 = Veraenderung gezeichnetes Kapital       (negativ = Ausgabe)
E72 = Aktienrueckkaeufe
E73 = SUMME(E70:E72)
```

Starbucks Year +1 [Valuation!E73]: `3.839,94 Mio.`

**Warum werden Rueckkaeufe addiert?** Sie sind wirtschaftlich dasselbe wie eine
Dividende -- Geld fliesst von der Firma zu den Aktionaeren, nur in anderer Form.
**Warum werden Aktienausgaben abgezogen?** Dabei fliesst Geld in die Gegenrichtung.

**Diskontsatz:** Eigenkapitalkosten (`F36`), nicht WACC [Valuation!E75]. Begruendung:
Der Zahlungsstrom fliesst ausschliesslich an Eigenkapitalgeber.

### Modell 2: Free Cash Flow to Equity

> Fundstelle: [Valuation!A95-E116], Buch Kap. 12 [Valuation!L95]

Statt der tatsaechlich ausgeschuetteten Betraege wird das Geld betrachtet, das
**ausschuettbar waere**.

```
FCF to Equity = Operativer Cashflow
                - Zunahme der betriebsnotwendigen Kasse
                + Investitions-Cashflow
                + Netto-Cashflow aus Fremdfinanzierung
                + Anpassung Finanzanlagen
                + Anpassung Vorzugsaktien und Minderheiten
```

Formeln im Blatt [Valuation!E97-E103]:
```
E97  = Operativer Cashflow                    (Forecasts Zeile 297)
E98  = -Veraenderung der Kasse                (Forecasts Zeile 315)
E99  = Investitions-Cashflow                  (Forecasts Zeile 305)
E100 = Veraenderung kurz- + langfristige Schulden
E101 = -Anpassung Finanzanlagen
E102 = Vorzugsaktien und Minderheiten
E103 = SUMME(E97:E102)
```

**Die Zeile E98 verdient Aufmerksamkeit** [Valuation!L98]:

> "As firms grow, they typically require larger cash balances for liquidity in
> operating activities. FSAP is programmed to automatically adjust free cash flows for
> the change in the cash balance, which is assumed to be required for operations."

Uebersetzt: Waechst die Firma, muss sie mehr Kasse vorhalten. Dieses Geld ist gebunden
und steht den Aktionaeren **nicht** zur Verfuegung. Es wird deshalb abgezogen. Genau
diese Kasse wurde in Schritt 3 ueber die Umschlagsdauer prognostiziert.

**Diskontsatz:** Eigenkapitalkosten [Valuation!E105].

### Modell 3: Residual Income

> Fundstelle: [Valuation!A151-E173], Buch Kap. 13 [Valuation!L151]

Der konzeptionell interessanteste Ansatz. Grundidee: Eine Firma schafft nur dann Wert,
wenn sie **mehr verdient als die Kapitalkosten verlangen**.

```
Geforderter Gewinn = Buchwert Eigenkapital (Jahresanfang) x Eigenkapitalkosten
Residualgewinn     = Tatsaechlicher Gewinn - Geforderter Gewinn
```

Formeln im Blatt [Valuation!E153-E158]:
```
E153 = Gesamtergebnis fuer Stammaktionaere
E155 = Buchwert Eigenkapital zu Jahresbeginn (t-1)
E157 = E155 * F36
E158 = E153 - E157
```

Starbucks Year +1 [Valuation!E153-E158]:
```
Gesamtergebnis      = 2.794,30
Buchwert (Anfang)   = 5.818,00
Geforderter Gewinn  = 5.818,00 x 0,072 = 418,90
Residualgewinn      = 2.794,30 - 418,90 = 2.375,41
```

Interpretation: Die Aktionaere haben 5.818 Mio. investiert und verlangen darauf 7,2 %,
also 418,9 Mio. Starbucks verdient 2.794,3 Mio. -- 2.375,4 Mio. mehr als gefordert.
Diese Uebererfuellung ist die Wertschaffung.

**Der entscheidende Unterschied zu den anderen Modellen** [Valuation!E165]:

```
Unternehmenswert = Buchwert des Eigenkapitals heute
                   + Barwert aller kuenftigen Residualgewinne
```

Das Modell startet also beim bereits vorhandenen Buchwert und addiert nur, was darueber
hinaus erwirtschaftet wird. Praktischer Vorteil: Ein Teil des Werts (hier 5.818 von
98.159 Mio.) ist ein harter Bilanzwert und keine Prognose. Das macht das Modell weniger
empfindlich gegenueber Prognosefehlern.

**Warum Gesamtergebnis und nicht Nettogewinn?** Damit die Verknuepfung mit der Bilanz
sauber bleibt: Jede Eigenkapitalaenderung muss entweder Ergebnis oder Ausschuettung
sein. Diese Bedingung heisst *clean surplus relation* und ist Voraussetzung dafuer,
dass das Modell denselben Wert liefert wie die anderen.

### Modell 4: Residual Income Market-to-Book

> Fundstelle: [Valuation!A207-E234], Buch Kap. 14 [Valuation!L208]

Rechnerisch identisch mit Modell 3, aber in Verhaeltniszahlen statt Geldbetraegen.
Ergebnis ist zunaechst ein **Kurs-Buchwert-Verhaeltnis**, das dann mit dem Buchwert
multipliziert wird.

```
Implizite ROCE      = Gesamtergebnis / Buchwert EK (Jahresanfang)
Residual-ROCE       = Implizite ROCE - Eigenkapitalkosten
Kumul. Wachstumsfaktor = Buchwert EK (t-1) / Buchwert EK (heute)
Beitrag             = Residual-ROCE x Kumul. Wachstumsfaktor
```

Formeln im Blatt [Valuation!E214-E217, E224-E229]:
```
E214 = E210 / E212
E215 = E214 - F36
E216 = E212 / $E$212
E217 = E215 * E216
...
E224 = 1                              (fuer den Buchwert selbst)
E225 = E223 + E224
E227 = E225 * E226                    -> implizites Kurs-Buchwert-Verhaeltnis
E229 = E227 * E228                    -> Wert des Eigenkapitals
```

Die `1` in Zeile E224 steht fuer den vorhandenen Buchwert (Verhaeltnis 1,0 zu sich
selbst); alles darueber ist Wertschaffung.

**Interpretation:** Ein Kurs-Buchwert-Verhaeltnis ueber 1 bedeutet, dass der Markt der
Firma zutraut, mehr als die Kapitalkosten zu verdienen. Fuer Starbucks ergibt sich
`98.159 / 5.818 = 16,9` -- ein sehr hoher Wert, der die Erwartung dauerhaft hoher
Renditen ausdrueckt.

FSAP merkt an, dass die Sensitivitaetsanalyse dieses Modells zwangslaeufig identisch zu
Modell 3 ist [Valuation!A236] -- die Modelle sind algebraisch aequivalent.

### Modell 5: Free Cash Flow to All Debt and Equity

> Fundstelle: [Valuation!A244-E270], Buch Kap. 12 [Valuation!L244]

Das einzige Modell, das den WACC verwendet. Es bewertet zuerst das **gesamte
Unternehmen** (Eigen- und Fremdkapitalgeber zusammen) und zieht danach die Schulden ab.

```
FCF All Debt and Equity = Operativer Cashflow
                          + Zinsaufwand nach Steuern
                          - Zinsertrag nach Steuern
                          - Zunahme der betriebsnotwendigen Kasse
                          + Investitions-Cashflow
                          + Anpassung Finanzanlagen
```

Formeln im Blatt [Valuation!E246-E253]:
```
E246 = Operativer Cashflow
E247 = -Zinsaufwand * (1 - Steuersatz)
E248 = Zinsertrag nach Steuern            (bei Starbucks auf 0 gesetzt)
E249 = -Veraenderung der Kasse
E250 = SUMME(E246:E249)
E251 = Investitions-Cashflow
E252 = Anpassung Finanzanlagen            (bei Starbucks 0)
E253 = SUMME(E250:E252)
```

**Warum wird der Zinsaufwand zurueckaddiert?** [Valuation!L247] Der Zahlungsstrom soll
*allen* Kapitalgebern zustehen -- auch den Glaeubigern. Zinsen sind aber bereits an die
Glaeubiger geflossen und im operativen Cashflow abgezogen. Sie muessen deshalb
rueckgaengig gemacht werden. Nach Steuern, weil das tax shield real ist.

**Der Rueckweg zum Eigenkapital** [Valuation!E260-E263]:
```
Wert des Eigenkapitals = Gesamtunternehmenswert
                         - Wert des Fremdkapitals
                         - Wert der Vorzugsaktien
                         + Wert der Finanzanlagen
```

FSAP zur Bewertung der Schulden [Valuation!L260]:

> "Value should be market value, if known, or fair value if disclosed. If not, use book
> value."

Fuer eine API-basierte Umsetzung ist der Buchwert der praktikable Weg.

---

## 8.3 Der Fortfuehrungswert

> Fundstelle: [Valuation!E78, E108, E163, E222, E258]

Das ist der wichtigste einzelne Rechenschritt des ganzen Kapitels -- und der, bei dem
die meisten Fehler passieren.

### Das Problem

Prognostiziert wurden fuenf Jahre. Ein Unternehmen existiert aber laenger. Der Wert
nach Jahr 5 muss in einer einzigen Zahl zusammengefasst werden.

### Die Formel

FSAP verwendet die Gordon-Wachstumsformel [Valuation!L78]:

> "Year +6 dividends are treated as a perpetuity with growth using the long-run growth
> rate assumption, discounted to present value at the equity cost of capital."

```
Fortfuehrungswert = Zahlungsstrom(Year +6) / (Diskontsatz - Langfristiges Wachstum)
                    x Abzinsungsfaktor(Year +5)
```

Formel im Blatt [Valuation!E78]: `= J73 / ($F$36 - $F$29) * $I$75`

Starbucks, Dividendenmodell [Valuation!E78]: `81.112,20 Mio.`

### Die drei Fallstricke

**Fallstrick 1: Der Abzinsungsfaktor von Jahr 5, nicht Jahr 6.**
Die Formel `Zahlung / (r - g)` liefert bereits einen Wert **zum Zeitpunkt Jahr 5** --
ein Jahr vor der ersten Zahlung der Rente. Deshalb wird mit `I75` (Faktor Jahr 5)
multipliziert, nicht mit einem Faktor fuer Jahr 6. Wer hier Jahr 6 verwendet, zinst
doppelt ab.

**Fallstrick 2: Wachstum muss kleiner sein als der Diskontsatz.**
Ist `g >= r`, wird der Nenner null oder negativ und das Ergebnis unsinnig. Bei
Starbucks: `0,072 - 0,03 = 0,042`. Diese Bedingung muss in der Implementierung
geprueft werden.

**Fallstrick 3: Die Wachstumsannahme muss zu Schritt 1 passen.**
FSAP prueft das ausdruecklich [Valuation!A30, L29]:

> "This growth rate must agree with the long run growth rate used to forecast Year +6
> and Beyond in the Forecasts spreadsheet."

Die 3 % aus Schritt 1 und die 3 % hier sind derselbe Parameter. Werden sie
unterschiedlich gesetzt, ist das Ergebnis intern widerspruechlich.

### Wie dominant der Fortfuehrungswert ist

Starbucks, Dividendenmodell [Valuation!E77-E79]:
```
Barwert Jahre 1-5      =  13.636,05  ( 14,4 %)
Fortfuehrungswert      =  81.112,20  ( 85,6 %)
-----------------------------------------------
Summe                  =  94.748,25  (100,0 %)
```

**Mehr als 85 % des gesamten Unternehmenswerts stecken im Fortfuehrungswert.** Das ist
kein Ausreisser, sondern typisch. Die praktische Konsequenz: Die detaillierte
Fuenfjahresprognose aus den Schritten 1-7 bestimmt nur ein Siebtel des Ergebnisses. Die
beiden Parameter `r` und `g` bestimmen den Rest.

Wer das Modell kritisch liest, prueft zuerst diese beiden Zahlen -- nicht die
Umsatzprognose.

---

## 8.4 Abzinsung

> Fundstelle: [Valuation!E75, E105, E160, E219, E255]

```
Abzinsungsfaktor(Jahr n) = 1 / (1 + Diskontsatz)^n
Barwert                  = Zahlung(Jahr n) x Abzinsungsfaktor(Jahr n)
```

Formel im Blatt [Valuation!E75]: `= 1 / (1 + $F$36)^E67`

Bei 7,2 % Eigenkapitalkosten:
```
Jahr 1: 1 / 1,072^1 = 0,9328
Jahr 2: 1 / 1,072^2 = 0,8701
Jahr 3: 1 / 1,072^3 = 0,8117
Jahr 4: 1 / 1,072^4 = 0,7572
Jahr 5: 1 / 1,072^5 = 0,7063
```

**Welcher Diskontsatz zu welchem Modell:**

| Modell | Diskontsatz | Blattzelle |
|---|---|---|
| 1 Dividenden | Eigenkapitalkosten | `F36` [Valuation!E75] |
| 2 FCF to Equity | Eigenkapitalkosten | `F36` [Valuation!E105] |
| 3 Residual Income | Eigenkapitalkosten | `F36` [Valuation!E160] |
| 4 Market-to-Book | Eigenkapitalkosten | `F36` [Valuation!E219] |
| 5 FCF All Debt and Equity | **WACC** | `F59` [Valuation!E255] |

Die Regel dahinter: Der Diskontsatz muss zur Anspruchsgruppe passen. Fliesst der
Zahlungsstrom nur an Aktionaere, gelten Eigenkapitalkosten. Fliesst er an alle
Kapitalgeber, gilt der WACC.

---

## 8.5 Die Mitteljahres-Korrektur

> Fundstelle: [Valuation!E80, E110, E167, E226, E264]

```
Korrekturfaktor = 1 + Diskontsatz / 2
```

Formel im Blatt [Valuation!E80]: `= (1 + $F$36/2)`

Starbucks: `1 + 0,072/2 = 1,036` -- der Gesamtwert steigt also um 3,6 %.

FSAP begruendet [Valuation!L80]:

> "The present value factors discount from the end of each year to the present, whereas
> dividends, cash flows, and earnings are generated throughout the year. This adjustment
> computes the present value so that dividends, cash flows, and earnings are discounted
> from the mid-point of each year."

Uebersetzt: Die Standard-Abzinsung tut so, als kaeme das ganze Jahresgeld am
31. Dezember. Tatsaechlich faellt es ueber das Jahr verteilt an, im Schnitt zur
Jahresmitte. Ohne Korrektur wird ein halbes Jahr zu viel abgezinst.

**Hinweis:** `(1 + r/2)` ist eine Naeherung fuer den exakten Wert `(1 + r)^0,5`. Bei
7,2 % stehen 1,0360 gegen 1,0354 -- der Unterschied ist vernachlaessigbar. FSAP
verwendet die einfache Variante.

---

## 8.6 Wert je Aktie

> Fundstelle: [Valuation!E82-E83, E112-E113, E169-E170, E230-E231, E266-E267]

```
Wert je Aktie = Gesamtwert des Eigenkapitals / Anzahl ausstehender Aktien
```

Starbucks, Dividendenmodell [Valuation!E81-E83]:
```
Gesamtwert    = 98.159,19 Mio.
Aktien        =  1.485,1 Mio.
Wert je Aktie = 98.159,19 / 1.485,1 = 66,10 USD
```

---

## 8.7 Die Kaufentscheidung

> Fundstelle: [Valuation!E85-E86, L86]

Hier laeuft alles zusammen:

```
Prozentuale Abweichung = Wert je Aktie / Boersenkurs - 1
```

Formel im Blatt [Valuation!E86]: `= E83 / E85 - 1`

Starbucks:
```
Wert je Aktie          = 66,10 USD
Boersenkurs            = 56,84 USD
Prozentuale Abweichung = 66,10 / 56,84 - 1 = +16,28 %
```

**Die Entscheidungsregel** nennt FSAP explizit [Valuation!L86]:

> "(Value/price)-1: positive number indicates underpricing."

| Ergebnis | Bedeutung | Entscheidung |
|---|---|---|
| **positiv** | Wert ueber Kurs -- unterbewertet | **Kaufen** |
| **negativ** | Wert unter Kurs -- ueberbewertet | **Verkaufen** |
| **nahe null** | fair bewertet | Halten |

Fuer Starbucks: **+16,3 % -> Kaufsignal.**

**Was FSAP nicht vorgibt:** eine Mindestschwelle. Ob +2 % schon ein Kaufsignal ist oder
erst +20 %, bleibt offen. Angesichts der Sensitivitaet aus Abschnitt 8.3 waere es
unsauber, kleine Abweichungen als Signal zu werten -- sie liegen innerhalb der
Modellungenauigkeit. Eine Sicherheitsmarge ist daher zu empfehlen; ihre Hoehe ist eine
Nutzerentscheidung.

---

## 8.8 Die Kontrollen von FSAP

### Kontrolle 1: Alle Modelle muessen uebereinstimmen

> Fundstelle: [Valuation!A8-A15, F9-F13]

FSAP stellt die fuenf Ergebnisse an den Anfang des Blattes [Valuation!A14-A15]:

> "Check: All Estimated Value per Share amounts should be the same, with the possible
> exception of the share value from the Free Cash Flow for All Debt and Equity model."

Die tatsaechlichen Werte im Starbucks-Blatt [Valuation!F9-F13]:

| Modell | Wert je Aktie |
|---|---|
| Dividendenmodell | 66,0960151720624 |
| Free Cash Flow to Equity | 66,0960151720624 |
| Residual Income | 66,0960151720625 |
| Residual Income Market-to-Book | 66,0960151720625 |
| FCF All Debt and Equity | **65,9537593298281** |

Die ersten vier stimmen bis zur 12. Nachkommastelle ueberein. Das ist kein Zufall,
sondern eine mathematische Notwendigkeit: Bei konsistenten Prognosen und eingehaltener
clean surplus relation sind die Modelle algebraisch aequivalent.

**Das macht die Uebereinstimmung zum besten verfuegbaren Test der Implementierung.**
Weichen die vier Modelle voneinander ab, liegt ein Fehler in den Prognosen aus den
Schritten 1-7 -- nicht in der Bewertung.

### Kontrolle 2: Warum Modell 5 abweichen darf

FSAP erklaert die Abweichung [Valuation!L267]:

> "The first-iteration estimate of share value using this approach frequently differs
> slightly from the other share value estimates. Several iterations can be required to
> adjust the weights of debt and equity used to compute WACC to agree with the value of
> common equity implied by this valuation model."

Der Grund ist eine **zweite Zirkularitaet** -- nach der aus Schritt 6:

```
WACC braucht Marktwert des Eigenkapitals als Gewicht
  -> Marktwert wird aber erst durch das Modell berechnet
  -> das Modell braucht den WACC
```

Im Starbucks-Blatt wird der WACC mit dem **Boersenkurs** (56,84 USD) gewichtet. Das
Modell selbst kommt aber auf 66,10 USD. Waere der berechnete Wert als Gewicht
eingesetzt worden, stiege der Eigenkapitalanteil, der WACC naeherte sich den
Eigenkapitalkosten -- und der Wert konvergierte gegen die anderen Modelle.

Die Abweichung betraegt hier `65,95 vs. 66,10 = -0,22 %` und ist damit unerheblich. Bei
stark verschuldeten Firmen faellt sie deutlich groesser aus.

**Praktische Konsequenz:** Modell 5 ist das aufwaendigste und das einzige mit
Iterationsbedarf. Fuer eine erste Implementierung sind Modell 1 und 3 die bessere Wahl.

### Kontrolle 3: Sensitivitaetsanalyse

> Fundstelle: [Valuation!A181-J198]

FSAP legt eine Matrix an: Diskontsaetze von 6 % bis 12 % (Zeilen) gegen langfristige
Wachstumsraten von 0 % bis 5 % (Spalten) [Valuation!B185-J198].

Auszug (Wert je Aktie in USD):

| r \ g | 0 % | 2 % | 3 % | 4 % | 5 % |
|---|---|---|---|---|---|
| 6,0 % | 52,05 | 72,57 | 93,09 | 134,12 | 257,23 |
| 7,0 % | 44,30 | 57,72 | 69,47 | 89,04 | 128,18 |
| **7,2 %** | 43,01 | 55,44 | **66,10** | 83,41 | 116,46 |
| 8,0 % | 38,51 | 47,85 | 55,32 | 66,53 | 85,21 |
| 10,0 % | 30,45 | 35,56 | 39,21 | 44,07 | 50,89 |
| 12,0 % | 25,13 | 28,24 | 30,31 | 32,90 | 36,23 |

Was diese Tabelle zeigt:

- **Die Spannweite ist enorm:** von 25,13 bis 257,23 USD -- Faktor 10, bei identischen
  Prognosen aus den Schritten 1-7.
- **Bei niedrigen Diskontsaetzen explodiert die Empfindlichkeit.** In der Zeile 6 % ist
  der Sprung von 4 % auf 5 % Wachstum ein Plus von 92 % (134 -> 257 USD). Der Grund ist
  der Nenner `r - g`, der gegen null geht.
- **Der Boersenkurs von 56,84 USD** liegt etwa im Feld r = 8 %, g = 3 %. Der Markt
  bewertet Starbucks also ungefaehr so, als verlange er 8 % Rendite bei 3 % Wachstum.

Diese letzte Beobachtung ist analytisch wertvoll: Statt zu fragen "ist die Aktie
billig?", laesst sich fragen "welche Annahmen rechtfertigen den aktuellen Kurs, und
sind die plausibel?".

---

## 8.9 Zusammenfassung der Rechenkette

| Schritt | Formel | Blattzelle |
|---|---|---|
| Eigenkapitalkosten | `rf + Beta x MRP` | `F36` |
| Fremdkapitalkosten n. St. | `Zins x (1 - Steuersatz)` | `F42` |
| WACC | `w_EK x r_EK + w_FK x r_FK` | `F59` |
| Zahlungsstrom | modellabhaengig | `E73/E103/E158/E217/E253` |
| Abzinsungsfaktor | `1 / (1+r)^n` | `E75` |
| Barwert Jahre 1-5 | `SUMME(Zahlung x Faktor)` | `E77` |
| Fortfuehrungswert | `Zahlung(+6) / (r-g) x Faktor(+5)` | `E78` |
| Mitteljahres-Korrektur | `x (1 + r/2)` | `E80` |
| Wert je Aktie | `Gesamtwert / Aktienanzahl` | `E83` |
| **Kaufentscheidung** | **`Wert / Kurs - 1`** | **`E86`** |

## 8.10 Was in Python zu bauen ist

**Input aus den Schritten 1-7:**
- Dividenden, Aktienrueckkaeufe, Veraenderung gezeichnetes Kapital (Schritt 5)
- Operativer Cashflow, Investitions-Cashflow, Kassenveraenderung (Schritt 7)
- Gesamtergebnis je Jahr (Schritt 5)
- Buchwert des Eigenkapitals je Jahr (Schritt 6)
- Zinsaufwand, Steuersatz (Schritt 4 und 5)
- Year-+6-Werte fuer den Fortfuehrungswert

**Input aus den APIs:**
- `FMP.get_profile()` -> `beta`
- `FMP.get_quote()` -> `price`
- `FMP.get_shares_float()` -> `outstandingShares`
- `FMP.get_treasury_rates()` -> risikofreier Zins
- `FMP.get_balance_sheet()` -> `totalDebt`

**Nicht aus APIs verfuegbar:** Marktrisikopraemie und langfristige Wachstumsrate. Beide
sind Setzungen.

**Rechenlogik:**
1. Kapitalkosten berechnen (CAPM, nach-Steuer-Fremdkapitalkosten, WACC)
2. Pruefen: `g < r` -- sonst Abbruch
3. Je Modell den Zahlungsstrom fuer Year +1 bis +6 ableiten
4. Abzinsungsfaktoren fuer Jahre 1-5 berechnen
5. Barwerte der Jahre 1-5 summieren
6. Fortfuehrungswert aus Year +6 berechnen und abzinsen
7. Bei Residual Income: Anfangsbuchwert addieren
8. Bei Modell 5: Schulden abziehen, Finanzanlagen addieren
9. Mitteljahres-Korrektur anwenden
10. Durch Aktienanzahl teilen
11. Modelle gegeneinander pruefen (Kontrolle 1)
12. Mit Boersenkurs vergleichen -> Entscheidung

**Vom Nutzer zu entscheiden:**
- **Welche Modelle implementieren?** Alle fuenf, oder nur eines? Empfehlung: Modell 1
  und 3, weil sie ohne Iteration auskommen und sich gegenseitig pruefen.
- Marktrisikopraemie: welcher Wert?
- Langfristige Wachstumsrate: fest, oder aus Schritt 1 uebernehmen?
- Mitteljahres-Korrektur anwenden? Naeherung `(1+r/2)` oder exakt `(1+r)^0,5`?
- Toleranz fuer Kontrolle 1 (Uebereinstimmung der Modelle)?
- Modell 5 iterativ loesen oder erste Iteration akzeptieren?
- **Schwelle fuer das Kaufsignal:** ab welcher prozentualen Abweichung wird gekauft?
- Verhalten bei `g >= r`: Fehler werfen oder Wachstumsrate begrenzen?
- Klassen- oder Funktionsstruktur, Datenstrukturen, Rueckgabetypen

## 8.11 Abweichungen zwischen Excel und geplanter Implementierung

| # | FSAP-Excel | Implementierung | LLM | Fundstelle |
|---|---|---|---|---|
| 13 | Beta, risikofreier Zins, Marktrisikopraemie sind manuelle Analysteneingaben | Beta und Zins aus FMP; Marktrisikopraemie bleibt Setzung | nein -- Marktgroessen, stehen in keinem Abschluss | [Valuation!F33-F35, L7] |
| 14 | Steuersatz als negative Zahl (FSAP-Vorzeichenkonvention) | positiver Steuersatz, Formel `Zins x (1 - s)` | nein -- reine Vorzeichenkonvention | [Valuation!F41-F42] |
| 15 | Marktwert der Schulden, falls bekannt | Buchwert -- von FSAP als Rueckfalloption genannt | nein -- Marktwert ist keine Abschlussgroesse | [Valuation!L260] |
| 16 | WACC-Gewichte iterativ anpassen (Modell 5) | erste Iteration, oder Modell 5 weglassen | nein -- Rechenverfahren, deterministisch | [Valuation!L267] |
| 17 | Zinsertrag nach Steuern manuell zu setzen (bei SBUX = 0) | aus Schritt 4 ableiten oder 0 setzen | nein -- folgt aus Schritt 4 | [Valuation!E248, L248] |

Die Nummerierung setzt die Tabelle aus Kapitel 7 fort.

**Kapitel 8 enthaelt keine [LLM-LOESBAR]-Stellen.** Der Grund ist systematisch: Die
Bewertung rechnet nur noch mit den Prognosen aus den Schritten 1-7 und mit
*Marktgroessen* (Beta, risikofreier Zins, Marktrisikopraemie, Marktwert der Schulden).
Marktgroessen stehen in keinem Jahresabschluss -- ein LLM koennte sie nur erfinden. Die
Modelle selbst sind feste Formeln, die laut FSAP zum selben Ergebnis fuehren muessen
(Kontrolle 1); dort ist jede Freiheit ein Fehler.

Alle LLM-gesetzten Annahmen liegen also **vor** der Bewertung, in den Schritten 1-6.
Ihre Wirkung erreicht die Bewertung ueber die prognostizierten Abschluesse.
