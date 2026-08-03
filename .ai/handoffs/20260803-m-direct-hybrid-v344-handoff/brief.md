# 20260803 M 直接需求混合規則 Handoff（v3.4.4）

**日期 / Date:** 2026-08-03  
**版本 / Version:** 3.4.4  
**狀態 / Status:** Cursor 實作完成；待 Hermes 品質閘門／排程後續  
**父版本 / Parent:** `84f5b58`（v3.4.3）  
**工作樹 / Working tree:** 未 commit（diff 已產出）

## Objective

實作「M 子料直接需求」混合規則，並在 Step3 結果區表格上方提供公式說明＋匯出操作列；Excel／CSV／複製匯出含公式前言列。

## Locked business rules

| 條件（逐子料列） | 行為 |
|---|---|
| `L=0` 且 `M>0` | 母池／H 不抵 M；`Q=0`；`R=P−M` |
| `L>0` | 維持 Rule D：母池蓋 `N=L+M`；不足進 Q；`R=P−Q` |
| `L=0` 且 `M=0` | `Q=0`；`R=P` |

**Y 合貼備料齊套：** 同 `(SO+C+Segment)`；只檢查非 MH04 且 `L>0` 是否 `母蓋L+Q ≥ L`；通過整組標 Y；全無 L>0 不標 Y。

**不做：** 不改 G pick-once、ambiguous confirm、依序處理流程。

## Files changed（in diff）

- `allocation-web.html`
- `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`
- `docs/07-allocation-v3-spec.md`
- `README.md`
- `allocation-manual.html`
- `config/conversion-rules.v1.json`
- `docs/03-collaboration-governance.md`（SoT 指向 `07-spec`）

## Supporting artifacts（not in git diff）

- `.ai/handoffs/20260731-mn090157252-formula-review/MN090157252_formula_review.xlsx`
- `.ai/handoffs/20260731-mn090157252-formula-review/MN090157252_formula_review_v3.4.4.xlsx`
- `.ai/handoffs/20260731-mn090157252-formula-review/regen_formula_review_v344.py`

## Package contents

| 檔案 | 用途 |
|---|---|
| `brief.md` | 本簡報 |
| `decisions.md` | 已定決策 |
| `result.md` | 實作結果與驗證 |
| `hermes-next.md` | Hermes 後續安排建議 |
| `allocation-v3.4.4.diff` | UTF-8 文字 patch（對 HEAD） |
