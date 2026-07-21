# 任務簡報：RAW MAT 庫存配發引擎 v2.2.2

- **Task ID**：`20260718-raw-mat-allocation-v2`
- **Owner**：Cursor（實作）；Paul（驗收）；Codex（品質閘門）
- **Status**：implemented — fixture verify passed；待 Codex 品質閘門
- **App version**：`2.2.2`
- **Base commit**：`8d4333f`（v2.1.1）
- **Diff**：[`allocation-v2.2.2.diff`](allocation-v2.2.2.diff)（自 v2.1.1 起完整工作區變更，約 112 KB，含 manual）

## 目標

在 v2.1.1 配發引擎上，完成 v2.2 系列功能：SHT 末碼換算、Y 欄群組規則、UI 強化、三語系與操作手冊。

## 範圍（v2.2.0 → v2.2.2）

| 版本 | 內容 |
|---|---|
| v2.2.0 | SHT 末碼換算（Excel3.F）、可編輯換算表、localStorage |
| v2.2.1 | 斑馬色對比加強；Y 欄改為 SO+母料群組判定 |
| v2.2.2 | 操作手冊 `allocation-manual.html`；緬甸文 i18n；錯誤 modal 右上角 × 關閉 |

## 鎖定業務規則

| 項目 | 規則 |
|---|---|
| 末碼來源 | Excel3.**F** `Material Full Description(EN)` |
| SHT 換算 | 母 SHT + 子≠SHT → 查末碼表；SHT→SHT → 1:1 |
| Y 欄 | 同 SO+母料：全部子料 demand>0 且 provided≥demand → 群組全 Y |
| 語系 | EN / 繁中 / မြန်မာ（主程式與手冊共用 localStorage） |

## 變更檔案

- `allocation-web.html` — 主程式
- `allocation-manual.html` — 操作手冊（新建）
- `docs/06-allocation-engine-spec.md`、`README.md`
- `verify_allocation.py`、`run_real_allocation.py`、`fixtures/excel3.csv`

## 非目標

- 不 commit 真實 `1/2/3.xlsx`、`New data/`
- 不含 GitHub push

## Codex 驗收

見 [`codex-quality-gate.md`](codex-quality-gate.md)。
