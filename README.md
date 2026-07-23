# RAW MAT 庫存配發引擎

## 專案定位

本專案是一個在使用者電腦瀏覽器內執行的單頁工具，依核准業務規則將 **Schedule（排程）**、**COOIS（需求）**、**ZRMM0028（BOM／廠外）** 與 **MB52（廠內庫存）** 合併後做**庫存貪婪配發**，並匯出可比對「需求 vs 能提供」與「扣減後剩餘」的結果。

**現行程式入口：`allocation-web.html`（v3.1.4）**  
規格：[docs/07-allocation-v3-spec.md](docs/07-allocation-v3-spec.md)

舊檔 `vlookup-web.html` 為**已淘汰的兩段式查找原型**，僅供歷史對照，**不是**現行產品方向。  
v2 備份：`allocation-web-v2.4.0-backup.html`；舊規格見 [docs/06-allocation-engine-spec.md](docs/06-allocation-engine-spec.md)。

## Project purpose

This project is a browser-based, single-page allocation tool. It combines **Schedule**, **COOIS** demand, **ZRMM0028** BOM/outside stock, and **MB52** plant stock under approved business rules, then greedily allocates child stock and exports demand vs provided and remaining stock after each row.

**Current app entry point: `allocation-web.html` (v3.1.4)**  
Spec: [docs/07-allocation-v3-spec.md](docs/07-allocation-v3-spec.md)

Legacy `vlookup-web.html` is a **deprecated two-stage lookup prototype** kept for historical reference only.  
v2 backup: `allocation-web-v2.4.0-backup.html`; prior spec: [docs/06](docs/06-allocation-engine-spec.md).

## 目前狀態

- 狀態：配發引擎 **v3.1.4**（四輸入、英文表頭解析、Segment FLT/MTF、MB52 SUM、展開＋直接需求、**18 欄**輸出含母廠內／廠外庫存顯示、Y 標記）已實作。
- 程式版本：`allocation-web.html` **3.1.4**。
- 舊查找工具：`vlookup-web.html` **1.1.0**（deprecated）。
- 使用方式：本機離線優先；資料邊界核准前不得新增遙測或遠端服務。
- 語言規則：專案說明與規格採繁體中文在前、英文緊接；UI 為 English／繁體中文／မြန်မာ。
- 正式上線判定：`NEEDS WORK`（待真實檔 UI 驗收）。

## Current status

- Status: Allocation engine **v3.1.4** (four inputs, English header resolution, Segment FLT/MTF, MB52 SUM, expand + direct demand, **18-column** output with mother plant/outside display, Y flag) is implemented.
- App version: `allocation-web.html` **3.1.4**.
- Legacy lookup tool: `vlookup-web.html` **1.1.0** (deprecated).
- Operating model: Local/offline first. Telemetry and remote services are prohibited until the data boundary is approved.
- Language rule: Project docs place Traditional Chinese first and English immediately after. UI languages are English, Traditional Chinese, and Myanmar.
- Release assessment: Still `NEEDS WORK` pending real-file UI acceptance.

## 配發資料流程（v3）

1. **Schedule**：Order／so → cutting；同 SO 取最早 cutting。
2. **COOIS**：SD Document + Material + Open Quantity + Requirement Segment + Base Unit；雙表頭時以英文列為 header。
3. **ZRMM0028**：母料 Material → 子料 Article(Com.)；儲位 39* 排除；Batch 須對齊 Segment（BOM 展開不因 J/L=0 丢掉）。
4. **MB52**：Material + Stock Segment 的 Unrestricted **SUM**（排除 39*）；可配發池 = MB52。
5. 需求：母料展開（× conversion）＋同料直接 Open Quantity；單位換算同 v2（1:1／SHT 末碼表／M↔YD 白名單）。
6. 輸出 **18** 欄（含廠內／廠外母材料庫存顯示、子材料需求、雙 BATCH、Y）。細節見 [docs/07](docs/07-allocation-v3-spec.md)。

## Allocation data flow (v3)

1. **Schedule**: Order/so → cutting; earliest cutting wins per SO.
2. **COOIS**: SD Document + Material + Open Quantity + Requirement Segment + Base Unit; dual-header sheets use the English header row.
3. **ZRMM0028**: mother Material → child Article(Com.); exclude storage 39*; Batch must match Segment (BOM expand keeps children even when J/L is 0).
4. **MB52**: SUM Unrestricted by Material + Stock Segment (exclude 39*); allocatable pool = MB52 only.
5. Demand: mother expansion (× conversion) + direct Open Quantity; unit conversion same as v2.
6. Output **18** columns (mother plant/outside display, child demand, dual BATCH, Y). See [docs/07](docs/07-allocation-v3-spec.md).

## 文件索引

- [配發引擎規格 v3（現行）](docs/07-allocation-v3-spec.md)
- [操作手冊（EN／繁中／မြန်မာ）](allocation-manual.html)
- [配發引擎規格 v2（歷史）](docs/06-allocation-engine-spec.md)
- Fixture 驗證（v3）：`.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`（`python ...`；有 `New_0722/` 時一併 smoke）
- [現況系統規格（含歷史 VLOOKUP 描述）](docs/01-current-system-spec.md)
- [程式碼審查與優化 Roadmap](docs/02-code-review-and-roadmap.md)
- [跨 Agent／跨人員協作治理](docs/03-collaboration-governance.md)
- [測試與驗收規格](docs/04-test-and-acceptance.md)
- [修正流程與架構圖](docs/05-repair-flow-architecture.md)

## Documentation index

- [Allocation engine specification v3 (current)](docs/07-allocation-v3-spec.md)
- [Operation manual (EN / ZH / MY)](allocation-manual.html)
- [Allocation engine specification v2 (historical)](docs/06-allocation-engine-spec.md)
- Fixture verifier (v3): `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py` (optional `New_0722/` smoke)
- [Current system specification (includes historical VLOOKUP notes)](docs/01-current-system-spec.md)
- [Code review and optimization roadmap](docs/02-code-review-and-roadmap.md)
- [Cross-agent and cross-person collaboration governance](docs/03-collaboration-governance.md)
- [Test and acceptance specification](docs/04-test-and-acceptance.md)
- [Repair flow and architecture diagrams](docs/05-repair-flow-architecture.md)

## 安全與版本治理

真實來源檔與任何匯出結果均由 `.gitignore` 排除。跨 Agent 或跨人員交辦只能傳遞規格、雜湊、摘要、去識別 fixture 與驗證證據，不得傳遞真實業務資料。

## Security and version governance

Real source workbooks and generated exports are excluded by `.gitignore`. Cross-agent or cross-person handoffs may contain specifications, hashes, summaries, sanitized fixtures, and verification evidence, but must not contain real business data.
