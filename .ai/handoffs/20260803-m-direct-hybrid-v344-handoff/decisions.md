# Decisions — M 直接需求混合規則 v3.4.4

**日期：** 2026-08-03  
**範圍：** RAW MAT Allocation Engine

## 已核准 / Approved

1. **報表對象**：托外合貼供應商（outside lamination）。純直接需求不發外。
2. **混合規則採範圍 A（逐 `I` 子材料列）**，非整 SO／整母料一次切換。
3. **`L=0` 且 `M>0`：** 母池不抵 M；`Q=0`；`R=P−M`。
4. **`L>0`：** 維持現行 Rule D，母池先蓋 `N=L+M`；不足由子料 MB52 進 `Q`；`R=P−Q`（此分支不再額外扣 M）。
5. **Y：** 只看非 MH04 且 `L>0`；條件為 `母蓋L + Q ≥ L`；純 M／全無 L>0 → Y 空白。
6. **處理順序不變：** cutting → 同 SO + 母材料 + Segment 依序。
7. **UI：** Step3 統計列下、預覽表上固定「匯出＋公式說明」工具列；底部匯出鈕保留同 handler；匯出檔含代號／名稱／公式前言。
8. **版本號：** `APP_VERSION` / `appVersion` / spec → **3.4.4**。

## 不做 / Out of scope

- G pick-once 行為變更
- Ambiguous direct confirm 流程變更
- 大流程排序變更

## 錨點語意（0730 / MN090157252 / MA020165546）

早期 SO 多為 `L=0`：`Q=0`，`R` 依 M 遞減，Y 空白；母池不被 M 燒光，後續 SO 的 L 仍可為 0／Q=0。
