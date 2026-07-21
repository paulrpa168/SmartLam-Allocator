# 執行結果 — Allocation v2.2.2

## 版本

| 項目 | 值 |
|---|---|
| App version | **2.2.2** |
| Entry | `allocation-web.html` |
| Manual | `allocation-manual.html` |
| Spec | `docs/06-allocation-engine-spec.md` |
| Base | `8d4333f` (v2.1.1) |
| SHA-256 (`allocation-web.html`) | `2FAA1A76C20A7BFD25097C7992DBA81185CFDC6FD70428AE254AAA5F3D899533` |

## Diff（交 Codex 用）

| 檔案 | 大小 | 說明 |
|---|---|---|
| [**allocation-v2.2.2.diff**](allocation-v2.2.2.diff) | ~112 KB | **請用這份** — 自 v2.1.1 至目前工作區完整 diff（含 manual） |

### 變更檔案清單

| 檔案 | 變更 |
|---|---|
| `allocation-web.html` | v2.2.2 主程式（SHT 末碼、Y 群組、斑馬色、緬甸文、modal ×） |
| `allocation-manual.html` | **新建** — 三語操作手冊 |
| `docs/06-allocation-engine-spec.md` | 3.F、Y 群組規則 |
| `README.md` | 版本說明 |
| `verify_allocation.py` | SHT、群組 Y、3.F 衝突 |
| `run_real_allocation.py` | 同步引擎 |
| `fixtures/excel3.csv` | F 欄示範 |

## v2.2.2 已交付功能

### 配發引擎（v2.2.0+）
- Excel3.**F** 末碼 → SHT 換算表（可編輯，localStorage）
- 事前檢查 2.R vs 3.H；缺規則 modal 阻擋
- 10 欄輸出 + 貪婪配發（不變）

### v2.2.1
- 預覽／XLSX 斑馬色對比加強（`#c5d3e0`）
- **Y 欄**：同 SO+母料，全部子料 demand>0 且 provided≥demand 才標 Y

### v2.2.2
- 頂部 **操作手冊** 連結 → `allocation-manual.html`
- 語系：**English / 繁體中文 / မြန်မာ**
- 錯誤視窗右上角 **×** 可關閉

## 驗證

```text
python .ai/handoffs/20260718-raw-mat-allocation-v2/verify_allocation.py
→ ALL CHECKS PASSED
```

fixture 預期 Y：
- SO-A / MOTHER-1：兩列皆 `Y`（全配滿）
- SO-B / MOTHER-1：兩列皆空白（CHILD-2 短缺）

## Codex 品質閘門（2026-07-20）

- **判定**：`PASS`（12 項 post-check 全過）
- **報告**：[`cursor-handoff-v2.2.2-quality-review.md`](cursor-handoff-v2.2.2-quality-review.md)
- **Warning 處置**：W1／W2 **暫不修** — 見 `decisions.md` **D16**；日後複審。

## 待 Paul

- [x] Codex 審查 `allocation-v2.2.2.diff` → PASS
- [ ] 瀏覽器：手冊連結、緬甸文、錯誤 × 關閉（可選抽樣）
- [ ] 真實檔 UI 驗收（可選）

## Blockers

- GitHub push 未完成（與功能無關）
- `New data/` 未納入 diff（本地測試資料）

## Release assessment

`PASS`（Codex 閘門）— W1/W2 已知、刻意延期；真實檔 UI 驗收仍為可選。
