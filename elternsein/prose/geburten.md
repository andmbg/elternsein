# Elterngeld: Basisdaten von destatis

Hier führen wir einige Grunddaten ein, die bei destatis verfügbar sind.
"Verfügbar" heißt, die können auf den [Seiten von destatis](www.destatis.de) gefunden werden, oder über die [API](https://www-genesis.destatis.de/genesisWS/rest/2020/) bezogen werden.
Der Code in diesem Projekt tut letzteres, so dass automatisiert stets die neuesten Daten vorliegen.

## Geburten

Die Zahl der Geburten *(destatis: 12612-0100)* dient als Grundlage, ohne die Schwankungen beim Elterngeldbezug nicht zu verstehen sind.
Da die Spanne zwischen Bremen und NRW sehr groß ist und wir uns mehr für Unterschiede in den relativen Geburtenraten zwischen Ländern und über die Jahre hinweg interessieren, skalieren wir die Geburtenrate auf "Geburten je 100.000 Einwohner:innen", ziehen also noch die Einwohnerzahlen heran *(destatis: 12411-0010)*.
Die Tabelle enthält auch das Geschlecht des Kindes, das ignorieren wir hier.
