# Graph Architecture

## Canonical model

Minimal MVP node types may include:

- equipment
- pump
- valve
- vessel
- instrument
- process line

Minimal MVP relationship types may include:

- CONNECTED_TO
- FLOWS_TO
- CONTROLS
- MEASURES
- ASSOCIATED_WITH

Every material relationship should support provenance and confidence.

## Storage abstraction

The application imports `GraphStore`, not a concrete graph database.
