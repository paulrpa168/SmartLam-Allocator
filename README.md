# RAW MAT 庫存配發引擎

## 專案定位

本專案是一個在使用者電腦瀏覽器內執行的單頁工具，依核准業務規則將排程（Excel1）、需求 Open Quantity（Excel2）與 BOM／庫存（Excel3）合併後做**庫存貪婪配發**，並匯出可比對「需求 vs 能提供」與「扣減後剩餘」的結果。

**現行程式入口：`allocation-web.html`（v2.1.0）**  
規格：[docs/06-allocation-engine-spec.md](docs/06-allocation-engine-spec.md)

舊檔 `vlookup-web.html` 為**已淘汰的兩段式查找原型**，僅供歷史對照，**不是**現行產品方向。

## Project purpose

This project is a browser-based, single-page allocation tool. It combines schedule (Excel1), Open Quantity demand (Excel2), and BOM/stock (Excel3) under approved business rules, then greedily allocates child stock and exports a result that compares demand vs provided and remaining stock after each row.

**Current app entry point: `allocation-web.html` (v2.1.0)**  
Spec: [docs/06-allocation-engine-spec.md](docs/06-allocation-engine-spec.md)

Legacy `vlookup-web.html` is a **deprecated two-stage lookup prototype** kept for historical reference only — it is **not** the current product direction.

## 目前狀態

- 狀態：配發引擎 **v2.1.0**（單位事前檢查、可編輯換算白名單、篩選、斑馬色、Y 欄）已實作；fixture 驗證通過。
- 程式版本：`allocation-web.html` **2.1.0**。
- 舊查找工具：`vlookup-web.html` **1.1.0**（deprecated）。
- 使用方式：本機離線優先；資料邊界核准前不得新增遙測或遠端服務。
- 語言規則：專案說明與規格採繁體中文在前、英文緊接；v2 UI 為英文與繁體中文。
- 正式上線判定：`NEEDS WORK`（待真實檔 UI 驗收；真實檔若有 SHT↔YD 等單位需在換算表補規則）。

## Current status

- Status: Allocation engine **v2.1.0** (unit pre-check, editable conversion whitelist, filters, zebra rows, Y flag) is implemented; fixture verification passed.
- App version: `allocation-web.html` **2.1.0**.
- Legacy lookup tool: `vlookup-web.html` **1.1.0** (deprecated).
- Operating model: Local/offline first. Telemetry and remote services are prohibited until the data boundary is approved.
- Language rule: Project docs place Traditional Chinese first and English immediately after. The v2 UI languages are English and Traditional Chinese.
- Release assessment: Still `NEEDS WORK` pending real-file UI acceptance (add conversion rows for units such as SHT↔YD when prompted).

## 配發資料流程（v2）

1. Excel 1：`so`（A）→ `cutting`（B）；同 SO 取最早 cutting。
2. Excel 2：`SD Document`（B）+ `Material` 母料（F）+ `Open Quantity`（Q）加總；母料須存在於 Excel3.E。
3. Excel 3：母料（E）→ 子料 `Article(Com.)`（I）；子料初始庫存 = **MAX(Unrestricted K)**。
4. 母：子需求 **1:1**；排序 cutting / SO / mother / child；由上而下貪婪配發。
5. 輸出欄：cutting、so、mother、child、demand qty、provided qty、remaining after row。

## Allocation data flow (v2)

1. Excel 1: `so` (A) → `cutting` (B); earliest cutting wins per SO.
2. Excel 2: aggregate `Open Quantity` (Q) by (`SD Document` B, mother `Material` F); mother must exist in Excel3.E.
3. Excel 3: mother (E) → child `Article(Com.)` (I); initial stock = **MAX(Unrestricted K)** per child.
4. Mother:child demand ratio **1:1**; sort by cutting / SO / mother / child; greedy allocate top-to-bottom.
5. Output columns: cutting, so, mother, child, demand qty, provided qty, remaining after row.

## 文件索引

- [配發引擎規格（現行產品）](docs/06-allocation-engine-spec.md)
- [現況系統規格（含歷史 VLOOKUP 描述）](docs/01-current-system-spec.md)
- [程式碼審查與優化 Roadmap](docs/02-code-review-and-roadmap.md)
- [跨 Agent／跨人員協作治理](docs/03-collaboration-governance.md)
- [測試與驗收規格](docs/04-test-and-acceptance.md)
- [修正流程與架構圖](docs/05-repair-flow-architecture.md)
- [配發引擎 v2 交辦](.ai/handoffs/20260718-raw-mat-allocation-v2/brief.md)
- [Phase 2 P0/P1 舊工具修正交辦](.ai/handoffs/20260717-raw-mat-phase2-p0p1/brief.md)

## Documentation index

- [Allocation engine specification (current product)](docs/06-allocation-engine-spec.md)
- [Current system specification (includes historical VLOOKUP notes)](docs/01-current-system-spec.md)
- [Code review and optimization roadmap](docs/02-code-review-and-roadmap.md)
- [Cross-agent and cross-person collaboration governance](docs/03-collaboration-governance.md)
- [Test and acceptance specification](docs/04-test-and-acceptance.md)
- [Repair flow and architecture diagrams](docs/05-repair-flow-architecture.md)
- [Allocation engine v2 handoff](.ai/handoffs/20260718-raw-mat-allocation-v2/brief.md)
- [Phase 2 P0/P1 legacy-tool fix handoff](.ai/handoffs/20260717-raw-mat-phase2-p0p1/brief.md)

## 安全與版本治理

真實來源檔 `1.xlsx`、`2.xlsx`、`3.xlsx`、原始 Word/PDF 操作說明與任何匯出結果均由 `.gitignore` 排除。跨 Agent 或跨人員交辦只能傳遞規格、雜湊、摘要、去識別 fixture 與驗證證據，不得傳遞真實業務資料。

## Security and version governance

The real source workbooks, original Word/PDF instructions, and generated exports are excluded by `.gitignore`. Cross-agent and cross-person handoffs may contain specifications, hashes, summaries, sanitized fixtures, and verification evidence, but must not contain real business data.
