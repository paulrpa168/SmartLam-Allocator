# 20260728 Outside G Same-Unit Handoff

## Objective

Document the completed change to outside mother-stock `G` so Hermes can route the next follow-up.

## Implemented Rule

- For each effective 0028 mother, if any child has `OUn == BUn` (after unit normalization like `Y -> YD`), `G` uses only those same-unit children.
- In that normal path, `G` does not use conversion ratios.
- If a mother has no same-unit child anywhere in effective 0028, `G` falls back to the original `J/P` aggregation without dividing by a conversion ratio.
- Fallback mothers are highlighted with a red `G` cell in the browser result table.

## Files Changed

- `allocation-web.html`
- `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`
- `docs/07-allocation-v3-spec.md`
- `allocation-manual.html`
- `README.md`
- `config/conversion-rules.v1.json`

## Version

- App/config bumped to `v3.4.1`.
