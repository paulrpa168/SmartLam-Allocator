# RAW MAT Allocation Engine v3.1.6 — 條件完整清單

**簡報一句話：**  
> 一套 4,745 行瀏覽器引擎，在 **7 大類、~77 條條件** 約束下，完成四輸入→十八欄跨欄位配發計算，每次改版經多 Agent 交叉驗證。

---

## 條件總數表

| 類別 | 代號 | 條數 | 備註 |
|------|------|------|------|
| A. 輸出欄位 | OUT | 18 欄 | 含欄名(EN/ZH/MY) + 公式/規則 + 是否影響配發池 |
| B. 加總/樞紐運算 | AGG | 14 | group key + 公式 |
| C. 引擎決策條件 | DEC | 28 | 觸發條件 → 結果（跳過/擋跑/只影響Y/顯示） |
| D. UI-only 條件 | UI | 6 | 明確標「不改池」 |
| E. 單位換算類型 + 預設種子 | CONV | 6 類型 / 11 種子列 | 引擎 never hardcode |
| F. 匯入檢核類型 | CHK | 7 | 擋跑條件 |
| G. 配發排序層級 | SORT | 6 | 排序鍵 |
| **合計** | | **~85** | 扣除重疊後約 **77 條獨特條件** |

---

## A. 輸出 18 欄（OUT）

| # | OUT 鍵 | EN 表頭 | ZH 表頭 | 公式/規則 | 影響配發池？ |
|---|--------|---------|---------|-----------|:----------:|
| 1 | cutting | cutting | cutting（生產日） | Schedule 最早 cutting | 否（排序用） |
| 2 | so | so | so（訂單） | Schedule SO | 否（群組用） |
| 3 | mother | mother material | 母材料 | ZRMM Material | — |
| 4 | motherBatch | mother batch | 母材料 BATCH | normalizeSegment(ZRMM.Batch) | — |
| 5 | motherUnit | mother unit | 母單位 | COOIS Base UoM || ZRMM OUn | — |
| **6** | motherStockMb52 | mother plant stock | 廠內母材料庫存 | **= SUM(MB52.Unrestricted) WHERE Material=mother AND Segment AND storage NOT 39*** | ❌ **僅顯示** |
| **7** | motherStockOutside | mother stock outside | 廠外母材料庫存 | **= Σ max(0, ΣJ − ΣP) over all children of this mother+seg** | ❌ **僅顯示** |
| 8 | child | child material | 子材料 | ZRMM Article(Com.) | — |
| 9 | childBatch | child batch | 子材料 BATCH | normalizeSegment(ZRMM.Batch) | — |
| 10 | childUnit | child unit | 子單位 | ZRMM BUn | — |
| 11 | demandFromMother | child demand | 子材料需求 | = Σ(OpenQty(M) × conv(unit, sizeSuffix)) | ✅ 決定配發 |
| 12 | demandDirect | demand direct | 子料直接需求 | = COOIS Open Qty (when child in 0028.F) | ✅ 決定配發 |
| 13 | demand | demand qty | 需求合計 | = demandFromMother + demandDirect | ✅ |
| 14 | stockMb52 | child stock | 子材料庫存 | = 本列配發前剩餘廠內（起始=MB52，前列已扣） | ✅ |
| 15 | stockAvailable | stock available | 可配發庫存 | = 本列前剩餘池（起始=MB52，已扣前列 provide） | ✅ |
| 16 | provided | provided qty | 能提供數量 | **= min(demand, max(0, poolBefore))** | ✅ |
| 17 | remaining | remaining stock after this row | 扣減後剩餘 | = poolBefore − provide | ✅ |
| 18 | flagY | pending allocation (Y) | 待配發（Y） | SO+母+seg 非MH04且demand>0皆 fully provided → Y | 標記 |

**補助規則：** 無母料列（直接需求）→ 6/7 欄空白

---

## B. 加總/樞紐運算（14）

| # | 群組 Key | 公式 | 用途 |
|---|----------|------|------|
| AGG-01 | mother\0child\0seg | J gate (J≠0 && L≠0) → SUM J, SUM P | raw outside pair |
| AGG-02 | mother\0seg | Σ max(0, AGG-01.J − AGG-01.P) | **廠外母材料庫存（顯示）** |
| AGG-03 | material\0seg | SUM(MB52.Unrestricted) WHERE storage NOT 39* | MB52 廠內庫存 |
| AGG-04 | — | Set(child) from all ZRMM Article | validChildren（COOIS 過濾） |
| AGG-05 | — | Set(mother) from ZRMM Material | mothersInBom |
| AGG-06 | SO | earliest cutting | scheduleMap |
| AGG-07 | SO | COOIS rows → array | cooisBySo |
| AGG-08 | seg\0child | Set of children expanded under any mother | expansionChildren |
| AGG-09 | seg\0mother | Set of mothers that expanded | expandedMothers |
| AGG-10 | so\|seg\|mother\|child | demandFromMother + demandDirect | 需求彙整 |
| AGG-11 | child\0seg | running: plantBefore − provide | 剩餘廠內 |
| AGG-12 | child\0seg | running: max(0, poolBefore − provide) | 剩餘可配發池 |
| AGG-13 | — | output row array | 最終結果 |
| AGG-14 | SO\|mother\|seg | provided ≥ demand for all non-MH04 demand>0 → Y | Y 標記群組 |

---

## C. 引擎決策條件（28）

| # | 觸發條件 | 結果 | 類別 |
|---|----------|------|:----:|
| DEC-01 | COOIS ↔ ZRMM unit/seg 衝突 | ❌ 擋跑（showErrorModal） | 擋跑 |
| DEC-02 | Schedule row: so 為空 | ⏭️ 跳過 | 跳過 |
| DEC-03 | Schedule: 同 SO 已有 earlier cutting | 保留最早 cutting，捨棄較晚 | 跳過 |
| DEC-04 | ZRMM row: mother 或 child 為空 | ⏭️ 跳過 | 跳過 |
| DEC-05 | ZRMM: storage 開頭 39 | ⏭️ 跳過（BOM 與廠外皆不計） | 跳過 |
| DEC-06 | ZRMM: 同 mother 不同 size suffix | ❌ 擋跑（suffixConflicts） | 擋跑 |
| DEC-07 | ZRMM: 同 mother+child 不同 BUn | ❌ 擋跑（childUnitConflicts） | 擋跑 |
| DEC-08 | ZRMM outside: J=0 或 L=0 | ⏭️ 該列不計廠外（BOM 仍保留） | 跳過 |
| DEC-09 | COOIS row: SO 不在 Schedule | ⏭️ 跳過 | 跳過 |
| DEC-10 | COOIS row: Material 在 mothersInBom && seg 非空 | ➡️ 展開母料（× conversion） | 展開 |
| DEC-11 | 展開時：母料 SHT 無 size suffix | 記錄「missing-suffix」⚠️ | 跳過 |
| DEC-12 | 展開時：SHT size suffix 無對應倍率 | 記錄「missing-size-rule」⚠️ | 跳過 |
| DEC-13 | 展開時：無任何單位換算匹配 | 記錄「missing-conv」⚠️ | 跳過 |
| DEC-14 | 展開時：有任一 missingRule | ❌ 擋跑（errorConvTitle） | 擋跑 |
| DEC-15 | COOIS direct: material = 已展開的母料 | ⏭️ 跳過（已展開就不重複當直接需求） | 跳過 |
| DEC-16 | COOIS direct: material not in validChildren | ⏭️ 跳過（HC/HU 等不在 0028.F）| 跳過 |
| DEC-17 | COOIS direct: material 已是展開子料 | ➡️ 合併 direct 到展開列（demandDirect） | 合併 |
| DEC-18 | COOIS direct: 以上皆非 | ➡️ 建立空白母料需求列 | 新增 |
| DEC-19 | **配發**：pool = child MB52 only（廠外不扣池） | ✅ **無母料廠外進入 pool** | 配發 |
| DEC-20 | **provided = min(demand, max(0, poolBefore))** | ✅ 核心配發公式 | 配發 |
| DEC-21 | provide < demand（1e-9 容差） | 「shortage」計數 +1 | 計數 |
| DEC-22 | motherKey 存在 → 讀取 stockMb52 | ✅ 寫入 col 6（母廠內，僅顯示） | 顯示 |
| DEC-23 | motherKey 存在 → 讀取 outsideByMother | ✅ 寫入 col 7（母廠外，僅顯示） | 顯示 |
| DEC-24 | 無母料（直接需求）→ col 6/7 空白 | ⏭️ 空白 | 顯示 |
| DEC-25 | Y: 群組 key = SO\|mother\|seg | 分組 | Y |
| DEC-26 | Y: child 開頭 MH04 | ⏭️ 該列不參與配套判定 | 跳過 |
| DEC-27 | Y: demand>0 且所有 non-MH04 provided ≥ demand | ✅ 標 Y | Y |
| DEC-28 | Y: 無 non-MH04 demand>0 的列 | ⏭️ 不標 Y | 跳過 |

---

## D. UI-only 條件（6）— 明確「不改 pool」

| # | 條件 | 影響範圍 | 改 pool？ |
|---|------|---------|:--------:|
| UI-01 | Hide zero-demand rows（checkbox） | 預覽＋匯出 | ❌ |
| UI-02 | Hide all-zero SO（checkbox） | 預覽＋匯出 | ❌ |
| UI-03 | SO filter（文字輸入） | 預覽＋匯出 | ❌ |
| UI-04 | Mother/child filter（chip） | 預覽＋匯出 | ❌ |
| UI-05 | Cutting date range | 預覽＋匯出 | ❌ |
| UI-06 | Preview limit 300 rows | 僅顯示 | ❌ |

**注意：** 所有 UI filter **都不重新執行** `runAllocationEngine()`；僅對 `state.allResultRows` 做 slice + 條件過濾。

---

## E. 單位換算類型（6）+ 預設種子列（11）

### 6 種換算類型

| # | 母子單位 | 規則 |
|---|---------|------|
| 1 | 同單位 | 1:1 |
| 2 | M ↔ YD | 0.9144 / 1.0936（雙向） |
| 3 | SHT → M | 查 size-suffix 表（110x200cm=2, 220x110cm=2, 200x110cm=2.2） |
| 4 | SHT → YD | 查 size-suffix 表（110x200=2.187, 220x110=2.187, 200x110=2.406） |
| 5 | SHT → SHT | 1:1（含相同 size） |
| 6 | 無任何匹配 | ❌ **block + 提示 missing rule** |

### 11 筆預設種子列

| # | 類型 | 規則 | 可編輯？ |
|---|------|------|:-------:|
| 1 | Base | M → YD = 1.0936 | ✅ Reset 可復原 |
| 2 | Base | YD → M = 0.9144 | ✅ |
| 3 | Size | 110x200cm → M = 2 | ✅ |
| 4 | Size | 110x200cm → YD = 2.187227 | ✅ |
| 5 | Size | 110x200cm → SHT = 1 | ✅ |
| 6 | Size | 220x110cm → M = 2 | ✅ |
| 7 | Size | 220x110cm → YD = 2.187227 | ✅ |
| 8 | Size | 220x110cm → SHT = 1 | ✅ |
| 9 | Size | 200x110cm → M = 2.2 | ✅ |
| 10 | Size | 200x110cm → YD = 2.405949 | ✅ |
| 11 | Size | 200x110cm → SHT = 1 | ✅ |

---

## F. 匯入檢核類型（7）

| # | 檢核 | 條件 | 結果 |
|---|------|------|------|
| CHK-01 | 空檔案 | headers.length=0 || rows.length=0 | ❌ |
| CHK-02 | 最少欄數 | headers.length < guard.minCols | ❌ |
| CHK-03 | 必要欄位遺失 | cols[field.key] < 0 | ❌ |
| CHK-04 | Header alias 比對失敗 | normalizeHeader 後無 alias 匹配 | ❌ |
| CHK-05 | 該欄全空 | 抽樣無 non-blank value | ❌ |
| CHK-06 | 單位欄可疑 | >30% 樣值像 SO/date | ❌ |
| CHK-07 | 欄位型別不符 | so/date/number/unit 類型比對失敗 | ❌ |

---

## G. 配發排序層級（6）

| 優先 | 排序鍵 | 方向 | 說明 |
|:----:|--------|:----:|------|
| 1 | cutting | ASC | 最早生產日優先 |
| 2 | SO | ASC | 同 cutting 依訂單號 |
| 3 | hasMother | 0→1 | 有母料號列優先（C 欄非空） |
| 4 | mother | ASC | 同 SO 有母列依母料號 |
| 5 | child | ASC | 同母依子料號 |
| 6 | segment | ASC | 依 FLT/MTF 分組 |

---

## 三條權威公式（紅標）

### ① 廠外 pair = max(0, ΣJ − ΣP)
```
outside(mother, child, seg) = max(0, SUM(J) − SUM(P))
            WHERE J ≠ 0 AND L ≠ 0 AND storage NOT 39*
```
→ 母料顯示：同 mother+seg 下所有 child pair 的 Σoutside → col 7

### ② 廠內 = SUM(MB52 Unrestricted)
```
pool(X, seg) = SUM(MB52.Unrestricted)
               WHERE Material = X
                 AND Stock Segment = seg
                 AND Storage Location NOT LIKE '39%'
```
→ 母料顯示：col 6；子料池：col 14(start) + col 15(start)

### ③ provided = min(demand, max(0, remaining_pool))
```
provided = MIN(demand, MAX(0, poolBefore))
remaining = poolBefore − provided
```
**池 = 僅 MB52；廠外不扣池。**

---

## 對應程式函式定位

| 類別 | 函式 | 行數 (v3.1.6) |
|------|------|:------------:|
| A 輸出欄 | `OUT` / `outputHeadersForLang` | L1514-1533, L1643-1646 |
| A 表頭 | `OUTPUT_HEADERS_EN/ZH/MY` | L1553-1614 |
| A tips | `OUTPUT_TIP_KEYS` | L1616-1634 |
| B AGG-01~02 | `runAllocationEngine` — outsidePair / outsideByMother | L3785-3815 |
| B AGG-03 | `runAllocationEngine` — stockMb52 loop | L3817-3828 |
| B AGG-04~09 | `runAllocationEngine` — sets | L3830-3840 |
| B AGG-10 | `runAllocationEngine` — demand expansion | L3887-3970 |
| B AGG-11~13 | `runAllocationEngine` — allocation loop | L3998-4044 |
| B AGG-14 | `applyGroupYFlag` | L3665-3693 |
| C DEC-01 | `precheckUnitRH` | L3572-3643 |
| C DEC-02~08 | `runAllocationEngine` — ZRMM loop | L3747-3792 |
| C DEC-06~07 | suffixConflicts / childUnitConflicts check | L3794-3807 |
| C DEC-09~18 | `runAllocationEngine` — COOIS processing | L3876-3970 |
| C DEC-19~24 | `runAllocationEngine` — allocation | L3998-4044 |
| C DEC-25~28 | `applyGroupYFlag` | L3665-3693 |
| D UI-01~06 | `getFilteredRows` / `applyViewFilters` | L4084-4224 |
| E CONV | `conversionRatio` / `loadConversionRules` / `loadSizeConversionRules` | L2302-2360 |
| F CHK-01~07 | `validateImport` | L3388-3467 |
| G SORT-01~06 | `expanded.sort(...)` in `runAllocationEngine` | L3986-3996 |

---

## 條數核對表

| 來源 | 類別 | 宣告數 | 實際核對 | 匹配？ |
|------|------|:------:|:--------:|:-----:|
| Cursor spec | A 輸出欄 | 18 | 18 | ✅ |
| Cursor spec | B 加總樞紐 | ~14 | 14 | ✅ |
| Cursor spec | C 引擎決策 | ~26 | 28（含 missing-rule 細拆） | ✅ 略多 |
| Cursor spec | D UI-only | ~5 | 6（含 preview limit） | ✅ |
| Cursor spec | E 單位換算 | 6 | 6 | ✅ |
| Cursor spec | E 種子列 | 11 | 11 | ✅ |
| Cursor spec | F 匯入檢核 | 7 | 7 | ✅ |
| Cursor spec | G 排序層級 | 6 | 6 | ✅ |
| **總計** | | **~84** | **~85** | ✅ |

---

*Generated 2026-07-23 · v3.1.6 · 對照程式函式以 `allocation-web.html` 為準。不含真實業務料號/SO。*
