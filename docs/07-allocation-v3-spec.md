# 07 — RAW MAT 庫存配發引擎規格 v3.4.2 / RAW MAT Allocation Engine Specification v3.4.2

**版本 / Version:** 3.4.2<br>
**狀態 / Status:** 已確認（含歸屬不明確認後比例拆分、廠外 G 同單位優先、緬甸語 UI 復原，2026-07-30）/ Confirmed (includes ambiguous confirm + Open Qty split, same-unit-first outside G, and Myanmar UI restore, 2026-07-30)<br>
**主程式 / Application:** `allocation-web.html`<br>
**驗證器 / Verifier:** `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`

本文件是 v3.4.2 的公開行為契約。欄位以英文表頭解析，不以 Excel 欄位字母寫死。程式完全在本機瀏覽器執行；真實業務檔案不得提交 Git 或跨 Agent 傳送。<br>
This document is the public behavior contract for v3.4.2. Columns are resolved by English header names rather than fixed Excel letters. Processing remains local in the browser; real business files must not be committed to Git or transferred across agents.

## 1. 輸入與欄位契約 / Inputs and column contract

### Schedule

- `Order`／`Order NO`／`so`：銷售訂單。/ Sales order.
- `cutting`／`cutting process`：生產日期。/ Production date.
- 同一 SO 若有多列，取最早 cutting；同日保留 Schedule 原始列序。/ For repeated SO rows, use the earliest cutting date; preserve original Schedule row order for equal dates.

### COOIS

- `SD Document`：SO。/ Sales order.
- `Material`：需求料號。/ Demand material.
- `Open Quantity`：需求量。/ Demand quantity.
- `Requirement Segment`：庫存區段，例如 FLT／MTF。/ Stock segment such as FLT/MTF.
- `Base Unit of Measure`：需求單位。/ Demand unit.
- 所有列先依 `SO + Material + Segment` 加總 `Open Quantity`，並保留該組首次出現列序。/ Aggregate all Open Quantity by `SO + Material + Segment` and retain the first source-row position.

### ZRMM0028

- `Material`：母料。/ Mother material.
- `Article(Com.)`：子料。/ Child material.
- `GI SC(541/542)`、`Stock of Vendor`、`GR SC(543/544)`：廠外庫存計算來源。/ Inputs for outside-stock calculation.
- `Storage Location`：`39*` 列排除。/ Rows starting with `39` are excluded.
- `Batch`：Segment。/ Segment.
- `OUn`／`BUn`：母料／子料單位。/ Mother/child units.
- `Material Full Description(CN/EN)`：SHT 尺寸末碼來源。/ Source of the SHT size suffix.

### MB52

- `Material`、`Stock Segment`、`Unrestricted`：依 Material + Segment 加總。/ SUM by Material + Segment.
- `Storage Location`：`39*` 列排除。/ Rows starting with `39` are excluded.
- `Base Unit of Measure`：庫存單位，用於對帳。/ Stock unit for reconciliation.

COOIS 與 ZRMM0028 可有中文第一列、英文第二列；解析器以英文表頭列為準。<br>
COOIS and ZRMM0028 may contain a Chinese first header row and an English second header row; the English header row is authoritative.

## 2. 前置過濾與資料邊界 / Pre-filtering and data boundary

所有檢核、關係建立、單位換算與計算之前，依下列順序處理：<br>
Apply the following before validation, relationship construction, unit conversion, or calculation:

1. ZRMM0028 任一列若 `Material` 或 `Article(Com.)` 去空白並轉大寫後以 `MB` 開頭，整列排除。/ Exclude the entire ZRMM0028 row when normalized `Material` or `Article(Com.)` starts with `MB`.
2. ZRMM0028 與 MB52 的 `Storage Location` 以 `39` 開頭者排除。/ Exclude ZRMM0028 and MB52 rows whose storage location starts with `39`.
3. COOIS 中不在 Schedule 的 SO 不計算。/ Ignore COOIS rows whose SO is absent from Schedule.
4. 直接子料需求只接受仍存在於有效 ZRMM0028 `Article(Com.)` 集合的料號。/ Direct child demand is eligible only when the material remains in the effective ZRMM0028 child set.
5. FLT、MTF 與空白 Segment 分池，不可混倉。/ FLT, MTF, and blank segments are separate pools and may not mix.

20260723 基準必須得到：排除 389 列、移除 45 組母子關係、雙重身分材料為 0。<br>
The 20260723 baseline must yield 389 excluded rows, 45 removed mother-child relationships, and zero dual-identity materials.

## 3. 母料需求與 F+G 共用池 / Mother demand and shared F+G pool

母料廠內庫存 F：<br>
Mother plant stock F:

```text
F(mother, segment) = SUM(MB52.Unrestricted)
```

每個有效母子 pair 的廠外原始量先依子料列計算：<br>
For each effective mother-child pair, calculate raw outside stock from the child-side row:

```text
outsideChild(pair) = max(0, SUM(J) - SUM(P))
```

只有同列 `J != 0` 且 `Stock of Vendor != 0` 的資料納入該 pair。G 採**同單位優先**：若某母料在有效 0028 中存在任何 `OUn == BUn` 的子料，G 只加總這些同單位子料的 `max(0, ΣJ − ΣP)`；**不使用換算率**。若整個母料完全找不到同單位子料，則 fallback 到原本的 J/P 聚合，但仍**不除換算率**；該母料在輸出欄 G 需標紅提示。<br>
Only rows where `J != 0` and `Stock of Vendor != 0` contribute to the pair. G uses a **same-unit-first** rule: if a mother has any child with `OUn == BUn` anywhere in effective 0028, G sums only those same-unit children using `max(0, ΣJ − ΣP)` and applies **no conversion ratio**. If the mother has no same-unit child at all, fall back to the original J/P aggregation, still **without dividing by a conversion ratio**; the mother’s G output must be highlighted red.

```text
if existsSameUnitChild(mother):
  G(mother, segment) = SUM(max(0, ΣJ - ΣP) for same-unit pairs only)
else:
  G(mother, segment) = SUM(max(0, ΣJ - ΣP) for all outside pairs)

poolMother = F + G
```

F 與 G 輸出欄固定顯示原始總量，不隨訂單扣減。H「本列配發前母料可用池」是母料需求已扣除、且同母料先前子料列亦已依 Rule D 扣除後的動態餘量；G 與 H 不得相加。fallback 算出的 G 必須以紅字提示。<br>
Output columns F and G always show their original totals. H, `mother stock available before this row`, is the dynamic mother-unit balance after mother demand and prior Rule D child rows; G and H must not be added. A fallback G must be highlighted in red.

COOIS 母料需求先由共用池覆蓋，僅不足量展開子料，母料池再依序覆蓋直接子料需求：<br>
Mother demand is covered from the shared pool first; only the shortage expands to children, after which the remaining mother pool covers direct child demand in order:

```text
motherCoverUsed = min(motherDemand, motherPoolBeforeSO)
motherPoolAfterMother = motherPoolBeforeSO - motherCoverUsed
qtyExpand = motherDemand - motherCoverUsed
childDemandFromMother = qtyExpand * conversionRatio

motherPoolBeforeRow = current mother pool
motherCoverChild = min(demandQty, motherPoolBeforeRow * conversionRatio)
motherPoolAfterRow = motherPoolBeforeRow - motherCoverChild / conversionRatio
```

## 4. Rule D、直接子料需求與歸屬 / Rule D, direct child demand, and ownership

Rule A 維持取消；Rule D 自 v3.3 恢復。COOIS 的直接子料需求永遠完整保留在 `demand direct` 與 `demand qty`，先由母料需求扣除後的母料餘量覆蓋，未覆蓋量才從該子料 MB52 配發。Q 只顯示實際子料 MB52 領用量。<br>
Rule A remains removed; Rule D is restored in v3.3. Direct COOIS child demand remains fully visible in `demand direct` and `demand qty`, is first covered by the mother balance after mother demand, and only the uncovered amount uses child MB52. Q shows only actual child-MB52 usage.

多個直接子料共用同一母料餘量時，依 ZRMM0028 子料首次出現列序逐列扣減。母料池跨 SO 延續，且同時承接母料需求與 Rule D 覆蓋量。<br>
When multiple direct children share a mother balance, consume it by first ZRMM0028 child occurrence. The mother pool persists across SOs and is reduced by both mother demand and Rule D coverage.

若同一 SO + Segment 的直接子料同時可歸入兩個以上母料，先列出全部衝突（SO／Segment／子料／各母料 Open Qty），彈窗請使用者確認；**未確認不得自動拆分**。使用者取消 → 整批停止、不產結果。使用者確認 → 依各母料在該 SO＋Segment 的 Open Qty 比例拆入各母料 `demandDirect`（權重全為 0 則均分；最後一母吃餘數），加總必須等於原直接開量，禁止重複加總。純直接需求且沒有母料者，全部由子料 MB52 配發。<br>
If direct demand in the same SO + Segment could belong to more than one mother, list every conflict (SO / Segment / child / each mother Open Qty) and prompt for confirmation; **never split automatically without confirmation**. Cancel stops the run with no output. Confirm splits that Open Qty across the candidate mothers by mother Open Qty share on that SO + Segment (equal share if all weights are 0; last mother receives the remainder). The parts must sum to the original direct Open Qty; never double-count. A direct-only demand with no mother uses child MB52 in full.

錨點 `10189518 / MN090134761 / MA020147549`：F=0、G=1.996708、母料需求=1.5、H=0.496708、N=0.02、Q=0、R=43.046；G 與 H 不得相加。<br>
Anchor `10189518 / MN090134761 / MA020147549`: F=0, G=1.996708, mother demand=1.5, H=0.496708, N=0.02, Q=0, and R=43.046; G and H must not be added.

## 5. 換算與停止條件 / Conversion and stop conditions

- 相同單位係數為 1。/ Same-unit ratio is 1.
- 一般單位與尺寸換算由共用 JSON 設定提供。/ General and size conversions come from the shared JSON configuration.
- `SHT → YD`、尺寸 `220x110cm` 的固定係數為 `2.187227`。/ The fixed `SHT → YD` factor for `220x110cm` is `2.187227`.
- 缺少換算、係數小於等於 0、同一關係單位衝突或尺寸末碼衝突時，整批停止，不略過任何列。/ Missing conversions, non-positive ratios, conflicting units, or conflicting size suffixes stop the entire run; no row is silently skipped.

共用 JSON 格式：<br>
Shared JSON format:

```json
{
  "schemaVersion": 1,
  "appVersion": "3.4.2",
  "conversionRules": [
    { "motherUnit": "M", "childUnit": "YD", "ratio": 1.0936 }
  ],
  "sizeConversionRules": [
    { "suffix": "220x110cm", "childUnit": "YD", "ratio": 2.187227 }
  ]
}
```

正式預設檔為 `config/conversion-rules.v1.json`。HTML 支援匯入／匯出；Python 以 `--conversion-config` 使用同一格式。<br>
The committed default is `config/conversion-rules.v1.json`. The HTML imports/exports this format; Python accepts the same format through `--conversion-config`.

## 6. 排序、子料池與配發 / Ordering, child pools, and allocation

配發順序：<br>
Allocation order:

1. cutting 日期升冪。/ Cutting date ascending.
2. cutting 同日時，Schedule 的 SO 原始列序。/ Original Schedule SO row order for equal cutting dates.
3. 同一 SO 內，COOIS 母料首次出現列序。/ Mother’s first COOIS occurrence within the same SO.
4. 同一母料內，ZRMM0028 子料首次出現列序。/ Child’s first ZRMM0028 occurrence within the mother.

多個母料共用同一子料時，依上列順序逐列扣同一 `Material + Segment` 子料池。<br>
When mothers share a child, rows consume the same `Material + Segment` child pool in that order.

```text
childStock = original MB52 total
stockAvailable = child pool before current row
childNeedNet = demandQty - motherCoverChild
providedQty = min(childNeedNet, stockAvailable)
remaining = stockAvailable - providedQty
fulfilled = motherCoverChild + providedQty
shortage = fulfilled < demandQty
```

`child stock` 固定顯示原始 MB52 總量；只有 `stock available` 與 `remaining stock after this row` 隨 Q 遞減。H 使用母料 OUn，N/Q 使用子料單位，不同單位不可直接相減。<br>
`child stock` always displays the original MB52 total; only `stock available` and `remaining stock after this row` decrease by Q. H uses mother OUn, while N/Q use the child unit; values in different units must not be subtracted directly.

## 7. 合貼備料齊套 Y / Lamination Kit Ready Y

同一 `(SO + mother + Segment)` 群組只有同時符合以下條件才標 `Y`：<br>
A `(SO + mother + Segment)` group is marked `Y` only when all conditions are met:

- 有母料。/ A mother exists.
- 至少一筆非 MH04 且需求大於 0。/ At least one non-MH04 row has positive demand.
- 所有正需求的非 MH04 列皆 `motherCoverChild + provided qty >= demand qty`。/ Every positive non-MH04 row is fulfilled by `motherCoverChild + provided qty`.

Y 判定使用內部原始數值（同一輪計算的 `fulfilled` 與 `demand_total`），不以格式化後的小數字串做比較；因此可避免 6 位小數四捨五入造成的邊界誤判。<br>
Y decision compares internal raw numbers from the same allocation pass (`fulfilled` vs `demand_total`), not formatted decimal strings, to avoid boundary misclassification caused by rounding to 6 decimals.

零需求群組、純直接需求、僅 MH04 群組不標 Y。MH04 列仍輸出與配發，但不參與 Y 判定。<br>
Zero-demand groups, direct-only rows, and MH04-only groups remain blank. MH04 rows are still exported and allocated but do not participate in the Y decision.

## 8. 公開輸出 19 欄 / Public 19-column output

| # | English header | 中文語意 / Chinese meaning |
|---:|---|---|
| 1 | cutting | cutting 日期 |
| 2 | so | 銷售訂單 |
| 3 | mother material | 母材料 |
| 4 | mother batch | 母料 Segment／Batch |
| 5 | mother unit | 母料單位 |
| 6 | mother plant stock | 母料 MB52 原始總量 F |
| 7 | mother stock outside | 母子 pair 換回母料 OUn 後的廠外總量 G |
| 8 | mother stock available before this row | 母料需求與先前 Rule D 列扣除後、本列前母料餘量（母料 OUn） |
| 9 | child material | 子材料 |
| 10 | child batch | 子料 Segment／Batch |
| 11 | child unit | 子料單位 |
| 12 | child demand | 母料不足展開需求 |
| 13 | demand direct | COOIS 直接子料需求 |
| 14 | demand qty | child demand + demand direct |
| 15 | child stock | 子料 MB52 原始總量 |
| 16 | stock available | 本列配發前子料池 |
| 17 | provided qty | 實際從子料 MB52 領用：min(demand qty - motherCoverChild, stock available) |
| 18 | remaining stock after this row | 本列配發後子料池 |
| 19 | lamination kit ready (Y) | 合貼備料齊套 |

預覽、CSV 與 XLSX 必須使用相同欄序與數值。日期輸出為可讀格式；CSV 使用 UTF-8 BOM，正確處理逗號、引號、換行與公式字首。<br>
Preview, CSV, and XLSX must use identical column order and values. Dates are human-readable; CSV uses UTF-8 BOM and safely handles commas, quotes, newlines, and formula prefixes.

## 9. 結果失效與介面 / Result invalidation and UI

任何輸入檔、欄位對應、MB 過濾規則、一般換算或尺寸換算變更後，舊結果立即失效並停用 CSV／XLSX 匯出，直到重新執行成功。語言切換不得改變資料、欄位對應或篩選選取。UI 僅支援 English 與繁體中文。<br>
Any change to input files, mappings, MB rules, general conversions, or size conversions immediately invalidates old results and disables CSV/XLSX export until a successful rerun. Language switching must not alter data, mappings, or filters. The UI supports only English and Traditional Chinese.

## 10. 驗收基準 / Acceptance baseline

20260723 全量驗證（不提交原始檔與輸出）：<br>
20260723 full-data acceptance (source files and generated output remain uncommitted):

- Schedule 246 列、COOIS 129,993 列、ZRMM0028 16,307 列、MB52 7,050 列。/ 246 Schedule, 129,993 COOIS, 16,307 ZRMM0028, and 7,050 MB52 rows.
- 輸出 3,505 列、母料 499、短缺列 71。/ 3,505 output rows, 499 mothers, and 71 shortage rows.
- MB 排除 389 列、45 組關係、雙重身分 0。/ 389 MB rows and 45 relationships removed; zero dual identities.
- 錨點 F=0、G=1.996708、母料需求=1.5、H=0.496708、N=0.02、Q=0、R=43.046，且不短缺。/ Anchor F=0, G=1.996708, mother demand=1.5, H=0.496708, N=0.02, Q=0, R=43.046, and no shortage.

驗證指令：<br>
Verification command:

```powershell
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py `
  --real-data 20260723 `
  --conversion-config config/conversion-rules.v1.json
```

## 11. v3.2.0 → v3.3.0 差異 / Rule changes

- 恢復 Rule D；直接需求仍完整顯示，但母料餘量先覆蓋，Q 只記子料 MB52 實領。/ Restored Rule D; direct demand remains fully visible, but mother balance covers it first and Q records only actual child-MB52 usage.
- H 從固定的 SO 前餘量改為逐列動態母料餘量；G 與 H 不得相加。/ Changed H from a fixed pre-SO value to a dynamic pre-row mother balance; G and H must not be added.
- 短缺與 Y 改以 `motherCoverChild + Q` 判定。/ Shortage and Y now use `motherCoverChild + Q`.
- 20260723 相較 v3.2：H 變更 1,333 列、Q 23 列、R 62 列、Y 13 列；短缺 81→71，Y 列 490→499。/ Versus v3.2 on 20260723: H changed on 1,333 rows, Q on 23, R on 62, and Y on 13; shortages changed 81→71 and Y rows 490→499.
- 維持 19 欄、`schemaVersion: 1`、MB 前置過濾、排序與換算停止條件；歸屬不明改為確認後按母料 Open Qty 比例拆分（見 §4）。/ Preserved 19 columns, `schemaVersion: 1`, MB pre-filtering, ordering, and conversion-stop rules; ambiguous direct demand now confirms then splits by mother Open Qty (see §4).

## 12. v3.3.0 → v3.4.0 差異 / Ambiguous confirm + split

- 歸屬不明改為先列出全部衝突並彈窗確認；取消仍整批停止。/ Ambiguous ownership lists every conflict and prompts; cancel still stops the run.
- 確認後依各母料在該 SO＋Segment 的 Open Qty 比例拆分直接需求；禁止未確認自動拆、禁止重複加總。/ After confirm, split direct demand by mother Open Qty share; never auto-split without confirm; never double-count.
- `APP_VERSION` / conversion config `appVersion` → `3.4.0`。/ App and conversion config version → `3.4.0`.

## 13. v3.4.0 → v3.4.1 差異 / Outside G same-unit first

- 廠外母料庫存 `G` 改為同單位優先：若母料在有效 0028 中存在任一 `OUn == BUn` 子料，只加總這些同單位子料的 `J/P`。/ Outside mother stock `G` is now same-unit first: if a mother has any `OUn == BUn` child in effective 0028, only those same-unit children contribute `J/P`.
- 同單位路徑不使用換算率；`G` 直接加總 `max(0, ΣJ - ΣP)`。/ The same-unit path does not use a conversion ratio; `G` sums `max(0, ΣJ - ΣP)` directly.
- 若母料完全無同單位子料，`G` fallback 到原本 `J/P` 聚合，但不除換算率。/ If a mother has no same-unit child at all, `G` falls back to the original `J/P` aggregation without dividing by a conversion ratio.
- fallback 算出的 `G` 在結果表以紅字顯示，提醒使用者這是例外算法。/ A fallback `G` is shown in red in the result table so users can spot the exception path.
- `APP_VERSION` / conversion config `appVersion` → `3.4.1`。/ App and conversion config version → `3.4.1`.

## 14. v3.4.1 → v3.4.2 差異 / Myanmar UI restore

- 復原 UI 緬甸文語系（my）：語系選單、	ranslations.my、OUTPUT_HEADERS_MY（19 欄）。/ Restore Myanmar UI language (my): language select, 	ranslations.my, and 19-column OUTPUT_HEADERS_MY.
- 補齊 v3.3／v3.4 新增文案（母料可用池 H tip、ambiguous confirm、換算設定匯出／匯入）。/ Add Myanmar strings for v3.3/v3.4 features (mother available tip H, ambiguous confirm, conversion config import/export).
- APP_VERSION / conversion config ppVersion → 3.4.2。/ App and conversion config version → 3.4.2.
