# 執行結果 — Allocation v2.1.0

## 版本

| 項目 | 值 |
|---|---|
| App version | `2.1.0` |
| Entry | `allocation-web.html` |
| Spec | `docs/06-allocation-engine-spec.md` |

## v2.1 已交付

- 事前檢查：同母料 Excel2.R vs Excel3.H；不一致彈錯誤並停止
- 換算白名單：2.R vs 3.M；相同 1:1；不同查表（預設 M↔YD）；缺規則停止；localStorage
- 輸出 10 欄：含母／子單位、demand、provided、remaining、Y
- 頂部篩選 SO／cutting／母料；匯出套用相同篩選
- 雙 checkbox：整張 SO 需求全 0／單列需求 0
- 預覽 SO 灰白斑馬＋分組色；XLSX 匯出帶底色

## 驗證

```text
python .ai/handoffs/20260718-raw-mat-allocation-v2/verify_allocation.py
→ ALL CHECKS PASSED
```

真實三檔若出現 SHT→YD 等未列換算，會正確阻擋並要求使用者在 Step 2 補規則。
