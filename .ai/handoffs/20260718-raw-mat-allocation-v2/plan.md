# 執行計畫：v2.2.2 完整交付

## Diff 位置

| 檔案 | 說明 |
|---|---|
| [`allocation-v2.2.2.diff`](allocation-v2.2.2.diff) | **最新** — 自 `8d4333f` 至工作區（含 manual、i18n、modal ×） |
| [`allocation-v2.2.0.diff`](allocation-v2.2.0.diff) | 舊版（僅 v2.2.0 核心，已過時） |

## 實作摘要

### v2.2.0 核心
- `COL.excel3.descF = 5`；`extractSizeSuffix()` / `sizeConversionRules`
- Step 2「SHT 末碼換算」UI + localStorage `rawmat.allocation.sizeConversionRules.v22`
- 引擎：`motherSuffix` from 3.F；`conversionRatio()` 分支 SHT

### v2.2.1 UI/邏輯
- 斑馬色 `#c5d3e0` / `#ffffff`（預覽 + XLSX）
- `applyGroupYFlag()` — SO+母料群組 Y

### v2.2.2 文件與 UX
- `allocation-manual.html` — 三語操作手冊，頂部連結
- `translations.my` + `OUTPUT_HEADERS_MY`
- `LANG_STORAGE_KEY` 主程式／手冊同步
- `#errorModalX` 右上角關閉

## 驗證

```powershell
cd "D:\0.AI-Agent-Workspace\03_projects\RAW MAT Project"
python .ai/handoffs/20260718-raw-mat-allocation-v2/verify_allocation.py
```

預期：`ALL CHECKS PASSED`

## 給 Codex 的審查重點

1. `descF: 5`（非 3.J）
2. `applyGroupYFlag` 群組邏輯
3. 錯誤 modal 可關閉（× + OK）
4. 緬甸文 key 覆蓋主要 UI
5. 不含真實 xlsx
