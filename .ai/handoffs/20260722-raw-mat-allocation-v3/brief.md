# brief.md — RAW MAT Allocation v3.1.4（請 Hermes → Codex 品質審查）

**任務類型：** code-review / 品質閘門  
**目標審查者：** Codex（`agency-code-reviewer` + `agency-reality-checker`）  
**語言：** 繁體中文回覆  
**日期：** 2026-07-23  
**Base：** `3ccdadd`（v3.1.3 hygiene，已 push）  
**工作樹：** 尚未 commit（請審 `allocation-v3.1.4.diff`）

---

## 1. 變更摘要

相對 v3.1.3，在輸出 **母單位之後** 新增兩欄（僅顯示，不影響配發）：

| 欄位 | 規則 |
|------|------|
| 廠內母材料庫存 / mother plant stock | MB52 Unrestricted SUM；Material + Stock Segment；排除儲位 39* |
| 廠外母材料庫存 / mother stock outside | ZRMM：J=0 或 L=0 不計；pair `max(0,ΣJ−ΣP)`；同母+Batch 加總所有子料 |

- 輸出 **16 → 18** 欄；`APP_VERSION = 3.1.4`
- 可配發池仍 = **子料 MB52 only**
- 無母料列：兩新欄空白

## 2. 請審查的 diff

| 檔案 | 說明 |
|------|------|
| [allocation-v3.1.4.diff](./allocation-v3.1.4.diff) | `git diff HEAD`（相對 `3ccdadd`） |

**納入路徑：** `allocation-web.html`、`allocation-manual.html`、`README.md`、`docs/07-allocation-v3-spec.md`、`verify_allocation_v3.py`

## 3. 規格

[`docs/07-allocation-v3-spec.md`](../../../docs/07-allocation-v3-spec.md) — 輸出 18 欄；§3／§4 母庫存顯示規則

## 4. 測試證據

見 [result.md](./result.md)。`verify_allocation_v3.py` 含新 fixture `test_mother_outside_clamps_negative_pair`（例型 J−P&lt;0 → 0）。

## 5. Codex 重點

1. 18 欄 OUT／EN·ZH·MY／tips 一致；Y 索引正確  
2. 母兩欄僅顯示、不進配發池  
3. outside：J/L 過濾、39*、Segment 鎖定、加總語意  
4. 母廠內：MB52 排除 39*（含 39G2）  
5. JS ↔ Python 镜像一致  
6. 無 secrets／xlsx 誤入 diff  

## 6. 期望產出

Findings（Critical/High/Medium/Low）+ 測試缺口 + Verdict（APPROVE / NEEDS WORK / BLOCK）。  
預設 NEEDS WORK。**不要修改業務檔案**。報告寫入 `review-hermes-codex.md`（文首標 v3.1.4）。
