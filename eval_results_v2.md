| Metric | Value |
| --- | --- |
| Notes evaluated | 108 |
| Category accuracy | 96.3% |
| Urgency accuracy | 61.1% |
| Median latency | 1289 ms |
| p95 latency | 6927 ms |
| Failed calls | 0 |

Misclassified:
- `Polizeiabsperrung wg Bombenfund, Strasse voll gesperrt`: expected other, got delay
- `Nachbar verweigert Paketannahme wg Streit mit Empf`: expected other, got refused
- `outer carton torn, contents visible, rcpt refused sign`: expected damaged, got refused
- `Klingel ohne Namen, Empf. nicht erreichbar per Telefon`: expected recipient_absent, got address_issue

Failed: