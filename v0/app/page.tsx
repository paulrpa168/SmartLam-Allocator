"use client"

import { useState } from "react"
import { TopBar } from "@/components/allocation/top-bar"
import { Stepper, type Step } from "@/components/allocation/stepper"
import { StepImport } from "@/components/allocation/step-import"
import { StepMapping } from "@/components/allocation/step-mapping"
import { StepResults } from "@/components/allocation/step-results"
import {
  DEFAULT_CONVERSIONS,
  DEFAULT_MAPPING,
  DEFAULT_SIZE_CONVERSIONS,
  runMockAllocation,
  SAMPLE_EXCEL_1,
  SAMPLE_EXCEL_2,
  SAMPLE_EXCEL_3,
  type AllocationResult,
  type ConversionRow,
  type SizeConversionRow,
} from "@/lib/allocation-data"

const STEPS: Step[] = [
  { id: 1, title: "Import files", subtitle: "Excel sources" },
  { id: 2, title: "Mapping & run", subtitle: "Rules & allocate" },
  { id: 3, title: "Filter & preview", subtitle: "Review & export" },
]

const VERSION = "2.3.0"

export default function Page() {
  const [current, setCurrent] = useState(1)
  const [completed, setCompleted] = useState<number[]>([])
  const [status, setStatus] = useState("Ready")

  const [files, setFiles] = useState({ left: "", right: "", third: "" })
  const [conversions, setConversions] = useState<ConversionRow[]>(DEFAULT_CONVERSIONS.map((r) => ({ ...r })))
  const [sizeConversions, setSizeConversions] = useState<SizeConversionRow[]>(
    DEFAULT_SIZE_CONVERSIONS.map((r) => ({ ...r })),
  )
  const [result, setResult] = useState<AllocationResult | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  function goTo(id: number) {
    setCurrent(id)
    if (typeof window !== "undefined") window.scrollTo({ top: 0, behavior: "smooth" })
  }

  function markDoneAndGo(fromStep: number, to: number) {
    setCompleted((c) => (c.includes(fromStep) ? c : [...c, fromStep]))
    goTo(to)
  }

  function loadSample() {
    setFiles({ left: SAMPLE_EXCEL_1, right: SAMPLE_EXCEL_2, third: SAMPLE_EXCEL_3 })
    setStatus("Sample data loaded")
  }

  function runAllocation() {
    setIsRunning(true)
    setStatus("Running allocation…")
    setTimeout(() => {
      const res = runMockAllocation()
      setResult(res)
      setIsRunning(false)
      setStatus(`Done · ${res.stats.rowsExported} rows`)
      setCompleted((c) => Array.from(new Set([...c, 1, 2])))
      goTo(3)
    }, 700)
  }

  return (
    <div className="min-h-screen bg-background">
      <TopBar status={status} version={VERSION} />

      <main className="mx-auto grid max-w-7xl gap-5 px-4 py-6 sm:px-6 lg:px-10">
        <Stepper steps={STEPS} current={current} completed={completed} onSelect={goTo} />

        {current === 1 && (
          <StepImport
            values={files}
            onChange={(key, value) => setFiles((f) => ({ ...f, [key]: value }))}
            onLoadSample={loadSample}
            onNext={() => markDoneAndGo(1, 2)}
          />
        )}

        {current === 2 && (
          <StepMapping
            mapping={DEFAULT_MAPPING}
            conversions={conversions}
            sizeConversions={sizeConversions}
            setConversions={setConversions}
            setSizeConversions={setSizeConversions}
            onBack={() => goTo(1)}
            onRun={runAllocation}
            isRunning={isRunning}
          />
        )}

        {current === 3 && <StepResults result={result} onBack={() => goTo(2)} />}
      </main>

      <footer className="mx-auto max-w-7xl px-4 pb-10 pt-2 text-center text-xs text-muted-foreground sm:px-6 lg:px-10">
        RAW MAT Allocation Engine · v{VERSION} · UI reference build
      </footer>
    </div>
  )
}
