import 'dotenv/config'
import cors from 'cors'
import express from 'express'
import mysql from 'mysql2/promise'

const PORT = Number(process.env.API_PORT || 3850)
const pool = mysql.createPool({
  host: process.env.MYSQL_HOST || '127.0.0.1',
  port: Number(process.env.MYSQL_PORT || 3310),
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD || 'rootpass',
  database: process.env.MYSQL_DATABASE || 'smartgift',
  charset: 'utf8mb4',
  waitForConnections: true,
  connectionLimit: 10,
})

const app = express()
app.use(cors())
app.use(express.json({ limit: '2mb' }))

async function q(sql, params = []) {
  const [rows] = await pool.query(sql, params)
  return rows
}

function empIdFrom(req) {
  const h = Number(req.headers['x-emp-id'] || 0)
  const qid = Number(req.query.empId || 0)
  const bid = Number(req.body?.empId || 0)
  return h || qid || bid || 0
}

async function loadAccess(empId) {
  if (!empId) return null
  const rows = await q(
    `SELECT e.id, e.is_active, r.code AS role_code
     FROM employees e JOIN roles r ON r.id = e.role_id
     WHERE e.id = ? LIMIT 1`,
    [empId],
  )
  if (!rows.length || !rows[0].is_active) return null
  const perms = await q(
    `SELECT p.code FROM employees e
     JOIN role_permissions rp ON rp.role_id = e.role_id
     JOIN permissions p ON p.id = rp.permission_id
     WHERE e.id = ?`,
    [empId],
  )
  const codes = perms.map((p) => p.code)
  return {
    empId,
    role: rows[0].role_code,
    permissions: codes,
    has: (code) => codes.includes(code),
    quoteAll: codes.includes('quote.read_all'),
    customerAll: codes.includes('customer.read_all'),
  }
}

async function requireAccess(req, res) {
  const empId = empIdFrom(req)
  const access = await loadAccess(empId)
  if (!access) {
    res.status(401).json({ error: 'ต้องระบุ X-Emp-Id ของพนักงานที่ล็อกอิน' })
    return null
  }
  return access
}

app.get('/api/health', async (_req, res) => {
  try {
    await q('SELECT 1')
    res.json({ ok: true, db: process.env.MYSQL_DATABASE || 'smartgift' })
  } catch (e) {
    res.status(500).json({ ok: false, error: String(e.message || e) })
  }
})

app.post('/api/auth/login', async (req, res) => {
  const username = String(req.body?.username || '').trim()
  if (!username) return res.status(400).json({ error: 'username required' })
  const rows = await q(
    `SELECT e.id, e.emp_code, e.username, e.full_name, e.email, e.is_active,
            r.code AS role_code, r.name_th AS role_th
     FROM employees e
     JOIN roles r ON r.id = e.role_id
     WHERE e.username = ? LIMIT 1`,
    [username],
  )
  if (!rows.length || !rows[0].is_active) {
    return res.status(401).json({ error: 'ไม่พบผู้ใช้หรือถูกปิดใช้งาน' })
  }
  const emp = rows[0]
  const perms = await q(
    `SELECT p.code FROM v_employee_access v
     JOIN permissions p ON p.code = v.permission_code
     WHERE v.employee_id = ?`,
    [emp.id],
  )
  res.json({
    user: {
      id: emp.id,
      empCode: emp.emp_code,
      username: emp.username,
      fullName: emp.full_name,
      email: emp.email,
      role: emp.role_code,
      roleTh: emp.role_th,
      permissions: perms.map((p) => p.code),
    },
  })
})

app.get('/api/stats', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return

  const [[offers]] = await pool.query('SELECT COUNT(*) AS n FROM smartgift_offer')
  const [[prices]] = await pool.query('SELECT COUNT(*) AS n FROM smartgift_price')
  const [[products]] = await pool.query('SELECT COUNT(*) AS n FROM products')

  const custSql = access.customerAll
    ? 'SELECT COUNT(*) AS n FROM customers'
    : 'SELECT COUNT(*) AS n FROM customers WHERE owner_emp_id = ?'
  const quoteSql = access.quoteAll
    ? 'SELECT COUNT(*) AS n FROM quotations'
    : 'SELECT COUNT(*) AS n FROM quotations WHERE owner_emp_id = ?'
  const submittedSql = access.quoteAll
    ? `SELECT COUNT(*) AS n FROM quotations WHERE status = 'submitted'`
    : `SELECT COUNT(*) AS n FROM quotations WHERE status = 'submitted' AND owner_emp_id = ?`

  const custParams = access.customerAll ? [] : [access.empId]
  const quoteParams = access.quoteAll ? [] : [access.empId]
  const [[customers]] = await pool.query(custSql, custParams)
  const [[quotations]] = await pool.query(quoteSql, quoteParams)
  const [[submitted]] = await pool.query(submittedSql, quoteParams)

  res.json({
    offers: offers.n,
    prices: prices.n,
    customers: customers.n,
    quotations: quotations.n,
    catalogProducts: products.n,
    submittedQuotes: submitted.n,
  })
})

app.get('/api/queue/submitted', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('quote.approve') && !access.quoteAll) {
    // sale: own submitted only (waiting)
  }
  const where = access.quoteAll
    ? `WHERE q.status = 'submitted'`
    : `WHERE q.status = 'submitted' AND q.owner_emp_id = ?`
  const params = access.quoteAll ? [] : [access.empId]
  const rows = await q(
    `SELECT v.* FROM v_quotation_summary v
     JOIN quotations q ON q.id = v.id
     ${where}
     ORDER BY v.id ASC LIMIT 50`,
    params,
  )
  res.json({ rows })
})

app.get('/api/offers', async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 20, 100)
  const offset = Number(req.query.offset) || 0
  const qtext = String(req.query.q || '').trim()
  const where = qtext
    ? `WHERE code LIKE ? OR name_th LIKE ? OR name_en LIKE ? OR IFNULL(description,'') LIKE ?`
    : ''
  const params = qtext ? Array(4).fill(`%${qtext}%`) : []
  const rows = await q(
    `SELECT id, code, name_th, name_en, offer_kind, status, branding, origin, rmb, image
     FROM smartgift_offer ${where}
     ORDER BY code LIMIT ? OFFSET ?`,
    [...params, limit, offset],
  )
  const [{ n }] = await q(
    `SELECT COUNT(*) AS n FROM smartgift_offer ${where}`,
    params,
  )
  res.json({ rows, total: n, limit, offset })
})

app.get('/api/offers/:code/prices', async (req, res) => {
  const rows = await q(
    `SELECT p.id, p.offer_id, p.qty_tier, p.unit_price, p.unit_price_with_vat, p.price_missing,
            p.price_list_group, p.flow_account_code
     FROM smartgift_price p
     JOIN smartgift_offer o ON o.id = p.offer_id
     WHERE o.code = ?
     ORDER BY p.qty_tier IS NULL, p.qty_tier`,
    [req.params.code],
  )
  res.json({ rows })
})

app.get('/api/customers', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('customer.read') && !access.customerAll) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์ดูลูกค้า' })
  }
  const qtext = String(req.query.q || '').trim()
  const clauses = []
  const params = []
  if (!access.customerAll) {
    clauses.push('c.owner_emp_id = ?')
    params.push(access.empId)
  }
  if (qtext) {
    clauses.push('(c.customer_code LIKE ? OR c.name_th LIKE ? OR IFNULL(c.phone,\'\') LIKE ?)')
    params.push(`%${qtext}%`, `%${qtext}%`, `%${qtext}%`)
  }
  const where = clauses.length ? `WHERE ${clauses.join(' AND ')}` : ''
  const rows = await q(
    `SELECT c.*, e.full_name AS owner_name
     FROM customers c
     LEFT JOIN employees e ON e.id = c.owner_emp_id
     ${where}
     ORDER BY c.id DESC LIMIT 200`,
    params,
  )
  res.json({ rows })
})

app.post('/api/customers', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('customer.write') && !access.has('customer.write_all')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์สร้างลูกค้า' })
  }
  const b = req.body || {}
  if (!b.customerCode || !b.nameTh) {
    return res.status(400).json({ error: 'customerCode and nameTh required' })
  }
  const ownerId = access.customerAll && b.ownerEmpId ? Number(b.ownerEmpId) : access.empId
  const result = await q(
    `INSERT INTO customers
      (customer_code, name_th, name_en, customer_type, tax_id, branch, billing_address, shipping_address,
       province, phone, email, contact_name, contact_phone, contact_email, credit_days,
       price_list_group, owner_emp_id, status, note, created_by)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      b.customerCode,
      b.nameTh,
      b.nameEn || null,
      b.customerType || 'company',
      b.taxId || null,
      b.branch || null,
      b.billingAddress || null,
      b.shippingAddress || null,
      b.province || null,
      b.phone || null,
      b.email || null,
      b.contactName || null,
      b.contactPhone || null,
      b.contactEmail || null,
      b.creditDays != null ? Number(b.creditDays) : 0,
      b.priceListGroup || null,
      ownerId,
      b.status || 'active',
      b.note || null,
      access.empId,
    ],
  )
  res.status(201).json({ id: result.insertId })
})

app.get('/api/customers/:id', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  const id = Number(req.params.id)
  const rows = await q(
    `SELECT c.*, e.full_name AS owner_name
     FROM customers c
     LEFT JOIN employees e ON e.id = c.owner_emp_id
     WHERE c.id = ?`,
    [id],
  )
  const c = rows[0]
  if (!c) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (!access.customerAll && Number(c.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }
  const contacts = await q(
    `SELECT * FROM customer_contacts WHERE customer_id = ? ORDER BY is_primary DESC, id`,
    [id],
  )
  res.json({ customer: c, contacts, readiness: customerReadiness(c) })
})

app.get('/api/customers/:id/contacts', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  const id = Number(req.params.id)
  const rows = await q(`SELECT id, owner_emp_id FROM customers WHERE id = ?`, [id])
  const c = rows[0]
  if (!c) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (!access.customerAll && Number(c.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }
  const contacts = await q(
    `SELECT * FROM customer_contacts WHERE customer_id = ? ORDER BY is_primary DESC, id`,
    [id],
  )
  res.json({ rows: contacts })
})

app.post('/api/customers/:id/contacts', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('customer.write') && !access.has('customer.write_all')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์แก้ลูกค้า' })
  }
  const id = Number(req.params.id)
  const rows = await q(`SELECT id, owner_emp_id FROM customers WHERE id = ?`, [id])
  const c = rows[0]
  if (!c) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (!access.customerAll && Number(c.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }
  const b = req.body || {}
  if (!b.name) return res.status(400).json({ error: 'name required' })
  if (b.isPrimary) {
    await q(`UPDATE customer_contacts SET is_primary = 0 WHERE customer_id = ?`, [id])
  }
  const result = await q(
    `INSERT INTO customer_contacts
      (customer_id, name, title, phone, email, line_id, is_primary, note)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id,
      b.name,
      b.title || null,
      b.phone || null,
      b.email || null,
      b.lineId || null,
      b.isPrimary ? 1 : 0,
      b.note || null,
    ],
  )
  if (b.isPrimary) {
    await q(
      `UPDATE customers SET contact_name = ?, contact_phone = ?, contact_email = ? WHERE id = ?`,
      [b.name, b.phone || null, b.email || null, id],
    )
  }
  res.status(201).json({ id: result.insertId })
})

app.patch('/api/customers/:id/contacts/:contactId', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('customer.write') && !access.has('customer.write_all')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์แก้ลูกค้า' })
  }
  const id = Number(req.params.id)
  const contactId = Number(req.params.contactId)
  const rows = await q(`SELECT id, owner_emp_id FROM customers WHERE id = ?`, [id])
  const c = rows[0]
  if (!c) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (!access.customerAll && Number(c.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }
  const b = req.body || {}
  if (b.isPrimary) {
    await q(`UPDATE customer_contacts SET is_primary = 0 WHERE customer_id = ?`, [id])
  }
  await q(
    `UPDATE customer_contacts SET
      name = COALESCE(?, name),
      title = COALESCE(?, title),
      phone = COALESCE(?, phone),
      email = COALESCE(?, email),
      line_id = COALESCE(?, line_id),
      is_primary = COALESCE(?, is_primary),
      note = COALESCE(?, note)
     WHERE id = ? AND customer_id = ?`,
    [
      b.name ?? null,
      b.title ?? null,
      b.phone ?? null,
      b.email ?? null,
      b.lineId ?? null,
      b.isPrimary != null ? (b.isPrimary ? 1 : 0) : null,
      b.note ?? null,
      contactId,
      id,
    ],
  )
  if (b.isPrimary) {
    const name = b.name || (await q(`SELECT name FROM customer_contacts WHERE id = ?`, [contactId]))[0]?.name
    await q(
      `UPDATE customers SET contact_name = ?, contact_phone = COALESCE(?, contact_phone), contact_email = COALESCE(?, contact_email) WHERE id = ?`,
      [name, b.phone ?? null, b.email ?? null, id],
    )
  }
  res.json({ ok: true })
})

app.delete('/api/customers/:id/contacts/:contactId', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('customer.write') && !access.has('customer.write_all')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์แก้ลูกค้า' })
  }
  const id = Number(req.params.id)
  const contactId = Number(req.params.contactId)
  const rows = await q(`SELECT id, owner_emp_id FROM customers WHERE id = ?`, [id])
  const c = rows[0]
  if (!c) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (!access.customerAll && Number(c.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }
  await q(`DELETE FROM customer_contacts WHERE id = ? AND customer_id = ?`, [contactId, id])
  res.json({ ok: true })
})

function customerReadiness(c) {
  const missing = []
  const warnings = []
  if (!c.name_th) missing.push('name_th')
  if (!c.customer_code) missing.push('customer_code')
  if (c.status !== 'active') missing.push('status_active')
  if (c.customer_type === 'company' || c.customer_type === 'government') {
    if (!c.tax_id) warnings.push('tax_id')
    if (!c.billing_address) warnings.push('billing_address')
    if (!c.branch) warnings.push('branch')
  }
  if (!c.phone && !c.contact_phone) warnings.push('phone')
  if (!c.contact_name) warnings.push('contact_name')
  if (!c.province) warnings.push('province')
  if (!c.shipping_address && !c.billing_address) warnings.push('shipping_or_billing')
  const ready = missing.length === 0 && warnings.length === 0
  const quoteReady = missing.length === 0
  return { ready, quoteReady, missing, warnings }
}

app.patch('/api/customers/:id', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  const id = Number(req.params.id)
  const rows = await q(`SELECT * FROM customers WHERE id = ?`, [id])
  const c = rows[0]
  if (!c) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (!access.customerAll && Number(c.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }
  if (!access.has('customer.write') && !access.has('customer.write_all')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์แก้ลูกค้า' })
  }
  const b = req.body || {}
  await q(
    `UPDATE customers SET
      name_th = COALESCE(?, name_th),
      name_en = COALESCE(?, name_en),
      customer_type = COALESCE(?, customer_type),
      tax_id = COALESCE(?, tax_id),
      branch = COALESCE(?, branch),
      billing_address = COALESCE(?, billing_address),
      shipping_address = COALESCE(?, shipping_address),
      province = COALESCE(?, province),
      phone = COALESCE(?, phone),
      email = COALESCE(?, email),
      contact_name = COALESCE(?, contact_name),
      contact_phone = COALESCE(?, contact_phone),
      contact_email = COALESCE(?, contact_email),
      credit_days = COALESCE(?, credit_days),
      price_list_group = COALESCE(?, price_list_group),
      status = COALESCE(?, status),
      note = COALESCE(?, note)
     WHERE id = ?`,
    [
      b.nameTh ?? null,
      b.nameEn ?? null,
      b.customerType ?? null,
      b.taxId ?? null,
      b.branch ?? null,
      b.billingAddress ?? null,
      b.shippingAddress ?? null,
      b.province ?? null,
      b.phone ?? null,
      b.email ?? null,
      b.contactName ?? null,
      b.contactPhone ?? null,
      b.contactEmail ?? null,
      b.creditDays != null ? Number(b.creditDays) : null,
      b.priceListGroup ?? null,
      b.status ?? null,
      b.note ?? null,
      id,
    ],
  )
  res.json({ id, ok: true })
})

app.get('/api/quotations', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('quote.read') && !access.quoteAll) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์ดูใบเสนอราคา' })
  }
  const status = String(req.query.status || '').trim()
  const clauses = []
  const params = []
  if (!access.quoteAll) {
    clauses.push('q.owner_emp_id = ?')
    params.push(access.empId)
  }
  if (status) {
    clauses.push('v.status = ?')
    params.push(status)
  }
  const where = clauses.length ? `WHERE ${clauses.join(' AND ')}` : ''
  const rows = await q(
    `SELECT v.* FROM v_quotation_summary v
     JOIN quotations q ON q.id = v.id
     ${where}
     ORDER BY v.id DESC LIMIT 200`,
    params,
  )
  res.json({ rows })
})

app.get('/api/quotations/:id', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  const id = Number(req.params.id)
  const heads = await q(`SELECT * FROM v_quotation_summary WHERE id = ?`, [id])
  const head = heads[0]
  if (!head) return res.status(404).json({ error: 'ไม่พบใบเสนอราคา' })
  const raw = await q(
    `SELECT owner_emp_id, customer_note, internal_note, payment_term, delivery_term, trade_term,
            subtotal, discount_amt, vat_pct, vat_amt, currency, quote_date, valid_until, status,
            customer_id, contact_id, approved_by, approved_at, sent_at
     FROM quotations WHERE id = ?`,
    [id],
  )
  const qrow = raw[0]
  if (!access.quoteAll && Number(qrow.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ใบในความดูแล' })
  }
  const customers = await q(
    `SELECT id, customer_code, name_th, name_en, customer_type, tax_id, branch,
            billing_address, shipping_address, province, phone, email,
            contact_name, contact_phone, contact_email, credit_days,
            price_list_group, status, note
     FROM customers WHERE id = ?`,
    [qrow.customer_id],
  )
  const cust = customers[0] || null
  let contacts = []
  if (cust) {
    contacts = await q(
      `SELECT * FROM customer_contacts WHERE customer_id = ? ORDER BY is_primary DESC, id`,
      [cust.id],
    )
  }
  const items = await q(
    `SELECT * FROM quotation_items WHERE quotation_id = ? ORDER BY sort_order, line_no, id`,
    [id],
  )
  const itemIds = items.map((it) => it.id)
  let breaks = []
  if (itemIds.length) {
    breaks = await q(
      `SELECT * FROM quotation_line_breaks WHERE quotation_item_id IN (${itemIds.map(() => '?').join(',')})
       ORDER BY quotation_item_id, sort_order, qty`,
      itemIds,
    )
  }
  const logs = await q(
    `SELECT l.*, e.full_name AS emp_name
     FROM quotation_status_logs l
     LEFT JOIN employees e ON e.id = l.emp_id
     WHERE l.quotation_id = ?
     ORDER BY l.id`,
    [id],
  )
  const itemsOut = items.map((it) => ({
    ...it,
    breaks: breaks.filter((b) => Number(b.quotation_item_id) === Number(it.id)),
  }))
  const selectedContact = qrow.contact_id
    ? contacts.find((c) => Number(c.id) === Number(qrow.contact_id)) || null
    : contacts.find((c) => c.is_primary) || contacts[0] || null
  res.json({
    quote: { ...head, ...qrow },
    customer: cust,
    contact: selectedContact,
    contacts,
    readiness: cust ? customerReadiness(cust) : null,
    items: itemsOut,
    logs,
  })
})

app.post('/api/quotations', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('quote.write')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์สร้างใบเสนอราคา' })
  }
  const b = req.body || {}
  const ownerEmpId = access.quoteAll && b.ownerEmpId ? Number(b.ownerEmpId) : access.empId
  if (!b.customerId || !b.quoteNo) {
    return res.status(400).json({ error: 'quoteNo, customerId required' })
  }
  const custRows = await q(
    `SELECT id, status, owner_emp_id, price_list_group, credit_days FROM customers WHERE id = ?`,
    [b.customerId],
  )
  const cust = custRows[0]
  if (!cust) return res.status(404).json({ error: 'ไม่พบลูกค้า' })
  if (cust.status === 'blacklist') {
    return res.status(409).json({ error: 'ลูกค้าอยู่ใน blacklist — สร้างใบเสนอราคาไม่ได้' })
  }
  if (cust.status !== 'active') {
    return res.status(409).json({ error: `ลูกค้าสถานะ ${cust.status} — ต้องเป็น active` })
  }
  if (!access.customerAll && Number(cust.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ลูกค้าในความดูแล' })
  }

  let contactId = b.contactId ? Number(b.contactId) : null
  if (contactId) {
    const ok = await q(
      `SELECT id FROM customer_contacts WHERE id = ? AND customer_id = ?`,
      [contactId, b.customerId],
    )
    if (!ok.length) return res.status(400).json({ error: 'ผู้ติดต่อไม่ใช่ของลูกค้ารายนี้' })
  } else {
    const prim = await q(
      `SELECT id FROM customer_contacts WHERE customer_id = ? ORDER BY is_primary DESC, id LIMIT 1`,
      [b.customerId],
    )
    contactId = prim[0]?.id || null
  }

  const items = Array.isArray(b.items) ? b.items : []
  if (!items.length) {
    return res.status(400).json({ error: 'ต้องมีอย่างน้อย 1 รายการสินค้า' })
  }

  const quoteDate = b.quoteDate || new Date().toISOString().slice(0, 10)
  let validUntil = b.validUntil || null
  if (!validUntil) {
    const d = new Date(quoteDate)
    d.setDate(d.getDate() + 30)
    validUntil = d.toISOString().slice(0, 10)
  }

  const paymentTerm =
    b.paymentTerm ||
    (cust.credit_days > 0 ? `เครดิต ${cust.credit_days} วัน` : 'เงินสด / โอนก่อนผลิต')
  const priceListGroup = b.priceListGroup || cust.price_list_group || null

  const conn = await pool.getConnection()
  try {
    await conn.beginTransaction()
    const [ins] = await conn.query(
      `INSERT INTO quotations
        (quote_no, customer_id, contact_id, owner_emp_id, status, quote_date, valid_until, currency, price_list_group,
         payment_term, delivery_term, trade_term, customer_note, internal_note, created_by)
       VALUES (?, ?, ?, ?, 'draft', ?, ?, 'THB', ?, ?, ?, ?, ?, ?, ?)`,
      [
        b.quoteNo,
        b.customerId,
        contactId,
        ownerEmpId,
        quoteDate,
        validUntil,
        priceListGroup,
        paymentTerm,
        b.deliveryTerm || 'ส่งตามนัดหมายหลังผลิต',
        b.tradeTerm || null,
        b.customerNote || null,
        b.internalNote || null,
        access.empId,
      ],
    )
    const quoteId = ins.insertId
    let subtotal = 0
    for (let i = 0; i < items.length; i++) {
      const it = items[i]
      const lineTotal = Number(it.qty || 1) * Number(it.unitPrice || 0) - Number(it.discountAmt || 0)
      subtotal += lineTotal
      const [itemIns] = await conn.query(
        `INSERT INTO quotation_items
          (quotation_id, line_no, offer_code, sku_code, item_name, description, qty, qty_tier, unit,
           unit_price, discount_amt, line_total, branding_note, carton_note, profile_code, sort_order)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          quoteId,
          i + 1,
          it.offerCode || null,
          it.skuCode || it.offerCode || null,
          it.itemName,
          it.description || null,
          it.qty || 1,
          it.qtyTier || null,
          it.unit || 'ชิ้น',
          it.unitPrice || 0,
          it.discountAmt || 0,
          lineTotal,
          it.brandingNote || null,
          it.cartonNote || null,
          it.profileCode || null,
          i + 1,
        ],
      )
      const itemId = itemIns.insertId
      const lineBreaks = Array.isArray(it.breaks) ? it.breaks : []
      for (let j = 0; j < lineBreaks.length; j++) {
        const br = lineBreaks[j]
        await conn.query(
          `INSERT INTO quotation_line_breaks (quotation_item_id, qty, unit_price, sort_order)
           VALUES (?, ?, ?, ?)`,
          [itemId, Number(br.qty), Number(br.unitPrice), j + 1],
        )
      }
      // if no breaks provided, seed from selected tier
      if (!lineBreaks.length && it.qty != null) {
        await conn.query(
          `INSERT INTO quotation_line_breaks (quotation_item_id, qty, unit_price, sort_order)
           VALUES (?, ?, ?, 1)`,
          [itemId, Number(it.qtyTier || it.qty || 1), Number(it.unitPrice || 0)],
        )
      }
    }
    const vatPct = Number(b.vatPct != null ? b.vatPct : 7)
    const discountAmt = Number(b.discountAmt || 0)
    const base = Math.max(0, subtotal - discountAmt)
    const vatAmt = Math.round(base * vatPct) / 100
    const grand = base + vatAmt
    await conn.query(
      `UPDATE quotations SET subtotal=?, discount_amt=?, vat_pct=?, vat_amt=?, grand_total=? WHERE id=?`,
      [subtotal, discountAmt, vatPct, vatAmt, grand, quoteId],
    )
    await conn.query(
      `INSERT INTO quotation_status_logs (quotation_id, from_status, to_status, emp_id, note)
       VALUES (?, NULL, 'draft', ?, 'สร้างใบเสนอราคา')`,
      [quoteId, access.empId],
    )
    await conn.commit()
    res.status(201).json({ id: quoteId, subtotal, vatAmt, grandTotal: grand })
  } catch (e) {
    await conn.rollback()
    res.status(500).json({ error: String(e.message || e) })
  } finally {
    conn.release()
  }
})

app.patch('/api/quotations/:id', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('quote.write')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์แก้ใบเสนอราคา' })
  }
  const id = Number(req.params.id)
  const rows = await q(`SELECT * FROM quotations WHERE id = ?`, [id])
  const quote = rows[0]
  if (!quote) return res.status(404).json({ error: 'ไม่พบใบเสนอราคา' })
  if (!access.quoteAll && Number(quote.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'ไม่ใช่ใบในความดูแล' })
  }
  if (!['draft', 'rejected'].includes(quote.status) && !access.has('admin.access')) {
    return res.status(409).json({ error: `แก้ได้เฉพาะ draft/rejected (ปัจจุบัน: ${quote.status})` })
  }
  const b = req.body || {}
  let nextContactId = quote.contact_id
  if (b.contactId !== undefined) {
    nextContactId = b.contactId ? Number(b.contactId) : null
    if (nextContactId) {
      const ok = await q(
        `SELECT id FROM customer_contacts WHERE id = ? AND customer_id = ?`,
        [nextContactId, quote.customer_id],
      )
      if (!ok.length) return res.status(400).json({ error: 'ผู้ติดต่อไม่ใช่ของลูกค้ารายนี้' })
    }
  }
  await q(
    `UPDATE quotations SET
      contact_id = ?,
      valid_until = COALESCE(?, valid_until),
      payment_term = COALESCE(?, payment_term),
      delivery_term = COALESCE(?, delivery_term),
      trade_term = COALESCE(?, trade_term),
      customer_note = COALESCE(?, customer_note),
      internal_note = COALESCE(?, internal_note),
      price_list_group = COALESCE(?, price_list_group)
     WHERE id = ?`,
    [
      nextContactId,
      b.validUntil ?? null,
      b.paymentTerm ?? null,
      b.deliveryTerm ?? null,
      b.tradeTerm ?? null,
      b.customerNote ?? null,
      b.internalNote ?? null,
      b.priceListGroup ?? null,
      id,
    ],
  )
  res.json({ ok: true, id })
})

/** Quotation status transitions — mirrors docs/workflow-quotation.md */
const QUOTE_TRANSITIONS = {
  submit: { from: ['draft'], to: 'submitted', perm: 'quote.submit' },
  approve: { from: ['submitted'], to: 'approved', perm: 'quote.approve' },
  reject: { from: ['submitted'], to: 'rejected', perm: 'quote.approve', noteRequired: true },
  revise: { from: ['rejected'], to: 'draft', perm: 'quote.write' },
  send: { from: ['approved'], to: 'sent', perm: 'quote.send' },
  accept: { from: ['sent'], to: 'accepted', perm: 'quote.write' },
  cancel: {
    from: ['draft', 'submitted', 'approved', 'sent', 'rejected'],
    to: 'cancelled',
    perm: 'quote.cancel',
    noteRequired: true,
  },
}

app.post('/api/quotations/:id/transition', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  const id = Number(req.params.id)
  const action = String(req.body?.action || '')
  const note = req.body?.note ? String(req.body.note).trim() : ''
  const rule = QUOTE_TRANSITIONS[action]
  if (!id || !rule) {
    return res.status(400).json({ error: 'id, action required' })
  }
  if (rule.noteRequired && !note) {
    return res.status(400).json({ error: 'note required for this action' })
  }
  if (!access.has(rule.perm)) {
    return res.status(403).json({ error: `missing permission ${rule.perm}` })
  }

  const rows = await q(`SELECT id, status, owner_emp_id FROM quotations WHERE id = ?`, [id])
  const quote = rows[0]
  if (!quote) return res.status(404).json({ error: 'quotation not found' })
  if (!rule.from.includes(quote.status)) {
    return res.status(409).json({ error: `cannot ${action} from status ${quote.status}` })
  }
  if (!access.quoteAll && Number(quote.owner_emp_id) !== access.empId) {
    return res.status(403).json({ error: 'not owner of this quotation' })
  }

  const conn = await pool.getConnection()
  try {
    await conn.beginTransaction()
    await conn.query(`UPDATE quotations SET status = ? WHERE id = ?`, [rule.to, id])
    if (action === 'approve') {
      await conn.query(
        `UPDATE quotations SET approved_by = ?, approved_at = NOW() WHERE id = ?`,
        [access.empId, id],
      )
    }
    if (action === 'send') {
      await conn.query(`UPDATE quotations SET sent_at = NOW() WHERE id = ?`, [id])
    }
    await conn.query(
      `INSERT INTO quotation_status_logs (quotation_id, from_status, to_status, emp_id, note)
       VALUES (?, ?, ?, ?, ?)`,
      [id, quote.status, rule.to, access.empId, note || action],
    )
    await conn.commit()
    res.json({ id, from: quote.status, to: rule.to, action })
  } catch (e) {
    await conn.rollback()
    res.status(500).json({ error: String(e.message || e) })
  } finally {
    conn.release()
  }
})

app.get('/api/employees', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  if (!access.has('employee.read') && !access.has('employee.write')) {
    return res.status(403).json({ error: 'ไม่มีสิทธิ์ดูพนักงาน' })
  }
  const rows = await q(
    `SELECT e.id, e.emp_code, e.username, e.full_name, e.email, e.phone, e.is_active,
            r.code AS role_code, r.name_th AS role_th,
            m.full_name AS manager_name
     FROM employees e
     JOIN roles r ON r.id = e.role_id
     LEFT JOIN employees m ON m.id = e.manager_id
     ORDER BY r.id, e.id`,
  )
  res.json({ rows })
})

app.get('/api/roles', async (req, res) => {
  const access = await requireAccess(req, res)
  if (!access) return
  const roles = await q(`SELECT id, code, name_th, name_en, description FROM roles WHERE is_active=1`)
  const perms = await q(
    `SELECT r.code AS role_code, p.code AS permission_code, p.module, p.name_th
     FROM role_permissions rp
     JOIN roles r ON r.id = rp.role_id
     JOIN permissions p ON p.id = rp.permission_id
     ORDER BY r.id, p.module, p.id`,
  )
  res.json({ roles, permissions: perms })
})

app.get('/api/report/smartgift/summary', async (_req, res) => {
  const byGroup = await q(
    `SELECT * FROM v_smartgift_report_by_group ORDER BY type_group`,
  )
  const byType = await q(
    `SELECT * FROM v_smartgift_report_by_type ORDER BY type_group, type_label LIMIT 200`,
  )
  const [[c]] = await pool.query(`
    SELECT
      (SELECT COUNT(*) FROM catalogs) AS catalogs,
      (SELECT COUNT(*) FROM products) AS products,
      (SELECT COUNT(*) FROM smartgift_group) AS groups_n,
      (SELECT COUNT(*) FROM smartgift_type) AS types_n,
      (SELECT COUNT(*) FROM smartgift_model) AS models,
      (SELECT COUNT(*) FROM smartgift_offer) AS offers,
      (SELECT COUNT(*) FROM smartgift_model_offer) AS model_offer_links,
      (SELECT COUNT(*) FROM smartgift_price) AS price_rows,
      (SELECT COUNT(*) FROM product_offer_link) AS product_offer_links,
      (SELECT COUNT(*) FROM smartgift_model WHERE type_id IS NULL) AS models_no_type,
      (SELECT COUNT(*) FROM smartgift_offer o
        WHERE NOT EXISTS (
          SELECT 1 FROM smartgift_price p WHERE p.offer_id = o.id AND p.price_missing = 0
        )) AS offers_no_price,
      (SELECT COUNT(*) FROM products p
        WHERE NOT EXISTS (
          SELECT 1 FROM product_offer_link l WHERE l.product_id = p.id
        )) AS products_no_offer,
      (SELECT COUNT(*) FROM v_smartgift_report) AS report_rows
  `)
  res.json({ byGroup, byType, coverage: c })
})

app.get('/api/report/smartgift', async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 50, 200)
  const offset = Number(req.query.offset) || 0
  const qtext = String(req.query.q || '').trim()
  const group = String(req.query.group || '').trim()
  const typeId = String(req.query.type || '').trim()
  const onlyPriced = String(req.query.priced || '') === '1'
  const onlyLinked = String(req.query.linked || '') === '1'

  const where = []
  const params = []
  if (qtext) {
    where.push(
      `(IFNULL(model_name,'') LIKE ? OR IFNULL(offer_code,'') LIKE ? OR IFNULL(offer_th,'') LIKE ? OR IFNULL(type_th,'') LIKE ?)`,
    )
    params.push(`%${qtext}%`, `%${qtext}%`, `%${qtext}%`, `%${qtext}%`)
  }
  if (group) {
    where.push(`type_group = ?`)
    params.push(group)
  }
  if (typeId) {
    where.push(`(CAST(type_id AS CHAR) = ? OR type_code = ?)`)
    params.push(typeId, typeId)
  }
  if (onlyPriced) {
    where.push(`price_tier_count > 0`)
  }
  if (onlyLinked) {
    where.push(`product_id IS NOT NULL`)
  }
  const wh = where.length ? `WHERE ${where.join(' AND ')}` : ''
  const rows = await q(
    `SELECT group_id, type_group, type_id, type_code, type_th, type_en,
            model_id, sig_hash, model_name, model_name_en, model_status, price_source,
            offer_id, offer_code, offer_th, offer_en, offer_kind, offer_status, branding, origin,
            catalog_rmb, price_min, price_max, price_vat_min, price_vat_max, price_tier_count, product_id
     FROM v_smartgift_report
     ${wh}
     ORDER BY type_group, type_th, model_name, offer_code
     LIMIT ? OFFSET ?`,
    [...params, limit, offset],
  )
  const [{ n }] = await q(`SELECT COUNT(*) AS n FROM v_smartgift_report ${wh}`, params)
  res.json({ rows, total: n, limit, offset })
})

app.get('/api/report/smartgift.csv', async (req, res) => {
  const qtext = String(req.query.q || '').trim()
  const group = String(req.query.group || '').trim()
  const typeId = String(req.query.type || '').trim()
  const onlyPriced = String(req.query.priced || '') === '1'
  const onlyLinked = String(req.query.linked || '') === '1'
  const where = []
  const params = []
  if (qtext) {
    where.push(
      `(IFNULL(model_name,'') LIKE ? OR IFNULL(offer_code,'') LIKE ? OR IFNULL(offer_th,'') LIKE ? OR IFNULL(type_th,'') LIKE ?)`,
    )
    params.push(`%${qtext}%`, `%${qtext}%`, `%${qtext}%`, `%${qtext}%`)
  }
  if (group) {
    where.push(`type_group = ?`)
    params.push(group)
  }
  if (typeId) {
    where.push(`(CAST(type_id AS CHAR) = ? OR type_code = ?)`)
    params.push(typeId, typeId)
  }
  if (onlyPriced) where.push(`price_tier_count > 0`)
  if (onlyLinked) where.push(`product_id IS NOT NULL`)
  const wh = where.length ? `WHERE ${where.join(' AND ')}` : ''
  const rows = await q(
    `SELECT group_id, type_group, type_id, type_code, type_th,
            model_id, model_name, model_status,
            offer_id, offer_code, offer_th, offer_kind, offer_status,
            product_id, catalog_rmb, price_min, price_max, price_vat_min, price_vat_max, price_tier_count
     FROM v_smartgift_report ${wh}
     ORDER BY type_group, type_th, model_name, offer_code
     LIMIT 20000`,
    params,
  )
  const headers = [
    'group_id',
    'type_group',
    'type_id',
    'type_code',
    'type_th',
    'model_id',
    'model_name',
    'model_status',
    'offer_id',
    'offer_code',
    'offer_th',
    'offer_kind',
    'offer_status',
    'product_id',
    'catalog_rmb',
    'price_min',
    'price_max',
    'price_vat_min',
    'price_vat_max',
    'price_tier_count',
  ]
  const esc = (v) => {
    if (v == null) return ''
    const s = String(v)
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`
    return s
  }
  const lines = [headers.join(',')]
  for (const r of rows) {
    lines.push(headers.map((h) => esc(r[h])).join(','))
  }
  const bom = '\uFEFF'
  res.setHeader('Content-Type', 'text/csv; charset=utf-8')
  res.setHeader('Content-Disposition', 'attachment; filename="smartgift-report.csv"')
  res.send(bom + lines.join('\n'))
})

app.get('/api/report/sales-command', async (req, res) => {
  const periodCode = String(req.query.period || '').trim()
  const periods = await q(
    `SELECT id, period_code, label_th, year_num, month_num, quota_pre_vat, is_current, note
     FROM sales_period ORDER BY period_code DESC`,
  )
  let period = periods.find((p) => p.period_code === periodCode)
  if (!period) period = periods.find((p) => p.is_current) || periods[0]
  if (!period) return res.json({ period: null, splits: [], kpis: [], weeks: [] })

  const splits = await q(
    `SELECT source_id, source_code, source_th, color_hex, amount, pct
     FROM v_sales_quota_split WHERE period_id = ? ORDER BY pct DESC`,
    [period.id],
  )
  const kpis = await q(
    `SELECT kpi_id, kpi_code, kpi_th, unit, direction, target_value, target_op,
            actual_value, actual_note, measure_note
     FROM v_sales_period_kpi WHERE period_id = ? ORDER BY sort_order`,
    [period.id],
  )
  const weekRows = await q(
    `SELECT week_plan_id, week_no, theme_th, date_range, revenue_goal,
            task_id, task_th, task_sort, is_done
     FROM v_sales_week_plan WHERE period_id = ?
     ORDER BY week_no, task_sort`,
    [period.id],
  )
  const weekMap = new Map()
  for (const r of weekRows) {
    if (!weekMap.has(r.week_plan_id)) {
      weekMap.set(r.week_plan_id, {
        week_plan_id: r.week_plan_id,
        week_no: r.week_no,
        theme_th: r.theme_th,
        date_range: r.date_range,
        revenue_goal: r.revenue_goal,
        tasks: [],
      })
    }
    if (r.task_id) {
      weekMap.get(r.week_plan_id).tasks.push({
        task_id: r.task_id,
        task_th: r.task_th,
        is_done: !!r.is_done,
      })
    }
  }
  res.json({
    periods,
    period,
    splits,
    kpis,
    weeks: [...weekMap.values()],
  })
})

app.listen(PORT, () => {
  console.log(`price_boss API http://127.0.0.1:${PORT}`)
})
