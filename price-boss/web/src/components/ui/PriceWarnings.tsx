import type { PriceWarning } from '../../lib/api'

const LEVEL_CLASS: Record<PriceWarning['level'], string> = {
  crit: 'bg-[#f3dcdc] text-crit',
  warn: 'bg-[#f3e5cc] text-warn',
}

const LEVEL_MARK: Record<PriceWarning['level'], string> = {
  crit: '!!',
  warn: '!',
}

/** Sanity-check notices for a price ladder — see PriceWarning in lib/api.ts. */
export function PriceWarnings({ warnings }: { warnings: PriceWarning[] | undefined }) {
  if (!warnings?.length) return null
  return (
    <div className="mt-2 flex flex-col gap-1.5">
      {warnings.map((w, i) => (
        <div
          key={i}
          className={`flex items-start gap-2 rounded-[2px] px-2 py-1.5 text-xs ${LEVEL_CLASS[w.level]}`}
        >
          <span className="font-mono font-bold">{LEVEL_MARK[w.level]}</span>
          <span>{w.message}</span>
        </div>
      ))}
    </div>
  )
}
