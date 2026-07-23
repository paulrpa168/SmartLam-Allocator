# brief.md — RAW MAT Allocation v3.1.3（請 Hermes → Codex 品質審查）

**任務類型：** code-review / 品質閘門  
**目標審查者：** Codex（`agency-code-reviewer` + `agency-reality-checker`）  
**語言：** 繁體中文回覆  
**日期：** 2026-07-22  
**Git commit：** `ac618e9`（parent `fe7b59f` / v3.0.0）  
**已 push：** `origin/master`

---

## 1. 變更摘要

相對 v3.0.0 的增量（**v3.1.3**）：

| 項目 | 變更 |
|------|------|
| 可配發池 | **Option A**：pool = **MB52 only**；子料廠外**不扣池** |
| 輸出欄 | **19 → 16**：刪除 F 母材料廠內、G 母材料廠外、P 子材料廠外 |
| 更名 | 原「母料展開需求」→ **子材料需求**（EN: `child demand`） |
| 引擎 | 不再聚合／輸出 outside／母料 MB52 顯示欄；ZRMM 仍做 BOM 展開（不因 J/L=0 丢掉） |
| App | `APP_VERSION = 3.1.3` |

## 2. 請審查的 diff

| 檔案 | 說明 |
|------|------|
| [allocation-v3.1.3.diff](./allocation-v3.1.3.diff) | `fe7b59f..ac618e9` unified diff（約 1200+ 行） |

**納入 diff 的路徑：**
- `allocation-web.html`
- `allocation-manual.html`
- `README.md`
- `docs/07-allocation-v3-spec.md`
- `.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py`

**刻意排除：**
- `New_0722/`、`bk_0722/`、真實 xlsx
- 舊 `allocation-v3.0.0.diff` / `allocation-v3-utf8.diff`（歷史交件，非本次審查對象）

## 3. 規格對照

- 現行規格：[`docs/07-allocation-v3-spec.md`](../../../docs/07-allocation-v3-spec.md)（輸出 **16 欄**；廠外不輸出、不扣池）

## 4. 已執行測試（證據）

見同目錄 [result.md](./result.md)。

指令：

```text
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
```

全部 fixture PASS + New_0722 smoke OK。

## 5. 請 Codex 重點檢查

1. **輸出契約：** 16 欄順序／表頭（EN/ZH/MY）與 `OUT.*` 索引、`applyGroupYFlag` 是否一致  
2. **池語意：** `stock available` / remaining 皆為 MB52 剩餘；不再出現 outside 扣減  
3. **刪欄完整性：** 預覽／CSV／Excel／tips／i18n 無殘留 F/G/P 或 mother stock 欄  
4. **更名：** `child demand` / 子材料需求 語意仍 = 母料展開量（非 demand total）  
5. **JS ↔ Python 镜像：** `verify_allocation_v3.py` 與 `runAllocationEngine` 是否同步  
6. **回歸風險：** Y 標記、FLT/MTF 分池、MH04 略過配套、母列排序、雙重身分  
7. **安全性：** 無 secrets；真實 xlsx 未進 diff  
8. **測試缺口：** 是否需補瀏覽器 E2E／golden 16 欄 snapshot

## 6. 期望產出

請以繁體中文回覆：

1. **Findings**（Critical / High / Medium / Low）— 每條含檔案／問題／風險／建議  
2. **測試缺口**  
3. **Verdict：** `APPROVE` / `NEEDS WORK` / `BLOCK`

預設傾向：**沒有壓倒性證據不要 APPROVE**（reality-checker）。  
**不要修改業務檔案**，只做審查；最終報告寫入 `review-hermes-codex.md`（可覆寫或標註 v3.1.3 段落）。
