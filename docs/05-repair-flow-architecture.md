# RAW MAT 修正流程與架構圖

# RAW MAT Repair Flow and Architecture Diagrams

本文件將審查、修正優先序、角色、品質閘門與資料邊界轉成可快速閱讀的圖示。繁體中文在前，英文緊接；詳細規則仍以 docs/01 至 docs/04 為準。

This document turns the review, repair priorities, roles, quality gates, and data boundary into quick-reference diagrams. Traditional Chinese appears first, followed by English; docs/01 through docs/04 remain authoritative.

## 圖例 / Legend

| 圖示 | 中文 | English |
|---|---|---|
| ✅ | 已完成／通過 | Completed / passed |
| ⏳ | 等待人工決策 | Awaiting human decision |
| 🟥 | P0，最優先 | P0, highest priority |
| 🟧 | P1，正確性與安全 | P1, correctness and security |
| 🟦 | P2，可維護性 | P2, maintainability |
| 🔒 | 資料或發布閘門 | Data or release gate |
| 🔁 | 修正後重測 | Retest after repair |

目前位置：✅ 階段一文件完成；⏳ 等待 Paul 與原開發者共同核准；程式仍為 NEEDS WORK。

Current position: ✅ Phase 1 documentation is complete; ⏳ joint approval by Paul and the original developer is pending; the application remains NEEDS WORK.

## 1. 修正生命週期 / Repair lifecycle

```mermaid
flowchart LR
    A["✅ ① 現況基準<br/>Current baseline<br/>17 / 17 / 17 / 26"]
    B{"⏳ ② 共同核准規格<br/>Joint specification approval"}
    C["🟥 ③ P0 RM-001<br/>舊結果失效<br/>Invalidate stale results"]
    D["🟧 ④ P1 RM-002～006<br/>正確性與安全<br/>Correctness and security"]
    E["🧪 ⑤ 自動化＋UI 驗收<br/>Automated and UI acceptance"]
    F{"🔎 ⑥ Codex 品質閘門<br/>Codex quality gate"}
    G{"⏳ ⑦ 共同驗收<br/>Joint acceptance"}
    H["✅ ⑧ 本機離線發布<br/>Local offline release"]

    A --> B
    B -- "通過 / Approved" --> C
    B -- "修訂 / Revise" --> A
    C --> D --> E --> F
    F -- "Fail" --> C
    F -- "Pass" --> G
    G -- "Changes" --> C
    G -- "Accepted" --> H

    R{"⏳ 第一筆匹配規則<br/>First-match rule"}
    S{"🔒 資料邊界<br/>Data boundary"}
    R -. "未核准不得改變筆數<br/>No cardinality change" .-> D
    S -. "未核准不得遠端化<br/>No remote processing" .-> H

    classDef done fill:#dcfce7,stroke:#15803d,color:#14532d;
    classDef p0 fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d;
    classDef p1 fill:#ffedd5,stroke:#c2410c,color:#7c2d12;
    classDef gate fill:#fef3c7,stroke:#a16207,color:#713f12;
    classDef test fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a;
    class A,H done;
    class C p0;
    class D p1;
    class B,G,R,S gate;
    class E,F test;
```

中文重點：未共同核准，不改業務筆數規則；未通過品質閘門，不發布。

English key point: no business-cardinality change without joint approval, and no release without passing the quality gate.

## 2. 程式資料流與 P0 控制點 / Program data flow and P0 control point

```mermaid
flowchart LR
    X1["📄 1.xlsx<br/>schedule"]
    DF["📅 cutting 篩選<br/>Inclusive date filter"]
    X2["📄 2.xlsx<br/>COIS"]
    J1["🔗 so = SD Document"]
    X3["📄 3.xlsx<br/>ZRMm"]
    J2["🔗 Material = Material"]
    W["⚠️ 空白鍵／重複鍵<br/>Blank and duplicate keys"]
    R["📊 七欄結果<br/>Seven-column result"]
    E1["📗 XLSX<br/>Readable dates"]
    E2["📄 CSV<br/>BOM＋formula safety"]

    X1 --> DF --> J1
    X2 --> J1
    J1 --> J2
    X3 --> J2
    J1 --> W
    J2 --> W
    W --> R
    J2 --> R
    R --> E1
    R --> E2

    CFG["⚙️ 查找／回傳／輸出／大小寫／第一筆設定<br/>Lookup, return, output, case, first-match settings"]
    DIRTY["🟥 markResultDirty()<br/>清除舊結果＋停用匯出<br/>Clear stale results and disable exports"]
    CFG -- "任何變更 / Any change" --> DIRTY
    DIRTY -. "必須重跑 / Rebuild required" .-> DF

    classDef source fill:#f8fafc,stroke:#475569,color:#0f172a;
    classDef process fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a;
    classDef warning fill:#fef3c7,stroke:#a16207,color:#713f12;
    classDef output fill:#dcfce7,stroke:#15803d,color:#14532d;
    classDef p0 fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d;
    class X1,X2,X3 source;
    class DF,J1,J2,CFG process;
    class W warning;
    class R,E1,E2 output;
    class DIRTY p0;
```

中文重點：任何影響結果的設定一變動，舊結果與 XLSX／CSV／複製功能必須立即失效。

English key point: any result-affecting setting change must immediately invalidate the old result and XLSX/CSV/copy actions.

## 3. 跨 Agent／跨人員泳道 / Cross-agent and cross-person swimlane

```mermaid
flowchart TB
    subgraph AP["👥 Paul＋原開發者 / Joint approvers"]
        AP1["核准規格與非目標<br/>Approve specification and non-goals"]
        AP2["決定第一筆／排序／全部展開<br/>Decide first row, sort/filter, or expansion"]
        AP3["共同接受或要求修正<br/>Jointly accept or request changes"]
    end

    subgraph HE["🧭 Hermes / Orchestration"]
        H1["建立 task ID、brief 與核准點<br/>Create task ID, brief, and gates"]
        H2["追蹤狀態、成本、blocker、下一位 owner<br/>Track status, cost, blockers, next owner"]
    end

    subgraph CU["🛠️ Cursor / Implementation"]
        C1["依核准範圍實作 P0／P1<br/>Implement approved P0/P1 scope"]
        C2["交付 diff、自測與限制<br/>Deliver diff, self-tests, limitations"]
    end

    subgraph CO["🔎 Codex / Quality verification"]
        Q1["審查 diff、安全與回歸風險<br/>Review diff, security, regression risk"]
        Q2["執行 fixtures、真實基準、UI 驗收<br/>Run fixtures, real baseline, UI acceptance"]
        Q3{"品質閘門<br/>Quality gate"}
    end

    H1 --> AP1 --> AP2 --> C1 --> C2 --> Q1 --> Q2 --> Q3
    Q3 -- "Fail" --> H2
    H2 -- "修正任務 / Repair task" --> C1
    Q3 -- "Pass" --> AP3
    AP3 -- "Changes" --> H2
    AP3 -- "Accepted" --> REL["✅ 本機發布＋result.md<br/>Local release and result.md"]
```

中文重點：任何 Agent 都不得自行決定多筆匹配規則；每次交辦需保留 brief、plan、decisions、result、diff 與測試證據。

English key point: no agent may decide multi-match behavior independently; every handoff retains the brief, plan, decisions, result, diff, and test evidence.

## 4. 優先順序與相依關係 / Priority and dependency map

```mermaid
flowchart TD
    P0["🟥 P0<br/>RM-001 舊結果失效<br/>Stale-result invalidation"]
    P1A["🟧 P1-A<br/>RM-002 XLSX＋CSV<br/>XLSX and CSV"]
    P1B["🟧 P1-B<br/>RM-004 空白鍵＋重複警告<br/>Blank keys and duplicate warnings"]
    P1C["🟧 P1-C<br/>RM-005～006<br/>CSV safety and readable dates"]
    DEC["⏳ RM-003<br/>第一筆業務決策<br/>First-match decision"]
    P2["🟦 P2<br/>RM-007～010<br/>Parser, stable IDs, metrics, dependencies"]
    M["🧩 Phase 3<br/>模組化＋自動測試<br/>Modularization and automated tests"]
    B["📈 Phase 4<br/>業務規則優化<br/>Business-rule optimization"]
    R["✅ 發布候選<br/>Release candidate"]

    P0 --> P1A
    P0 --> P1B
    P0 --> P1C
    P1A --> P2
    P1B --> P2
    P1C --> P2
    P2 --> M
    DEC --> B
    M --> B
    B --> R
```

| 順序 / Order | 工作 / Work | 完成條件 / Completion condition |
|---|---|---|
| 1 | 🟥 RM-001 | 設定變更即清除結果並停用匯出 / Configuration changes clear results and disable exports |
| 2 | 🟧 RM-002、004、005、006 | 安全 XLSX／CSV、空白鍵不匹配、日期可讀 / Safe XLSX/CSV, no blank-key matches, readable dates |
| 3 | ⏳ RM-003 | Paul 與原開發者書面核准 / Written joint approval |
| 4 | 🟦 RM-007～010 | parser、穩定 ID、指標、依賴修正 / Parser, stable IDs, metrics, dependency fixes |
| 5 | 🧩 Phase 3 | 核心模組可獨立測試 / Core modules independently testable |
| 6 | 📈 Phase 4 | 核准業務規則與資料邊界後評估 / Evaluate only after rule and data-boundary approval |

## 5. 資料安全邊界 / Data security boundary

```mermaid
flowchart LR
    subgraph LOCAL["🔒 核准的本機邊界 / Approved local boundary"]
        REAL["📁 真實 XLSX／DOCX／PDF<br/>Real business files"]
        APP["🖥️ 離線 HTML 工具<br/>Offline HTML tool"]
        OUT["📤 本機 XLSX／CSV<br/>Local XLSX/CSV outputs"]
        REAL --> APP --> OUT
    end

    subgraph SHARE["✅ 可跨 Agent／人員分享 / Shareable"]
        SPEC["📘 雙語規格與決策<br/>Bilingual specs and decisions"]
        HASH["#️⃣ 雜湊與摘要<br/>Hashes and summaries"]
        FIX["🧪 去識別 fixtures 與測試證據<br/>Sanitized fixtures and test evidence"]
    end

    LOCAL -- "只輸出治理資料<br/>Governance data only" --> SHARE
    LOCAL -.- BLOCK["⛔ 未核准：上傳、遙測、遠端服務<br/>Not approved: upload, telemetry, remote services"]
```

中文重點：真實業務檔案不進 Git、不跨 Agent、不由 Agent 修改；資料邊界核准前維持完全本機。

English key point: real business files do not enter Git, cross agent boundaries, or get modified by agents; processing remains fully local until data-boundary approval.

## 6. 實作備忘錄 / Implementation memo

- 目標 / Goal：把修正優先序、責任與閘門轉成單頁視覺架構 / Turn repair priorities, responsibilities, and gates into a one-page visual architecture.
- 範圍 / Scope：只新增文件；不修改 vlookup-web.html 或業務資料 / Documentation only; no change to vlookup-web.html or business data.
- 判斷 / Judgment：使用 Mermaid，方便 Git、Markdown viewer 與 handoff 直接維護 / Use Mermaid for direct maintenance in Git, Markdown viewers, and handoffs.
- 下一步 / Next：共同核准後另建 Phase 2 handoff，依第 4 節順序執行 / After joint approval, create the Phase 2 handoff and execute Section 4 in order.