# Status Quo

## Offen: LLM-Service fuer die Textdaten aus dem 10-K

### Worum es geht

Die Node `initialize_core_state` in `graphs/core_graph.py` befuellt alle Parameter des
Modells `FSAPSchema`. Die meisten davon liefern die beiden APIs direkt: `services/fmp_api.py`
fuer Bilanz, GuV, Kapitalflussrechnung und Marktdaten, `services/sec_api.py` fuer die
XBRL-Posten, die FMP nicht kennt.

Vier Parameter liefert aber keine der beiden APIs, weil sie nirgends als Zahl getaggt sind.
Sie stehen ausschliesslich im Fliesstext des Geschaeftsberichts (10-K), im Abschnitt MD&A:

| Key in `FSAPSchema.other_data` | FSAP-Zeile | Was fehlt |
|---|---|---|
| `non_recurring_operating_gains_losses` | Data!75 | Einmalige Gewinne oder Verluste des Jahres |
| `number_of_stores_per_segment` | Forecast Development | Anzahl Filialen je Segment |
| `revenue_per_store_per_segment` | Forecast Development | Umsatz je Filiale je Segment |
| `new_stores_per_segment` | Forecast Development | Neueroeffnungen je Segment |

Warum keine API sie liefert: XBRL kennt kein einheitliches Tag fuer "einmaliger Posten" —
jedes Unternehmen beschreibt so etwas in eigenen Worten. Segment- und Filialzahlen sind
Betriebskennzahlen, die gar nicht Teil des Jahresabschlusses sind.

Zusaetzlich haengt ein fuenfter Parameter davon ab:
`after_tax_effects_of_nonrecurring_and_unusual_items` (Data!144) berechnet sich aus
`non_recurring_operating_gains_losses` mal (1 minus `statutory_tax_rate`). Solange der
erste Wert fehlt, bleibt auch dieser leer.

### Aktueller Zustand

Diese fuenf Keys erhalten in `initialize_core_state` eine leere Tabelle
(`empty_frame()`, also die Spalten `date` und `value` ohne Zeilen). Alle uebrigen Parameter
sind vollstaendig befuellt. Die Liste der betroffenen Keys steht in `core_graph.py` in der
Konstante `LLM_KEYS`.

### Naechster Schritt

Ein neuer Service in `codes/services/`, der ein LLM den 10-K-Text lesen laesst und die
gesuchten Zahlen je Geschaeftsjahr zurueckgibt. Die Voraussetzung dafuer ist schon da:
`SEC.get_filings("10-K")` liefert zu jedem Geschaeftsbericht die URL des Dokuments.

Noch zu entscheiden, bevor der Service gebaut werden kann:
- Welches Modell und ueber welche Bibliothek es angesprochen wird.
- Wie der lange 10-K-Text auf die relevanten Abschnitte reduziert wird, damit er in den
  Kontext passt.
- Welche Pydantic-Modelle Eingabe und Ausgabe des Service beschreiben.
- Was passiert, wenn das LLM einen Wert nicht findet — leer lassen oder 0 setzen.
