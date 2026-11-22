| Metric | Value |
| --- | --- |
| Notes evaluated | 42 |
| Category accuracy | 78.6% |
| Urgency accuracy | 69.0% |
| Median latency | 2877 ms |
| p95 latency | 7050 ms |
| Failed calls | 1 |

Misclassified:
- `wet package due to rain, barcode scannable, delivered to porch`: expected damaged, got recipient_absent
- `Techn Defekt Ladebordwand, Verzögerung bei Entladung`: expected delay, got other
- `another pkg leaked on this parcel needs cleanup`: expected other, got damaged
- `Kunde laut Nachbar verstorben, Todesfall gemeldet`: expected other, got address_issue
- `mechanical failure on delivery truck, waiting for tow`: expected delay, got other
- `Pkt nass geworden durch undichte Decke im Hub FFM`: expected other, got damaged
- `severe storm alert safety stop issued by dispatch`: expected other, got delay
- `label torn, street name partially cut off`: expected address_issue, got damaged

Failed:
- `Zoll-Hold: Ursprungszeugnis fehlt im Begleitbeutel`

Urgency errors (expected -> got: count):
- low -> medium: 4
- medium -> low: 3
- medium -> high: 3
- high -> medium: 2

Urgency misclassified:
- `customer out, 2nd attempt failed -> return to hub`: expected low, got medium
- `recipient away on holiday per neighbour, pkg to shop`: expected low, got medium
- `scanner batt dead manually logged deliv time`: expected low, got medium
- `Refused delivery, client insists on inspection before signing.`: expected medium, got low
- `Kunde laut Nachbar verstorben, Todesfall gemeldet`: expected low, got medium
- `Pkt beschädigt kdn will nicht annehmen.`: expected medium, got high
- `Hub Bad Hersfeld Überlastung, Pkt verspätet eingetroffen`: expected medium, got low
- `Empf. refused delivery, wrong order number.`: expected medium, got low
- `Pkt nass geworden durch undichte Decke im Hub FFM`: expected high, got medium
- `Karton offen, Klebeband gelöst, Empf meint Inhalt unvollständig`: expected medium, got high
- `pkg contains live insects depot mgr stopped deliv`: expected high, got medium
- `label torn, street name partially cut off`: expected medium, got high