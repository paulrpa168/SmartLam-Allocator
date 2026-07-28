# Result

## Diff Summary

### `allocation-web.html`

- Added same-unit detection for each mother while reading effective 0028 rows.
- Reworked outside-stock `G` calculation:
  - same-unit child exists -> sum only same-unit `J/P`
  - no same-unit child -> fallback to raw `J/P` aggregation without conversion
- Added `outsideFallback` flag on output rows.
- Render `mother stock outside` in red for fallback mothers.
- Bumped `APP_VERSION` to `3.4.1`.

### `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`

- Mirrored the same-unit-first outside `G` logic.
- Added verifier coverage for:
  - same-unit priority
  - fallback without conversion
- Updated the single-child cross-unit expectation to match the new fallback rule.
- Added `outside_fallback_mothers` statistic.

### Docs and metadata

- Updated `docs/07-allocation-v3-spec.md` section 3 for same-unit-first `G`.
- Updated `allocation-manual.html` and `README.md`.
- Updated `config/conversion-rules.v1.json` appVersion to `3.4.1`.

## Verification

Command run:

```powershell
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
```

Result:

- All fixture tests passed
- `New_0722 smoke OK`
- No linter errors on changed files

## Relevant Git Diff Scope

Touched files in working tree:

- `allocation-web.html`
- `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`
- `docs/07-allocation-v3-spec.md`
- `allocation-manual.html`
- `README.md`
- `config/conversion-rules.v1.json`

## Suggested Hermes Next Steps

1. Ask Paul to validate `20260728` visually in the browser, especially `MN090112366`.
2. Decide whether fallback red styling should also propagate to exported XLSX.
3. If needed, add a focused real-data probe for the 3 fallback mothers.
