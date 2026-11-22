| Metric | Value |
| --- | --- |
| Notes evaluated | 108 |
| Category accuracy | 98.1% |
| Urgency accuracy | 87.0% |
| Median latency | 1289 ms |
| p95 latency | 3150 ms |
| Failed calls | 0 |

Misclassified:
- `Nachbar verweigert Paketannahme wg Streit mit Empf`: expected other, got refused
- `Karton zusammengedrückt, Empf nicht da, Benachrichtigt trotz Schaden`: expected damaged, got recipient_absent

Failed:

Urgency errors (expected -> got: count):
- medium -> high: 5
- medium -> low: 4
- low -> medium: 3
- high -> medium: 1
- low -> high: 1

Urgency misclassified:
- `scanner touchscreen kaputt restart needed`: expected low, got medium
- `Nass vom Regen, Etikett weich, barcode kaum lesbar`: expected medium, got high
- `Polizeiabsperrung wg Bombenfund, Strasse voll gesperrt`: expected high, got medium
- `Umreifungsband gerissen, Pkt öffnet sich fast`: expected medium, got high
- `Pkt hat Delle, Empf. wollte Fotos machen vor Unterschrift`: expected low, got medium
- `heavy traffic A9, delivery window missed, reschedule tmrw`: expected medium, got low
- `Schaumstoff ragt aus Verpackung, Folie zerrissen`: expected medium, got high
- `Karton zusammengedrückt, Empf nicht da, Benachrichtigt trotz Schaden`: expected medium, got low
- `pkg arrived late from sorting center, delivery postponed tmrw`: expected medium, got low
- `Empfängerin verweigert, Karton kaputt.`: expected medium, got high
- `Rcpt verweigert Annahme, pkg crushed.`: expected medium, got high
- `Zeitüberschreitung Fahrzeit, Restpakete gehen zurück ins Depot`: expected medium, got low
- `Loch im Karton ca 5cm, Ware schaut raus aber intakt`: expected low, got high
- `box open on side, Klebeband nachgeklebt im ZSP, pkg intact now`: expected low, got medium