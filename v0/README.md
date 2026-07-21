# v0 — UI design reference only

> **不是正式配發程式。** 請使用專案根目錄的 [`allocation-web.html`](../allocation-web.html)。

## 用途 / Purpose

- v0 為 [v0.dev](https://v0.dev) 產生的 **Next.js 視覺原型**（版面、色彩、元件風格）。
- 樣式已整合進 `allocation-web.html`（v2.4.0+）；此資料夾僅供設計對照與日後改版參考。

## 重要限制 / Limitations

| 項目 | v0 | 正式產品 `allocation-web.html` |
|------|-----|--------------------------------|
| 配發演算法 | **Mock**（見 `lib/allocation-data.ts` 註解） | 真實 Excel 解析 + `runAllocationEngine()` |
| 欄位對照 | 示意用，可能與 `COL` 索引不一致 | 固定 `COL` / `OUT`（見 `docs/06`） |
| 部署 | 需 `pnpm install` + Next.js | 單檔離線，雙擊即可 |

## 本地預覽（可選）

```bash
cd v0
pnpm install
pnpm dev
```

不需為工廠現場部署此目錄；現場請只發佈 `allocation-web.html` 與 `allocation-manual.html`。
