# Status Quo

Stand: 30.08.2026

## 1. Was heute gebaut wurde

### Die erste Node des Core-Graphs

`graphs/core_graph.py` war vorher leer. Jetzt enthaelt die Datei die Node
`initialize_core_state` und den kompilierten Graphen dazu:

```
StateGraph(CoreGraphStateSchema) -> initialize_core_state -> END
```

Die Node bekommt den Core-Graph-State, liest daraus `import_config` und befuellt
`fsap_data`. Sie gibt nichts zurueck, sondern aendert den State direkt.

Ablauf innerhalb der Node:
1. `FMP` und `SEC` werden mit dem Ticker aus `import_config` erzeugt.
2. Bilanz, GuV, Kapitalflussrechnung, Ratios und Enterprise Values werden **je einmal**
   geholt und danach vielfach ausgelesen. Das haelt die Zahl der API-Aufrufe klein.
3. Tabelle 1 aus `fsap_functions.md` (81 Keys) wird ueber ein Mapping-Dictionary
   `FSAP-Key -> (Antwort, Feldname)` befuellt.
4. Tabelle 2 (16 Keys) wird ueber die Konstante `SEC_TAGS` von der SEC geholt.
5. Tabelle 3 (37 Keys) wird berechnet, aus der Konfiguration uebernommen oder auf 0 gesetzt.

### Datenformat: pandas statt Listen

In `pydantic_models/pydantic_models.py` sind die drei Felder von `FSAPSchema` von
`dict[str, list[float]]` auf `dict[str, pd.DataFrame]` umgestellt. Jeder Wert ist eine
Tabelle mit genau zwei Spalten:

| Spalte | Typ | Bedeutung |
|---|---|---|
| `date` | `datetime.date` | Geschaeftsjahresende bzw. Stichtag des Werts |
| `value` | `float` | der Wert selbst |

Sortiert ist immer aeltestes Jahr zuerst. Weil Pydantic pandas nicht von Haus aus kennt,
steht auf `FSAPSchema` jetzt `model_config = ConfigDict(arbitrary_types_allowed=True)`.
Die Hilfsfunktion `empty_frame()` liefert die leere Tabelle mit diesen beiden Spalten.

Jede Quelle behaelt ihr eigenes Datum: FMP nutzt das Feld `date` des Abschlusses, die SEC
das Feld `end`. Die beiden weichen um wenige Tage voneinander ab (z. B. FMP `2024-09-30`
gegen SEC `2024-09-29`); das ist so gewollt und wird nicht angeglichen.

### Zwei neue Felder in `DataImportSchema`

`market_risk_premium` (Standard 0.06) und `long_run_growth_assumption` (Standard 0.03).
Beides sind reine Analystenannahmen ohne Marktdatenquelle, deshalb setzt sie der Nutzer.

### Vorzeichen-Regel

FSAP schreibt Aufwendungen und Abschreibungen in spitzen Klammern, erwartet sie also
negativ. FMP liefert sie uneinheitlich: in der GuV positiv, in der Kapitalflussrechnung
bereits negativ. Deshalb gilt fuer alle Keys in der Konstante `NEGATIVE_KEYS`
`value = -abs(value)`. Das ergibt in beiden Faellen dasselbe richtige Ergebnis, ohne dass
der Code wissen muss, aus welchem Endpunkt ein Wert stammt.

Sonderfall Steuersatz: FSAP nutzt denselben FMP-Wert `effectiveTaxRate` zweimal, aber mit
unterschiedlichem Vorzeichen. `average_tax_rate` (Data!143) steht positiv ueber alle Jahre,
`effective_tax_rate_valuation` (Valuation!F41) steht negativ und nur fuer das neueste Jahr.

### Fehlende Werte

Ein Feld, das eine Antwort nicht enthaelt, wird `None`. Ein XBRL-Tag, das ein Unternehmen
nicht berichtet, fuehrt zu einer leeren Tabelle statt zu einem Abbruch. Die Node laeuft
also auch dann durch, wenn einzelne Posten fehlen.

## 2. Testlauf

Getestet mit `SBUX` gegen die echten APIs. Ergebnis: alle 134 Keys werden geschrieben,
kein Key enthaelt ausschliesslich `None`. Alle 81 FMP-Keys sind mit echten Werten gefuellt.
Die Vorzeichen, die Sortierung und die Einheiten stimmen.

Acht Keys bleiben leer, alle aus bekannten Gruenden (siehe Abschnitte 3 und 4).

## 3. Offen: LLM-Service fuer die Textdaten aus dem 10-K

Vier Parameter liefert keine der beiden APIs, weil sie nirgends als Zahl getaggt sind.
Sie stehen nur im Fliesstext des Geschaeftsberichts (10-K), im Abschnitt MD&A:

| Key in `FSAPSchema.other_data` | FSAP-Zeile | Was fehlt |
|---|---|---|
| `non_recurring_operating_gains_losses` | Data!75 | Einmalige Gewinne oder Verluste des Jahres |
| `number_of_stores_per_segment` | Forecast Development | Anzahl Filialen je Segment |
| `revenue_per_store_per_segment` | Forecast Development | Umsatz je Filiale je Segment |
| `new_stores_per_segment` | Forecast Development | Neueroeffnungen je Segment |

Warum keine API sie liefert: XBRL kennt kein einheitliches Tag fuer "einmaliger Posten" —
jedes Unternehmen beschreibt so etwas in eigenen Worten. Segment- und Filialzahlen sind
Betriebskennzahlen, die gar nicht Teil des Jahresabschlusses sind.

Ein fuenfter Parameter haengt davon ab:
`after_tax_effects_of_nonrecurring_and_unusual_items` (Data!144) berechnet sich aus
`non_recurring_operating_gains_losses` mal (1 minus `statutory_tax_rate`). Solange der
erste Wert fehlt, bleibt auch dieser leer.

Diese fuenf Keys bekommen aktuell `empty_frame()`. Die Liste steht in `core_graph.py` in
der Konstante `LLM_KEYS`.

**Naechster Schritt:** ein neuer Service in `codes/services/`, der ein LLM den 10-K-Text
lesen laesst und die Zahlen je Geschaeftsjahr zurueckgibt. Die Voraussetzung ist da:
`SEC.get_filings("10-K")` liefert zu jedem Bericht die Dokument-URL.

Vorher zu entscheiden:
- Welches Modell und ueber welche Bibliothek es angesprochen wird.
- Wie der lange 10-K-Text auf die relevanten Abschnitte reduziert wird, damit er in den
  Kontext passt.
- Welche Pydantic-Modelle Eingabe und Ausgabe des Service beschreiben.
- Was passiert, wenn das LLM einen Wert nicht findet — leer lassen oder 0 setzen.

## 4. Weitere offene Punkte

### `store_operating_expenses` passt nicht zur FSAP-Vorlage

Der Wert wird als Restgroesse gerechnet: `operatingExpenses` minus D&A minus G&A. Im Test
ergibt das fuer SBUX nur −62 Mio. bis −1,1 Mrd. bei rund 37 Mrd. Umsatz. Offenbar enthaelt
FMPs `operatingExpenses` die Filialkosten gar nicht, die FSAP in dieser Zeile erwartet.
Die Formel ist so umgesetzt wie besprochen, aber die Zahl wird sich nicht mit der Vorlage
decken. Sollte geklaert werden, bevor der FSAP-Sub-Graph damit rechnet.

### `depreciation_expense` bleibt leer

FSAP braucht die Abschreibung ohne die Amortisation. Der Fallback ist eingebaut: zuerst das
Tag `Depreciation`, danach `DepreciationDepletionAndAmortization`. Bei SBUX liefert keines
der beiden etwas, deshalb bleibt die Tabelle leer. Falls hier ein Wert noetig ist, bliebe
als Quelle nur die zusammengefasste D&A-Zahl von FMP.

### Zwei SEC-Tags liefern bei SBUX nichts

`income_from_equity_affiliates_net_of_dividends` und `proceeds_from_stock_option_exercises`.
Beide waren in `fsap_functions.md` als ungeprueft markiert. Ob das Tag falsch ist oder SBUX
den Posten schlicht nicht berichtet, ist noch offen.

### `sec_api.py` ist langsam

`SEC.get_cik()` laedt die SEC-Tickerliste bei **jedem** `get_concept`-Aufruf neu herunter.
Die Node macht 17 solche Aufrufe, also 17 Downloads derselben grossen Datei. Deshalb
dauert ein Durchlauf mehrere Minuten. Die CIK einmal je Instanz zu merken wuerde das
loesen. Nicht umgesetzt, weil ausserhalb des Auftrags.

### Sechstes Geschaeftsjahr

Das Blatt `Data` in FSAP nutzt sechs Geschaeftsjahre, `n_years_history` steht auf 5
(so entschieden). Die Analyse hat damit eine Spalte weniger als die Vorlage.

## 5. Was als Naechstes ansteht

1. Die beiden Datenpunkte oben klaeren (`store_operating_expenses`, `depreciation_expense`).
2. Den LLM-Service aus Abschnitt 3 definieren und bauen.
3. Den FSAP-Sub-Graph (`graphs/sub_graphs/fsap.py`) auf `fsap_data` aufsetzen.

`graphs/sub_graphs/data_import.py` ist unveraendert und wird aktuell nicht genutzt.
