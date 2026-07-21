# RAW MAT Allocation Engine v2.2.2 — Codex Quality Review Handoff

> **給 Cursor：** 這是 Codex 做完品質閘門後的改善建議。請閱讀後評估是否要修正。

---

## 判定：PASS ✅

12 項 post-check 全部通過，verify 通過，無 blocking 缺陷。

---

## 可選改善項目（Warning，低嚴重度）

### W1 — `normalizeSizeSuffix` 雙重 match 邏輯

**檔案：** `allocation-web.html`
**行數：** ~1240-1248

**現狀：**
```js
function normalizeSizeSuffix(value) {
  const text = String(value || "").trim().toLowerCase().replace(/\s+/g, "");
  const match = text.match(/^(\d+)[x×*](\d+)cm$/i) || String(value || "").match(SIZE_SUFFIX_RE);
  if (match && match[1] && match[2]) {
    return `${match[1]}x${match[2]}cm`.toLowerCase();
  }
  if (!text) return "";
  return text.replace(/[×*]/g, "x");
}
```

**問題：**
1. 先對去空白後的 `text` match，失敗後又回頭對原始 `value` match，邏輯重複
2. 若完全無匹配，回傳 `text.replace(/[×*]/g, "x")` — garbage in, garbage out

**建議改成（與 `extractSizeSuffix` 統一邏輯）：**
```js
function normalizeSizeSuffix(value) {
  const raw = String(value || "");
  const match = raw.replace(/\s+/g, " ").trim().match(SIZE_SUFFIX_RE);
  if (match && match[1] && match[2]) {
    return `${match[1]}x${match[2]}cm`.toLowerCase();
  }
  return "";
}
```

---

### W2 — 非標準 suffix 可能不命中

**檔案：** `allocation-web.html`
**行數：** ~1241 vs 1251

`normalizeSizeSuffix` 完全移除空白；`extractSizeSuffix` 壓成單空格再 match。
兩者最終輸出格式相同，無實質問題。

但若使用者在自訂規則輸入了 `"220x110"`（不含 `cm`），`normalizeSizeSuffix` 會回傳 `"220x110"`，此值永遠不會與 `extractSizeSuffix` 的回傳值匹配（後者一定回傳 `xxxcm` 格式），導致該規則永不被命中，使用者又看不到錯誤。

**建議：** 在 `normalizeSizeSuffix` 中若最終格式不含 `cm`，回傳空字串讓它 fall through。

---

## 附：12 項 Post-Check 一覽（供參考）

| # | 檢查項目 | 結果 |
|---|---------|:----:|
| 1 | 語法 | ✅ |
| 2 | 欄位 3.F (descF:5) | ✅ |
| 3 | SHT 換算 | ✅ |
| 4 | 不寫死倍率 | ✅ |
| 5 | Y 群組 | ✅ |
| 6 | 測試覆蓋 | ✅ |
| 7 | Modal × 關閉 | ✅ |
| 8 | 緬甸文 i18n | ✅ |
| 9 | 操作手冊 | ✅ |
| 10 | 敏感資訊 | ✅ |
| 11 | 文件一致 | ✅ |
| 12 | Greedy/10 欄 | ✅ |

---

---

## Cursor / Paul 處置（2026-07-20）

- **判定採納**：維持 **PASS**，不擋發布。
- **W1 / W2**：評估後 **暫不修改**；理由與複審觸發已寫入 `decisions.md` **D16**、`result.md`。
- **日後複審**：若現場出現「換算表有列卻 missing-size-rule」，或下一版整理 size-suffix API，再決定是否收緊 `normalizeSizeSuffix` + 呼叫端 `|| raw` fallback。

**By Codex (GPT-5.5) + Hermes (DeepSeek)**  
**Cursor 備註：Paul 決定 defer W1/W2 — 2026-07-20**
