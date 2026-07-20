# 決策紀錄

# Decision Log

| 日期 | 決策 | 理由 | 未採方案 | Owner／核准狀態 |
|---|---|---|---|---|
| 2026-07-17 | Phase 1 只做文件、handoff 與本機 Git，不修改程式 | 先建立可信規格與治理，避免未核准修正 | 同階段直接修 P0/P1；全面重構 | Paul approved scope |
| 2026-07-17 | 所有說明繁中在前、英文緊接 | 支援本地管理與跨語言交辦 | 只翻標題；英文單語；簡中 | Paul approved |
| 2026-07-17 | 未來 UI 為英文＋繁體中文 | 與文件治理一致 | 英文 only；英文＋簡中 | Paul approved target |
| 2026-07-17 | 部署預設為本機離線 | 符合現況與最小資料暴露 | 立即建內網服務；雙軌部署 | Paul approved default |
| 2026-07-17 | 資料邊界未核准前禁止資料離機 | 是否可送內網尚未確認 | 假設允許上傳 | Blocking default |
| 2026-07-17 | 正式匯出目標為 XLSX＋CSV | XLSX 保留型別；CSV 供交換 | CSV only；XLSX only | Paul approved target |
| 2026-07-17 | 真實檔本機驗收，另建 sanitized fixture | 兼顧真實性、安全與可分享測試 | 只用實檔；只用合成資料 | Paul approved policy |
| 2026-07-17 | 建立本機 Git，不建立遠端 repo | 先取得 diff/rollback，避免資料分享風險 | 直接遠端；不使用 Git | Paul approved |
| 2026-07-17 | Paul 與原開發者共同核准規格與修正 | 結合管理責任與原始技術脈絡 | Paul 單獨；開發者單獨；業務單獨 | Paul approved model |
| 2026-07-17 | 第一筆規則暫時按來源順序記載，不視為正確業務規則 | 使用者尚無法確認；需先保留相容基準 | 直接展開全部；自行指定排序 | Pending joint approval |

## 未決事項

1. 多筆匹配應取來源第一筆、排序／篩選後第一筆，或全部展開？Owner：Paul＋原開發者；在 Phase 2 開發前完成。
2. 三份 Excel 是否允許傳到公司內網服務？Owner：Paul＋資料／資訊安全 Owner；任何 hosted design 前完成。
3. Git identity 的正確名稱與 email 為何？Owner：Paul；baseline commit 前完成。

## Open decisions

1. Should duplicate matches use the source first row, a sorted/filtered first row, or all rows? Owner: Paul and the original developer; due before Phase 2 implementation.
2. May the three workbooks be transmitted to a company intranet service? Owner: Paul and the data/security owner; due before any hosted design.
3. What Git user name and email should be used? Owner: Paul; due before the baseline commit.
