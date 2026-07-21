import { cn } from "@/lib/utils"

type SectionProps = {
  title: string
  badge?: string
  description?: string
  children: React.ReactNode
  className?: string
}

export function Section({ title, badge, description, children, className }: SectionProps) {
  return (
    <section className={cn("overflow-hidden rounded-2xl border border-border bg-card shadow-sm", className)}>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-surface/60 px-5 py-4">
        <div className="min-w-0">
          <h2 className="text-base font-semibold tracking-tight text-foreground">{title}</h2>
          {description ? <p className="mt-0.5 text-sm text-muted-foreground">{description}</p> : null}
        </div>
        {badge ? (
          <span className="rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground">
            {badge}
          </span>
        ) : null}
      </div>
      <div className="p-5">{children}</div>
    </section>
  )
}

export function Hint({ tone = "muted", children }: { tone?: "muted" | "brand"; children: React.ReactNode }) {
  return (
    <p
      className={cn(
        "rounded-lg border px-3 py-2 text-[13px] leading-relaxed",
        tone === "brand"
          ? "border-brand/20 bg-brand-muted text-accent-foreground"
          : "border-border bg-surface/70 text-muted-foreground",
      )}
    >
      {children}
    </p>
  )
}
