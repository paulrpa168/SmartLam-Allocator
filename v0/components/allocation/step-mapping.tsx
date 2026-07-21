"use client"

import { ArrowLeft, Play, Plus, RotateCcw, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Section, Hint } from "@/components/allocation/section"
import {
  DEFAULT_CONVERSIONS,
  DEFAULT_SIZE_CONVERSIONS,
  type ConversionRow,
  type MappingRow,
  type SizeConversionRow,
} from "@/lib/allocation-data"

type StepMappingProps = {
  mapping: MappingRow[]
  conversions: ConversionRow[]
  sizeConversions: SizeConversionRow[]
  setConversions: (rows: ConversionRow[]) => void
  setSizeConversions: (rows: SizeConversionRow[]) => void
  onBack: () => void
  onRun: () => void
  isRunning: boolean
}

let idSeed = 100
const nextId = () => `row-${idSeed++}`

export function StepMapping({
  mapping,
  conversions,
  sizeConversions,
  setConversions,
  setSizeConversions,
  onBack,
  onRun,
  isRunning,
}: StepMappingProps) {
  return (
    <Section
      title="Step 2 · Fixed mapping & allocate"
      badge="Fixed column mapping"
      description="Review detected columns and unit-conversion rules, then run the allocation."
    >
      <div className="grid gap-5">
        {/* Column mapping */}
        <div className="overflow-hidden rounded-xl border border-border">
          <div className="thin-scroll overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-surface/70 text-left text-xs uppercase tracking-wide text-muted-foreground">
                  <Th>Source</Th>
                  <Th>Column</Th>
                  <Th>Meaning</Th>
                  <Th>Detected header</Th>
                </tr>
              </thead>
              <tbody>
                {mapping.map((row, i) => (
                  <tr key={`${row.source}-${row.column}`} className={i % 2 ? "bg-surface/30" : "bg-card"}>
                    <Td>
                      <span className="font-medium text-foreground">{row.source}</span>
                    </Td>
                    <Td>
                      <span className="inline-grid h-6 min-w-6 place-items-center rounded-md bg-brand-muted px-1.5 font-mono text-xs font-semibold text-accent-foreground">
                        {row.column}
                      </span>
                    </Td>
                    <Td>{row.meaning}</Td>
                    <Td>
                      <code className="rounded bg-secondary px-1.5 py-0.5 font-mono text-xs text-secondary-foreground">
                        {row.detected}
                      </code>
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <Hint>
          Pre-check: Excel2.R must equal Excel3.H for the same mother. If 2.R = 3.M then 1:1; otherwise use the
          conversion table below. A missing rule blocks the run.
        </Hint>

        {/* Unit conversion */}
        <ConvBox
          title="Unit conversion whitelist"
          help="Mother unit × ratio = child demand. Defaults are editable; same units always resolve to 1:1."
          onAdd={() => setConversions([...conversions, { id: nextId(), motherUnit: "", childUnit: "", ratio: "1" }])}
          onReset={() => setConversions(DEFAULT_CONVERSIONS.map((r) => ({ ...r })))}
          headers={["Mother unit (2.R)", "Child unit (3.M)", "Ratio", ""]}
        >
          {conversions.map((row) => (
            <tr key={row.id} className="border-t border-border">
              <Td>
                <Cell
                  value={row.motherUnit}
                  onChange={(v) => setConversions(conversions.map((r) => (r.id === row.id ? { ...r, motherUnit: v } : r)))}
                />
              </Td>
              <Td>
                <Cell
                  value={row.childUnit}
                  onChange={(v) => setConversions(conversions.map((r) => (r.id === row.id ? { ...r, childUnit: v } : r)))}
                />
              </Td>
              <Td>
                <Cell
                  mono
                  value={row.ratio}
                  onChange={(v) => setConversions(conversions.map((r) => (r.id === row.id ? { ...r, ratio: v } : r)))}
                />
              </Td>
              <Td className="w-10">
                <RemoveBtn onClick={() => setConversions(conversions.filter((r) => r.id !== row.id))} />
              </Td>
            </tr>
          ))}
        </ConvBox>

        {/* Size conversion */}
        <ConvBox
          title="SHT size-suffix conversion"
          help="When mother unit (2.R) is SHT and the child unit differs, demand = Q × ratio (suffix read from Excel3.F). SHT→SHT is always 1:1."
          onAdd={() =>
            setSizeConversions([...sizeConversions, { id: nextId(), suffix: "", childUnit: "", ratio: "1" }])
          }
          onReset={() => setSizeConversions(DEFAULT_SIZE_CONVERSIONS.map((r) => ({ ...r })))}
          headers={["Size suffix (from 3.F)", "Child unit (3.M)", "Ratio", ""]}
        >
          {sizeConversions.map((row) => (
            <tr key={row.id} className="border-t border-border">
              <Td>
                <Cell
                  value={row.suffix}
                  onChange={(v) =>
                    setSizeConversions(sizeConversions.map((r) => (r.id === row.id ? { ...r, suffix: v } : r)))
                  }
                />
              </Td>
              <Td>
                <Cell
                  value={row.childUnit}
                  onChange={(v) =>
                    setSizeConversions(sizeConversions.map((r) => (r.id === row.id ? { ...r, childUnit: v } : r)))
                  }
                />
              </Td>
              <Td>
                <Cell
                  mono
                  value={row.ratio}
                  onChange={(v) =>
                    setSizeConversions(sizeConversions.map((r) => (r.id === row.id ? { ...r, ratio: v } : r)))
                  }
                />
              </Td>
              <Td className="w-10">
                <RemoveBtn onClick={() => setSizeConversions(sizeConversions.filter((r) => r.id !== row.id))} />
              </Td>
            </tr>
          ))}
        </ConvBox>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <Button variant="outline" onClick={onBack} className="h-10 gap-2 px-4">
            <ArrowLeft className="h-4 w-4" aria-hidden />
            Back to import
          </Button>
          <Button onClick={onRun} disabled={isRunning} className="h-10 gap-2 px-5">
            <Play className="h-4 w-4" aria-hidden />
            {isRunning ? "Running…" : "Run allocation"}
          </Button>
        </div>
      </div>
    </Section>
  )
}

function ConvBox({
  title,
  help,
  headers,
  onAdd,
  onReset,
  children,
}: {
  title: string
  help: string
  headers: string[]
  onAdd: () => void
  onReset: () => void
  children: React.ReactNode
}) {
  return (
    <div className="rounded-xl border border-border bg-surface/40 p-4">
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">{help}</p>
      <div className="mt-3 overflow-hidden rounded-lg border border-border bg-card">
        <div className="thin-scroll overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-surface/70 text-left text-xs uppercase tracking-wide text-muted-foreground">
                {headers.map((h, i) => (
                  <Th key={i}>{h}</Th>
                ))}
              </tr>
            </thead>
            <tbody>{children}</tbody>
          </table>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button variant="secondary" size="sm" onClick={onAdd} className="gap-1.5">
          <Plus className="h-3.5 w-3.5" aria-hidden />
          Add row
        </Button>
        <Button variant="ghost" size="sm" onClick={onReset} className="gap-1.5 text-muted-foreground">
          <RotateCcw className="h-3.5 w-3.5" aria-hidden />
          Reset defaults
        </Button>
      </div>
    </div>
  )
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="px-4 py-2.5 font-medium">{children}</th>
}

function Td({ children, className }: { children: React.ReactNode; className?: string }) {
  return <td className={`px-4 py-2.5 align-middle text-foreground ${className ?? ""}`}>{children}</td>
}

function Cell({ value, onChange, mono }: { value: string; onChange: (v: string) => void; mono?: boolean }) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`w-full rounded-md border border-input bg-card px-2 py-1 text-sm text-foreground outline-none transition-colors focus:border-ring focus:ring-2 focus:ring-ring/25 ${
        mono ? "font-mono" : ""
      }`}
    />
  )
}

function RemoveBtn({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="Remove row"
      className="grid h-7 w-7 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-warn-muted hover:text-warn"
    >
      <Trash2 className="h-4 w-4" aria-hidden />
    </button>
  )
}
