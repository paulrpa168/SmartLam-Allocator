# Codex 驗證 — 複製貼上 Prompt

請依 handoff 目錄 `.ai/handoffs/20260718-raw-mat-allocation-v2/` 執行品質閘門：

1. 讀取 `codex-quality-gate.md`、`brief.md`、`result.md`
2. 審查 diff：`allocation-v2.2.2.diff`（自 commit `8d4333f` v2.1.1 至目前工作區）
3. 執行：
   ```powershell
   cd "D:\0.AI-Agent-Workspace\03_projects\RAW MAT Project"
   python .ai/handoffs/20260718-raw-mat-allocation-v2/verify_allocation.py
   ```
4. 重點確認：
   - SHT 末碼來自 Excel3.F（`descF: 5`），非 3.J
   - `applyGroupYFlag` 群組 Y 邏輯
   - `allocation-manual.html` 三語操作手冊
   - 錯誤 modal 右上角 × 可關閉
   - 緬甸文 i18n（`translations.my`）
5. 回報：缺陷清單（severity + 位置）、建議 diff（若有）、`NEEDS WORK` 或 `PASS` 判定

**SHA-256**（`allocation-web.html`）：`2FAA1A76C20A7BFD25097C7992DBA81185CFDC6FD70428AE254AAA5F3D899533`  
**App version**：2.2.2
