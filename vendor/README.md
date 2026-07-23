# Vendored Excel parser

`xlsx.full.min.js` is the SheetJS community build used by `allocation-web.html` for offline `.xlsx` / `.xlsm` import.

Keep this file next to `allocation-web.html` (same relative path `vendor/xlsx.full.min.js`). Opening only the HTML without this file will show a clear import error.

Do not replace with a CDN `<script>` — this project stays local/offline-first.
