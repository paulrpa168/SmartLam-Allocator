# Codex Review — RAW MAT Allocation v3.4.4 (M Direct Hybrid)

**日期：** 2026-08-03  
**版本：** v3.4.4  
**審查方式：** 真實 Codex CLI（非 Hermes 代審）  
**Model：** gpt-5.5（Codex CLI v0.145.0）  
**Tokens：** 124,336  
**Base：** `84f5b58`（v3.4.3）→ 工作樹 v3.4.4（未 commit）  
**Handoff：** `.ai/handoffs/20260803-m-direct-hybrid-v344-handoff/`

---

## Verdict：NEEDS WORK

---

## 外部測試結果（Hermes 獨立執行）

```text
python -m pytest .ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py -q --tb=line
20 passed in 0.04s
```

---

## Codex 審查發現

### Critical：0

### High：0

### Medium：1
1. **規格文件殘留 `appVersion: "3.4.3"` 範例**  
   - `docs/07-allocation-v3-spec.md:145` 的 Shared JSON format 範例仍是 `3.4.3`  
   - spec title、Version、`APP_VERSION`、`config/conversion-rules.v1.json` 都已是 `3.4.4`，但此段是使用者會照抄的 config 格式範例，版本混淆風險

### Low：1
2. **Export preamble 未完整涵蓋 UI formula panel 的 summary 文字**  
   - `allocation-web.html:4890` UI formula panel 顯示 `formulaHybridSummary`，但 `exportPreambleMatrix()`（L4900）只輸出三列（欄位代號／欄名／逐欄 notes），缺少 hybrid summary  
   - 若驗收定義是「export preamble = formulaPanel 全部文字」則未對齊；若只要求表格列一致則可接受但需明確記錄

---

## 規則核對結果（Codex 靜態）

| 規則 | 狀態 | 位置 |
|------|------|------|
| `L=0,M>0` → 不扣母池、`Q=0`、`R=P−M` | ✅ 正確 | JS L4513 / Py L543 |
| `L>0` → Rule D 蓋 `N=L+M`、不足進 Q、`R=P−Q` | ✅ 正確 | JS L4572 / Py L591 |
| `L=0,M=0` → `Q=0,R=P` | ✅ 自然成立 | — |
| Y flag：只查非 MH04 且 `L>0`；無 L>0 不標 Y | ✅ 正確 | JS L4102 / Py L637 |
| G pick-once／ambiguous confirm／排序未改動 | ✅ 無實質改動 | diff scope |
| `docs/03` SoT 指向 `07-spec` | ✅ 可接受治理修正 | — |
| JS ↔ Python mirror 一致 | ✅ 主邏輯一致 | — |

---

## 測試缺口

- Codex 依「Static review only」未重跑 pytest／UI／CSV／XLSX
- Hermes 外部執行：**20 passed** ✅
- 仍待人工：瀏覽器六步互動、三語 export preamble 實際開啟、XLSX 匯出驗收

---

## 給 Paul 的結論

v3.4.4 核心 hybrid M-direct 規則已正確落在 JS 與 Python mirror，Y flag 邏輯與 spec 一致，G pick-once／排序未受影響。但兩點交付一致性問題：

1. **修 `docs/07` L145 的 JSON 範例 `3.4.3` → `3.4.4`**（Medium）
2. **確認 export preamble 是否需含 formulaHybridSummary**（Low，或明確定義範圍）

修正後即可 APPROVE。人工 UI／0730 錨點驗收仍為 Paul 決策點。

---

*本報告由 Codex CLI（gpt-5.5）產出 + Hermes 外部 pytest 驗證合併。*
