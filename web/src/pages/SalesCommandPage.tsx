import { useEffect, useMemo, useState } from 'react'
import FadeContent from '../components/bits/FadeContent'
import SpotlightCard from '../components/bits/SpotlightCard'
import { api, type SalesKpi, type SalesPeriod, type SalesQuotaSplit, type SalesWeek } from '../lib/api'

function baht(v: number | null | undefined) {
  if (v == null) return '—'
  return Number(v).toLocaleString('th-TH')
}

function targetLabel(k: SalesKpi) {
  if (k.target_value == null) return '—'
  const n = Number(k.target_value)
  if (k.unit === 'THB') return baht(n)
  if (k.target_op === 'gte') return `≥ ${n}`
  if (k.target_op === 'lte') return `≤ ${n}`
  return String(n)
}

export default function SalesCommandPage() {
  const [periods, setPeriods] = useState<SalesPeriod[]>([])
  const [period, setPeriod] = useState<SalesPeriod | null>(null)
  const [splits, setSplits] = useState<SalesQuotaSplit[]>([])
  const [kpis, setKpis] = useState<SalesKpi[]>([])
  const [weeks, setWeeks] = useState<SalesWeek[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  function load(code?: string) {
    setLoading(true)
    api
      .salesCommand(code)
      .then((r) => {
        setPeriods(r.periods)
        setPeriod(r.period)
        setSplits(r.splits)
        setKpis(r.kpis)
        setWeeks(r.weeks)
        setError('')
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const gradient = useMemo(() => {
    if (!splits.length) return 'conic-gradient(#cbd5e1 0 100%)'
    let acc = 0
    const parts = splits.map((s) => {
      const start = acc
      acc += Number(s.pct) || 0
      return `${s.color_hex || '#64748B'} ${start}% ${acc}%`
    })
    return `conic-gradient(${parts.join(', ')})`
  }, [splits])

  return (
    <div>
      <FadeContent>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold">Quota & แผน</h2>
            <p className="mt-1 text-sm text-ink-3">
              Sales Command · DB <span className="font-mono text-brass">smartgift</span> · join ด้วย
              period_id / source_id / kpi_id
            </p>
          </div>
          <select
            className="rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
            value={period?.period_code || ''}
            onChange={(e) => load(e.target.value)}
            aria-label="เดือน"
          >
            {periods.map((p) => (
              <option key={p.id} value={p.period_code}>
                {p.label_th} ({baht(Number(p.quota_pre_vat))})
              </option>
            ))}
          </select>
        </div>
      </FadeContent>

      {error ? <p className="mt-3 text-sm text-crit">{error}</p> : null}
      {loading ? <p className="mt-4 text-sm text-ink-3">กำลังโหลด…</p> : null}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <SpotlightCard className="p-5">
          <h3 className="text-sm font-semibold">
            แจกเป้า {period?.label_th || ''} {period ? baht(Number(period.quota_pre_vat)) : ''} — 4
            แหล่งรายได้
          </h3>
          <div className="mt-4 flex flex-wrap items-center gap-6">
            <div
              className="relative h-40 w-40 shrink-0 rounded-full"
              style={{ background: gradient }}
              aria-hidden
            >
              <div className="absolute inset-[28%] flex flex-col items-center justify-center rounded-full bg-paper text-center">
                <p className="font-mono text-lg font-bold tabular-nums">
                  {period ? `${Math.round(Number(period.quota_pre_vat) / 1000)}K` : '—'}
                </p>
                <p className="text-[10px] text-ink-3">เป้า</p>
              </div>
            </div>
            <ul className="min-w-0 flex-1 space-y-2 text-sm">
              {splits.map((s) => (
                <li key={s.source_id} className="flex items-center justify-between gap-3">
                  <span className="inline-flex items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 rounded-full"
                      style={{ background: s.color_hex || '#64748B' }}
                    />
                    {s.source_th}
                  </span>
                  <span className="font-mono tabular-nums text-ink-2">
                    {baht(Number(s.amount))} ({Number(s.pct)}%)
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </SpotlightCard>

        <SpotlightCard className="p-5">
          <h3 className="text-sm font-semibold">KPI เดือน {period?.label_th || ''} (วัดทุกศุกร์)</h3>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs text-ink-3 uppercase">
                <tr>
                  <th className="py-1.5 pr-2">KPI</th>
                  <th className="py-1.5 pr-2">เป้า</th>
                  <th className="py-1.5">จริง</th>
                </tr>
              </thead>
              <tbody>
                {kpis.map((k) => (
                  <tr key={k.kpi_id} className="border-t border-rule">
                    <td className="py-2 pr-2">{k.kpi_th}</td>
                    <td className="py-2 pr-2 font-mono tabular-nums">{targetLabel(k)}</td>
                    <td className="py-2 font-mono tabular-nums text-brass">
                      {k.actual_note ||
                        (k.actual_value != null
                          ? k.unit === 'THB'
                            ? baht(Number(k.actual_value))
                            : String(k.actual_value)
                          : '—')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SpotlightCard>
      </div>

      <FadeContent className="mt-5">
        <SpotlightCard className="p-5">
          <h3 className="text-sm font-semibold">Weekly Plan {period?.label_th || ''}</h3>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {weeks.map((w) => (
              <div key={w.week_plan_id} className="rounded-[2px] border border-rule bg-field p-3">
                <p className="font-mono text-xs text-brass">
                  W{w.week_no} · {w.date_range || ''}
                </p>
                <p className="mt-1 font-semibold">{w.theme_th}</p>
                <p className="mt-1 font-mono text-xs text-ink-3">
                  เป้าสะสม {baht(Number(w.revenue_goal))}
                </p>
                <ul className="mt-3 space-y-1.5 text-sm text-ink-2">
                  {w.tasks.map((t) => (
                    <li key={t.task_id} className="flex gap-2">
                      <span aria-hidden>{t.is_done ? '✓' : '·'}</span>
                      <span>{t.task_th}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </SpotlightCard>
      </FadeContent>
    </div>
  )
}
