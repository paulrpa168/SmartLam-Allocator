**Findings**

Critical：無。

High：無。

Medium：
- [README.md](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/README.md:7) / [README.md](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/README.md:35)：README 仍宣稱入口與 App version 是 `v3.1.2`，但實作 `allocation-web.html` 的 `APP_VERSION` 已是 `3.1.3`。  
  風險：交付審核、使用者驗收、後續 issue/commit 追蹤會對不上版本。  
  建議：README 全部 `v3.1.2` 更新為 `v3.1.3`，並與 release assessment 同步。

Low：
- [allocation-web.html](D:/0.AI-Agent-Workspace/03_projects/RAW%20MAT%20Project/allocation-web.html:4)：檔頭註解仍寫 `Version: 3.0.0`，但 runtime `APP_VERSION` 是 `3.1.3`。  
  風險：靜態檢查或人工追溯時容易誤判版本。  
  建議：同步檔頭版本註解。
- `.ai/handoffs/20260722-raw-mat-allocation-v3/allocation-v3.1.3.diff` 與 `verify-stdout-v313.txt` 目前是 untracked；`brief.md` / `result.md` 也有工作樹修改。  
  風險：交付證據無法完全從 commit `ac618e9` 重建。  
  建議：若這是正式交付包，應把 handoff 證據納入明確版本化流程，或在 handoff 中標明「commit 後產生、未納入 commit」。

**Reality Check**

通過項目：
- 16 欄契約在 JS `OUT`、EN/ZH/MY headers、tips、Python `OUTPUT_HEADERS` 基本一致。
- F/G/P 舊輸出欄已移除；`stock available` 以 MB52-only running pool 計算，未扣 outside。
- `child demand` 更名完成，語意仍是母料展開量。
- Y flag 有排除 MH04 的 `toCheck`；FLT/MTF 分池用 `Material + Segment` key；MH04 保留輸出但不阻擋 Y。
- JS `runAllocationEngine` 與 Python `verify_allocation_v3.py` 的核心索引與流程高度鏡像。
- `git diff --name-only fe7b59f ac618e9` 只含 5 個文字檔；`git ls-tree` 未發現 v3.1.3 commit 誤入 `.xlsx/.xls/.xlsm` 或明顯 secrets。工作區有真實 xlsx，但未進 commit。

我重新執行了：
`PYTHONDONTWRITEBYTECODE=1 python .ai\handoffs\20260722-raw-mat-allocation-v3\verify_allocation_v3.py`

結果：9 個 fixture PASS，`New_0722` smoke OK，`out_rows=465`。

**測試缺口**

- 缺 JS 端直接執行的 golden snapshot，不能只靠 Python mirror 證明 browser/export 完全一致。
- 缺 CSV/Excel 匯出檔的 16 欄欄序與三語表頭 snapshot。
- 缺真實 UI 匯入流程驗證：xlsx 讀取、雙表頭偵測、語言切換、匯出後欄寬/樣式。
- 缺負向測試：缺欄、空 Segment、未知 unit、SHT suffix 缺失、全 MH04 group 的 Y 行為。
- 缺 release hygiene test：版本號、README、手冊、規格、handoff 一致性。

**Verdict：NEEDS WORK**

核心 allocation engine 看起來可接受，但文件版本不一致與交付證據未完全版本化，還不足以在 reality-checker 標準下 APPROVE。給 Paul 的短結論：邏輯本體接近過關，先補版本一致性與 golden/export/UI 證據，再升級到 release approval。  
