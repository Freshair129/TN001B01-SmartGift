import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import PageHeader from '../components/ui/PageHeader'
import ListState from '../components/ui/ListState'
import { StatusBadge } from '../components/ui/StatusBadge'
import { useToast } from '../components/ui/Toast'
import {
  api,
  type Customer,
  type CustomerContact,
  type QuoteDetail,
  type QuoteItem,
  type QuoteLog,
} from '../lib/api'
import { useAuth } from '../lib/auth'

const SHEET_NOTES = [
  'ราคารวมสกรีนโลโก้ Full Color ทุกชิ้น',
  'ราคารวมชุดกล่องของขวัญและถุงพร้อมสกรีน',
  'ราคานี้อ้างอิงจำนวนสั่งซื้อตามตาราง สั่งจำนวนอื่นกรุณาสอบถามฝ่ายขาย',
  'ราคายังไม่รวมภาษีมูลค่าเพิ่ม 7% (แสดงแยกในสรุปยอด)',
]

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

function fmt(n: number) {
  return Number(n).toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export default function QuotationDetailPage() {
  const { id } = useParams()
  const quoteId = Number(id)
  const { can } = useAuth()
  const toast = useToast()
  const printRef = useRef<HTMLDivElement>(null)
  const [quote, setQuote] = useState<QuoteDetail | null>(null)
  const [customer, setCustomer] = useState<Customer | null>(null)
  const [contact, setContact] = useState<CustomerContact | null>(null)
  const [contacts, setContacts] = useState<CustomerContact[]>([])
  const [items, setItems] = useState<QuoteItem[]>([])
  const [logs, setLogs] = useState<QuoteLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showPrint, setShowPrint] = useState(false)
  const [editTerms, setEditTerms] = useState({
    contactId: '',
    validUntil: '',
    paymentTerm: '',
    deliveryTerm: '',
    tradeTerm: '',
    customerNote: '',
  })

  async function load() {
    const r = await api.quotation(quoteId)
    setQuote(r.quote)
    setCustomer(r.customer)
    setContact(r.contact)
    setContacts(r.contacts)
    setItems(r.items)
    setLogs(r.logs)
    setEditTerms({
      contactId: r.quote.contact_id ? String(r.quote.contact_id) : r.contact ? String(r.contact.id) : '',
      validUntil: r.quote.valid_until || '',
      paymentTerm: r.quote.payment_term || '',
      deliveryTerm: r.quote.delivery_term || '',
      tradeTerm: r.quote.trade_term || '',
      customerNote: r.quote.customer_note || '',
    })
  }

  useEffect(() => {
    if (!quoteId) return
    setLoading(true)
    load()
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [quoteId])

  async function saveTerms() {
    if (!quote || !can('quote.write')) return
    try {
      await api.updateQuotation(quote.id, {
        contactId: editTerms.contactId ? Number(editTerms.contactId) : null,
        validUntil: editTerms.validUntil || null,
        paymentTerm: editTerms.paymentTerm || null,
        deliveryTerm: editTerms.deliveryTerm || null,
        tradeTerm: editTerms.tradeTerm || null,
        customerNote: editTerms.customerNote || null,
      })
      toast.push('บันทึกเงื่อนไขใบแล้ว', 'good')
      await load()
    } catch (err) {
      toast.push(err instanceof Error ? err.message : 'บันทึกไม่สำเร็จ', 'crit')
    }
  }

  async function runAction(a: Action) {
    if (!quote || !can(a.perm)) return
    let note: string | undefined
    if (a.note) {
      const typed = window.prompt(`เหตุผล (${a.label})`)
      if (!typed?.trim()) return
      note = typed.trim()
    }
    try {
      const r = await api.transitionQuotation(quote.id, { action: a.action, note })
      toast.push(`${quote.quote_no}: ${r.from} → ${r.to}`, 'good')
      await load()
    } catch (err) {
      toast.push(err instanceof Error ? err.message : 'ไม่สำเร็จ', 'crit')
    }
  }

  function doPrint() {
    setShowPrint(true)
    window.setTimeout(() => window.print(), 120)
  }

  const acts = quote
    ? ACTIONS.filter((a) => a.from.includes(quote.status) && can(a.perm))
    : []

  const quoteDateTh = quote
    ? new Date(quote.quote_date).toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : ''

  return (
    <div>
      <PageHeader
        backTo="/quotations"
        backLabel="รายการใบเสนอราคา"
        eyebrow="Quote detail"
        title={quote?.quote_no || 'ใบเสนอราคา'}
        description={customer ? `${customer.customer_code} · ${customer.name_th}` : undefined}
        actions={
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={doPrint}
              className="rounded-[2px] border border-rule px-3 py-1.5 text-sm hover:bg-paper-2"
            >
              พิมพ์ / พรีวิว
            </button>
            {acts.map((a) => (
              <button
                key={a.action}
                type="button"
                onClick={() => runAction(a)}
                className={`rounded-[2px] px-3 py-1.5 text-sm font-medium ${
                  a.action === 'cancel' || a.action === 'reject'
                    ? 'border border-crit/40 text-crit'
                    : 'bg-ink text-paper'
                }`}
              >
                {a.label}
              </button>
            ))}
          </div>
        }
      />

      <ListState loading={loading} error={error} empty={!loading && !quote} emptyText="ไม่พบใบ">
        {quote ? (
          <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_280px]">
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-3 rounded-[3px] border border-rule bg-paper-2 p-3 text-sm">
                <StatusBadge status={quote.status} />
                <span>วันที่ {quoteDateTh}</span>
                {quote.valid_until ? (
                  <span className="text-ink-3">ยืนราคาถึง {quote.valid_until}</span>
                ) : null}
                <span className="font-mono text-brass">{quote.owner_name}</span>
              </div>

              <div className="space-y-3">
                {items.map((it) => (
                  <article key={it.id} className="rounded-[3px] border border-rule bg-field p-3">
                    <div className="flex flex-wrap justify-between gap-2">
                      <div>
                        <h3 className="font-semibold">{it.item_name}</h3>
                        <p className="font-mono text-xs text-brass">
                          {it.sku_code || it.offer_code || '—'}
                          {it.carton_note ? ` · ${it.carton_note}` : ''}
                        </p>
                      </div>
                      <p className="font-mono text-sm tabular-nums">
                        {fmt(it.line_total)} ฿
                      </p>
                    </div>
                    {it.breaks?.length ? (
                      <table className="mt-3 w-full max-w-lg text-sm">
                        <thead>
                          <tr className="text-xs text-ink-3">
                            {it.breaks.map((b) => (
                              <th key={b.qty} className="px-2 py-1 font-normal">
                                {b.qty} ชุด
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            {it.breaks.map((b) => (
                              <td key={b.qty} className="px-2 py-1 font-mono text-brass tabular-nums">
                                {fmt(Number(b.unit_price))}
                              </td>
                            ))}
                          </tr>
                        </tbody>
                      </table>
                    ) : (
                      <p className="mt-2 text-sm text-ink-3">
                        {it.qty} × {fmt(Number(it.unit_price))} ฿
                      </p>
                    )}
                  </article>
                ))}
              </div>

              <div className="rounded-[3px] border border-rule p-3 text-sm">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-mono">{fmt(Number(quote.subtotal))}</span>
                </div>
                <div className="mt-1 flex justify-between text-ink-3">
                  <span>VAT {Number(quote.vat_pct)}%</span>
                  <span className="font-mono">{fmt(Number(quote.vat_amt))}</span>
                </div>
                <div className="mt-2 flex justify-between border-t border-rule pt-2 font-semibold">
                  <span>Grand total</span>
                  <span className="font-mono text-brass">{fmt(Number(quote.grand_total))} ฿</span>
                </div>
              </div>
            </div>

            <aside className="space-y-3">
              <div className="rounded-[3px] border border-rule bg-paper-2 p-3 text-sm">
                <h3 className="font-semibold">ลูกค้าบนใบ</h3>
                {customer ? (
                  <dl className="mt-2 space-y-1.5 text-ink-2">
                    <div>
                      <dt className="text-xs text-ink-3">รหัส</dt>
                      <dd className="font-mono">{customer.customer_code}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-ink-3">ชื่อ</dt>
                      <dd>
                        {customer.name_th}
                        {customer.branch ? (
                          <span className="block text-xs text-ink-3">{customer.branch}</span>
                        ) : null}
                      </dd>
                    </div>
                    {customer.tax_id ? (
                      <div>
                        <dt className="text-xs text-ink-3">เลขผู้เสียภาษี</dt>
                        <dd className="font-mono">{customer.tax_id}</dd>
                      </div>
                    ) : (
                      <p className="text-xs text-warn">ยังไม่มีเลขผู้เสียภาษี</p>
                    )}
                    {customer.billing_address ? (
                      <div>
                        <dt className="text-xs text-ink-3">ที่อยู่เรียกเก็บ</dt>
                        <dd className="whitespace-pre-wrap text-xs">{customer.billing_address}</dd>
                      </div>
                    ) : null}
                    {customer.shipping_address ? (
                      <div>
                        <dt className="text-xs text-ink-3">ที่อยู่จัดส่ง</dt>
                        <dd className="whitespace-pre-wrap text-xs">{customer.shipping_address}</dd>
                      </div>
                    ) : null}
                    {contact || customer?.contact_name ? (
                      <div>
                        <dt className="text-xs text-ink-3">ผู้ติดต่อบนใบ</dt>
                        <dd>
                          {contact?.name || customer?.contact_name}
                          {contact?.title ? ` (${contact.title})` : ''}
                          <span className="block text-xs text-ink-3">
                            {[
                              contact?.phone || customer?.contact_phone || customer?.phone,
                              contact?.email || customer?.contact_email || customer?.email,
                              contact?.line_id ? `Line ${contact.line_id}` : '',
                            ]
                              .filter(Boolean)
                              .join(' · ')}
                          </span>
                        </dd>
                      </div>
                    ) : null}
                    <Link to="/customers" className="mt-2 inline-block text-xs text-teal hover:underline">
                      แก้รายละเอียดลูกค้า
                    </Link>
                  </dl>
                ) : null}
              </div>

              {(quote.status === 'draft' || quote.status === 'rejected') && can('quote.write') ? (
                <div className="rounded-[3px] border border-rule p-3 text-sm">
                  <h3 className="font-semibold">เงื่อนไขใบ (แก้ได้ตอนร่าง)</h3>
                  <div className="mt-2 space-y-2">
                    <label className="block text-xs text-ink-3">
                      ผู้ติดต่อ
                      <select
                        className="mt-1 w-full rounded-[2px] border border-rule bg-field px-2 py-1.5 text-sm"
                        value={editTerms.contactId}
                        onChange={(e) => setEditTerms((t) => ({ ...t, contactId: e.target.value }))}
                      >
                        <option value="">— ไม่ระบุ —</option>
                        {contacts.map((ct) => (
                          <option key={ct.id} value={ct.id}>
                            {ct.is_primary ? '(หลัก) ' : ''}
                            {ct.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="block text-xs text-ink-3">
                      ยืนราคาถึง
                      <input
                        type="date"
                        className="mt-1 w-full rounded-[2px] border border-rule bg-field px-2 py-1.5 font-mono text-sm"
                        value={editTerms.validUntil}
                        onChange={(e) => setEditTerms((t) => ({ ...t, validUntil: e.target.value }))}
                      />
                    </label>
                    <label className="block text-xs text-ink-3">
                      ชำระเงิน
                      <input
                        className="mt-1 w-full rounded-[2px] border border-rule bg-field px-2 py-1.5 text-sm"
                        value={editTerms.paymentTerm}
                        onChange={(e) => setEditTerms((t) => ({ ...t, paymentTerm: e.target.value }))}
                      />
                    </label>
                    <label className="block text-xs text-ink-3">
                      ส่งของ
                      <input
                        className="mt-1 w-full rounded-[2px] border border-rule bg-field px-2 py-1.5 text-sm"
                        value={editTerms.deliveryTerm}
                        onChange={(e) => setEditTerms((t) => ({ ...t, deliveryTerm: e.target.value }))}
                      />
                    </label>
                    <label className="block text-xs text-ink-3">
                      Trade term
                      <input
                        className="mt-1 w-full rounded-[2px] border border-rule bg-field px-2 py-1.5 text-sm"
                        value={editTerms.tradeTerm}
                        onChange={(e) => setEditTerms((t) => ({ ...t, tradeTerm: e.target.value }))}
                      />
                    </label>
                    <label className="block text-xs text-ink-3">
                      ข้อความถึงลูกค้า
                      <textarea
                        className="mt-1 w-full rounded-[2px] border border-rule bg-field px-2 py-1.5 text-sm"
                        rows={2}
                        value={editTerms.customerNote}
                        onChange={(e) => setEditTerms((t) => ({ ...t, customerNote: e.target.value }))}
                      />
                    </label>
                    <button
                      type="button"
                      onClick={saveTerms}
                      className="rounded-[2px] bg-teal px-3 py-1.5 text-xs font-semibold text-paper"
                    >
                      บันทึกเงื่อนไข
                    </button>
                  </div>
                </div>
              ) : (
                <div className="rounded-[3px] border border-rule p-3 text-sm">
                  <h3 className="font-semibold">เงื่อนไขใบ</h3>
                  <dl className="mt-2 space-y-1 text-xs text-ink-2">
                    <div>
                      <dt className="text-ink-3">ชำระ</dt>
                      <dd>{quote.payment_term || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-ink-3">ส่งของ</dt>
                      <dd>{quote.delivery_term || '—'}</dd>
                    </div>
                    {quote.trade_term ? (
                      <div>
                        <dt className="text-ink-3">Trade</dt>
                        <dd>{quote.trade_term}</dd>
                      </div>
                    ) : null}
                    {quote.customer_note ? (
                      <div>
                        <dt className="text-ink-3">ข้อความ</dt>
                        <dd className="whitespace-pre-wrap">{quote.customer_note}</dd>
                      </div>
                    ) : null}
                  </dl>
                </div>
              )}

              <div className="rounded-[3px] border border-rule p-3 text-sm">
                <h3 className="font-semibold">ประวัติสถานะ</h3>
                <ol className="mt-2 space-y-2">
                  {logs.map((l) => (
                    <li key={l.id} className="border-l-2 border-brass pl-2">
                      <p className="font-mono text-xs">
                        {l.from_status || '—'} → {l.to_status}
                      </p>
                      <p className="text-xs text-ink-3">
                        {l.emp_name || '—'} · {new Date(l.created_at).toLocaleString('th-TH')}
                      </p>
                      {l.note ? <p className="text-xs">{l.note}</p> : null}
                    </li>
                  ))}
                </ol>
              </div>
            </aside>
          </div>
        ) : null}
      </ListState>

      {/* Print sheet — screen preview + @media print */}
      {showPrint && quote ? (
        <div className="print-root fixed inset-0 z-40 overflow-auto bg-black/40 p-4 print:static print:bg-transparent print:p-0">
          <div className="mx-auto max-w-3xl">
            <div className="mb-3 flex justify-end gap-2 print:hidden">
              <button
                type="button"
                className="rounded-[2px] bg-ink px-3 py-1.5 text-sm text-paper"
                onClick={() => window.print()}
              >
                พิมพ์
              </button>
              <button
                type="button"
                className="rounded-[2px] border border-rule bg-paper px-3 py-1.5 text-sm"
                onClick={() => setShowPrint(false)}
              >
                ปิด
              </button>
            </div>
            <div
              ref={printRef}
              className="bg-paper p-8 text-ink shadow print:shadow-none"
              style={{ fontFamily: 'Leelawadee UI, Sarabun, sans-serif' }}
            >
              <div className="flex flex-wrap items-end justify-between gap-4 border-b-2 border-ink pb-3">
                <div>
                  <h1 className="text-2xl font-bold">ใบเสนอราคา · SmartGift</h1>
                  <p className="mt-1 text-xs text-ink-3">
                    www.smartgiftthailand.com · Line @smartgiftthailand · Tel 02-101-1644
                  </p>
                </div>
                <div className="text-right text-sm">
                  <p>
                    เลขที่ <span className="font-mono">{quote.quote_no}</span>
                  </p>
                  <p>{quoteDateTh}</p>
                </div>
              </div>

              {customer ? (
                <div className="mt-4 grid gap-2 text-sm md:grid-cols-2">
                  <div>
                    <p className="text-xs text-ink-3">ถึง</p>
                    <p className="font-semibold">{customer.name_th}</p>
                    {customer.branch ? <p className="text-xs">{customer.branch}</p> : null}
                    {customer.tax_id ? (
                      <p className="font-mono text-xs">เลขผู้เสียภาษี {customer.tax_id}</p>
                    ) : null}
                    {customer.billing_address ? (
                      <p className="mt-1 whitespace-pre-wrap text-xs">{customer.billing_address}</p>
                    ) : null}
                    {customer.province ? <p className="text-xs">จ.{customer.province}</p> : null}
                  </div>
                  <div>
                    <p className="text-xs text-ink-3">ผู้ติดต่อ</p>
                    <p>{contact?.name || customer.contact_name || '—'}</p>
                    <p className="text-xs text-ink-3">
                      {[
                        contact?.phone || customer.contact_phone || customer.phone,
                        contact?.email || customer.contact_email || customer.email,
                        contact?.line_id ? `Line ${contact.line_id}` : '',
                      ]
                        .filter(Boolean)
                        .join(' · ') || '—'}
                    </p>
                    {customer.shipping_address ? (
                      <p className="mt-2 whitespace-pre-wrap text-xs">
                        <span className="text-ink-3">จัดส่ง: </span>
                        {customer.shipping_address}
                      </p>
                    ) : null}
                  </div>
                </div>
              ) : null}

              <div className="mt-4 grid gap-2 text-sm md:grid-cols-3">
                <p>
                  <span className="text-xs text-ink-3">ชำระ </span>
                  {quote.payment_term || '—'}
                </p>
                <p>
                  <span className="text-xs text-ink-3">ส่งของ </span>
                  {quote.delivery_term || '—'}
                </p>
                <p>
                  <span className="text-xs text-ink-3">Trade </span>
                  {quote.trade_term || '—'}
                </p>
              </div>

              <div className="mt-6 space-y-6">
                {items.map((it) => (
                  <div key={it.id} className="border-b border-rule pb-4">
                    <h3 className="text-lg font-semibold">{it.item_name}</h3>
                    <p className="font-mono text-xs text-ink-3">
                      รหัส {it.sku_code || it.offer_code || '—'}
                      {it.carton_note ? ` · ${it.carton_note}` : ''}
                    </p>
                    {it.breaks?.length ? (
                      <table className="mt-2 w-full max-w-xl border-collapse text-sm">
                        <thead>
                          <tr>
                            {it.breaks.map((b) => (
                              <th key={b.qty} className="border border-rule px-2 py-1 font-normal">
                                {b.qty} ชุด
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            {it.breaks.map((b) => (
                              <td
                                key={b.qty}
                                className="border border-rule px-2 py-1 text-center font-mono font-semibold"
                              >
                                {fmt(Number(b.unit_price))}
                              </td>
                            ))}
                          </tr>
                        </tbody>
                      </table>
                    ) : null}
                  </div>
                ))}
              </div>

              <div className="mt-6 text-sm">
                <p className="font-semibold">เงื่อนไข</p>
                {SHEET_NOTES.map((n) => (
                  <p key={n}>• {n}</p>
                ))}
                {quote.customer_note ? <p className="mt-2 whitespace-pre-wrap">{quote.customer_note}</p> : null}
              </div>

              <div className="mt-6 flex flex-wrap justify-between gap-2 border-t border-ink pt-3 text-xs text-ink-3">
                <span>ราคาต่อชุด สกุลเงิน{quote.currency || 'THB'}</span>
                <span>
                  ยืนราคา {quote.valid_until || '30 วัน'} นับจากวันที่ออกใบเสนอราคา
                </span>
              </div>
              <div className="mt-4 text-right text-sm">
                <p>
                  รวมก่อน VAT <span className="font-mono">{fmt(Number(quote.subtotal))}</span>
                </p>
                <p>
                  VAT <span className="font-mono">{fmt(Number(quote.vat_amt))}</span>
                </p>
                <p className="text-base font-bold">
                  รวมทั้งสิ้น <span className="font-mono">{fmt(Number(quote.grand_total))}</span> บาท
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <style>{`
        @media print {
          body * { visibility: hidden !important; }
          .print-root, .print-root * { visibility: visible !important; }
          .print-root { position: static !important; inset: auto !important; background: white !important; padding: 0 !important; }
          .print\\:hidden { display: none !important; }
        }
      `}</style>
    </div>
  )
}
