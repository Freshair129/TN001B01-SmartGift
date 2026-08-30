import { useEffect, useState, type FormEvent } from 'react'
import { Download } from 'lucide-react'
import FadeContent from '../components/bits/FadeContent'
import SpotlightCard from '../components/bits/SpotlightCard'
import {
  api,
  type ReportByGroup,
  type ReportByType,
  type ReportCoverage,
  type ReportRow,
} from '../lib/api'

const PAGE = 50

function n(v: number | string | null | undefined) {
  return Number(v ?? 0).toLocaleString()
}

export default function ReportPage() {
  const [q, setQ] = useState('')
  const [query, setQuery] = useState('')
  const [group, setGroup] = useState('')
  const [typeId, setTypeId] = useState('')
  const [pricedOnly, setPricedOnly] = useState(false)
  const [linkedOnly, setLinkedOnly] = useState(false)
  const [page, setPage] = useState(0)
  const [rows, setRows] = useState<ReportRow[]>([])
  const [total, setTotal] = useState(0)
  const [byGroup, setByGroup] = useState<ReportByGroup[]>([])
  const [byType, setByType] = useState<ReportByType[]>([])
  const [coverage, setCoverage] = useState<ReportCoverage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .reportSummary()
      .then((r) => {
        setByGroup(r.byGroup)
        setByType(r.byType)
        setCoverage(r.coverage)
      })
      .catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    let alive = true
    setLoading(true)
    api
      .report(query, {
        group: group || undefined,
        type: typeId || undefined,
        priced: pricedOnly,
        linked: linkedOnly,
        offset: page * PAGE,
        limit: PAGE,
      })
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
  }, [query, group, typeId, pricedOnly, linkedOnly, page])

  function onSearch(e: FormEvent) {
    e.preventDefault()
    setPage(0)
    setQuery(q.trim())
  }

  const pages = Math.max(1, Math.ceil(total / PAGE))
  const csvHref = api.reportCsvUrl({
    q: query,
    group: group || undefined,
    type: typeId || undefined,
    priced: pricedOnly,
    linked: linkedOnly,
  })

  const typesForGroup = byType.filter((t) => !group || t.type_group === group)

  const coverageCards = coverage
    ? [
        { label: 'แถวรายงาน', value: coverage.report_rows, hint: 'model × offer' },
        { label: 'Offers', value: coverage.offers, hint: `ไม่มีราคา ${n(coverage.offers_no_price)}` },
        { label: 'Products', value: coverage.products, hint: `ไม่ผูก offer ${n(coverage.products_no_offer)}` },
        { label: 'Models', value: coverage.models, hint: `ไม่มี type ${n(coverage.models_no_type)}` },
      ]
    : []

  return (
    <div>
      <FadeContent>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold">รายงาน SmartGift</h2>
            <p className="mt-1 text-sm text-ink-3">
              DB <span className="font-mono text-brass">smartgift</span> · join ID: group → type →
              model ↔ offer → price (+ product)
            </p>
          </div>
          <a
            href={csvHref}
            className="inline-flex items-center gap-2 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm font-semibold hover:bg-paper-2"
          >
            <Download size={16} aria-hidden /> ส่งออก CSV
          </a>
        </div>
      </FadeContent>

      {coverageCards.length ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {coverageCards.map((c, i) => (
            <FadeContent key={c.label} delay={0.03 * i}>
              <SpotlightCard className="p-4">
                <p className="text-xs tracking-wide text-ink-3 uppercase">{c.label}</p>
                <p className="mt-2 font-mono text-2xl tabular-nums text-ink">{n(c.value)}</p>
                <p className="text-xs text-ink-3">{c.hint}</p>
              </SpotlightCard>
            </FadeContent>
          ))}
        </div>
      ) : null}

      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {byGroup.map((g, i) => (
          <FadeContent key={g.type_group} delay={0.04 * i}>
            <button
              type="button"
              onClick={() => {
                setGroup(g.type_group === '(ไม่มีกลุ่ม)' ? '' : g.type_group)
                setTypeId('')
                setPage(0)
              }}
              className="w-full text-left"
            >
              <SpotlightCard
                className={`p-4 ${group === g.type_group ? 'ring-2 ring-brass' : ''}`}
              >
                <p className="font-mono text-xs text-brass uppercase">{g.type_group}</p>
                <p className="mt-2 font-mono text-2xl tabular-nums text-ink">{n(g.offer_count)}</p>
                <p className="text-xs text-ink-3">
                  offers · {n(g.model_count)} models · มีราคา {n(g.offers_with_price)}
                </p>
              </SpotlightCard>
            </button>
          </FadeContent>
        ))}
      </div>

      <form onSubmit={onSearch} className="mt-5 flex flex-wrap gap-2">
        <input
          className="min-w-[200px] flex-1 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
          placeholder="ค้น model / offer / ประเภท"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select
          className="rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
          value={group}
          onChange={(e) => {
            setGroup(e.target.value)
            setTypeId('')
            setPage(0)
          }}
          aria-label="กลุ่ม"
        >
          <option value="">ทุกกลุ่ม</option>
          {byGroup.map((g) => (
            <option key={g.type_group} value={g.type_group === '(ไม่มีกลุ่ม)' ? '' : g.type_group}>
              {g.type_group}
            </option>
          ))}
        </select>
        <select
          className="rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
          value={typeId}
          onChange={(e) => {
            setTypeId(e.target.value)
            setPage(0)
          }}
          aria-label="ประเภท"
        >
          <option value="">ทุกประเภท</option>
          {typesForGroup.map((t) => (
            <option key={`${t.type_group}-${t.type_id}`} value={String(t.type_id)}>
              {t.type_label} ({t.offer_count})
            </option>
          ))}
        </select>
        <label className="inline-flex items-center gap-2 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm">
          <input
            type="checkbox"
            checked={pricedOnly}
            onChange={(e) => {
              setPricedOnly(e.target.checked)
              setPage(0)
            }}
          />
          มีราคาแล้ว
        </label>
        <label className="inline-flex items-center gap-2 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm">
          <input
            type="checkbox"
            checked={linkedOnly}
            onChange={(e) => {
              setLinkedOnly(e.target.checked)
              setPage(0)
            }}
          />
          ผูก product แล้ว
        </label>
        <button type="submit" className="rounded-[2px] bg-ink px-4 py-2 text-sm font-semibold text-paper">
          ค้นหา
        </button>
      </form>

      {error ? <p className="mt-3 text-sm text-crit">{error}</p> : null}
      {loading ? <p className="mt-4 text-sm text-ink-3">กำลังโหลดรายงาน…</p> : null}

      <div className="mt-4 overflow-x-auto rounded-[3px] border border-rule">
        <table className="w-full min-w-[1100px] text-left text-sm">
          <thead className="bg-paper-3 text-xs tracking-wide text-ink-3 uppercase">
            <tr>
              <th className="px-3 py-2">กลุ่ม</th>
              <th className="px-3 py-2">ประเภท</th>
              <th className="px-3 py-2">Model</th>
              <th className="px-3 py-2">Offer</th>
              <th className="px-3 py-2">ชื่อสินค้า</th>
              <th className="px-3 py-2">Product ID</th>
              <th className="px-3 py-2">ราคาต่ำสุด</th>
              <th className="px-3 py-2">ราคาสูงสุด</th>
              <th className="px-3 py-2">ขั้นราคา</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr
                key={`${r.model_id || r.sig_hash || i}-${r.offer_id || r.offer_code || i}`}
                className="border-t border-rule"
              >
                <td className="px-3 py-2 font-mono text-xs text-ink-3">{r.type_group || '—'}</td>
                <td className="px-3 py-2">{r.type_th || r.type_code || r.type_id || '—'}</td>
                <td className="px-3 py-2">
                  <span>{r.model_name || '—'}</span>
                  {r.model_id != null ? (
                    <span className="ml-1 font-mono text-[10px] text-ink-3">#{r.model_id}</span>
                  ) : null}
                </td>
                <td className="px-3 py-2 font-mono text-brass">{r.offer_code || '—'}</td>
                <td className="px-3 py-2 max-w-[240px] truncate">{r.offer_th || r.offer_en || '—'}</td>
                <td className="px-3 py-2 font-mono text-xs">{r.product_id ?? '—'}</td>
                <td className="px-3 py-2 font-mono tabular-nums">
                  {r.price_min != null ? Number(r.price_min).toLocaleString() : '—'}
                </td>
                <td className="px-3 py-2 font-mono tabular-nums">
                  {r.price_max != null ? Number(r.price_max).toLocaleString() : '—'}
                </td>
                <td className="px-3 py-2 font-mono">{r.price_tier_count || 0}</td>
              </tr>
            ))}
            {!loading && !rows.length ? (
              <tr>
                <td colSpan={9} className="px-3 py-6 text-ink-3">
                  ไม่พบข้อมูลตามตัวกรอง
                </td>
              </tr>
            ) : null}
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
          <span className="px-2 py-1 font-mono">
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
    </div>
  )
}
