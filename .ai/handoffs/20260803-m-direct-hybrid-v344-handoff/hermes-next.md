# Hermes 後續安排建議 — v3.4.4 M hybrid

**Handoff path:** `.ai/handoffs/20260803-m-direct-hybrid-v344-handoff/`  
**Diff:** `allocation-v3.4.4.diff`  
**Base:** `84f5b58` (v3.4.3) → working tree v3.4.4（未 commit）

## 建議路由

```
Cursor 實作完成
  ↓
Hermes：Codex 品質閘門（code-reviewer + reality-checker）
  ↓
Paul：人工 UI／0730 錨點驗收
  ↓
Paul 指示後：atomic commit（feat: hybrid M-direct + formula toolbar v3.4.4）
```

## Codex 建議檢查清單

1. JS ↔ Python 混合規則／Y 是否完全鏡像（尤其 `L=0` 時不扣母池、R 扣 M）。
2. 匯出 Excel／CSV／Copy 前言列與 UI `formulaPanel` 文案一致（三語）。
3. 未改動 G pick-once／ambiguous confirm／排序（diff 範圍審查）。
4. `APP_VERSION` / config `appVersion` / spec 標題是否皆為 `3.4.4`。
5. `docs/03` SoT 改指向 `07-spec` 是否可接受（小範圍治理修正，可同 commit 或拆 `docs:`）。

## 不建議重做

- 不要重開規則討論（混合規則 A + Y 看 L 已定案，見 `decisions.md`）。
- 不要把 `0730/`、`0731/` 業務資料 commit 進 Git。

## Paul 決策點

| 決策 | 選項 |
|---|---|
| Commit | 單 commit vs `feat` + `docs` 拆分 |
| Codex review | 立刻 dispatch / 先人工 UI 再 review |
| 公式 xlsx | 僅保留 `_v3.4.4.xlsx` 或覆寫別名後刪除重複 |

## 一鍵給 Codex 的 scope 字串（可貼）

```
Review uncommitted v3.4.4 hybrid M-direct changes in RAW MAT Project.
Diff: .ai/handoffs/20260803-m-direct-hybrid-v344-handoff/allocation-v3.4.4.diff
Context: .ai/handoffs/20260803-m-direct-hybrid-v344-handoff/{brief,decisions,result}.md
Focus: correctness of L=0&M>0 → Q=0/R=P-M/no mother cover; L>0 Rule D; Y checks L only;
formula toolbar + export preamble; JS/Python parity; version 3.4.4 alignment.
Do not request reopening locked business decisions.
```
