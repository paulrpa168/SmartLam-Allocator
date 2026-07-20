# 執行計畫

1. 以 SHA-256 `88AAD977...` 建立 baseline 複本。
2. 實作 `markResultDirty()` 並掛到所有影響結果的控制項。
3. 索引／查找略過空白鍵；結果訊息顯示空白鍵與多筆匹配警告。
4. 對選定日期欄做 Excel 序號 → 可讀日期轉換。
5. CSV：公式字首中和＋UTF-8 BOM。
6. 以本機 ZIP/OOXML 實作 XLSX 匯出（不依賴 CDN）。
7. 產出 `vlookup-web.v1.1.0.diff` 與驗證腳本。
