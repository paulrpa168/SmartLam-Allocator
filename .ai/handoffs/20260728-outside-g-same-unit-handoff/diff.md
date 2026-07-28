# Diff Notes

This handoff does not include a committed patch. Use this command to reproduce the exact workspace diff for the completed change:

```powershell
git diff -- "allocation-web.html" "config/conversion-rules.v1.json" "README.md" "allocation-manual.html" "docs/07-allocation-v3-spec.md" ".ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py"
```

## High-signal changes

- `allocation-web.html`
  - `G` computation no longer converts outside pairs back to mother units.
  - Same-unit children are preferred; fallback mothers are flagged for red styling.
  - Result rendering colors the `mother stock outside` cell red when fallback was used.

- `verify_allocation_v3.py`
  - Same-unit-first outside logic mirrors the browser engine.
  - Added regression tests for same-unit priority and no-conversion fallback.

- Docs
  - Spec/manual/README updated to describe `v3.4.1` and the red fallback `G`.
