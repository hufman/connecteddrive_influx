# ConnectedDrive InfluxDB Importer

Imports car status from BMW/Mini ConnectedDrive

Inspired by https://hawar.no/2020/08/grafana-bmw-and-mini/
except using InfluxDB instead of MySQL. This adds time-series features
such as showing mileage over time, calculating efficiency over time,
drawing a trace on a map over time, and others.

## InfluxDB Setup

```
CREATE DATABASE connecteddrive
ALTER RETENTION POLICY "default" ON "connecteddrive" DURATION 26w
CREATE RETENTION POLICY "history" ON "connecteddrive" DURATION inf REPLICATION 1
CREATE CONTINUOUS QUERY "history_archive" ON "connecteddrive" BEGIN SELECT mean(mileage), mean(lat), mean(lon) INTO history.history FROM status GROUP BY time(5m), * END
```
