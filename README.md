[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Home Assistant PromQL

This is a custom component for quering Prometheus values with Home Assistant.

## Installation

1. Install this Integration as a [HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories) or just copy the content of the custom_components folder.
2. Add a query by navigating to Configuration -> Integrations -> Add Integration and search for *PromQL*

## Sensors

The integration will create a seperate sensor for each combination of labels. 

You can also use complex PromQL queries like e.g. 
```
100 - (avg by (instance) (irate(node_cpu_seconds_total{job="node",mode="idle"}[5m])) * 100)
```
