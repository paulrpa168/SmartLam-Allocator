# Cursor follow-up — Codex review fixes（v3.4.4）

**日期：** 2026-08-03  
**對應審查：** `review-hermes-codex.md`（Verdict: NEEDS WORK）

## 已修

| # | 嚴重度 | 項目 | 處置 |
|---|---|---|---|
| 1 | Medium | `docs/07` L145 `appVersion` 範例仍為 `3.4.3` | 已改為 **`3.4.4`** |
| 2 | Low | export preamble 缺 `formulaHybridSummary` | `exportPreambleMatrix()` 第一列改為混合規則摘要（CSV／XLSX／Copy 共用） |
| — | — | §16 匯出說明 | 已寫明含混合規則摘要列 |

## 建議 Hermes 狀態

修正後可改判 **APPROVE**（核心規則原先已通過；本輪僅文件／匯出一致性）。

## 仍待 Paul

1. 人工 UI／0730 錨點（`MN090157252` / `MA020165546` / SO `10172127`）
2. 指示後 atomic commit：`feat: hybrid M-direct + formula toolbar v3.4.4`
