# Extraction Architecture

## Output

Extraction produces observable facts and uncertainty, not final plant topology.

## Required concepts

- entity ID
- entity type
- bounding box / geometry
- tag text
- source page
- line candidates
- confidence
- uncertainty records

## Design rule

Extraction may say “these pixels look like a pump” and “this line candidate exists here”. It should not silently assert a final process connection when that decision belongs to topology reconstruction.
