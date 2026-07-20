# RAW MAT 跨 Agent／跨人員協作治理

- 文件狀態：Draft
- 日期：2026-07-17
- 適用範圍：RAW MAT 專案的規格、實作、測試、交接與核准

# RAW MAT Cross-Agent and Cross-Person Collaboration Governance

- Document status: Draft
- Date: 2026-07-17
- Applies to: Specification, implementation, testing, handoff, and approval for the RAW MAT project

## 1. 治理原則

- 使用一位明確的調度者，不採無負責人的 Agent mesh。
- 每位 Agent 或人員只接收完成其任務所需的最小資料與權限。
- 真實 Excel、Word、PDF 與匯出內容不得放入 prompt、handoff 或版本庫。
- handoff 傳遞摘要、規格、雜湊、決策、diff 與驗證證據，不傳完整對話紀錄。
- 任何 Agent 都不能自行核准業務多筆匹配規則或資料離機。

## 1. Governance principles

- Use one accountable orchestrator; do not use an ownerless agent mesh.
- Give each person or agent only the minimum data and permissions required for the assigned task.
- Real Excel, Word, PDF, and export contents must not enter prompts, handoffs, or version control.
- Handoffs transfer summaries, specifications, hashes, decisions, diffs, and verification evidence rather than full transcripts.
- No agent may independently approve duplicate-match business rules or off-device data processing.

## 2. 責任矩陣

| 角色 | 主要責任 | 不負責 | 必要輸出 |
|---|---|---|---|
| Paul | 與原開發者共同核准 scope、業務規則與結果 | 不需自行撰寫程式或測試 | 核准、拒絕或修改決策 |
| 原開發者 | 說明現況意圖、資料排序假設與技術背景；共同核准 | 不可單方面改變核准規格 | 技術澄清、風險回覆、共同簽核 |
| Hermes | 任務分類、狀態、成本、handoff、提醒與核准點 | 不直接核准業務規則 | task ledger、路由、狀態摘要 |
| Cursor | 依核准規格進行程式與 UI 實作 | 不自行擴 scope 或改第一筆規則 | diff、實作說明、自測證據 |
| Codex | Code review、測試、安全檢查、diff 驗證與品質閘門 | 未授權時不修改程式 | findings、測試、驗收矩陣、result.md |
| 業務 Owner | 必要時定義材料選取、排序、篩選與展開規則 | 不負責技術架構 | 書面業務規則與範例 |

## 2. Responsibility matrix

| Role | Primary responsibility | Not responsible for | Required output |
|---|---|---|---|
| Paul | Jointly approve scope, business rules, and outcomes with the original developer | Writing all code or tests personally | Approve, reject, or modify decisions |
| Original developer | Explain intent, ordering assumptions, and technical context; jointly approve | Unilaterally changing approved rules | Clarifications, risk response, joint sign-off |
| Hermes | Task routing, state, cost, handoff, reminders, and approval gates | Approving business rules directly | Task ledger, routing, status summary |
| Cursor | Implement approved program and UI changes | Expanding scope or changing first-match rules independently | Diff, implementation notes, self-test evidence |
| Codex | Code review, tests, security checks, diff validation, and quality gate | Modifying code without authorization | Findings, tests, acceptance matrix, `result.md` |
| Business owner | Define material selection, sorting, filtering, or expansion when required | Technical architecture | Written business rule and examples |

## 3. 單一事實來源

- `README.md`：專案入口與狀態。
- `docs/01-current-system-spec.md`：目前公開行為契約。
- `docs/02-code-review-and-roadmap.md`：缺陷、風險與優先順序。
- `docs/04-test-and-acceptance.md`：驗收案例與證據要求。
- `.ai/handoffs/<task-id>/decisions.md`：已核准與待決事項。
- `.ai/handoffs/<task-id>/result.md`：實際完成狀態、diff 與測試證據。

衝突時依序以「最新共同核准 decisions → current-system-spec → task plan →實作」為準。任何未記錄的口頭或 Agent 推論不得覆寫核准規格。

## 3. Sources of truth

- `README.md`: Project entry point and status.
- `docs/01-current-system-spec.md`: Current public behavior contract.
- `docs/02-code-review-and-roadmap.md`: Findings, risks, and priorities.
- `docs/04-test-and-acceptance.md`: Acceptance cases and evidence requirements.
- `.ai/handoffs/<task-id>/decisions.md`: Approved and unresolved decisions.
- `.ai/handoffs/<task-id>/result.md`: Actual completion state, diff, and test evidence.

When conflicts exist, use the latest jointly approved decisions, then the current specification, task plan, and implementation in that order. Unrecorded verbal statements or agent inferences must not override an approved specification.

## 4. 標準交辦流程

1. Hermes 或人工建立 `<task-id>` 與 `brief.md`，定義目標、scope、非目標、輸入雜湊、敏感邊界及驗收條件。
2. Codex 或 Cursor 在 `plan.md` 記錄 current-state、方法、變更介面、測試、rollback 與 owner。
3. 任何 outcome-changing 決策寫入 `decisions.md`，包含替代方案與核准者。
4. 實作者只修改核准範圍；輸出 diff、自測與限制。
5. Codex 重新執行驗收，將每項判定為 pass、fail、blocked 或 not tested。
6. Paul 與原開發者共同接受或要求修改；結果寫入 `result.md`。

## 4. Standard handoff flow

1. Hermes or a person creates `<task-id>` and `brief.md` with the goal, scope, non-goals, source hashes, sensitive boundary, and acceptance criteria.
2. Codex or Cursor records the current state, approach, interface changes, tests, rollback, and owners in `plan.md`.
3. Every outcome-changing decision is recorded in `decisions.md` with alternatives and approvers.
4. The implementer changes only the approved scope and returns the diff, self-tests, and limitations.
5. Codex reruns acceptance checks and classifies each item as pass, fail, blocked, or not tested.
6. Paul and the original developer jointly accept or request revisions; the outcome is written to `result.md`.

## 5. 人工核准門檻

| 事件 | 門檻 | 未核准時行為 |
|---|---|---|
| 改變第一筆／全部匹配 | Paul＋原開發者共同核准；必要時業務 Owner | 維持現況並標記警告 |
| 新增遠端服務、上傳或遙測 | 資料邊界書面核准 | 預設拒絕；保持完全本機 |
| 修改真實來源檔或刪除資料 | 明確指定檔案與可回復方案 | 停止並升級人工處理 |
| Phase 2 程式修正 | 核准的 spec、測試與 diff review | 不合併、不發布 |
| 建立遠端 Git／分享 repo | 核准平台、權限與資料清單 | 維持 local-only Git |

## 5. Human approval gates

| Event | Required gate | Behavior without approval |
|---|---|---|
| Change first-match or all-match behavior | Joint approval by Paul and the original developer; business owner if needed | Preserve current behavior and show a warning |
| Add a remote service, upload, or telemetry | Written data-boundary approval | Default deny; remain fully local |
| Modify real source files or delete data | Explicit files and recovery method | Stop and escalate to a human |
| Phase 2 program fixes | Approved specification, tests, and diff review | Do not merge or release |
| Create remote Git or share repository | Approved platform, permissions, and data inventory | Keep Git local only |

## 6. 失敗、重試與復原

- Hard failure：最多重試一次相同、可重入且唯讀的檢查；再次失敗即記錄 blocker，不無限重試。
- Partial result：保留已驗證證據，缺失欄位列入 `result.md`，不得宣告完整通過。
- Agent contradiction：由 Hermes 彙整差異，Paul 與原開發者裁決；不得用多數決覆蓋業務規則。
- 程式回復：以最近核准 Git commit 為 checkpoint；禁止 `git reset --hard` 等不可逆清理。
- 真實資料：永不由 Agent 修改；測試以唯讀來源與 sanitized fixture 執行。

## 6. Failure, retry, and recovery

- Hard failure: Retry the same idempotent read-only check at most once; on a second failure, record a blocker rather than looping.
- Partial result: Preserve verified evidence, list missing items in `result.md`, and do not claim full completion.
- Agent contradiction: Hermes summarizes the disagreement and Paul/original developer decide; majority voting must not override a business rule.
- Program recovery: Use the latest approved Git commit as the checkpoint; destructive cleanup such as `git reset --hard` is prohibited.
- Real data: Agents never modify it; tests use read-only sources and sanitized fixtures.

## 7. 可觀測性與成本

每次 handoff 至少記錄 task ID、agent/person、開始／完成時間、狀態、輸入雜湊、修改檔案、執行檢查、錯誤、核准與下一步。大型 Codex 任務仍遵循既有 token-cost-guard；上下游 Agent 接收摘要與固定欄位，不接收完整 transcript。

## 7. Observability and cost

Each handoff records at least the task ID, agent/person, start/completion time, status, input hashes, changed files, executed checks, errors, approvals, and next step. Large Codex work continues to follow the existing token-cost guard. Downstream agents receive summaries and fixed fields rather than full transcripts.
