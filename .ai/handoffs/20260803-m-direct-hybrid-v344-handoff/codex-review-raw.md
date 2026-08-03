**審查結論：NEEDS WORK**

未發現 Critical/High 的業務規則破壞；JS 與 Python mirror 的 hybrid 主邏輯看起來一致。但有兩個交付一致性問題，依你指定的預設門檻，我不建議直接 APPROVE。

**Findings**

Medium - 規格文件仍殘留 `appVersion: "3.4.3"` 範例。  
[docs/07-allocation-v3-spec.md](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/docs/07-allocation-v3-spec.md:145) 的 Shared JSON format 範例還是 `3.4.3`，雖然 spec title、Version、APP_VERSION、`config/conversion-rules.v1.json` 都已是 `3.4.4`。這會讓「APP_VERSION / config appVersion / spec title all = 3.4.4」主檢查大致通過，但治理上仍有版本混淆風險，尤其這段是使用者會照抄的 config 格式範例。

Low - Export preamble 未完整涵蓋 UI formula panel 的 summary 文字。  
[allocation-web.html](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:4890) 會在 UI formula panel 顯示 `formulaHybridSummary`，但 [allocation-web.html](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:4900) 的 `exportPreambleMatrix()` 只輸出三列：欄位代號、欄名、逐欄 formula notes。若驗收定義是「export preamble 要等同 formulaPanel 全部文字」，目前少了 hybrid summary；若定義只要求表格列一致，則可接受但應明確記錄。

**規則核對**

Hybrid 運算主體看起來正確：`L=0,M>0` 不扣母池、`Q=0`、`R=P-M`；`L>0` 仍讓母池覆蓋 `N=L+M`，不足進 `Q`，`R=P-Q`；`L=0,M=0` 會自然得到 `Q=0,R=P`。對應 JS 在 [allocation-web.html](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:4513) 與 [allocation-web.html](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:4572)，Python mirror 在 [verify_allocation_v3.py](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py:543) 與 [verify_allocation_v3.py](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py:591)。

Y flag 靜態看起來與規格一致：以 `SO + mother(C欄) + Segment` 分組，只檢查非 MH04 且 `L>0` 的列，沒有 `L>0` 不給 Y。JS 在 [allocation-web.html](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:4102)，Python 在 [verify_allocation_v3.py](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py:637)。

G pick-once、ambiguous confirm、排序在 diff 範圍內沒有看到實質改動；主要是提示文字與 hybrid 計算改動。`docs/03` 指向 `docs/07-allocation-v3-spec.md` 作為 current public behavior contract 是可接受的小治理修正。

**Test Gaps**

我依照「Static review only」沒有執行 pytest、UI、CSV 或 XLSX 匯出測試。handoff 宣稱 Python 20 passed 與 Excel 未測，但本次未重新驗證。仍需要手動 UI/CSV/XLSX acceptance，尤其是三語 preamble 與實際匯出檔開啟結果。

**給 Paul 的短結論**

v3.4.4 的核心 hybrid M-direct 規則看起來已正確落在 JS 與 Python mirror；但文件版本範例殘留 3.4.3，加上 export preamble 是否要包含 formula summary 尚未完全對齊。建議修正這兩點後再 APPROVE。  
