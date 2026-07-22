# Review: RAW MAT Allocation v3.0.0 — Hermes + Codex 靜態品質審查

**日期：** 2026-07-22  
**審查者：** Hermes (DeepSeek V4 Flash) → Codex (GPT-5.5)  
**Diff：** `allocation-v3.0.0.diff`（3575 行，主要 ~2212 行在 `allocation-web.html`）  
**Verdict：** **NEEDS WORK**

---

## 1. Hermes 自評風險摘要

### 正向觀察

| 項目 | 狀態 |
|------|------|
| 四輸入架構（Schedule/COOIS/ZRMM0028/MB52） | ✅ 完整實作 |
| 英文表頭解析（`detectHeaderRow` / `FIELD_ALIASES` / `findCol`） | ✅ 正確，Open Quantity vs Quantity withdrawn 不會誤綁 |
| 雙表頭偵測（中文→英文） | ✅ `looksChineseHeaderRow` + `rowHasEnglishKeys` |
| 廠外庫存 `max(0, ΣJ−ΣP)` | ✅ 按 mother\0child\0seg 聚合 |
| MB52 SUM + 39* 排除 | ✅ 正確 |
| Segment FLT/MTF 鎖定（空白不混配） | ✅ `childrenForMotherSeg` 回傳 exact match only |
| 雙重身分母料自我排除 | ✅ `expandedMothers` Set 阻擋 |
| 17 欄輸出（含雙 BATCH、庫存拆分、Y） | ✅ 欄序與規格 `docs/07` 一致 |
| `stock available` 語意 = MB52 − 廠外 | ✅ 財報欄位顯示計算值，配發 clamp ≥ 0 |
| 匯出安全（CSV formula injection 防護、XLSX inlineStr） | ✅ |
| `New_0722/` 已進 `.gitignore` | ✅ |
| 測試 fixture 4 項 PASS + 真實資料 smoke 2579 列 | ✅ |

### 需關注

| 項目 | 風險 |
|------|------|
| 多 mother 展開同一 child + child 自身 direct demand | Medium — direct 量全部併到排序後的第一個 mother row |
| 根目錄 `0028.xlsx` / `MB52_new.xlsx` 未 ignore | Medium — 可能誤提交真實資料 |
| MY 語系 `mapStock` 翻譯殘留 v2「MAX」 | Low — 應為 SUM |
| 無 JS 層直接測試（Python mirror 非 JS） | High — 實際 browser 行為未驗證 |

---

## 2. Codex Findings（GPT-5.5 靜態分析）

**Medium**
1. **Multi-mother direct demand merge** — `allocation-web.html` `runAllocationEngine`：同一 SO+Segment+child 若由多個 mother 展開，child 的 direct demand 全部併到 `mother.localeCompare()` 排序後的第一個 mother row。現有 fixture 未覆蓋此情境。建議：明確定義多 mother 時 direct demand 應拆成獨立 direct row、按比例分攤，或阻擋並提示。
2. **`.gitignore` 缺 root xlsx** — 根目錄 `0028.xlsx`、`MB52_new.xlsx` 未追蹤但不在 ignore 清單，`git add .` 易誤提交真實資料。建議：加入 `/0028.xlsx` 與 `/MB52_new.xlsx`。

**Low**
3. **MY 翻譯殘留** — `allocation-web.html:2177` `mapStock` 仍寫 `Unrestricted (... MAX)`，v3 規格是 SUM。建議：改為 SUM，全面掃 v3 文案殘留。
4. **README.md trailing whitespace** — 行尾空白讓 diff hygiene 檢查失敗。

### Codex 測試缺口清單

- 缺 JS-level smoke test（驗證腳本是 Python mirror，非執行 `allocation-web.html` 的 `runAllocationEngine`）
- 缺 browser E2E（四檔上傳/貼上、run allocation、預覽、CSV/XLSX 匯出）
- 缺多 mother 同 child + direct demand 測試
- 缺 duplicate header fixture（ZRMM0028 多個 `Storage Location` 時必須取第一個）
- 缺 blank segment direct/stock 對帳測試
- 缺 17 欄 golden output snapshot（鎖定欄序、欄名、`stock available = MB52 - outside`）

### Codex Token 使用

- Token count：85,980 tokens
- 僅靜態分析，未修改程式

---

## 3. 合併 Verdict

**NEEDS WORK**

核心引擎邏輯（四輸入解析、過濾、廠外、MB52 SUM、Segment 鎖定、展開＋直接需求、17 欄輸出、Y 標記）正確符合 `docs/07-allocation-v3-spec.md`。4 項 fixture 測試 + 真實資料 2579 列 smoke 均 PASS。

但 2 項 Medium Finding 應在合併前處理：
1. 多 mother→child 的 direct demand 歸屬邊界（需業務決策後補測試）
2. `.gitignore` 補上根目錄真實 xlsx（低風險快速 fix）

此外，JS-level smoke test 與 browser E2E 應列為產出正式版本前的必要品質閘門。

---

## 4. 建議下一步

1. [P0] 補 `.gitignore` 排除 `0028.xlsx` / `MB52_new.xlsx`（1 分鐘）
2. [P1] 確認多 mother→child 的 direct demand 業務規則
3. [P1] 補 JS-level smoke test（可用 Node.js + jsdom 或 headless browser）
4. [P2] 補 MY `mapStock` 翻譯修正
5. [P2] 移除 README.md trailing whitespace
