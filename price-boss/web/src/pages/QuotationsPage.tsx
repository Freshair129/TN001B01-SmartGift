import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import PageHeader from '../components/ui/PageHeader'
import ListState from '../components/ui/ListState'
import { StatusBadge, STATUS_TH } from '../components/ui/StatusBadge'
import { useToast } from '../components/ui/Toast'
import { api, type Customer, type CustomerContact, type Offer, type PriceTier, type QuoteSummary } from '../lib/api'
import { customerReadiness, readinessTone } from '../lib/customerReadiness'
import { useAuth } from '../lib/auth'

type BasketItem = {
  key: string
  offerCode: string
  itemName: string
  qty: number
  qtyTier: number
  unitPrice: number
  breaks: { qty: number; unitPrice: number }[]
  cartonNote?: string
  image?: string | null
}

type Action = { action: string; label: string; perm: string; from: string[]; note?: boolean }

const ACTIONS: Action[] = [
  { action: 'submit', label: 'ส่งอนุมัติ', perm: 'quote.submit', from: ['draft'] },
  { action: 'approve', label: 'อนุมัติ', perm: 'quote.approve', from: ['submitted'] },
  { action: 'reject', label: 'ตีกลับ', perm: 'quote.approve', from: ['submitted'], note: true },
  { action: 'revise', label: 'แก้ใหม่', perm: 'quote.write', from: ['rejected'] },
  { action: 'send', label: 'ส่งลูกค้า', perm: 'quote.send', from: ['approved'] },
  { action: 'accept', label: 'ลูกค้ารับ', perm: 'quote.write', from: ['sent'] },
  {
    action: 'cancel',
    label: 'ยกเลิก',
    perm: 'quote.cancel',
    from: ['draft', 'submitted', 'approved', 'sent', 'rejected'],
    note: true,
  },
]

const FILTERS = ['all', 'draft', 'submitted', 'approved', 'sent', 'rejected', 'accepted', 'cancelled'] as const

export default function QuotationsPage() {
  const { can } = useAuth()
  const toast = useToast()
  const nav = useNavigate()
  const [rows, setRows] = useState<QuoteSummary[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [offerQ, setOfferQ] = useState('')
  const [offers, setOffers] = useState<Offer[]>([])
  const [tiers, setTiers] = useState<PriceTier[]>([])
  const [customerId, setCustomerId] = useState('')
  const [contactId, setContactId] = useState('')
  const [contacts, setContacts] = useState<CustomerContact[]>([])
  const [validUntil, setValidUntil] = useState('')
  const [paymentTerm, setPaymentTerm] = useState('')
  const [deliveryTerm, setDeliveryTerm] = useState('ส่งตามนัดหมายหลังผลิต')
  const [tradeTerm, setTradeTerm] = useState('')
  const [customerNote, setCustomerNote] = useState('')
  const [picked, setPicked] = useState<Offer | null>(null)
  const [qty, setQty] = useState(100)
  const [unitPrice, setUnitPrice] = useState(0)
  const [basket, setBasket] = useState<BasketItem[]>([])
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>('all')
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [error, setError] = useState('')

  const activeCustomers = useMemo(
    () => customers.filter((c) => c.status === 'active'),
    [customers],
  )

  const selectedCustomer = useMemo(
    () => activeCustomers.find((c) => String(c.id) === customerId) || null,
    [activeCustomers, customerId],
  )
  const selectedReady = useMemo(
    () => (selectedCustomer ? customerReadiness(selectedCustomer) : null),
    [selectedCustomer],
  )

  useEffect(() => {
    if (!customerId) {
      setContacts([])
      setContactId('')
      return
    }
    const c = activeCustomers.find((x) => String(x.id) === customerId)
    if (c?.credit_days) {
      setPaymentTerm((prev) => prev || `เครดิต ${c.credit_days} วัน`)
    }
    api
      .customer(Number(customerId))
      .then((d) => {
        setContacts(d.contacts)
        const prim = d.contacts.find((x) => x.is_primary) || d.contacts[0]
        setContactId(prim ? String(prim.id) : '')
        if (!validUntil) {
          const dt = new Date()
          dt.setDate(dt.getDate() + 30)
          setValidUntil(dt.toISOString().slice(0, 10))
        }
      })
      .catch(() => {
        setContacts([])
        setContactId('')
      })
  }, [customerId])

  async function refresh() {
    const [q, c] = await Promise.all([api.quotations(), api.customers()])
    setRows(q.rows)
    setCustomers(c.rows)
    const actives = c.rows.filter((x) => x.status === 'active')
    if (!customerId && actives[0]) setCustomerId(String(actives[0].id))
  }

  useEffect(() => {
    setLoading(true)
    refresh()
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(
    () => (filter === 'all' ? rows : rows.filter((r) => r.status === filter)),
    [rows, filter],
  )

  const counts = useMemo(() => {
    const m: Record<string, number> = { all: rows.length }
    for (const r of rows) m[r.status] = (m[r.status] || 0) + 1
    return m
  }, [rows])

  async function searchOffers(e: FormEvent) {
    e.preventDefault()
    const r = await api.offers(offerQ, 0, 12)
    setOffers(r.rows)
  }

  async function pickOffer(o: Offer) {
    setPicked(o)
    const prices = await api.offerPrices(o.code)
    setTiers(prices.rows.filter((p) => !p.price_missing))
    const hit =
      prices.rows.find((p) => p.qty_tier === qty && !p.price_missing) ||
      prices.rows.find((p) => !p.price_missing)
    if (hit) {
      setQty(Number(hit.qty_tier || qty))
      setUnitPrice(Number(hit.unit_price))
    } else {
      setUnitPrice(0)
    }
  }

  function addToBasket() {
    if (!picked) return
    const breaks =
      tiers.length > 0
        ? tiers
            .filter((t) => t.qty_tier != null)
            .map((t) => ({ qty: Number(t.qty_tier), unitPrice: Number(t.unit_price) }))
        : [{ qty, unitPrice }]
    const item: BasketItem = {
      key: `${picked.code}-${Date.now()}`,
      offerCode: picked.code,
      itemName: picked.name_th || picked.name_en || picked.code,
      qty,
      qtyTier: qty,
      unitPrice,
      breaks,
      image: picked.image,
    }
    setBasket((prev) => {
      const at = prev.findIndex((b) => b.offerCode === item.offerCode)
      if (at >= 0) {
        const next = [...prev]
        next[at] = item
        return next
      }
      return [...prev, item]
    })
    toast.push(`ใส่ ${picked.code} ในตะกร้าแล้ว`, 'good')
  }

  async function createQuote(e: FormEvent) {
    e.preventDefault()
    if (!can('quote.write') || !basket.length || !customerId) return
    if (selectedReady && !selectedReady.quoteReady) {
      toast.push('ลูกค้ายังออกใบไม่ได้ — ตรวจสถานะ/ข้อมูลบังคับ', 'crit')
      return
    }
    if (selectedReady && !selectedReady.ready) {
      const ok = window.confirm(
        `ลูกค้ายังขาด: ${selectedReady.labels.join(', ')}\nสร้างใบต่อหรือไปเติมข้อมูลก่อน?`,
      )
      if (!ok) return
    }
    setError('')
    try {
      const quoteNo = `Q${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${String(Date.now()).slice(-4)}`
      const r = await api.createQuotation({
        quoteNo,
        customerId: Number(customerId),
        contactId: contactId ? Number(contactId) : null,
        validUntil: validUntil || null,
        paymentTerm: paymentTerm || null,
        deliveryTerm: deliveryTerm || null,
        tradeTerm: tradeTerm || null,
        customerNote: customerNote || null,
        priceListGroup: selectedCustomer?.price_list_group || null,
        items: basket.map((b) => ({
          offerCode: b.offerCode,
          itemName: b.itemName,
          qty: b.qty,
          qtyTier: b.qtyTier,
          unitPrice: b.unitPrice,
          breaks: b.breaks,
          cartonNote: b.cartonNote,
        })),
      })
      toast.push(`สร้างใบ ${quoteNo} แล้ว`, 'good')
      setBasket([])
      setPicked(null)
      setCustomerNote('')
      await refresh()
      nav(`/quotations/${r.id}`)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'สร้างใบไม่สำเร็จ'
      setError(msg)
      toast.push(msg, 'crit')
    }
  }

  async function runAction(row: QuoteSummary, a: Action) {
    if (!can(a.perm)) return
    let note: string | undefined
    if (a.note) {
      const typed = window.prompt(`เหตุผล (${a.label})`)
      if (!typed?.trim()) return
      note = typed.trim()
    }
    setBusyId(row.id)
    try {
      const r = await api.transitionQuotation(row.id, { action: a.action, note })
      toast.push(`${row.quote_no}: ${r.from} → ${r.to}`, 'good')
      await refresh()
    } catch (err) {
      toast.push(err instanceof Error ? err.message : 'เปลี่ยนสถานะไม่สำเร็จ', 'crit')
    } finally {
      setBusyId(null)
    }
  }

  function actionsFor(row: QuoteSummary) {
    return ACTIONS.filter((a) => a.from.includes(row.status) && can(a.perm))
  }

  return (
    <div>
      <PageHeader
        eyebrow="Quote desk"
        title="ใบเสนอราคา"
        description="ตะกร้าหลายรายการ + บันไดราคา · sale เห็นเฉพาะใบของตน"
        meta={<span className="font-mono text-sm tabular-nums text-ink-3">{rows.length} ใบ</span>}
      />

      <div className="mt-4 flex flex-wrap gap-1.5" role="tablist" aria-label="กรองสถานะ">
        {FILTERS.map((f) => {
          const n = counts[f] || 0
          if (f !== 'all' && n === 0) return null
          return (
            <button
              key={f}
              type="button"
              role="tab"
              aria-selected={filter === f}
              onClick={() => setFilter(f)}
              className={`rounded-[2px] px-2.5 py-1.5 text-xs font-medium ${
                filter === f ? 'bg-ink text-paper' : 'border border-rule text-ink-2 hover:bg-paper-2'
              }`}
            >
              {f === 'all' ? 'ทั้งหมด' : STATUS_TH[f] || f}
              <span className="ml-1.5 font-mono opacity-70">{n}</span>
            </button>
          )
        })}
      </div>

      {can('quote.write') ? (
        <form onSubmit={createQuote} className="mt-4 space-y-3 rounded-[3px] border border-rule bg-paper-2 p-4">
          <h3 className="text-sm font-semibold">สร้างใบใหม่ — ใส่หลายรายการในตะกร้า</h3>
          <div className="grid gap-2 md:grid-cols-2">
            <label className="text-sm text-ink-2">
              ลูกค้า (active เท่านั้น)
              <select
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                required
              >
                {activeCustomers.map((c) => {
                  const r = customerReadiness(c)
                  const tone = readinessTone(r)
                  const mark = tone === 'good' ? '✓' : tone === 'warn' ? '!' : '×'
                  return (
                    <option key={c.id} value={c.id}>
                      {mark} {c.customer_code} — {c.name_th}
                      {c.tax_id ? ` · ภาษี ${c.tax_id}` : ''}
                    </option>
                  )
                })}
              </select>
            </label>
            <label className="text-sm text-ink-2">
              จำนวน / ขั้นราคา
              <input
                type="number"
                min={1}
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 font-mono text-sm"
                value={qty}
                onChange={(e) => setQty(Number(e.target.value))}
              />
            </label>
          </div>

          {selectedReady && !selectedReady.ready ? (
            <p
              className={`rounded-[2px] px-3 py-2 text-xs ${
                selectedReady.quoteReady ? 'bg-[#f3e5cc] text-warn' : 'bg-[#f3dcdc] text-crit'
              }`}
            >
              ลูกค้านี้ข้อมูลยังไม่ครบสำหรับใบสมบูรณ์: {selectedReady.labels.join(' · ')} —{' '}
              <Link to="/customers" className="underline">
                ไปเติมรายละเอียด
              </Link>
            </p>
          ) : selectedReady?.ready ? (
            <p className="rounded-[2px] bg-[#dcebe1] px-3 py-2 text-xs text-good">
              ลูกค้าพร้อมออกใบ · {selectedCustomer?.branch || '—'} · ภาษี{' '}
              {selectedCustomer?.tax_id || '—'}
            </p>
          ) : null}

          <div className="grid gap-2 md:grid-cols-2">
            <label className="text-sm text-ink-2">
              ผู้ติดต่อบนใบ
              <select
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
                value={contactId}
                onChange={(e) => setContactId(e.target.value)}
              >
                <option value="">— ใช้ผู้ติดต่อหลัก / ไม่ระบุ —</option>
                {contacts.map((ct) => (
                  <option key={ct.id} value={ct.id}>
                    {ct.is_primary ? '(หลัก) ' : ''}
                    {ct.name}
                    {ct.phone ? ` · ${ct.phone}` : ''}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-sm text-ink-2">
              ยืนราคาถึง
              <input
                type="date"
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 font-mono text-sm"
                value={validUntil}
                onChange={(e) => setValidUntil(e.target.value)}
              />
            </label>
            <label className="text-sm text-ink-2">
              เงื่อนไขชำระ
              <input
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
                value={paymentTerm}
                onChange={(e) => setPaymentTerm(e.target.value)}
                placeholder="เช่น เครดิต 30 วัน"
              />
            </label>
            <label className="text-sm text-ink-2">
              เงื่อนไขส่ง
              <input
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
                value={deliveryTerm}
                onChange={(e) => setDeliveryTerm(e.target.value)}
              />
            </label>
            <label className="text-sm text-ink-2">
              Trade term
              <input
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
                value={tradeTerm}
                onChange={(e) => setTradeTerm(e.target.value)}
                placeholder="EXW / FOB / DDP (ถ้ามี)"
              />
            </label>
            <label className="text-sm text-ink-2 md:col-span-2">
              ข้อความถึงลูกค้า (พิมพ์บนใบ)
              <textarea
                className="mt-1 w-full rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
                rows={2}
                value={customerNote}
                onChange={(e) => setCustomerNote(e.target.value)}
                placeholder="เงื่อนไขเพิ่ม / ขอบคุณที่สนใจ"
              />
            </label>
          </div>

          <div className="flex flex-wrap gap-2">
            <input
              className="min-w-[200px] flex-1 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
              placeholder="ค้นสินค้าใส่ใบ"
              value={offerQ}
              onChange={(e) => setOfferQ(e.target.value)}
              aria-label="ค้นสินค้า"
            />
            <button type="button" onClick={searchOffers} className="rounded-[2px] border border-rule px-3 py-2 text-sm">
              ค้นสินค้า
            </button>
          </div>

          {offers.length ? (
            <ul className="max-h-40 overflow-auto rounded-[2px] border border-rule bg-field text-sm">
              {offers.map((o) => (
                <li key={o.code}>
                  <button
                    type="button"
                    className="flex w-full justify-between px-3 py-2 text-left hover:bg-brass-soft/50"
                    onClick={() => pickOffer(o)}
                  >
                    <span className="font-mono text-brass">{o.code}</span>
                    <span className="truncate pl-3">{o.name_th || o.name_en}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}

          {picked ? (
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <span>
                เลือก: <span className="font-mono text-brass">{picked.code}</span>
              </span>
              <label>
                ราคา
                <input
                  type="number"
                  className="ml-1 w-28 rounded-[2px] border border-rule bg-field px-2 py-1 font-mono"
                  value={unitPrice}
                  onChange={(e) => setUnitPrice(Number(e.target.value))}
                />
              </label>
              {tiers.length ? (
                <span className="text-xs text-ink-3">
                  บันได {tiers.length} ขั้นจะติดไปกับรายการ
                </span>
              ) : null}
              <button
                type="button"
                onClick={addToBasket}
                className="rounded-[2px] bg-teal px-3 py-1.5 text-xs font-semibold text-paper"
              >
                ใส่ตะกร้า
              </button>
            </div>
          ) : null}

          {basket.length ? (
            <ul className="space-y-1 rounded-[2px] border border-rule bg-field p-2 text-sm">
              {basket.map((b) => (
                <li key={b.key} className="flex flex-wrap items-center justify-between gap-2 px-1 py-1">
                  <span>
                    <span className="font-mono text-brass">{b.offerCode}</span> · {b.itemName}
                    <span className="ml-2 text-ink-3">
                      {b.breaks.length} ขั้น · {b.unitPrice.toLocaleString()} ฿ @{b.qty}
                    </span>
                  </span>
                  <button
                    type="button"
                    className="text-crit"
                    onClick={() => setBasket((prev) => prev.filter((x) => x.key !== b.key))}
                  >
                    เอาออก
                  </button>
                </li>
              ))}
            </ul>
          ) : null}

          <button
            type="submit"
            disabled={!basket.length || !activeCustomers.length || !!(selectedReady && !selectedReady.quoteReady)}
            className="rounded-[2px] bg-ink px-4 py-2 text-sm font-semibold text-paper disabled:opacity-40"
          >
            สร้างใบจากตะกร้า ({basket.length} รายการ)
          </button>
          {!activeCustomers.length ? (
            <p className="text-sm text-warn">ต้องมีลูกค้าสถานะ active ก่อน</p>
          ) : null}
        </form>
      ) : null}

      {error ? (
        <p className="mt-3 rounded-[2px] bg-[#f3dcdc] px-3 py-2 text-sm text-crit" role="alert">
          {error}
        </p>
      ) : null}

      <div className="mt-4">
        <ListState
          loading={loading}
          empty={!loading && !filtered.length}
          emptyText={
            rows.length
              ? 'ไม่มีใบในสถานะที่เลือก'
              : 'ยังไม่มีใบเสนอราคา — สร้างจากตะกร้าด้านบน'
          }
        >
          <div className="overflow-x-auto rounded-[3px] border border-rule">
            <table className="w-full min-w-[920px] text-left text-sm">
              <thead className="bg-paper-3 text-xs text-ink-3 uppercase">
                <tr>
                  <th className="px-3 py-2">เลขที่</th>
                  <th className="px-3 py-2">ลูกค้า</th>
                  <th className="px-3 py-2">สถานะ</th>
                  <th className="px-3 py-2">ยอด</th>
                  <th className="px-3 py-2">เซลล์</th>
                  <th className="px-3 py-2">รายการ</th>
                  <th className="px-3 py-2">ดำเนินการ</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r) => {
                  const acts = actionsFor(r)
                  return (
                    <tr key={r.id} className="border-t border-rule align-top">
                      <td className="px-3 py-2.5">
                        <Link className="font-mono text-brass hover:underline" to={`/quotations/${r.id}`}>
                          {r.quote_no}
                        </Link>
                      </td>
                      <td className="px-3 py-2.5">
                        <span className="font-mono text-xs text-ink-3">{r.customer_code}</span>
                        <br />
                        {r.customer_name}
                      </td>
                      <td className="px-3 py-2.5">
                        <StatusBadge status={r.status} />
                      </td>
                      <td className="px-3 py-2.5 font-mono tabular-nums">
                        {Number(r.grand_total).toLocaleString()}
                      </td>
                      <td className="px-3 py-2.5">{r.owner_name}</td>
                      <td className="px-3 py-2.5 font-mono">{r.item_count}</td>
                      <td className="px-3 py-2.5">
                        <div className="flex flex-wrap gap-1">
                          <Link
                            to={`/quotations/${r.id}`}
                            className="rounded-[2px] border border-rule px-2 py-1 text-xs hover:bg-paper-2"
                          >
                            เปิด
                          </Link>
                          {acts.map((a) => (
                            <button
                              key={a.action}
                              type="button"
                              disabled={busyId === r.id}
                              onClick={() => runAction(r, a)}
                              className={`rounded-[2px] px-2 py-1 text-xs font-medium disabled:opacity-40 ${
                                a.action === 'cancel' || a.action === 'reject'
                                  ? 'border border-crit/40 text-crit'
                                  : a.action === 'approve' || a.action === 'send'
                                    ? 'bg-teal text-paper'
                                    : 'border border-rule'
                              }`}
                            >
                              {a.label}
                            </button>
                          ))}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </ListState>
      </div>
    </div>
  )
}
