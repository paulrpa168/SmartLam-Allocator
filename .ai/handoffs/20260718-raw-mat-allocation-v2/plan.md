# 執行計畫：allocation engine v2

## Scope

| 項目 | 作法 |
|---|---|
| 規格 | 鎖定規則寫入 `docs/06-allocation-engine-spec.md` |
| UI | 新建 `allocation-web.html`（不破壞舊 `vlookup-web.html`） |
| 解析／匯出 | 沿用 v1.1.0 本地 zip/xml 解析與 store-method OOXML |
| 驗證 | 去識別 CSV fixture + `verify_allocation.py` |
| 可選 | `smoke_real_counts.py` 僅印彙總計數 |

## Non-goals

- 不改業務規則（已 LOCKED）
- 不把真實 Excel 內容寫入 git／handoff
- 不自動 commit

## Implementation steps

1. 撰寫規格文件（繁中＋英文）
2. 實作配發核心：schedule earliest → SUM Q → BOM filter → MAX(K) → 1:1 expand → sort → greedy
3. 單檔 HTML：匯入 → 固定對應摘要 → 執行／預覽／匯出
4. 更新 README 產品定位與 deprecated 說明
5. Handoff + fixture verify；可選真實檔計數煙測

## Verification evidence expected

- `python verify_allocation.py` → `ALL CHECKS PASSED`
- `allocation-web.html` SHA-256 記錄於 `result.md`
- 真實檔煙測若存在：僅列數／匹配數，無樣本值
