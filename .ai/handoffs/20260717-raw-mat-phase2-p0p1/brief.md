# 任務簡報：Phase 2 P0/P1 明顯錯誤修正

- Task ID：`20260717-raw-mat-phase2-p0p1`
- Owner：Cursor（實作）；Paul（驗收）
- Status：implemented — awaiting local acceptance
- App version：`1.1.0`

## 目標

修正 `vlookup-web.html` 的 P0／P1 明顯缺陷，並產出可追溯版本與 diff。

## 範圍

- RM-001 P0：設定變更後舊結果失效
- RM-002 P1：啟用 Excel（XLSX）匯出
- RM-003 P1：維持第一筆規則，僅顯示多筆匹配警告
- RM-004 P1：空白查找鍵不互相匹配
- RM-005 P1：CSV 公式中和＋UTF-8 BOM
- RM-006 P1：日期欄輸出為可讀日期

## 非目標

- 不改變第一筆／全部展開業務筆數規則
- 不移除 CDN SheetJS（P2）
- 不模組化拆檔（P3）
- 不讀寫或提交真實業務 Excel
