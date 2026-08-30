import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from 'react'
import PageHeader from '../components/ui/PageHeader'
import ListState from '../components/ui/ListState'
import { useToast } from '../components/ui/Toast'
import { api, type Customer, type CustomerContact } from '../lib/api'
import { customerReadiness, readinessTone } from '../lib/customerReadiness'
import { useAuth } from '../lib/auth'

const emptyForm = {
  customerCode: '',
  nameTh: '',
  nameEn: '',
  customerType: 'company',
  taxId: '',
  branch: 'สำนักงานใหญ่',
  phone: '',
  email: '',
  contactName: '',
  contactPhone: '',
  contactEmail: '',
  province: '',
  billingAddress: '',
  shippingAddress: '',
  priceListGroup: '',
  creditDays: '0',
  note: '',
  status: 'active',
}

const emptyContact = {
  name: '',
  title: '',
  phone: '',
  email: '',
  lineId: '',
  isPrimary: true,
}

export default function CustomersPage() {
  const { can } = useAuth()
  const toast = useToast()
  const [rows, setRows] = useState<Customer[]>([])
  const [q, setQ] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(emptyForm)
  const [editId, setEditId] = useState<number | null>(null)
  const [contacts, setContacts] = useState<CustomerContact[]>([])
  const [contactForm, setContactForm] = useState(emptyContact)
  const [filterReady, setFilterReady] = useState<'all' | 'ready' | 'warn' | 'block'>('all')

  async function load(search = q) {
    try {
      const r = await api.customers(search)
      setRows(r.rows)
      setError('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'โหลดไม่สำเร็จ')
    }
  }

  useEffect(() => {
    setLoading(true)
    load('').finally(() => setLoading(false))
  }, [])

  function setField(key: keyof typeof emptyForm, value: string) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  const formReadiness = useMemo(
    () =>
      customerReadiness({
        customer_code: form.customerCode || (editId ? 'x' : ''),
        name_th: form.nameTh,
        customer_type: form.customerType,
        status: form.status,
        tax_id: form.taxId,
        branch: form.branch,
        billing_address: form.billingAddress,
        shipping_address: form.shippingAddress,
        province: form.province,
        phone: form.phone,
        contact_name: form.contactName,
        contact_phone: form.contactPhone,
        price_list_group: form.priceListGroup,
      }),
    [form, editId],
  )

  const visibleRows = useMemo(() => {
    if (filterReady === 'all') return rows
    return rows.filter((c) => {
      const r = customerReadiness(c)
      const tone = readinessTone(r)
      if (filterReady === 'ready') return tone === 'good'
      if (filterReady === 'warn') return tone === 'warn'
      return tone === 'crit'
    })
  }, [rows, filterReady])

  async function startEdit(c: Customer) {
    setEditId(c.id)
    setForm({
      customerCode: c.customer_code,
      nameTh: c.name_th,
      nameEn: c.name_en || '',
      customerType: c.customer_type || 'company',
      taxId: c.tax_id || '',
      branch: c.branch || '',
      phone: c.phone || '',
      email: c.email || '',
      contactName: c.contact_name || '',
      contactPhone: c.contact_phone || '',
      contactEmail: c.contact_email || '',
      province: c.province || '',
      billingAddress: c.billing_address || '',
      shippingAddress: c.shipping_address || '',
      priceListGroup: c.price_list_group || '',
      creditDays: String(c.credit_days ?? 0),
      note: c.note || '',
      status: c.status || 'active',
    })
    try {
      const d = await api.customer(c.id)
      setContacts(d.contacts)
    } catch {
      setContacts([])
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!can('customer.write') && !can('customer.write_all')) return
    try {
      const body = {
        customerCode: form.customerCode,
        nameTh: form.nameTh,
        nameEn: form.nameEn || null,
        customerType: form.customerType,
        taxId: form.taxId || null,
        branch: form.branch || null,
        phone: form.phone || null,
        email: form.email || null,
        contactName: form.contactName || null,
        contactPhone: form.contactPhone || null,
        contactEmail: form.contactEmail || null,
        province: form.province || null,
        billingAddress: form.billingAddress || null,
        shippingAddress: form.shippingAddress || null,
        priceListGroup: form.priceListGroup || null,
        creditDays: Number(form.creditDays) || 0,
        note: form.note || null,
        status: form.status,
      }
      if (editId) {
        await api.updateCustomer(editId, body)
        toast.push('บันทึกลูกค้าแล้ว', 'good')
      } else {
        const created = await api.createCustomer(body)
        toast.push('เพิ่มลูกค้าแล้ว', 'good')
        if (form.contactName) {
          await api.createContact(created.id, {
            name: form.contactName,
            phone: form.contactPhone || null,
            email: form.contactEmail || null,
            isPrimary: true,
          })
        }
        setEditId(created.id)
        const d = await api.customer(created.id)
        setContacts(d.contacts)
        setForm((f) => ({ ...f, customerCode: d.customer.customer_code }))
      }
      await load()
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'บันทึกไม่สำเร็จ'
      setError(msg)
      toast.push(msg, 'crit')
    }
  }

  async function addContact(e: FormEvent) {
    e.preventDefault()
    if (!editId || !contactForm.name) return
    try {
      await api.createContact(editId, {
        name: contactForm.name,
        title: contactForm.title || null,
        phone: contactForm.phone || null,
        email: contactForm.email || null,
        lineId: contactForm.lineId || null,
        isPrimary: contactForm.isPrimary,
      })
      toast.push('เพิ่มผู้ติดต่อแล้ว', 'good')
      setContactForm(emptyContact)
      const d = await api.customer(editId)
      setContacts(d.contacts)
      setForm((f) => ({
        ...f,
        contactName: d.customer.contact_name || f.contactName,
        contactPhone: d.customer.contact_phone || f.contactPhone,
        contactEmail: d.customer.contact_email || f.contactEmail,
      }))
      await load()
    } catch (err) {
      toast.push(err instanceof Error ? err.message : 'เพิ่มผู้ติดต่อไม่สำเร็จ', 'crit')
    }
  }

  async function removeContact(contactId: number) {
    if (!editId || !window.confirm('ลบผู้ติดต่อนี้?')) return
    await api.deleteContact(editId, contactId)
    const d = await api.customer(editId)
    setContacts(d.contacts)
  }

  async function setStatus(c: Customer, status: string) {
    if (!can('customer.write') && !can('customer.write_all')) return
    if (status === 'blacklist' && !window.confirm(`ตั้ง ${c.customer_code} เป็น blacklist? จะสร้างใบเสนอราคาไม่ได้`)) {
      return
    }
    try {
      await api.updateCustomer(c.id, { status })
      toast.push(`${c.customer_code} → ${status}`, 'good')
      await load()
    } catch (err) {
      toast.push(err instanceof Error ? err.message : 'อัปเดตสถานะไม่สำเร็จ', 'crit')
    }
  }

  const field = 'rounded-[2px] border border-rule bg-field px-3 py-2 text-sm w-full'
  const canWrite = can('customer.write') || can('customer.write_all')

  return (
    <div>
      <PageHeader
        eyebrow="CRM"
        title="ลูกค้า"
        description="รายละเอียดครบสำหรับออกใบเสนอราคา — เลขภาษี ที่อยู่ ผู้ติดต่อ กลุ่มราคา"
        meta={<span className="font-mono text-sm text-ink-3">{rows.length} ราย</span>}
      />

      <form
        className="mt-4 flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          load(q)
        }}
      >
        <input
          className="min-w-[200px] flex-1 rounded-[2px] border border-rule bg-field px-3 py-2 text-sm"
          placeholder="ค้นรหัส / ชื่อ / เบอร์"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button type="submit" className="rounded-[2px] bg-ink px-4 py-2 text-sm font-semibold text-paper">
          ค้นหา
        </button>
        {(
          [
            ['all', 'ทั้งหมด'],
            ['ready', 'พร้อมออกใบ'],
            ['warn', 'ข้อมูลไม่ครบ'],
            ['block', 'ออกใบไม่ได้'],
          ] as const
        ).map(([k, label]) => (
          <button
            key={k}
            type="button"
            onClick={() => setFilterReady(k)}
            className={`rounded-[2px] px-2.5 py-2 text-xs ${
              filterReady === k ? 'bg-ink text-paper' : 'border border-rule text-ink-2'
            }`}
          >
            {label}
          </button>
        ))}
      </form>

      {canWrite ? (
        <form onSubmit={onSubmit} className="mt-4 space-y-4 rounded-[3px] border border-rule bg-paper-2 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold">
              {editId ? `แก้ไขลูกค้า #${editId}` : 'เพิ่มลูกค้าใหม่'}
            </h3>
            <ReadinessPill readiness={formReadiness} />
          </div>

          {!formReadiness.ready && formReadiness.labels.length ? (
            <p className="rounded-[2px] border border-warn/40 bg-[#f3e5cc] px-3 py-2 text-xs text-warn">
              ยังขาดสำหรับใบเสนอราคาที่สมบูรณ์: {formReadiness.labels.join(' · ')}
            </p>
          ) : (
            <p className="rounded-[2px] border border-good/30 bg-[#dcebe1] px-3 py-2 text-xs text-good">
              ข้อมูลครบ — พร้อมออกใบเสนอราคา
            </p>
          )}

          <Section title="1) ข้อมูลองค์กร">
            <div className="grid gap-2 md:grid-cols-3">
              {!editId ? (
                <label className="text-xs text-ink-3">
                  รหัสลูกค้า *
                  <input required className={`${field} mt-1 font-mono`} value={form.customerCode} onChange={(e) => setField('customerCode', e.target.value)} />
                </label>
              ) : (
                <p className="text-sm">
                  รหัส <span className="font-mono text-brass">{form.customerCode}</span>
                </p>
              )}
              <label className="text-xs text-ink-3 md:col-span-2">
                ชื่อไทย *
                <input required className={`${field} mt-1`} value={form.nameTh} onChange={(e) => setField('nameTh', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3">
                ชื่ออังกฤษ
                <input className={`${field} mt-1`} value={form.nameEn} onChange={(e) => setField('nameEn', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3">
                ประเภท
                <select className={`${field} mt-1`} value={form.customerType} onChange={(e) => setField('customerType', e.target.value)}>
                  <option value="company">บริษัท</option>
                  <option value="individual">บุคคล</option>
                  <option value="government">ราชการ</option>
                </select>
              </label>
              <label className="text-xs text-ink-3">
                สถานะ
                <select className={`${field} mt-1`} value={form.status} onChange={(e) => setField('status', e.target.value)}>
                  <option value="active">active</option>
                  <option value="inactive">inactive</option>
                  <option value="blacklist">blacklist</option>
                </select>
              </label>
              <label className="text-xs text-ink-3">
                เลขผู้เสียภาษี {form.customerType !== 'individual' ? '(แนะนำ)' : ''}
                <input className={`${field} mt-1 font-mono`} value={form.taxId} onChange={(e) => setField('taxId', e.target.value)} placeholder="0-0000-00000-00-0" />
              </label>
              <label className="text-xs text-ink-3">
                สาขา / สำนักงานใหญ่
                <input className={`${field} mt-1`} value={form.branch} onChange={(e) => setField('branch', e.target.value)} />
              </label>
            </div>
          </Section>

          <Section title="2) ที่อยู่">
            <div className="grid gap-2 md:grid-cols-3">
              <label className="text-xs text-ink-3">
                จังหวัด
                <input className={`${field} mt-1`} value={form.province} onChange={(e) => setField('province', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3">
                โทรองค์กร
                <input className={`${field} mt-1`} value={form.phone} onChange={(e) => setField('phone', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3">
                อีเมลองค์กร
                <input type="email" className={`${field} mt-1`} value={form.email} onChange={(e) => setField('email', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3 md:col-span-3">
                ที่อยู่เรียกเก็บเงิน (บนใบเสนอราคา / ใบกำกับ)
                <textarea className={`${field} mt-1`} rows={2} value={form.billingAddress} onChange={(e) => setField('billingAddress', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3 md:col-span-3">
                ที่อยู่จัดส่งสินค้า
                <textarea
                  className={`${field} mt-1`}
                  rows={2}
                  value={form.shippingAddress}
                  onChange={(e) => setField('shippingAddress', e.target.value)}
                  placeholder="ว่างได้ถ้าเหมือนที่อยู่เรียกเก็บ"
                />
              </label>
            </div>
          </Section>

          <Section title="3) ผู้ติดต่อหลัก (แสดงบนใบ)">
            <div className="grid gap-2 md:grid-cols-3">
              <label className="text-xs text-ink-3">
                ชื่อผู้ติดต่อ
                <input className={`${field} mt-1`} value={form.contactName} onChange={(e) => setField('contactName', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3">
                โทรผู้ติดต่อ
                <input className={`${field} mt-1`} value={form.contactPhone} onChange={(e) => setField('contactPhone', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3">
                อีเมลผู้ติดต่อ
                <input type="email" className={`${field} mt-1`} value={form.contactEmail} onChange={(e) => setField('contactEmail', e.target.value)} />
              </label>
            </div>
          </Section>

          <Section title="4) การค้า / ราคา">
            <div className="grid gap-2 md:grid-cols-3">
              <label className="text-xs text-ink-3">
                กลุ่มราคา (P-xx)
                <input className={`${field} mt-1 font-mono`} value={form.priceListGroup} onChange={(e) => setField('priceListGroup', e.target.value)} placeholder="P-01" />
              </label>
              <label className="text-xs text-ink-3">
                เครดิต (วัน)
                <input type="number" min={0} className={`${field} mt-1 font-mono`} value={form.creditDays} onChange={(e) => setField('creditDays', e.target.value)} />
              </label>
              <label className="text-xs text-ink-3 md:col-span-3">
                โน้ตภายใน
                <textarea className={`${field} mt-1`} rows={2} value={form.note} onChange={(e) => setField('note', e.target.value)} />
              </label>
            </div>
          </Section>

          <div className="flex flex-wrap gap-2">
            <button type="submit" className="rounded-[2px] bg-teal px-4 py-2 text-sm font-semibold text-paper">
              {editId ? 'บันทึกลูกค้า' : 'เพิ่มลูกค้า'}
            </button>
            {editId ? (
              <button
                type="button"
                className="rounded-[2px] border border-rule px-4 py-2 text-sm"
                onClick={() => {
                  setEditId(null)
                  setForm(emptyForm)
                  setContacts([])
                }}
              >
                ยกเลิกแก้ไข / เพิ่มใหม่
              </button>
            ) : null}
          </div>

          {editId ? (
            <Section title="5) ผู้ติดต่อเพิ่มเติม">
              <ul className="mb-3 space-y-1 text-sm">
                {contacts.map((ct) => (
                  <li key={ct.id} className="flex flex-wrap items-center justify-between gap-2 rounded-[2px] border border-rule bg-field px-3 py-2">
                    <span>
                      {ct.is_primary ? <span className="mr-1 text-xs text-brass">หลัก</span> : null}
                      <strong>{ct.name}</strong>
                      {ct.title ? ` · ${ct.title}` : ''}
                      <span className="ml-2 text-xs text-ink-3">
                        {[ct.phone, ct.email, ct.line_id ? `Line ${ct.line_id}` : ''].filter(Boolean).join(' · ')}
                      </span>
                    </span>
                    <button type="button" className="text-xs text-crit" onClick={() => removeContact(ct.id)}>
                      ลบ
                    </button>
                  </li>
                ))}
                {!contacts.length ? <li className="text-xs text-ink-3">ยังไม่มีผู้ติดต่อเพิ่ม — ใช้ผู้ติดต่อหลักด้านบนได้</li> : null}
              </ul>
              <div className="grid gap-2 md:grid-cols-3" onSubmit={addContact}>
                <input className={field} placeholder="ชื่อ *" value={contactForm.name} onChange={(e) => setContactForm((f) => ({ ...f, name: e.target.value }))} />
                <input className={field} placeholder="ตำแหน่ง" value={contactForm.title} onChange={(e) => setContactForm((f) => ({ ...f, title: e.target.value }))} />
                <input className={field} placeholder="โทร" value={contactForm.phone} onChange={(e) => setContactForm((f) => ({ ...f, phone: e.target.value }))} />
                <input className={field} placeholder="อีเมล" value={contactForm.email} onChange={(e) => setContactForm((f) => ({ ...f, email: e.target.value }))} />
                <input className={field} placeholder="Line ID" value={contactForm.lineId} onChange={(e) => setContactForm((f) => ({ ...f, lineId: e.target.value }))} />
                <label className="flex items-center gap-2 text-sm text-ink-2">
                  <input
                    type="checkbox"
                    checked={contactForm.isPrimary}
                    onChange={(e) => setContactForm((f) => ({ ...f, isPrimary: e.target.checked }))}
                  />
                  ตั้งเป็นผู้ติดต่อหลัก
                </label>
                <button
                  type="button"
                  onClick={(e) => addContact(e as unknown as FormEvent)}
                  className="rounded-[2px] border border-rule px-3 py-2 text-sm md:col-span-3 md:w-fit"
                >
                  เพิ่มผู้ติดต่อ
                </button>
              </div>
            </Section>
          ) : null}
        </form>
      ) : null}

      <div className="mt-4">
        <ListState loading={loading} error={error} empty={!loading && !visibleRows.length} emptyText="ไม่มีลูกค้าตามตัวกรอง" onRetry={() => load()}>
          <div className="overflow-x-auto rounded-[3px] border border-rule">
            <table className="w-full min-w-[920px] text-left text-sm">
              <thead className="bg-paper-3 text-xs text-ink-3 uppercase">
                <tr>
                  <th className="px-3 py-2">รหัส</th>
                  <th className="px-3 py-2">ชื่อ</th>
                  <th className="px-3 py-2">ภาษี / ที่อยู่</th>
                  <th className="px-3 py-2">ติดต่อ</th>
                  <th className="px-3 py-2">พร้อมออกใบ</th>
                  <th className="px-3 py-2">สถานะ</th>
                  <th className="px-3 py-2">จัดการ</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((c) => {
                  const r = customerReadiness(c)
                  return (
                    <tr key={c.id} className="border-t border-rule align-top">
                      <td className="px-3 py-2 font-mono text-brass">{c.customer_code}</td>
                      <td className="px-3 py-2">
                        {c.name_th}
                        <br />
                        <span className="text-xs text-ink-3">
                          {c.customer_type}
                          {c.branch ? ` · ${c.branch}` : ''}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-xs">
                        <span className="font-mono">{c.tax_id || '—'}</span>
                        <br />
                        <span className="text-ink-3 line-clamp-2">{c.billing_address || c.province || '—'}</span>
                      </td>
                      <td className="px-3 py-2 text-xs">
                        {c.contact_name || '—'}
                        <br />
                        {c.phone || c.contact_phone || ''}
                      </td>
                      <td className="px-3 py-2">
                        <ReadinessPill readiness={r} compact />
                      </td>
                      <td className="px-3 py-2">
                        <span
                          className={`rounded-[2px] px-2 py-0.5 text-xs ${
                            c.status === 'active'
                              ? 'bg-[#dcebe1] text-good'
                              : c.status === 'blacklist'
                                ? 'bg-[#f3dcdc] text-crit'
                                : 'bg-paper-3 text-ink-3'
                          }`}
                        >
                          {c.status}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {canWrite ? (
                            <>
                              <button type="button" className="rounded-[2px] border border-rule px-2 py-1 text-xs" onClick={() => startEdit(c)}>
                                แก้รายละเอียด
                              </button>
                              {c.status !== 'active' ? (
                                <button type="button" className="rounded-[2px] border border-rule px-2 py-1 text-xs" onClick={() => setStatus(c, 'active')}>
                                  เปิดใช้
                                </button>
                              ) : null}
                              {c.status !== 'blacklist' ? (
                                <button type="button" className="rounded-[2px] border border-crit/40 px-2 py-1 text-xs text-crit" onClick={() => setStatus(c, 'blacklist')}>
                                  blacklist
                                </button>
                              ) : null}
                            </>
                          ) : null}
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

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-[2px] border border-rule/80 bg-paper/60 p-3">
      <h4 className="mb-2 text-xs font-semibold tracking-wide text-ink-2 uppercase">{title}</h4>
      {children}
    </section>
  )
}

function ReadinessPill({
  readiness,
  compact,
}: {
  readiness: ReturnType<typeof customerReadiness>
  compact?: boolean
}) {
  const tone = readinessTone(readiness)
  const label = tone === 'good' ? 'พร้อมออกใบ' : tone === 'warn' ? 'ข้อมูลไม่ครบ' : 'ออกใบไม่ได้'
  const cls =
    tone === 'good'
      ? 'bg-[#dcebe1] text-good'
      : tone === 'warn'
        ? 'bg-[#f3e5cc] text-warn'
        : 'bg-[#f3dcdc] text-crit'
  return (
    <span className={`inline-flex flex-col rounded-[2px] px-2 py-0.5 text-xs font-medium ${cls}`} title={readiness.labels.join(', ')}>
      <span>{label}</span>
      {!compact && readiness.labels.length ? (
        <span className="font-normal opacity-80">{readiness.labels.slice(0, 3).join(' · ')}</span>
      ) : null}
    </span>
  )
}
