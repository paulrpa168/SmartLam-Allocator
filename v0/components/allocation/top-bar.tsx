"use client"

import { LayoutGrid, Languages, Palette } from "lucide-react"

type TopBarProps = {
  status: string
  version: string
}

export function TopBar({ status, version }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-card/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-10">
        <div className="flex min-w-0 items-center gap-3">
          <div className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-brand text-brand-foreground shadow-sm">
            <LayoutGrid className="h-5 w-5" aria-hidden />
          </div>
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Inventory Allocation
            </p>
            <h1 className="truncate text-lg font-bold leading-tight tracking-tight text-foreground sm:text-xl">
              RAW MAT Allocation Engine
            </h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-1.5 text-[13px] text-muted-foreground">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-ok opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-ok" />
            </span>
            {status}
          </span>

          <SelectPill icon={<Palette className="h-4 w-4" aria-hidden />} label="Theme" defaultValue="soft">
            <option value="soft">Soft Enterprise</option>
            <option value="mill">Mill Ops</option>
          </SelectPill>

          <SelectPill icon={<Languages className="h-4 w-4" aria-hidden />} label="Language" defaultValue="en">
            <option value="en">English</option>
            <option value="zh">繁體中文</option>
            <option value="my">မြန်မာ</option>
          </SelectPill>

          <span className="rounded-lg bg-brand-muted px-2.5 py-1 font-mono text-xs font-medium text-accent-foreground">
            v{version}
          </span>
        </div>
      </div>
    </header>
  )
}

function SelectPill({
  icon,
  label,
  defaultValue,
  children,
}: {
  icon: React.ReactNode
  label: string
  defaultValue: string
  children: React.ReactNode
}) {
  return (
    <label className="flex items-center gap-1.5 rounded-lg border border-border bg-card pl-2.5 text-muted-foreground transition-colors focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/25">
      {icon}
      <span className="sr-only">{label}</span>
      <select
        defaultValue={defaultValue}
        aria-label={label}
        className="cursor-pointer rounded-lg bg-transparent py-1.5 pr-2 text-[13px] font-medium text-foreground outline-none"
      >
        {children}
      </select>
    </label>
  )
}
