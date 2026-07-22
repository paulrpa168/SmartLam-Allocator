# result.md — 測試與交付紀錄（v3.0.0）

**日期：** 2026-07-22  
**App：** `allocation-web.html` `APP_VERSION = 3.0.0`  
**規格：** `docs/07-allocation-v3-spec.md`  
**Diff：** [allocation-v3.0.0.diff](./allocation-v3.0.0.diff)  
**審查交辦：** [brief.md](./brief.md)

---

## 變更檔案

| 路徑 | 類型 |
|------|------|
| `allocation-web.html` | 主程式升版 v3 |
| `allocation-manual.html` | 手冊四檔／17 欄 |
| `README.md` | 入口改 v3 |
| `.gitignore` | 排除 `New_0722/` |
| `docs/07-allocation-v3-spec.md` | 新規格 |
| `verify_allocation_v3.py` | Fixture + New_0722 smoke |

---

## 測試指令與輸出

```text
python .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py
```

```text
PASS test_find_col_open_quantity
PASS test_expand_plus_direct_and_outside
PASS test_mother_not_double_counted
PASS test_segment_lock_blank
New_0722 smoke OK: schedule=733 coois=16325 zrmm=16275 mb52=7019 out_rows=2579 MA020162253_rows=18

All v3 fixture checks passed.
```

### Fixture 涵義（對應業務規則）

1. **test_find_col_open_quantity** — 表頭解析必須拿到 `Open Quantity`，不可誤用 `Quantity withdrawn`
2. **test_expand_plus_direct_and_outside** — 母展開＋子直接合併；outside=max(0,20−8)=12；MB52 SUM=50；pool=38；cutting 早者先配；Y 標記
3. **test_mother_not_double_counted** — 雙重身分 `MA020162253`：展開後不產生母料自身 blank-mother 列；SHT→M 換算 2×2=4
4. **test_segment_lock_blank** — 0028 Batch 空白時不對 FLT 展開
5. **New_0722 smoke** — 真實四報表可跑通（本機資料，未進 git）

---

## 已知限制（請審稿者留意）

1. 驗證為 **Python 镜像**，非瀏覽器執行 JS
2. **尚未**做 UI 四檔上傳端到端
3. MY 語系部分文案偏短／混英文（鍵齊全）
4. `docs/01`～`05` 未全面改寫為 v3（以 docs/07 為準）

---

## 建議 Hermes 轉交 Codex 的 prompt（可直接貼）

```text
請以 agency-code-reviewer + reality-checker 審查 RAW MAT Allocation v3.0.0。

工作目錄：RAW MAT Project
Diff：.ai/handoffs/20260722-raw-mat-allocation-v3/allocation-v3.0.0.diff
Brief：.ai/handoffs/20260722-raw-mat-allocation-v3/brief.md
規格：docs/07-allocation-v3-spec.md
測試證據：同目錄 result.md

請用繁體中文輸出 Findings（Critical/High/Medium/Low）、測試缺口、Verdict（APPROVE / NEEDS WORK / BLOCK）。
預設 NEEDS WORK，除非有壓倒性證據。
不要修改程式，只做審查。
```
