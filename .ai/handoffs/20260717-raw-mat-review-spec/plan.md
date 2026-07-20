# 執行計畫：RAW MAT Phase 1 文件與治理

# Implementation Plan: RAW MAT Phase 1 Documentation and Governance

## 現況發現

- 專案只有單一 2,021 行 HTML、三份真實 Excel 與 Word/PDF 操作說明。
- 專案開始時沒有 Git、README、測試、規格、handoff 或決策紀錄。
- 現況查找基準可重現 17 筆輸出、17/17 匹配、26 筆日期排除。
- RM-001 stale export 是 P0；RM-002 至 RM-006 是 P1；RM-003 同時需要業務決策。

## Current-state findings

- The project contains one 2,021-line HTML file, three real workbooks, and Word/PDF instructions.
- At task start it had no Git, README, tests, specification, handoff, or decision log.
- The current lookup baseline reproduces 17 output rows, 17/17 matches, and 26 date-filtered rows.
- RM-001 stale export is P0; RM-002 through RM-006 are P1; RM-003 also requires a business decision.

## 執行方法

1. 建立 `.gitignore`，排除真實業務檔與生成物。
2. 初始化本機 Git；使用既有 Git identity 建立 baseline commit，若缺失則 stage 並記錄 blocker。
3. 建立雙語 README 與四份 `docs/` 文件。
4. 建立 task-specific handoff 與 decision/result 記錄。
5. 驗證 HTML 雜湊未變、真實檔案未被追蹤、文件無空白 placeholder、所有 acceptance claims 有證據。

## Proposed approach

1. Add `.gitignore` rules for real business files and generated artifacts.
2. Initialize local Git and create a baseline commit using an existing identity; otherwise stage and record the blocker.
3. Create the bilingual README and four documents under `docs/`.
4. Create the task-specific handoff and decision/result records.
5. Verify that the HTML hash is unchanged, real files are untracked, no placeholders remain, and acceptance claims have evidence.

## 角色與責任

| 角色 | 責任 | 必要輸出 |
|---|---|---|
| Codex | 審查、文件、證據驗證、Git staging | README、docs、handoff、status/evidence |
| Paul | 共同核准規格與後續 scope | approve/reject/revise |
| 原開發者 | 說明意圖與共同核准 | clarification、sign-off |
| Hermes | 後續 task routing 與提醒 | task ledger、approval reminder |
| Cursor | Phase 2 核准後實作 | diff、self-test evidence |

## Roles and responsibilities

| Role | Responsibility | Required output |
|---|---|---|
| Codex | Review, documentation, evidence verification, Git staging | README, docs, handoff, status/evidence |
| Paul | Jointly approve the specification and later scope | Approve, reject, or revise |
| Original developer | Explain intent and jointly approve | Clarifications and sign-off |
| Hermes | Route later tasks and remind approvers | Task ledger and approval reminders |
| Cursor | Implement approved Phase 2 changes | Diff and self-test evidence |

## 預期變更檔案與介面

- 新增 `.gitignore`、`README.md`、`docs/*.md`、`.ai/handoffs/20260717-raw-mat-review-spec/*.md`。
- 不修改 `vlookup-web.html`，不改變任何 runtime interface。
- 文件將現況 input/output contract 與未來 XLSX＋CSV、英文＋繁中目標分開記錄。

## Files and interfaces expected to change

- Add `.gitignore`, `README.md`, `docs/*.md`, and `.ai/handoffs/20260717-raw-mat-review-spec/*.md`.
- Do not modify `vlookup-web.html` or any runtime interface.
- Documentation separates current input/output behavior from the future XLSX/CSV and English/Traditional Chinese target.

## 測試與驗證

- 比對執行前後 HTML SHA-256。
- `git check-ignore` 驗證五份真實業務來源檔均被排除。
- `git status --short --ignored` 確認只 stage 程式、`.gitignore` 與雙語文件。
- 搜尋 `TODO`、`TBD`、空白模板欄位與敏感資料列。
- 重跑 workbook 結構與 17/17/26 基準分析。
- 對每項 acceptance criterion 記錄 pass、blocked 或 not tested。

## Test and verification plan

- Compare the HTML SHA-256 before and after implementation.
- Use `git check-ignore` to verify exclusion of the five real business source files.
- Use `git status --short --ignored` to confirm that only the program, `.gitignore`, and bilingual documents are staged.
- Search for `TODO`, `TBD`, blank template fields, and sensitive row data.
- Rerun workbook structure and 17/17/26 baseline analysis.
- Record pass, blocked, or not-tested status for every acceptance criterion.

## 失敗、回復與升級

- Git identity 缺失：不代造，保留 staged 狀態，升級給 Paul 設定後再 commit。
- 文件驗證失敗：只修文件，重跑檢查；不碰 HTML。
- HTML hash 改變：停止、檢查 diff，回復本次未授權變更後再繼續。
- 真實檔案被 stage：立即取消該檔案 staging 並修正 `.gitignore`。
- 業務規則不確定：維持 current-state 描述並標記 blocking approval。

## Failure, rollback, and escalation behavior

- Missing Git identity: Do not invent one; retain staged state and escalate to Paul for configuration before committing.
- Documentation verification failure: Fix documentation only and rerun checks; do not touch the HTML.
- Changed HTML hash: Stop, inspect the diff, and remove any unauthorized task change before continuing.
- Real file staged: Unstage it immediately and correct `.gitignore`.
- Uncertain business rule: Preserve the current-state description and mark a blocking approval.
