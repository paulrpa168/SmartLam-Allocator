# Decisions

## Confirmed Business Logic

1. `G` is treated as a mother-material outside-stock field.
2. When a mother has at least one same-unit child in effective 0028, only those same-unit children contribute `J/P` to `G`.
3. No conversion ratio is applied in the same-unit path.
4. If a mother has no same-unit child at all, `G` falls back to the original `J/P` aggregation without conversion.
5. Fallback results are visually marked by rendering the `G` column in red.

## Data Validation Used

Using `20260728/Copy of 0028(3).xlsx`:

- Effective mothers: `499`
- Mothers with at least one same-unit child: `496`
- Mothers with no same-unit child: `3`

Fallback mothers identified during planning:

- `MC030005892`
- `MC040000928`
- `MC030007974`

## Follow-up Note

The red highlight is currently applied in the HTML preview table. If Hermes wants export-level styling in XLSX, that would be a separate enhancement.
