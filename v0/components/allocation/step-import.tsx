"use client"

import { useRef } from "react"
import { ArrowRight, FileSpreadsheet, Sparkles, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Section, Hint } from "@/components/allocation/section"

type FileKey = "left" | "right" | "third"

type StepImportProps = {
  values: Record<FileKey, string>
  onChange: (key: FileKey, value: string) => void
  onLoadSample: () => void
  onNext: () => void
}

const CARDS: { key: FileKey; title: string; role: string; required: boolean }[] = [
  { key: "left", title: "Excel 1 — Orders", role: "SO + cutting date", required: true },
  { key: "right", title: "Excel 2 — Mother stock", role: "Mother material + unit", required: true },
  { key: "third", title: "Excel 3 — Child demand", role: "Child material + qty", required: false },
]

export function StepImport({ values, onChange, onLoadSample, onNext }: StepImportProps) {
  const filledCount = Object.values(values).filter((v) => v.trim().length > 0).length
  const canContinue = values.left.trim() && values.right.trim()

  return (
    <Section
      title="Step 1 · Import Excel files"
      badge={`${filledCount}/3 sources loaded`}
      description="Upload .xlsx / .csv or paste tab-separated data. Excel 1 and Excel 2 are required."
    >
      <div className="grid gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Hint tone="brand">
            New here? Load a sanitized demo dataset to explore the full workflow without your own files.
          </Hint>
          <Button variant="outline" size="sm" onClick={onLoadSample} className="gap-2 whitespace-nowrap">
            <Sparkles className="h-4 w-4" aria-hidden />
            Load sample data
          </Button>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          {CARDS.map((card) => (
            <ImportCard
              key={card.key}
              card={card}
              value={values[card.key]}
              onChange={(v) => onChange(card.key, v)}
            />
          ))}
        </div>

        <div className="flex justify-end pt-1">
          <Button onClick={onNext} disabled={!canContinue} className="h-10 gap-2 px-5">
            Next: mapping &amp; run
            <ArrowRight className="h-4 w-4" aria-hidden />
          </Button>
        </div>
      </div>
    </Section>
  )
}

function ImportCard({
  card,
  value,
  onChange,
}: {
  card: { key: FileKey; title: string; role: string; required: boolean }
  value: string
  onChange: (value: string) => void
}) {
  const fileRef = useRef<HTMLInputElement>(null)
  const rows = value.trim() ? value.trim().split("\n").length - 1 : 0

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => onChange(String(reader.result ?? ""))
    reader.readAsText(file)
  }

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border bg-surface/40 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-muted text-accent-foreground">
            <FileSpreadsheet className="h-4.5 w-4.5" aria-hidden />
          </span>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{card.title}</h3>
            <p className="text-xs text-muted-foreground">{card.role}</p>
          </div>
        </div>
        <span
          className={
            card.required
              ? "rounded-full bg-warn-muted px-2 py-0.5 text-[11px] font-medium text-warn"
              : "rounded-full bg-secondary px-2 py-0.5 text-[11px] font-medium text-muted-foreground"
          }
        >
          {card.required ? "Required" : "Optional"}
        </span>
      </div>

      <input ref={fileRef} type="file" accept=".xlsx,.xls,.csv,.txt" onChange={handleFile} className="sr-only" />
      <button
        type="button"
        onClick={() => fileRef.current?.click()}
        className="flex items-center justify-center gap-2 rounded-lg border border-dashed border-border bg-card py-3 text-sm font-medium text-muted-foreground transition-colors hover:border-brand/50 hover:text-foreground"
      >
        <Upload className="h-4 w-4" aria-hidden />
        Choose file
      </button>

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
        placeholder="…or paste tab-separated rows here"
        className="thin-scroll min-h-28 w-full resize-y rounded-lg border border-input bg-card p-3 font-mono text-xs leading-relaxed text-foreground outline-none transition-colors focus:border-ring focus:ring-2 focus:ring-ring/25"
      />

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{rows > 0 ? `${rows} data row${rows === 1 ? "" : "s"}` : "No data yet"}</span>
        <button
          type="button"
          onClick={() => onChange("")}
          className="font-medium text-muted-foreground underline-offset-2 hover:text-foreground hover:underline disabled:opacity-40"
          disabled={!value}
        >
          Clear
        </button>
      </div>
    </div>
  )
}
