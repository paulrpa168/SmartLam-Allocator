# brief.md — RAW MAT Allocation v3.0.0（請 Hermes → Codex 品質審查）

**任務類型：** code-review / 品質閘門  
**目標審查者：** Codex（`agency-code-reviewer`）  
**語言：** 繁體中文回覆  
**日期：** 2026-07-22  

---

## 1. 變更摘要

將配發引擎由 v2（Excel1/2/3）升版為 **v3.0.0**（四輸入）：

| 槽位 | 檔案角色 |
|------|----------|
| Schedule | 訂單 + cutting |
| COOIS | 需求（Open Quantity + Requirement Segment） |
| ZRMM0028 | 母子 BOM + 廠外（J/L/P） |
| MB52 | 廠內 Unrestricted |

核心規則：英文表頭解析、雙表頭偵測、廠外 `max(0,ΣJ−ΣP)`、MB52 SUM、Segment FLT/MTF 鎖定、母料展開＋子料直接加成、舊版單位換算、cutting 貪婪、**17 欄輸出**（含 Y）。

## 2. 請審查的 diff

| 檔案 | 說明 |
|------|------|
| [allocation-v3.0.0.diff](./allocation-v3.0.0.diff) | 相對 `HEAD`（`333536d`）之完整 unified diff ≈ 3575 行 |

**納入 diff 的路徑：**
- `allocation-web.html`（主程式）
- `allocation-manual.html`、`README.md`、`.gitignore`
- `docs/07-allocation-v3-spec.md`（新規格）
- `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`
- `.ai/handoffs/20260722-raw-mat-allocation-v3/result.md`

**刻意排除（勿納入審查／勿提交）：**
- `New_0722/`、根目錄 `0028.xlsx` / `MB52_new.xlsx`（真實業務資料）
- `allocation-web-v2.4.0-backup.html`（本機備份）

## 3. 規格對照

- 現行規格：[`docs/07-allocation-v3-spec.md`](../../../docs/07-allocation-v3-spec.md)
- v2 歷史：`docs/06-allocation-engine-spec.md`（Deprecated）

## 4. 已執行測試（證據）

指令：

```text
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
```

結果（2026-07-22）：

```text
PASS test_find_col_open_quantity
PASS test_expand_plus_direct_and_outside
PASS test_mother_not_double_counted
PASS test_segment_lock_blank
New_0722 smoke OK: schedule=733 coois=16325 zrmm=16275 mb52=7019
  out_rows=2579 MA020162253_rows=18
All v3 fixture checks passed.
```

### 測試覆蓋說明

| 項目 | 狀態 |
|------|------|
| Fixture：展開＋直接、廠外、MB52 SUM、過濾、Y、17 欄 | ✅ PASS |
| Fixture：母料展開後不重複扣母料庫存（雙重身分） | ✅ PASS |
| Fixture：空白 Segment 不與 FLT 混配 | ✅ PASS |
| Fixture：Open Quantity ≠ Quantity withdrawn | ✅ PASS |
| 真實 `New_0722/` Python 規則镜像 smoke | ✅ 可跑通產出 2579 列 |
| 瀏覽器實際上傳四檔端到端 | ❌ **尚未做** |

> 注意：驗證腳本是 **Python 規則镜像**，不是直接執行 `allocation-web.html` 內的 JS。審查時請特別核對 JS 引擎與 Python 镜像是否語意一致。

## 5. 請 Codex 重點檢查

1. **正確性：** `runAllocationEngine` 是否符合 docs/07（過濾、outside、pool、展開／直接、換算、貪婪、Y）
2. **表頭解析：** `detectHeaderRow` / `FIELD_ALIASES` / `IMPORT_GUARDS` 是否會誤绑 `Quantity withdrawn`
3. **雙重身分料號：** 母展開後 skip 母料自身 direct；子料 direct 併入展開列
4. **Segment 鎖定：** 空白不與 FLT/MTF 互配；0028.Batch 必須對齊
5. **輸出契約：** 17 欄順序、`stock available` = 起始池 MB52−outside（非列前剩餘）
6. **安全性／資料：** 無 secrets；真實 xlsx 未進 diff
7. **可維護性：** 巨型單檔 HTML 內引擎是否有明顯重複／死碼／i18n 缺漏
8. **測試缺口：** 建議是否補 JS 層 smoke 或瀏覽器 E2E

## 6. 期望產出（給 Codex）

請以繁體中文回覆，結構建議：

1. **Findings**（依嚴重程度：Critical / High / Medium / Low）
2. 每條附：**檔案／函式、問題、為何有風險、建議修法**
3. **測試缺口** 清單
4. **Verdict：** `APPROVE` / `NEEDS WORK` / `BLOCK`

預設傾向：**沒有壓倒性證據不要 APPROVE**（reality-checker）。
