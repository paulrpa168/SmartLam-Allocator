# 任務簡報：RAW MAT Review 與雙語治理文件

- Task ID：`20260717-raw-mat-review-spec`
- Owner：Codex（文件與品質驗證）；Paul＋原開發者（共同核准）
- Target project：`D:\0.AI-Agent-Workspace\03_projects\RAW MAT Project`
- Workflow：feature-build（Phase 1 documentation/governance only）
- Status：in review

# Task Brief: RAW MAT Review and Bilingual Governance Documentation

- Task ID: `20260717-raw-mat-review-spec`
- Owner: Codex for documentation and quality verification; Paul and the original developer for joint approval
- Target project: `D:\0.AI-Agent-Workspace\03_projects\RAW MAT Project`
- Workflow: feature-build (Phase 1 documentation/governance only)
- Status: in review

## 問題與使用者

此工具由其他員工開發，缺少版本控制、README、可測試規格、Code Review、決策紀錄與跨 Agent／跨人員交辦資料。使用者需要先知道程式目前實際做什麼、有哪些風險、哪些規則尚未核准，以及後續應如何安全改善。

## Problem and users

This tool was developed by another employee and lacked version control, a README, testable specifications, code-review findings, a decision log, and cross-agent/cross-person handoff artifacts. The user first needs an evidence-based description of current behavior, risks, unresolved rules, and a safe improvement path.

## 期望結果

建立可追溯的本機 Git 基礎、雙語專案文件與標準 handoff，且不修改現有 HTML 邏輯。文件必須把現況、風險、驗收基準、owner、核准門檻與後續優先順序寫清楚。

## Desired outcome

Establish traceable local Git governance, bilingual project documents, and a standard handoff without modifying existing HTML logic. The documentation must clearly state current behavior, risks, acceptance baselines, owners, approval gates, and future priorities.

## 範圍

- 初始化本機 Git 並排除真實業務檔。
- 記錄來源檔案雜湊與現況 17/17/26 基準。
- 建立 README、現況規格、Code Review/Roadmap、協作治理、測試驗收。
- 建立 `brief.md`、`plan.md`、`decisions.md`、`result.md`。
- 所有說明繁體中文在前、英文緊接。

## Scope

- Initialize local Git and exclude real business files.
- Record source hashes and the 17/17/26 current baseline.
- Create the README, current specification, code review/roadmap, collaboration governance, and test/acceptance documents.
- Create `brief.md`, `plan.md`, `decisions.md`, and `result.md`.
- Place Traditional Chinese before English in every explanation.

## 非目標

- 不修改 `vlookup-web.html`。
- 不實作 XLSX exporter、不修復缺陷、不建立自動測試程式。
- 不決定多筆匹配業務規則。
- 不建立遠端 repo、內網服務、上傳、遙測或資料庫。

## Non-goals

- Do not modify `vlookup-web.html`.
- Do not implement XLSX export, fix defects, or create automated test code.
- Do not decide the duplicate-match business rule.
- Do not create a remote repository, intranet service, uploads, telemetry, or database.

## 驗收條件

- [x] 真實 XLSX/DOCX/PDF 與生成結果已由 `.gitignore` 排除。
- [x] HTML 基準 SHA-256 與來源雜湊已記錄。
- [x] 所有新文件均為繁中＋英文。
- [x] 現況欄位 mapping、inclusive dates、first-match 假設與 17/17/26 基準已寫入規格。
- [x] Findings 包含 severity、位置、影響與可行修正。
- [x] 跨 Agent／跨人員 owner、handoff、權限、失敗與人工核准已定義。
- [ ] 建立 baseline commit；目前因 Git identity 缺失而 blocked。
- [ ] Paul 與原開發者共同核准 Draft 文件。

## Acceptance criteria

- [x] Real XLSX/DOCX/PDF files and generated exports are excluded by `.gitignore`.
- [x] The HTML baseline SHA-256 and source hashes are recorded.
- [x] Every new document is bilingual in Traditional Chinese and English.
- [x] The current mappings, inclusive dates, first-match assumption, and 17/17/26 baseline are specified.
- [x] Findings include severity, location, impact, and feasible remediation.
- [x] Cross-agent/person owners, handoffs, permissions, failures, and human approvals are defined.
- [ ] Create the baseline commit; currently blocked by missing Git identity.
- [ ] Paul and the original developer jointly approve the Draft documents.

## 敏感邊界

真實資料不得進 Git、handoff、prompt、issue 或對外服務。只允許雜湊、欄位名、資料量、彙總數字與去識別 fixture。任何資料離機行為預設拒絕。

## Sensitive boundary

Real data must not enter Git, handoffs, prompts, issues, or external services. Only hashes, column names, dataset sizes, aggregate counts, and sanitized fixtures are allowed. Off-device data processing is denied by default.

## 輸入與參考

| 檔案 | SHA-256 |
|---|---|
| `1.xlsx` | `3E9D7BF848BA4BEEBADFD958DCCCD13C546B730C6EB36F873C4080AE868E6A96` |
| `2.xlsx` | `101E1C41551537EA4FAADAFBB07F2BCAF944AA11935D294C6832665B50A208BF` |
| `3.xlsx` | `79DB12054A9D9226F89DC6CAFBA1784C7D9F47428A715B280A09694794B550EB` |
| `New Microsoft Word Document.docx` | `6CFB11E95F4F52A0557A75F8A5F23146732EEB32BF5F5CCC92AD3746C94DC640` |
| `New Microsoft Word Document.pdf` | `BC4929C106FCC5E876B6826500A26D2D1A58E3451374C1662C8153CD84EA5F7A` |
| `vlookup-web.html` | `88AAD977615B67C575EBB84881D70208481446A15DBF805CC744BD7B06D798C3` |

## Inputs and references

The table above is the authoritative hash inventory for the Phase 1 review inputs.

## 風險、依賴與待決問題

- 第一筆規則依賴來源排序，待 Paul 與原開發者共同核准。
- 資料是否可送公司內網尚未確認，故保持完全本機。
- Git identity 未設定，baseline commit blocked。
- 真實瀏覽器端到端 UI journey 尚未執行，列為 Phase 2 品質閘門。

## Risks, dependencies, and open questions

- First-match behavior depends on source order and requires joint approval.
- Whether data may be processed on a company intranet is unresolved, so processing remains fully local.
- Git identity is not configured, blocking the baseline commit.
- A real browser end-to-end UI journey has not been executed and remains a Phase 2 quality gate.
