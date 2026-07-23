**Findings**

Critical：未發現。

High：
- [allocation-web.html](/D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:1572) 的 ZH 表頭與 [allocation-web.html](/D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:1593) 的 MY 表頭目前呈現 mojibake/亂碼；tooltip 文案也同樣受影響。這直接違反「18 欄輸出契約 EN/ZH/MY 表頭/tips 一致」的交付要求。即使 EN 18 欄與 OUT 索引正確，使用者在中文/緬文模式看到的是不可驗收的輸出契約。

Medium：
- [verify_allocation_v3.py](/D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py:857) 的 New_0722 smoke 只確認 engine 可跑、列數與部分欄位解析，沒有對真實資料抽樣斷言「母料 MB52 SUM」、「outside per child clamp 後母料加總」、「OUT 18 欄匯出值」是否等於人工/獨立計算結果。fixture 有覆蓋公式，但真實資料證據仍偏弱。
- [allocation-web.html](/D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:3708) 與 [verify_allocation_v3.py](/D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/.ai/handoffs/20260722-raw-mat-allocation-v3/verify_allocation_v3.py:170) 是高度鏡像，這有利於同步，但 reality-check 角度不能替代獨立 oracle。若 JS 與 Python 對規格同時誤解，現有測試不容易抓出來。

Low：
- 工作樹有未追蹤資料夾 `20260723/`、`bk_0722/`，其中含多個真實 `.xlsx`。我在 `allocation-v3.1.4.diff` 內未搜到 `.xlsx`、常見 secret/private-key/token 字樣，但 commit 前若使用寬鬆 `git add .` 仍有誤入風險。

**測試缺口**

已執行驗證器，結果 PASS；`New_0722` smoke 也通過。缺口是沒有獨立計算的真實資料抽樣，例如指定 2-3 個 mother+segment，從 MB52/ZRMM 原表重算後比對輸出欄 6/7；也沒有瀏覽器端匯出檔檢查 EN/ZH/MY 三種 header 與 tooltip 實際顯示。

**Verdict：NEEDS WORK**

核心 allocation 邏輯目前沒有看到破壞子料可配發池、provided、Y 的明顯問題；MB52 排除 39*、outside J/L gate、per-child clamp、display-only 的方向也一致。但多語表頭/tips 亂碼屬於輸出契約失敗，不能 approve。

**給 Paul 的短結論**

v3.1.4 的公式方向可以往前，但交付品質還沒過線。先修中文/緬文表頭與 tips 編碼，再補一個真實 New_0722 抽樣重算證據；完成後再進下一輪 review。  
