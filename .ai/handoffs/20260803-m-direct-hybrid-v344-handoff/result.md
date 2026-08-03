# Result — M 直接需求混合規則 v3.4.4

**日期 / Date:** 2026-08-03  
**結論 / Conclusion:** Cursor 實作完成；Python 單元測試 20 passed；人工瀏覽器六步／實際 xlsx 開啟仍待 Paul／Hermes 閘門。

## 1. 實作摘要

### Engine（JS + Python mirror）

- 混合規則：`L==0 && M>0` → 不從母池蓋 M、`Q=0`、`R=P−M`；`L>0` → Rule D 蓋 `N=L+M`、`R=P−Q`。
- Y：同組只檢查非 MH04 且 `L>0` 的 `母蓋L+Q≥L`；無 L>0 不標 Y。

### UI

- Step3：`resultToolbar`（Excel／CSV／複製＋公式說明摺疊）在表格上方。
- `formulaPanel`：代號＋名稱＋定案公式；混合規則摘要；zh／en／my。
- 匯出／複製：前置公式說明列，再接篩選後資料。
- 底部匯出鈕保留，共用同一 handler。

### Docs / version

- `docs/07-allocation-v3-spec.md` §4／§7／§16 → 3.4.4
- `README.md`、`allocation-manual.html`、`config/conversion-rules.v1.json` → 3.4.4
- `docs/03-collaboration-governance.md`：SoT 改指向 `07-allocation-v3-spec.md`

### Formula review Excel

- `.ai/handoffs/20260731-mn090157252-formula-review/MN090157252_formula_review.xlsx`
- `.ai/handoffs/20260731-mn090157252-formula-review/MN090157252_formula_review_v3.4.4.xlsx`
- 黃列＝定案公式；綠列＝`MA020165546`；資料＝0730 引擎輸出

## 2. Diff

- 檔案：`allocation-v3.4.4.diff`（對 `HEAD` / `84f5b58`）
- 約 **7 files, +448 / −98**（含 governance 兩行 SoT）

含：

```
allocation-web.html
.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
docs/07-allocation-v3-spec.md
README.md
allocation-manual.html
config/conversion-rules.v1.json
docs/03-collaboration-governance.md
```

## 3. 自動驗證

```powershell
python -m pytest .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py -q --tb=line
```

結果：**20 passed**（含 hybrid / Y / pure-M 不燒母池等回歸）。

0730 錨點抽樣（`MA020165546`）：

| SO | L | M | Q | R 行為 | Y |
|---|---:|---:|---:|---|---|
| 10172127 等早期 | 0 | >0 | 0 | 依 M 遞減 | 空白 |

## 4. 品質閘門狀態

| 項 | 狀態 |
|---|---|
| Python fixtures | PASS（20） |
| Spec / version 對齊 | PASS（3.4.4） |
| 瀏覽器六步互動 | NOT TESTED（人工） |
| 匯出 xlsx 實際開啟 | NOT TESTED（人工） |
| Codex 品質審查 | PENDING（Hermes 調度） |
| git commit | PENDING（需 Paul 指示） |

## 5. Artifact hashes（SHA256 前 16）

| Hash prefix | Path |
|---|---|
| `265b2593ca0e7c23` | `allocation-web.html` |
| `ae397e784be27970` | `verify_allocation_v3.py` |
| `0190ef69c7a93e14` | `docs/07-allocation-v3-spec.md` |
| `d041e556042a1d6d` | `README.md` |
| `15b108bb31504bfe` | `allocation-manual.html` |
| `1103c0f9aa929128` | `config/conversion-rules.v1.json` |
| `90284b6599746386` | `docs/03-collaboration-governance.md` |
| `959b534bebbe4112` | `MN090157252_formula_review_v3.4.4.xlsx` |
| `9a44422bce21d7d4` | `MN090157252_formula_review.xlsx` |

## 6. 建議人工驗收

1. 開 `allocation-web.html` → 載入 `0730/` → Run。
2. 篩母料 `MN090157252`、子料 `MA020165546`、SO `10172127`。
3. 確認表格上方可點匯出／公式說明；`Q=0`、`R` 扣 M、Y 空白。
4. 匯出 Excel：頂部有代號／名稱／公式列後接資料。
