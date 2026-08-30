import { useEffect, useState, type FormEvent } from 'react'
import FadeContent from '../components/bits/FadeContent'
import { api, type Offer, type PriceTier } from '../lib/api'

const PAGE = 20

export default function OffersPage() {
  const [q, setQ] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(0)
  const [rows, setRows] = useState<Offer[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<Offer | null>(null)
  const [tiers, setTiers] = useState<PriceTier[]>([])

  useEffect(() => {
    let alive = true
    setLoading(true)
    api
      .offers(query, page * PAGE, PAGE)
      .then((r) => {
        if (!alive) return
        setRows(r.rows)
        setTotal(r.total)
        setError('')
      })
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [query, page])

  async function openOffer(o: Offer) {
    setSelected(o)
    const r = await api.offerPrices(o.code)
    setTiers(r.rows)
  }

  function onSearch(e: FormEvent) {
    e.preventDefault()
    setPage(0)
    setQuery(q.trim())
  }

  const pages = Math.max(1, Math.ceil(total / PAGE))

  return (
    <div>
      <FadeContent>
        <h2 className="text-2xl font-bold">สินค้า / ราคา</h2>
        <p className="mt-1 text-sm text-ink-3">จาก smartgift_offer + smartgift_price</p>
      </FadeContent>

      <form onSubmit={onSearch} className="mt-4 flex flex-wrap gap-2">
        <input
          className="min-w-[220px] flex-1 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
          placeholder="ค้นรหัส / ชื่อสินค้า"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="ค้นหาสินค้า"
        />
        <button type="submit" className="rounded-[2px] bg-ink px-4 py-2 text-sm font-semibold text-paper">
          ค้นหา
        </button>
      </form>

      {error ? <p className="mt-3 text-sm text-crit">{error}</p> : null}
      {loading ? <p className="mt-6 text-sm text-ink-3">กำลังโหลด…</p> : null}
      {!loading && !rows.length ? <p className="mt-6 text-sm text-ink-3">ไม่พบรายการ</p> : null}

      <div className="mt-4 overflow-x-auto rounded-[3px] border border-rule">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-paper-3 text-xs tracking-wide text-ink-3 uppercase">
            <tr>
              <th className="px-3 py-2 font-semibold">รหัส</th>
              <th className="px-3 py-2 font-semibold">ชื่อ</th>
              <th className="px-3 py-2 font-semibold">ชนิด</th>
              <th className="px-3 py-2 font-semibold">สถานะ</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <tr
                key={o.code}
                className="cursor-pointer border-t border-rule hover:bg-brass-soft/40"
                onClick={() => openOffer(o)}
              >
                <td className="px-3 py-2 font-mono text-brass">{o.code}</td>
                <td className="px-3 py-2">{o.name_th || o.name_en || '—'}</td>
                <td className="px-3 py-2 text-ink-2">{o.offer_kind || '—'}</td>
                <td className="px-3 py-2 text-ink-2">{o.status || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-3 flex items-center justify-between text-sm">
        <p className="text-ink-3">
          แสดง {total ? page * PAGE + 1 : 0}–{Math.min((page + 1) * PAGE, total)} จาก {total}
        </p>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={page <= 0}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-[2px] border border-rule px-3 py-1 disabled:opacity-40"
          >
            ก่อนหน้า
          </button>
          <span className="px-2 py-1 font-mono text-ink-2">
            {page + 1}/{pages}
          </span>
          <button
            type="button"
            disabled={page + 1 >= pages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-[2px] border border-rule px-3 py-1 disabled:opacity-40"
          >
            ถัดไป
          </button>
        </div>
      </div>

      {selected ? (
        <div
          className="fixed inset-0 z-40 flex items-end justify-center bg-ink/40 p-4 sm:items-center"
          role="dialog"
          aria-modal
          aria-labelledby="offer-title"
          onClick={() => setSelected(null)}
        >
          <div
            className="max-h-[85vh] w-full max-w-lg overflow-auto rounded-[3px] border border-rule bg-paper p-5 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 id="offer-title" className="font-mono text-brass">
              {selected.code}
            </h3>
            <p className="mt-1 font-semibold">{selected.name_th || selected.name_en}</p>
            <p className="mt-2 text-sm text-ink-2">{selected.branding || selected.origin || '—'}</p>
            <h4 className="mt-4 text-xs tracking-wide text-ink-3 uppercase">ขั้นราคา</h4>
            <table className="mt-2 w-full text-sm">
              <thead>
                <tr className="text-left text-ink-3">
                  <th className="py-1">Qty</th>
                  <th className="py-1">ราคา</th>
                  <th className="py-1">รวม VAT</th>
                  <th className="py-1">กลุ่ม</th>
                </tr>
              </thead>
              <tbody>
                {tiers.length ? (
                  tiers.map((t, i) => (
                    <tr key={i} className="border-t border-rule-soft font-mono tabular-nums">
                      <td className="py-1.5">{t.qty_tier ?? '—'}</td>
                      <td className="py-1.5">{t.price_missing ? '—' : Number(t.unit_price).toLocaleString()}</td>
                      <td className="py-1.5">
                        {t.price_missing ? '—' : Number(t.unit_price_with_vat).toLocaleString()}
                      </td>
                      <td className="py-1.5">{t.price_list_group || '—'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="py-3 text-ink-3">
                      ยังไม่มีราคาในระบบ
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            <button
              type="button"
              className="mt-4 rounded-[2px] border border-rule px-3 py-2 text-sm"
              onClick={() => setSelected(null)}
            >
              ปิด
            </button>
          </div>
        </div>
      ) : null}
    </div>
  )
}
