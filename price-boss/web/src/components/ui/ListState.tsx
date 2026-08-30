import type { ReactNode } from 'react'

type Props = {
  loading?: boolean
  error?: string
  empty?: boolean
  emptyText?: string
  onRetry?: () => void
  children: ReactNode
}

export default function ListState({
  loading,
  error,
  empty,
  emptyText = 'ไม่มีข้อมูล',
  onRetry,
  children,
}: Props) {
  if (loading) {
    return <p className="px-3 py-8 text-center text-sm text-ink-3">กำลังโหลด…</p>
  }
  if (error) {
    return (
      <div className="rounded-[2px] bg-[#f3dcdc] px-3 py-3 text-sm text-crit" role="alert">
        <p>{error}</p>
        {onRetry ? (
          <button type="button" className="mt-2 underline" onClick={onRetry}>
            ลองใหม่
          </button>
        ) : null}
      </div>
    )
  }
  if (empty) {
    return <p className="px-3 py-10 text-center text-sm text-ink-3">{emptyText}</p>
  }
  return <>{children}</>
}
