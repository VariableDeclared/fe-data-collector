# FE Data Collector

A tool to scrape your nodes!

## Quickstart

Collect your nodes and dump them to a JSON list:

```
$ juju machines --format json | jq -r '[.machines[]."ip-addresses"[]]' > machines.json
$ fe-data-collector --hosts machines.json
```

