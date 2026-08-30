import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

type Props = {
  eyebrow?: string
  title: string
  description?: string
  backTo?: string
  backLabel?: string
  meta?: ReactNode
  actions?: ReactNode
}

export default function PageHeader({
  eyebrow,
  title,
  description,
  backTo,
  backLabel = 'กลับ',
  meta,
  actions,
}: Props) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3 border-b-2 border-ink pb-3">
      <div className="min-w-0">
        {backTo ? (
          <Link to={backTo} className="mb-1 inline-block text-xs text-teal hover:underline">
            ← {backLabel}
          </Link>
        ) : null}
        {eyebrow ? <p className="font-display text-sm italic text-brass">{eyebrow}</p> : null}
        <h2 className="text-2xl font-bold tracking-tight">{title}</h2>
        {description ? <p className="mt-1 text-sm text-ink-3">{description}</p> : null}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {meta}
        {actions}
      </div>
    </div>
  )
}
