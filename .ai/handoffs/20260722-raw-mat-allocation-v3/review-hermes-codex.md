# Codex 靜態品質審查報告 — RAW MAT Allocation v3.1.3

**審查日期：** 2026-07-23  
**Commit：** `ac618e9`（parent `fe7b59f` / v3.0.0）  
**Diff：** `allocation-v3.1.3.diff`  
**真實 Codex：** ✅ 是  
**Codex CLI：** `~/codex-cli.exe` **0.140.0-alpha.2**  
**Model：** `gpt-5.5`（強制指定；避開 config 預設 `gpt-5.6-luna` 不相容）  
**Sandbox：** `read-only`  
**Tokens used：** **103,246**  
**原始輸出：** [codex-review-raw.md](./codex-review-raw.md)  
**Stdout log：** [codex-review-stdout.log](./codex-review-stdout.log)

> 由 Cursor 直接調度真實 Codex CLI；Hermes 負責交件同步與 Telegram 摘要（非 Hermes 代審）。

---

## Verdict：**NEEDS WORK**

Critical：**0**　High：**0**　Medium：**1**　Low：**2**

核心配發引擎可接受；文件版本不一致與交付證據未完全版本化，尚不足以 APPROVE。

---

## Findings（Codex）

### Critical
無。

### High
無。

### Medium

| # | 檔案 | 問題 | 風險 | 建議 |
|---|------|------|------|------|
| M1 | `README.md`（約 L7 / L35） | 仍寫入口／App version `v3.1.2`，但 `APP_VERSION = "3.1.3"` | 驗收與追蹤版本錯位 | README 全部改為 `3.1.3` |

### Low

| # | 檔案 | 問題 | 風險 | 建議 |
|---|------|------|------|------|
| L1 | `allocation-web.html` 檔頭註解 | 仍寫 `Version: 3.0.0`，runtime 為 `3.1.3` | 人工追溯誤判 | 同步檔頭註解 |
| L2 | handoff 交件 | `allocation-v3.1.3.diff`、`brief.md`、`result.md` 等未進 `ac618e9` | 無法從該 commit 完整重建審查證據 | 納入版本化，或標明「commit 後產生」 |

---

## Reality Check（Codex 通過項）

- 16 欄契約：JS `OUT`、EN/ZH/MY headers、tips、Python `OUTPUT_HEADERS` 基本一致  
- F/G/P 已刪；`stock available` = MB52-only running pool，不扣 outside  
- `child demand`／子材料需求更名完成，語意仍為母料展開量  
- Y 排除 MH04；FLT/MTF 分池；MH04 保留輸出  
- JS ↔ Python 镜像高度一致  
- `fe7b59f..ac618e9` 僅 5 個文字檔；無 xlsx／secrets 進 commit  

**Codex 重跑測試：**

```text
PASS ×9 fixture + New_0722 smoke OK（out_rows=465）
```

---

## 測試缺口（Codex）

1. 缺 JS 端 golden snapshot（不能只靠 Python mirror）  
2. 缺 CSV/Excel 16 欄＋三語表頭 snapshot  
3. 缺 UI 匯入 E2E（xlsx／雙表頭／語言／匯出）  
4. 缺負向測試（缺欄、空 Segment、未知 unit、SHT suffix、全 MH04 Y）  
5. 缺 release hygiene（版本號跨 README／手冊／規格／檔頭一致）

---

## 給 Paul 的短結論

邏輯本體接近過關。先補 **README／檔頭版本一致性**（最快），再視需要補 golden／UI 證據，才升級到 release APPROVE。

---

## Follow-up（2026-07-23 Cursor）

已修復 Codex M1／L1／L2：
1. README 版本字串 → `3.1.3`
2. `allocation-web.html` 檔頭註解 → `Version: 3.1.3`；`docs/07` 同步
3. 本 handoff 交件（diff／brief／result／Codex 報告等）納入 git commit

---

## Archive：先前 Hermes-only 審查（2026-07-22）

上次因 Codex CLI 不支援 `gpt-5.6-luna`，曾由 Hermes 代審並誤標部分 High。本次以真實 Codex `gpt-5.5` 為準；舊結論僅供對照，不以 Hermes-only 為最終依據。

---

*Generated from real Codex CLI · synced for Hermes/Telegram · 2026-07-23*
