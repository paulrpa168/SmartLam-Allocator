# 任務簡則：RAW MAT 庫存配發引擎 v2

- Task ID：`20260718-raw-mat-allocation-v2`
- Owner：Cursor（實作）；Paul（驗收）
- Status：implemented — fixture verify passed
- App version：`2.0.0`

## 目標

依已鎖定業務規則實作離線配發引擎，取代舊兩段式 VLOOKUP 作為產品方向。

## 範圍

1. `docs/06-allocation-engine-spec.md`（繁中在前、英文緊接）
2. 新入口 `allocation-web.html`（v2.0.0）
3. 更新 `README.md`（產品目的、deprecated 舊檔、資料邊界）
4. 本 handoff：brief / plan / decisions / result + 去識別 fixture + verify script

## 非目標

- 不提交真實 `1.xlsx` / `2.xlsx` / `3.xlsx`
- 不在 handoff 貼真實料號／SO
- 不刪除 `vlookup-web.html`（僅標記 deprecated）
- 未要求前不 git commit

## 成功標準

- Fixture 證明：MAX(K)、貪婪扣減、一母二子、短缺、剩餘遞減、輸出欄序
- UI：三檔上傳、固定對應摘要、預覽、CSV（BOM+公式中和）與離線 XLSX
- `markResultDirty`；cutting 可讀日期；EN + 繁中
