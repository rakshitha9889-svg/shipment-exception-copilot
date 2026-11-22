| Metric | Value |
| --- | --- |
| Notes evaluated | 108 |
| Category accuracy | 99.1% |
| Urgency accuracy | 63.0% |
| Median latency | 1340 ms |
| p95 latency | 4553 ms |
| Failed calls | 0 |

Misclassified:
- `Nachbar verweigert Paketannahme wg Streit mit Empf`: expected other, got refused

Failed:

Urgency errors (expected -> got: count):
- low -> medium: 22
- high -> medium: 10
- medium -> low: 5
- low -> high: 2
- medium -> high: 1

Urgency misclassified:
- `Schneefall Schwarzwald, Schneeketten nötig, erhebliche Verspätung`: expected medium, got low
- `scanner touchscreen kaputt restart needed`: expected low, got medium
- `Consignee refused to pay customs fee of 42.50 EUR, returning to sender`: expected high, got medium
- `Zugverpätung Güterverkehr, Container verspätet im Depot Nürnberg`: expected low, got medium
- `barcode scuffed hand typed tracking nr manually`: expected medium, got low
- `Polizeiabsperrung wg Bombenfund, Strasse voll gesperrt`: expected high, got medium
- `Annahme verw., falscher Name auf Paket.`: expected low, got medium
- `no one home, tried calling rcpt no answer`: expected low, got medium
- `Pkt hat Delle, Empf. wollte Fotos machen vor Unterschrift`: expected low, got medium
- `heavy traffic A9, delivery window missed, reschedule tmrw`: expected medium, got low
- `Empf. refused pkg, return to sender directly.`: expected low, got medium
- `flight delayed into FRA hub, express delivery postponed`: expected low, got high
- `box split open at seam, missing top tape`: expected high, got medium
- `Importabgaben verweigert, Pkt geht zrück an Absender`: expected high, got medium
- `Nachbar verweigert Paketannahme wg Streit mit Empf`: expected low, got medium
- `Empf verweigert, Ware verspätet eingetroffen.`: expected low, got medium
- `Pkt wet & soft, barcode not scannable, kept in van`: expected high, got medium
- `Refused, customer wants refund not replacement.`: expected low, got medium
- `Annahme verweigert laut Empf falscher Inhalt.`: expected low, got medium
- `Sendung gestoppt Zoll FRA, Inhalt nicht eindeutig deklariert`: expected high, got medium
- `Empfänger für 3 Wochen abwesend laut Aushang`: expected medium, got low
- `Empf. verweigert Annahme, Annahmefrist abgelaufen meint er.`: expected low, got medium
- `Klingel reagiert nicht, Empfänger scheinbar nicht im Haus`: expected low, got medium
- `Duty unpaid by rcpt EUR 12.80, Zollstopp aktiv`: expected high, got medium
- `Knd verweigert postident und unterschrift.`: expected low, got medium
- `Clearance exception at HUB FRA: EORI No needed from receiver`: expected high, got medium
- `Hausmeister verweigert Annahme für Mieter top 4.`: expected low, got medium
- `Fr. Weber verweigert Annahme, hat widerrufen.`: expected low, got medium
- `Haustür verschlossen, Empfänger reagiert nicht auf Anruf`: expected low, got medium
- `outer box flattened, item inside broken, refused by customer`: expected high, got medium
- `Pkt beim Zoll wg. Pflanzenschutzbestimmungen festgehalten`: expected high, got medium
- `Klingel ohne Namen, Empf. nicht erreichbar per Telefon`: expected low, got medium
- `Loch im Karton ca 5cm, Ware schaut raus aber intakt`: expected low, got high
- `hub delay in Leipzig, linehaul arrived 3h late`: expected low, got medium
- `recipient unavailable, no safe place to leave pkg`: expected low, got medium
- `Empf. verweigert: nicht mehr benötigt.`: expected low, got medium
- `Strasse umbenannt, alte Bezeichng auf Paket`: expected low, got medium
- `Schlüssel im Tourbus eingeschlossen, ADAC gerufen`: expected medium, got high
- `pkg loose on shelf not linked to manifest list`: expected medium, got low
- `label printed twice duplicate barcode scan error`: expected low, got medium