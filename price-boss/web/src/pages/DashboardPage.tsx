import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import FadeContent from '../components/bits/FadeContent'
import SpotlightCard from '../components/bits/SpotlightCard'
import PageHeader from '../components/ui/PageHeader'
import { StatusBadge } from '../components/ui/StatusBadge'
import { api, type QuoteSummary } from '../lib/api'
import { useAuth } from '../lib/auth'

export default function DashboardPage() {
  const { user, can } = useAuth()
  const [stats, setStats] = useState<Awaited<ReturnType<typeof api.stats>> | null>(null)
  const [queue, setQueue] = useState<QuoteSummary[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.stats(), api.submittedQueue()])
      .then(([s, q]) => {
        setStats(s)
        setQueue(q.rows)
      })
      .catch((e) => setError(e.message))
  }, [])

  const cards = [
    { label: 'Offers', value: stats?.offers, to: '/offers' },
    { label: 'ราคาขาย (tiers)', value: stats?.prices, to: '/offers' },
    { label: 'ลูกค้า', value: stats?.customers, to: '/customers' },
    { label: 'ใบเสนอราคา', value: stats?.quotations, to: '/quotations' },
    { label: 'รออนุมัติ', value: stats?.submittedQuotes, to: '/quotations' },
    { label: 'Catalog จีน', value: stats?.catalogProducts, to: '/offers' },
  ]

  return (
    <div>
      <PageHeader
        eyebrow={`สวัสดี ${user?.fullName}`}
        title="ภาพรวมโต๊ะราคา"
        description={`บทบาท ${user?.roleTh} · สิทธิ์ ${user?.permissions.length} รายการ · ตัวเลขตาม scope ของคุณ`}
      />

      {error ? (
        <p className="mt-4 rounded-[2px] bg-[#f3dcdc] px-3 py-2 text-sm text-crit">{error}</p>
      ) : null}

      <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((c, i) => (
          <FadeContent key={c.label} delay={0.05 * i}>
            <Link to={c.to} className="block focus-visible:outline-offset-4">
              <SpotlightCard className="p-4 transition-transform hover:-translate-y-0.5">
                <p className="text-xs tracking-[0.12em] text-ink-3 uppercase">{c.label}</p>
                <p className="mt-2 font-mono text-3xl font-semibold text-brass tabular-nums">
                  {stats ? (c.value ?? 0) : '…'}
                </p>
                <p className="mt-2 text-xs text-ink-3">เปิดดู →</p>
              </SpotlightCard>
            </Link>
          </FadeContent>
        ))}
      </div>

      <section className="mt-8">
        <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
          <div>
            <h3 className="text-sm font-semibold">
              {can('quote.approve') ? 'คิวรออนุมัติ (submitted)' : 'ใบที่รออนุมัติของฉัน'}
            </h3>
            <p className="text-xs text-ink-3">อัปเดตจากฐานข้อมูลจริง — ไม่ใช่ลิงก์อย่างเดียว</p>
          </div>
          <Link to="/quotations" className="text-xs text-teal hover:underline">
            เปิดทุกใบ →
          </Link>
        </div>

        {queue.length ? (
          <div className="overflow-x-auto rounded-[3px] border border-rule">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="bg-paper-3 text-xs text-ink-3 uppercase">
                <tr>
                  <th className="px-3 py-2">เลขที่</th>
                  <th className="px-3 py-2">ลูกค้า</th>
                  <th className="px-3 py-2">เซลล์</th>
                  <th className="px-3 py-2">ยอด</th>
                  <th className="px-3 py-2">สถานะ</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((r) => (
                  <tr key={r.id} className="border-t border-rule">
                    <td className="px-3 py-2">
                      <Link className="font-mono text-brass hover:underline" to={`/quotations/${r.id}`}>
                        {r.quote_no}
                      </Link>
                    </td>
                    <td className="px-3 py-2">{r.customer_name}</td>
                    <td className="px-3 py-2">{r.owner_name}</td>
                    <td className="px-3 py-2 font-mono tabular-nums">
                      {Number(r.grand_total).toLocaleString()}
                    </td>
                    <td className="px-3 py-2">
                      <StatusBadge status={r.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="rounded-[3px] border border-rule bg-paper-2 px-3 py-6 text-center text-sm text-ink-3">
            ไม่มีใบสถานะ submitted ในตอนนี้
          </p>
        )}
      </section>
    </div>
  )
}
