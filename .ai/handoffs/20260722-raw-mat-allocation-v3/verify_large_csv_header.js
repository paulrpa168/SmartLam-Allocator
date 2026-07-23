"use strict";
const fs = require("fs");
const path = require("path");

function splitLine(line, delimiter) {
  const cells = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (char === delimiter && !inQuotes) {
      cells.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  cells.push(current);
  return cells;
}

function detectDelimiter(text) {
  let end = text.indexOf("\n");
  if (end < 0) end = text.indexOf("\r");
  const first = (end < 0 ? text : text.slice(0, end)).replace(/\r$/, "");
  const commas = (first.match(/,/g) || []).length;
  const tabs = (first.match(/\t/g) || []).length;
  const semis = (first.match(/;/g) || []).length;
  if (tabs >= commas && tabs >= semis && tabs > 0) return "\t";
  if (semis > commas) return ";";
  return ",";
}

function looksChineseHeaderRow() {
  return false;
}
function rowHasEnglishKeys(row) {
  const joined = row.map((c) => String(c || "").toLowerCase()).join("|");
  return /sd document|material|open quantity|requirement segment/.test(joined);
}

function detectHeaderRow(rows) {
  if (!rows || !rows.length) return { headerRowIndex: 0, headers: [], dataRows: [], rows: [] };
  let width = 0;
  for (const row of rows) {
    if (row && row.length > width) width = row.length;
  }
  const padRow = (row) => {
    const out = new Array(width);
    for (let i = 0; i < width; i++) out[i] = row[i] ?? "";
    return out;
  };
  const row0 = padRow(rows[0] || []);
  const row1 = rows.length >= 2 ? padRow(rows[1] || []) : null;
  let headerRowIndex = 0;
  if (row1 && looksChineseHeaderRow(row0) && rowHasEnglishKeys(row1)) {
    headerRowIndex = 1;
  } else if (rowHasEnglishKeys(row0)) {
    headerRowIndex = 0;
  } else if (row1 && rowHasEnglishKeys(row1)) {
    headerRowIndex = 1;
  }
  const headerCells = headerRowIndex === 0 ? row0 : row1 || row0;
  const headers = headerCells.map((header, index) => String(header || `Column ${index + 1}`));
  const dataRows = [];
  for (let r = headerRowIndex + 1; r < rows.length; r++) {
    const row = rows[r] || [];
    const out = new Array(headers.length);
    for (let i = 0; i < headers.length; i++) out[i] = row[i] ?? "";
    dataRows.push(out);
  }
  return { headerRowIndex, headers, dataRows, rows: dataRows };
}

function parseTextTable(text) {
  const trimmed = String(text || "").replace(/^\uFEFF/, "").trim();
  if (!trimmed) return { headers: [], rows: [] };
  const delimiter = detectDelimiter(trimmed);
  const lines = trimmed.split(/\r?\n/).filter((line) => line.length);
  const rawRows = lines.map((line) => splitLine(line, delimiter));
  return detectHeaderRow(rawRows);
}

// Prove old bug
try {
  Math.max(...Array.from({ length: 130000 }, () => 36));
  console.error("unexpected: old spread did not throw");
  process.exit(2);
} catch (err) {
  console.log("old_bug_confirmed", err.message);
}

const csvPath = path.join("20260723", "Copy of COOIS.csv");
const t0 = Date.now();
const parsed = parseTextTable(fs.readFileSync(csvPath, "utf8"));
console.log(
  JSON.stringify(
    {
      ms: Date.now() - t0,
      headerRowIndex: parsed.headerRowIndex,
      headers: parsed.headers.slice(0, 8),
      dataRows: parsed.dataRows.length,
      heapMB: Math.round(process.memoryUsage().heapUsed / 1048576),
    },
    null,
    2
  )
);
if (parsed.dataRows.length < 100000) {
  console.error("too few rows");
  process.exit(3);
}
console.log("VERIFY_OK");
