Label what the courier did or saw last. If the recipient refuses because of customs costs, the label is refused. If the parcel is still held at customs, it's customs_hold.

Damaged beats address: a wet label is damaged, even though the address may be unreadable too.

Anything that slows delivery without a failed attempt (weather, accident, breakdown, missed hub connection) is delay.

Urgency:
- high: every customs hold, and any refusal of customs duties; packaging split open or contents exposed,
  leaking or broken (also when the recipient refused because of it); a parcel so wet its barcode
  cannot be read; hazardous smells or threats to people (for example a police closure for a bomb threat).

- medium: second failed attempt or a long absence; an address that must be clarified or cannot be found
  (including a name missing on the doorbell); a refused cash-on-delivery payment, or a refusal because the
  box is damaged but contents are not exposed; delivery moved to the next day or the address cannot be
  reached at all (tour stopped, snow, capacity, road fully blocked, public event); damage that needs
  repacking or a claim; obstacles at the address (wasps, dogs, gate codes); locked-in keys; a system
  crash or parcels that must be entered manually.

- low: first failed attempt (card left, left with a neighbour, at a pickup point or a chosen place, or no
  safe place); a plain refusal that returns to sender; same-day delays of a few hours (traffic, accidents,
  hub, line-haul, train or flight delays); small or cosmetic damage with contents intact; minor issues the
  courier fixes on the spot (a scanner restart, a duplicate label, a renamed street).


Evaluation – v1 baseline (gemini-3.5-flash-lite)

Metric | Value |
| --- | --- |
| Notes evaluated | 108 |
| Category accuracy | 87.0% |
| Urgency accuracy | 61.1% |
| Median latency | 1292 ms |
| p95 latency | 3804 ms |
| Failed calls | 0 |

Misclassified:
- `scanner touchscreen kaputt restart needed`: expected other, got delay
- `Consignee refused to pay customs fee of 42.50 EUR, returning to sender`: expected refused, got customs_hold
- `Polizeiabsperrung wg Bombenfund, Strasse voll gesperrt`: expected other, got delay
- `Pkt stinkt stark nach Chemie, Depotleiter bittet um Überprüfung`: expected other, got damaged
- `Katze im Laderaum erwischt, Tourverzögerung ca 20 Min`: expected other, got delay
- `Baustelle blockiert Durchfahrt, kein Reinkommen möglich`: expected delay, got address_issue
- `Nachbar verweigert Paketannahme wg Streit mit Empf`: expected other, got recipient_absent
- `outer carton torn, contents visible, rcpt refused sign`: expected damaged, got refused
- `outer box flattened, item inside broken, refused by customer`: expected refused, got damaged
- `Customs inspect: Pkt Beschädigt, Wareninhalt vom Zoll geprüft`: expected customs_hold, got damaged
- `gate code changed need clearance from dispatch`: expected other, got address_issue
- `Klingel ohne Namen, Empf. nicht erreichbar per Telefon`: expected recipient_absent, got address_issue
- `Stadtfest im Zentrum, gesamte Innenstadt gesperrt`: expected delay, got address_issue
- `Schlüssel im Tourbus eingeschlossen, ADAC gerufen`: expected other, got delay





v2 

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





- Name missing on the doorbell → address_issue (the courier cannot identify the unit).
- v3 label fixes: "Polizeiabsperrung" other→delay (rule 3), "outer carton torn… refused" damaged→refused (rule 1),
  "Klingel ohne Namen" recipient_absent→address_issue (doorbell rule). Fixed because they contradicted the written
  rules, not because the model disagreed.


## Quick start
```bash
cp .env.example .env   # add your LLM API key
docker compose up --build -d
docker compose exec api python -m scripts.load_rules
open http://localhost:8000/docs
```





Version	  Change	                                    Category	Urgency	      p95 latency
v1	      baseline prompt	                            87.0%	    61.1%	        3.8 s
v2	      + category definitions and tie-break rules	96.3%	    61.1%	        6.9 s
v3	      + 3 inconsistent labels fixed	              99.1%	    63.0%	        4.6 s
v4	      + concrete urgency rubric	                  98.1%	    87.0%	        3.2 s


Held-out test set (42 notes, labeled independently, prompt not tuned on it):
Category 78.6% · Urgency 69.0% · 1 failed call (rate limit/timeout)

Error analysis: about 5 of 8 category errors were inconsistencies in my own labels
(e.g. weather notes labeled "other" although my guideline says "delay"); the model
followed the written rules more consistently than I did. I also found a conflict
between my labeling guide (breakdown → delay) and the prompt (vehicle problem → other),
and a category gap (deceased recipient). Next step would be double-labeling a sample
and resolving the guideline conflict before a fresh test set.