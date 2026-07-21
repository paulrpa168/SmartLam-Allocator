"use client"

import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

export type Step = {
  id: number
  title: string
  subtitle: string
}

type StepperProps = {
  steps: Step[]
  current: number
  completed: number[]
  onSelect: (id: number) => void
}

export function Stepper({ steps, current, completed, onSelect }: StepperProps) {
  return (
    <nav aria-label="Progress" className="grid gap-2 sm:grid-cols-3">
      {steps.map((step) => {
        const isActive = step.id === current
        const isDone = completed.includes(step.id)
        return (
          <button
            key={step.id}
            type="button"
            onClick={() => onSelect(step.id)}
            aria-current={isActive ? "step" : undefined}
            className={cn(
              "group flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-all",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40",
              isActive
                ? "border-brand bg-card shadow-sm ring-1 ring-brand/20"
                : "border-border bg-card/60 hover:border-brand/40 hover:bg-card",
            )}
          >
            <span
              className={cn(
                "grid h-8 w-8 flex-none place-items-center rounded-full font-mono text-sm font-semibold transition-colors",
                isActive
                  ? "bg-brand text-brand-foreground"
                  : isDone
                    ? "bg-ok text-ok-foreground"
                    : "bg-secondary text-muted-foreground",
              )}
            >
              {isDone && !isActive ? <Check className="h-4 w-4" aria-hidden /> : step.id}
            </span>
            <span className="min-w-0">
              <span
                className={cn(
                  "block text-sm font-semibold leading-tight",
                  isActive ? "text-foreground" : "text-muted-foreground",
                )}
              >
                {step.title}
              </span>
              <span className="block truncate text-xs text-muted-foreground">{step.subtitle}</span>
            </span>
          </button>
        )
      })}
    </nav>
  )
}
