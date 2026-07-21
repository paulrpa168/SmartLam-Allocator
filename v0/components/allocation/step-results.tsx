"use client"

import { useMemo, useState } from "react"
import { ArrowLeft, CircleHelp, Copy, Download, FileDown, Search, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Section } from "@/components/allocation/section"
import { RESULT_HEADERS, type AllocationResult, type ResultRow } from "@/lib/allocation-data"
import { cn } from "@/lib/utils"

type StepResultsProps = {
  result: AllocationResult | null
  onBack: () => void
}

const STAT_META = [
  { key: "rowsExported", label: "Rows exported", tip: "Rows in the current filtered export set." },
  { key: "demandKeys", label: "Demand keys kept", tip: "Distinct SO × child-material combinations." },
  { key: "mothersMatched", label: "Mothers matched", tip: "Distinct mother materials matched to demand." },
  {
    key: "shortage",
    label: "Shortage (full run)",
    tip: "Rows where provided qty < demand qty. Not affected by filters above.",
    warn: true,
  },
] as const

export function StepResults({ result, onBack }: StepResultsProps) {
  const [so, setSo] = useState("")
  const [mothers, setMothers] = useState<string[]>([])
  const [motherInput, setMotherInput] = useState("")
  const [hideZeroRows, setHideZeroRows] = useState(false)
  const [from, setFrom] = useState("")
  const [to, setTo] = useState("")

  const rows = result?.rows ?? []

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      if (so && !r.so.toLowerCase().includes(so.toLowerCase())) return false
      if (mothers.length && !mothers.some((m) => r.motherMaterial.toLowerCase().includes(m.toLowerCase())))
        return false
      if (hideZeroRows && r.demandQty === 0) return false
      if (from && r.cutting < from) return false
      if (to && r.cutting > to) return false
      return true
    })
  }, [rows, so, mothers, hideZeroRows, from, to])

  const stats = {
    rowsExported: filtered.length,
    demandKeys: new Set(filtered.map((r) => `${r.so}|${r.childMaterial}`)).size,
    mothersMatched: new Set(filtered.map((r) => r.motherMaterial)).size,
    shortage: result?.stats.shortage ?? 0,
  }

  const hasResult = Boolean(result)

  function addMother(value: string) {
    const v = value.trim()
    if (v && !mothers.includes(v)) setMothers([...mothers, v])
    setMotherInput("")
  }

  return (
    <Section
      title="Step 3 · Filter, preview & export"
      badge="Preview max 300 rows · export uses full filtered set"
      description="Filters stay on this page and instantly refresh both the preview and the export set."
    >
      <div className="grid gap-5">
        {/* Filter panel */}
        <div className="grid gap-4 rounded-xl border border-border bg-surface/40 p-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Field label="Filter SO">
              <div className="relative">
                <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
                <input
                  value={so}
                  onChange={(e) => setSo(e.target.value)}
                  placeholder="Type prefix, e.g. SO-A"
                  className="w-full rounded-lg border border-input bg-card py-2 pl-9 pr-3 text-sm text-foreground outline-none transition-colors focus:border-ring focus:ring-2 focus:ring-ring/25"
                />
              </div>
            </Field>

            <Field label="Cutting from / to">
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="date"
                  value={from}
                  onChange={(e) => setFrom(e.target.value)}
                  className="w-full rounded-lg border border-input bg-card px-2.5 py-2 text-sm text-foreground outline-none transition-colors focus:border-ring focus:ring-2 focus:ring-ring/25"
                />
                <input
                  type="date"
                  value={to}
                  onChange={(e) => setTo(e.target.value)}
                  className="w-full rounded-lg border border-input bg-card px-2.5 py-2 text-sm text-foreground outline-none transition-colors focus:border-ring focus:ring-2 focus:ring-ring/25"
                />
              </div>
            </Field>

            <Field label="Filter mother">
              <input
                value={motherInput}
                onChange={(e) => setMotherInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.nativeEvent.isComposing) {
                    e.preventDefault()
                    addMother(motherInput)
                  }
                }}
                placeholder="Type prefix, then Enter"
                className="w-full rounded-lg border border-input bg-card px-3 py-2 text-sm text-foreground outline-none transition-colors focus:border-ring focus:ring-2 focus:ring-ring/25"
              />
            </Field>
          </div>

          {mothers.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              {mothers.map((m) => (
                <span
                  key={m}
                  className="inline-flex items-center gap-1.5 rounded-full bg-brand-muted py-1 pl-3 pr-1.5 text-xs font-medium text-accent-foreground"
                >
                  {m}
                  <button
                    type="button"
                    onClick={() => setMothers(mothers.filter((x) => x !== m))}
                    aria-label={`Remove ${m}`}
                    className="grid h-4 w-4 place-items-center rounded-full hover:bg-brand/20"
                  >
                    <X className="h-3 w-3" aria-hidden />
                  </button>
                </span>
              ))}
              <button
                type="button"
                onClick={() => setMothers([])}
                className="text-xs font-medium text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
              >
                Clear all
              </button>
            </div>
          )}

          <label className="flex w-fit cursor-pointer items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={hideZeroRows}
              onChange={(e) => setHideZeroRows(e.target.checked)}
              className="h-4 w-4 rounded border-input accent-[var(--brand)]"
            />
            Hide rows where demand qty = 0
          </label>
        </div>

        {/* Stat band */}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {STAT_META.map((meta) => (
            <StatCard
              key={meta.key}
              label={meta.label}
              tip={meta.tip}
              value={hasResult ? stats[meta.key] : 0}
              warn={"warn" in meta ? meta.warn : false}
            />
          ))}
        </div>

        {/* Results table */}
        {!hasResult ? (
          <EmptyState />
        ) : (
          <div className="overflow-hidden rounded-xl border border-border">
            <div className="thin-scroll max-h-[520px] overflow-auto">
              <table className="w-full border-collapse text-sm">
                <thead className="sticky top-0 z-10">
                  <tr className="bg-surface text-left text-xs uppercase tracking-wide text-muted-foreground">
                    {RESULT_HEADERS.map((h) => (
                      <th
                        key={h}
                        className={cn(
                          "whitespace-nowrap border-b border-border px-3 py-3 font-medium",
                          isNumericHeader(h) && "text-right",
                        )}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan={RESULT_HEADERS.length} className="px-4 py-10 text-center text-sm text-muted-foreground">
                        No rows match the current filters.
                      </td>
                    </tr>
                  ) : (
                    filtered.map((row, i) => <ResultTr key={i} row={row} zebra={i % 2 === 1} />)
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <Button variant="outline" onClick={onBack} className="h-10 gap-2 px-4">
            <ArrowLeft className="h-4 w-4" aria-hidden />
            Back to mapping
          </Button>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" disabled={!hasResult} className="h-10 gap-2 px-4">
              <Copy className="h-4 w-4" aria-hidden />
              Copy table
            </Button>
            <Button variant="secondary" disabled={!hasResult} className="h-10 gap-2 px-4">
              <FileDown className="h-4 w-4" aria-hidden />
              Export CSV
            </Button>
            <Button disabled={!hasResult} className="h-10 gap-2 px-5">
              <Download className="h-4 w-4" aria-hidden />
              Export Excel
            </Button>
          </div>
        </div>
      </div>
    </Section>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="grid gap-1.5">
      <span className="text-xs font-semibold text-muted-foreground">{label}</span>
      {children}
    </label>
  )
}

function StatCard({ label, tip, value, warn }: { label: string; tip: string; value: number; warn?: boolean }) {
  return (
    <div className="group relative rounded-xl border border-border bg-card p-4 shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span className="text-muted-foreground/60" title={tip}>
          <CircleHelp className="h-3.5 w-3.5" aria-hidden />
        </span>
      </div>
      <p
        className={cn(
          "mt-2 text-2xl font-bold tabular tracking-tight",
          warn && value > 0 ? "text-warn" : "text-foreground",
        )}
      >
        {value}
      </p>
    </div>
  )
}

function ResultTr({ row, zebra }: { row: ResultRow; zebra: boolean }) {
  const short = row.providedQty < row.demandQty
  return (
    <tr className={cn("border-b border-border/70 transition-colors hover:bg-brand-muted/40", zebra && "bg-surface/30")}>
      <Cell className="whitespace-nowrap font-mono text-xs text-muted-foreground">{row.cutting}</Cell>
      <Cell className="font-medium text-foreground">{row.so}</Cell>
      <Cell className="whitespace-nowrap">{row.motherMaterial}</Cell>
      <Cell>
        <Unit>{row.motherUnit}</Unit>
      </Cell>
      <Cell className="whitespace-nowrap">{row.childMaterial}</Cell>
      <Cell>
        <Unit>{row.childUnit}</Unit>
      </Cell>
      <Cell className="text-right tabular">{row.demandQty}</Cell>
      <Cell className={cn("text-right tabular", short && "font-semibold text-warn")}>{row.providedQty}</Cell>
      <Cell className="text-right tabular text-muted-foreground">{row.remainingStock}</Cell>
      <Cell className="text-right">
        {row.allocated === "Y" ? (
          <span className="inline-flex items-center rounded-full bg-ok-muted px-2 py-0.5 text-xs font-semibold text-ok">
            Y
          </span>
        ) : (
          <span className="text-muted-foreground">—</span>
        )}
      </Cell>
    </tr>
  )
}

function Cell({ children, className }: { children: React.ReactNode; className?: string }) {
  return <td className={cn("px-3 py-2.5 align-middle text-foreground", className)}>{children}</td>
}

function Unit({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex rounded-md bg-secondary px-1.5 py-0.5 font-mono text-[11px] font-medium text-secondary-foreground">
      {children}
    </span>
  )
}

function EmptyState() {
  return (
    <div className="grid place-items-center rounded-xl border border-dashed border-border bg-surface/40 px-6 py-16 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full bg-brand-muted text-accent-foreground">
        <Search className="h-5 w-5" aria-hidden />
      </div>
      <p className="mt-3 text-sm font-medium text-foreground">No results yet</p>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">
        Run the allocation from Step 2 to preview and export the matched rows here.
      </p>
    </div>
  )
}

function isNumericHeader(h: string) {
  return ["Demand qty", "Provided qty", "Remaining stock", "Allocated (Y)"].includes(h)
}
