# RAW MAT 庫存配發引擎 / RAW MAT Allocation Engine

## 專案定位 / Project purpose

本專案是完全在本機瀏覽器執行的配發工具。它整合 Schedule、COOIS、ZRMM0028 與 MB52，依核准規則計算母料覆蓋、子料需求、可配發量及逐列剩餘庫存。<br>
This project is a local browser-based allocation tool. It combines Schedule, COOIS, ZRMM0028, and MB52 to calculate mother coverage, child demand, provided quantity, and running stock under approved rules.

**現行入口 / Current app:** `allocation-web.html` v3.4.4<br>
**現行規格 / Current spec:** [`docs/07-allocation-v3-spec.md`](docs/07-allocation-v3-spec.md)<br>
**操作手冊 / Manual:** [`allocation-manual.html`](allocation-manual.html)<br>
**共用換算設定 / Shared conversion config:** [`config/conversion-rules.v1.json`](config/conversion-rules.v1.json)

離線開啟時，請保留 `vendor/xlsx.full.min.js` 與主程式的相對位置。`vlookup-web.html` 是已淘汰的兩段式查找原型，只保留歷史對照。<br>
When opening offline, keep `vendor/xlsx.full.min.js` in its current relative location. `vlookup-web.html` is a deprecated two-stage lookup prototype retained only for historical reference.

## v3.4.4 核心行為 / v3.4.4 core behavior

- 在任何計算前，0028 的母料或子料若以 `MB` 開頭，整列排除。/ Before any calculation, exclude every 0028 row whose mother or child starts with `MB`.
- COOIS 依 `SO + Material + Segment` 加總全部 `Open Quantity`。/ Aggregate COOIS Open Quantity by `SO + Material + Segment`.
- 母料需求先由共用 F+G 池覆蓋；不足量才展開子料。/ Cover mother demand from the shared F+G pool; expand only the shortage to children.
- 廠外 G 採同單位優先且每母料只取一次：有同單位子料時擇一算 J/P；若完全無同單位子料，任意擇一算 J/P（不換算）並將 G 標紅。/ Outside G uses same-unit-first and pick-once: if same-unit children exist, pick one for J/P; if none exist, pick any one without conversion and mark G in red.
- 直接需求混合規則（逐子料列）：`L=0` 且 `M>0` 時母池不抵 M、`Q=0`、`R=P−M`；`L>0` 時 Rule D 仍蓋 `N=L+M`。/ Hybrid direct demand (per child): when L=0 and M>0, mother pool ignores M, Q=0, R=P−M; when L>0 Rule D still covers N=L+M.
- 同一 SO＋Segment 直接子料可歸多母時，先列出衝突並確認；確認後依母料 Open Qty 比例拆分，取消則停止。/ When direct child demand could belong to multiple mothers in the same SO + Segment, list conflicts and confirm; confirm splits by mother Open Qty, cancel stops.
- 排序為 cutting → Schedule 原始 SO 列序 → COOIS 母料首次列序。/ Ordering is cutting → original Schedule SO row → first COOIS mother row.
- 輸出維持 19 欄；結果區上方有公式說明與匯出按鈕；匯出檔頂部含公式列。/ Output remains at 19 columns; formula notes and export sit above the result table; exports include a formula preamble.
- `合貼備料齊套 / Lamination Kit Ready` 只看非 MH04 且 `L>0` 是否全部足量。/ Lamination Kit Ready checks only non-MH04 rows with L>0 for full supply.
- UI 語系：English、繁體中文、မြန်မာ（緬甸文）。/ UI languages: English, Traditional Chinese, and Myanmar.
- 缺少或衝突的換算規則會停止整批。/ Missing or conflicting conversion rules stop the entire run.

## 快速使用 / Quick use

1. 以瀏覽器開啟 `allocation-web.html`。/ Open `allocation-web.html` in a browser.
2. 匯入 Schedule、COOIS、ZRMM0028、MB52。/ Import Schedule, COOIS, ZRMM0028, and MB52.
3. 確認欄位對應與換算設定；需要時匯入 `config/conversion-rules.v1.json`。/ Confirm mappings and conversions; import `config/conversion-rules.v1.json` when needed.
4. 執行配發並檢查摘要與 19 欄結果。/ Run allocation and review the summary and 19-column result.
5. 匯出 CSV 或 XLSX。任何輸入或設定變更後必須重新執行。/ Export CSV or XLSX. Rerun after any input or configuration change.

## 驗證 / Verification

Fixture 與全量驗證器：<br>
Fixture and full-data verifier:

```powershell
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py `
  --real-data 20260723 `
  --conversion-config config/conversion-rules.v1.json
```

20260723 已驗證：3,505 筆輸出、短缺 71 筆；MB 過濾 389 列／45 組關係；雙重身分 0；錨點 H=0.496708、N=0.02、Q=0、R=43.046。<br>
The 20260723 baseline is verified: 3,505 output rows and 71 shortages; 389 MB rows and 45 relationships removed; zero dual identities; anchor H=0.496708, N=0.02, Q=0, and R=43.046.

## 文件索引 / Documentation index

- [`docs/07-allocation-v3-spec.md`](docs/07-allocation-v3-spec.md)：v3.3 公開行為契約 / v3.3 public behavior contract
- [`docs/04-test-and-acceptance.md`](docs/04-test-and-acceptance.md)：測試與驗收治理 / Test and acceptance governance
- [`docs/03-collaboration-governance.md`](docs/03-collaboration-governance.md)：跨 Agent／人員交辦 / Cross-agent/person handoff
- [`docs/05-repair-flow-architecture.md`](docs/05-repair-flow-architecture.md)：修正流程與架構圖 / Repair flow and architecture
- [`.ai/handoffs/20260724-raw-mat-allocation-handoff/brief.md`](.ai/handoffs/20260724-raw-mat-allocation-handoff/brief.md)：本次交接主檔 / Current handoff brief
- [`.ai/handoffs/20260724-raw-mat-allocation-handoff/result.md`](.ai/handoffs/20260724-raw-mat-allocation-handoff/result.md)：v3.3 實作與驗證結果 / v3.3 implementation and evidence

## 安全與版本治理 / Security and version governance

真實業務檔案、產生的測試輸出與匯出檔由 `.gitignore` 排除。跨 Agent 或跨人員只傳遞規格、程式差異、雜湊、去識別 fixtures 與驗證摘要，不傳送真實來源資料。程式目前不使用遙測、上傳或遠端服務。<br>
Real business files, generated test output, and exports are excluded by `.gitignore`. Cross-agent/person handoffs may include specifications, code diffs, hashes, sanitized fixtures, and test summaries, but not real source data. The application currently uses no telemetry, upload, or remote service.