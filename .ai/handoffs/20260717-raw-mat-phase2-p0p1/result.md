# 執行結果

## 版本

| 項目 | 值 |
|---|---|
| App version | `1.1.0` |
| Previous SHA-256 | `88AAD977615B67C575EBB84881D70208481446A15DBF805CC744BD7B06D798C3` |
| New SHA-256 | `6838C64583F11AF0A4E6173B0C99A99A219FBA3DC06ECC4D28B8B3C367BCC9D3` |
| Diff file | `vlookup-web.v1.1.0.diff`（約 526 行） |
| Baseline copy | `vlookup-web.baseline.html` |

## 已修正

- **RM-001 P0**：`markResultDirty()`；查找／回傳／輸出／大小寫／第一筆／日期變更會清除結果並停用匯出。
- **RM-002 P1**：`downloadXlsx()` 已接線；結果產生後 Excel 按鈕可按。
- **RM-003 P1（警告）**：多筆匹配時顯示警告；仍取來源第一筆。
- **RM-004 P1**：空白鍵不進索引、不互相匹配。
- **RM-005 P1**：CSV 公式中和＋BOM。
- **RM-006 P1**：選定日期欄輸出可讀日期（例：`46204` → `2026-07-01`）。

## 驗證

```text
node .ai/handoffs/20260717-raw-mat-phase2-p0p1/verify-p0p1.mjs
→ verify-p0p1: OK
```

尚未在本機以真實 `1/2/3.xlsx` 做瀏覽器端到端驗收（資料邊界：真實檔僅本機人工驗證）。

## 建議人工驗收

1. 載入三檔 → 依基準欄位產生 2026-07 結果 → 確認日期可讀、CSV／Excel 可下載。
2. 返回步驟 2 改任一查找設定 → 應提示需重新產生，且匯出按鈕停用。
3. 確認結果訊息若有多筆匹配會顯示警告。
