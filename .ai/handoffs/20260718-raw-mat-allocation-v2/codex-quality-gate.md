# Codex 品質閘門 — v2.2.2

> **Diff 請用：** [`allocation-v2.2.2.diff`](allocation-v2.2.2.diff)  
> **Handoff：** `brief.md` / `plan.md` / `result.md` / `decisions.md`

## 任務

審查 RAW MAT Allocation Engine **v2.2.2** 自 `8d4333f`（v2.1.1）以來的全部變更。

## 必跑驗證

```powershell
cd "D:\0.AI-Agent-Workspace\03_projects\RAW MAT Project"
python .ai/handoffs/20260718-raw-mat-allocation-v2/verify_allocation.py
```

預期：exit 0，`ALL CHECKS PASSED`。

## 12 項 post-check

| # | 檢查 | 通過條件 |
|---|---|---|
| 1 | 語法 | `allocation-web.html` script 可 parse；verifier 可執行 |
| 2 | 欄位 | `descF: 5` = Excel3.F；**未**用 3.J 做 SHT 末碼 |
| 3 | SHT 換算 | 母 SHT + 子≠SHT → size 表；SHT→SHT → 1:1 |
| 4 | 不寫死 | 倍率來自 localStorage `sizeConversionRules`，非引擎 hardcode |
| 5 | Y 群組 | `applyGroupYFlag`：SO+母料全 demand>0 且 provided≥demand |
| 6 | 測試 | verify 含 SHT、缺規則、F 衝突、SO-B 無 Y |
| 7 | Modal | `#errorModalX` 與 OK 皆可 `hideErrorModal()` |
| 8 | i18n | `translations.my` 存在；語系存 `rawmat.allocation.lang` |
| 9 | Manual | `allocation-manual.html` 可開、三語、回主程式連結 |
| 10 | 敏感資訊 | diff 無 `.xlsx`、無 API key、`New data/` 未納入 |
| 11 | 文件 | spec 與程式一致（3.F、Y 群組） |
| 12 | 範圍 | 貪婪配發／10 欄結構未破壞 |

## 重點函式（`allocation-web.html`）

| 函式 | 用途 |
|---|---|
| `extractSizeSuffix` / `normalizeSizeSuffix` | 3.F 末碼解析 |
| `conversionRatio(..., sizeRules, sizeSuffix)` | 單位 + SHT 換算 |
| `runAllocationEngine` | `motherSuffix` from descF |
| `applyGroupYFlag` | Y 欄群組 |
| `renderSizeConversionTable` | 末碼表 UI |
| `showErrorModal` / `hideErrorModal` | 錯誤視窗 |

## 建議 Codex Prompt

```
請依 .ai/handoffs/20260718-raw-mat-allocation-v2/codex-quality-gate.md
審查 allocation-v2.2.2.diff，執行 verify_allocation.py，
回報：缺陷清單、建議 diff（若有）、NEEDS WORK / PASS 判定。
```

## 已知限制

- 末碼 regex：`NNxNNcm`（含 ×、*）
- 緬甸文為功能翻譯，非母語校對
- 工作區相對於 git 有未 commit 變更；**以 allocation-v2.2.2.diff 為準**

## 建議產出

1. 缺陷清單（severity + 檔案:行）
2. 建議 diff（若有）
3. `NEEDS WORK` / `PASS` + 理由
