export type User = {
  id: number
  empCode: string
  username: string
  fullName: string
  email?: string
  role: 'administrator' | 'manager' | 'sale' | string
  roleTh: string
  permissions: string[]
}

const KEY = 'price_boss_user'

export function saveUser(user: User) {
  localStorage.setItem(KEY, JSON.stringify(user))
}

export function loadUser(): User | null {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

export function clearUser() {
  localStorage.removeItem(KEY)
}

export function can(user: User | null, perm: string) {
  return !!user?.permissions?.includes(perm)
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const user = loadUser()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string> | undefined),
  }
  if (user?.id) headers['X-Emp-Id'] = String(user.id)
  const res = await fetch(path, { ...init, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || res.statusText)
  return data as T
}

export const api = {
  health: () => req<{ ok: boolean }>('/api/health'),
  login: (username: string) =>
    req<{ user: User }>('/api/auth/login', { method: 'POST', body: JSON.stringify({ username }) }),
  stats: () =>
    req<{
      offers: number
      prices: number
      customers: number
      quotations: number
      catalogProducts: number
      submittedQuotes: number
    }>('/api/stats'),
  submittedQueue: () => req<{ rows: QuoteSummary[] }>('/api/queue/submitted'),
  offers: (q = '', offset = 0, limit = 20) =>
    req<{ rows: Offer[]; total: number }>(
      `/api/offers?q=${encodeURIComponent(q)}&offset=${offset}&limit=${limit}`,
    ),
  offerPrices: (code: string) =>
    req<{ rows: PriceTier[] }>(`/api/offers/${encodeURIComponent(code)}/prices`),
  customers: (q = '') => req<{ rows: Customer[] }>(`/api/customers?q=${encodeURIComponent(q)}`),
  customer: (id: number) =>
    req<{ customer: Customer; contacts: CustomerContact[]; readiness: { ready: boolean; quoteReady: boolean; missing: string[]; warnings: string[] } }>(
      `/api/customers/${id}`,
    ),
  createCustomer: (body: Record<string, unknown>) =>
    req<{ id: number }>('/api/customers', { method: 'POST', body: JSON.stringify(body) }),
  updateCustomer: (id: number, body: Record<string, unknown>) =>
    req<{ id: number; ok: boolean }>(`/api/customers/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  createContact: (customerId: number, body: Record<string, unknown>) =>
    req<{ id: number }>(`/api/customers/${customerId}/contacts`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updateContact: (customerId: number, contactId: number, body: Record<string, unknown>) =>
    req<{ ok: boolean }>(`/api/customers/${customerId}/contacts/${contactId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  deleteContact: (customerId: number, contactId: number) =>
    req<{ ok: boolean }>(`/api/customers/${customerId}/contacts/${contactId}`, { method: 'DELETE' }),
  quotations: (status?: string) =>
    req<{ rows: QuoteSummary[] }>(
      `/api/quotations${status ? `?status=${encodeURIComponent(status)}` : ''}`,
    ),
  quotation: (id: number) =>
    req<{
      quote: QuoteDetail
      customer: Customer | null
      contact: CustomerContact | null
      contacts: CustomerContact[]
      readiness: { ready: boolean; quoteReady: boolean; missing: string[]; warnings: string[] } | null
      items: QuoteItem[]
      logs: QuoteLog[]
    }>(`/api/quotations/${id}`),
  createQuotation: (body: Record<string, unknown>) =>
    req<{ id: number }>('/api/quotations', { method: 'POST', body: JSON.stringify(body) }),
  updateQuotation: (id: number, body: Record<string, unknown>) =>
    req<{ ok: boolean; id: number }>(`/api/quotations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  transitionQuotation: (id: number, body: { action: string; note?: string }) =>
    req<{ id: number; from: string; to: string; action: string }>(
      `/api/quotations/${id}/transition`,
      { method: 'POST', body: JSON.stringify(body) },
    ),
  employees: () => req<{ rows: Employee[] }>('/api/employees'),
  roles: () => req<{ roles: Role[]; permissions: RolePerm[] }>('/api/roles'),
  reportSummary: () =>
    req<{ byGroup: ReportByGroup[]; byType: ReportByType[]; coverage: ReportCoverage }>(
      '/api/report/smartgift/summary',
    ),
  report: (
    q = '',
    opts: {
      group?: string
      type?: string
      priced?: boolean
      linked?: boolean
      offset?: number
      limit?: number
    } = {},
  ) => {
    const sp = new URLSearchParams()
    if (q) sp.set('q', q)
    if (opts.group) sp.set('group', opts.group)
    if (opts.type) sp.set('type', opts.type)
    if (opts.priced) sp.set('priced', '1')
    if (opts.linked) sp.set('linked', '1')
    sp.set('offset', String(opts.offset ?? 0))
    sp.set('limit', String(opts.limit ?? 50))
    return req<{ rows: ReportRow[]; total: number }>(`/api/report/smartgift?${sp}`)
  },
  reportCsvUrl: (
    opts: { q?: string; group?: string; type?: string; priced?: boolean; linked?: boolean } = {},
  ) => {
    const sp = new URLSearchParams()
    if (opts.q) sp.set('q', opts.q)
    if (opts.group) sp.set('group', opts.group)
    if (opts.type) sp.set('type', opts.type)
    if (opts.priced) sp.set('priced', '1')
    if (opts.linked) sp.set('linked', '1')
    const qs = sp.toString()
    return `/api/report/smartgift.csv${qs ? `?${qs}` : ''}`
  },
  salesCommand: (period?: string) =>
    req<{
      periods: SalesPeriod[]
      period: SalesPeriod | null
      splits: SalesQuotaSplit[]
      kpis: SalesKpi[]
      weeks: SalesWeek[]
    }>(`/api/report/sales-command${period ? `?period=${encodeURIComponent(period)}` : ''}`),
}

export type Offer = {
  id?: number
  code: string
  name_th: string | null
  name_en: string | null
  offer_kind: string | null
  status: string | null
  branding: string | null
  origin: string | null
  rmb: number | null
  image: string | null
}

export type PriceTier = {
  qty_tier: number | null
  unit_price: number
  unit_price_with_vat: number
  price_missing: number
  price_list_group: string | null
  flow_account_code: string | null
}

export type Customer = {
  id: number
  customer_code: string
  name_th: string
  name_en: string | null
  customer_type: string
  tax_id?: string | null
  branch?: string | null
  billing_address?: string | null
  shipping_address?: string | null
  province?: string | null
  phone: string | null
  email: string | null
  contact_name: string | null
  contact_phone?: string | null
  contact_email?: string | null
  credit_days?: number | null
  status: string
  owner_name: string | null
  price_list_group: string | null
  note?: string | null
}

export type CustomerContact = {
  id: number
  customer_id: number
  name: string
  title: string | null
  phone: string | null
  email: string | null
  line_id: string | null
  is_primary: number
  note: string | null
}

export type QuoteSummary = {
  id: number
  quote_no: string
  status: string
  quote_date: string
  valid_until: string | null
  grand_total: number
  customer_code: string
  customer_name: string
  owner_code: string
  owner_name: string
  item_count: number
}

export type QuoteLineBreak = {
  id?: number
  quotation_item_id?: number
  qty: number
  unit_price: number
  sort_order?: number
}

export type QuoteItem = {
  id: number
  quotation_id: number
  line_no: number
  offer_code: string | null
  sku_code: string | null
  item_name: string
  description: string | null
  qty: number
  qty_tier: number | null
  unit: string
  unit_price: number
  discount_amt: number
  line_total: number
  branding_note: string | null
  carton_note: string | null
  profile_code: string | null
  breaks: QuoteLineBreak[]
}

export type QuoteLog = {
  id: number
  from_status: string | null
  to_status: string
  note: string | null
  created_at: string
  emp_name: string | null
}

export type QuoteDetail = QuoteSummary & {
  owner_emp_id: number
  customer_id: number
  contact_id: number | null
  customer_note: string | null
  internal_note: string | null
  payment_term: string | null
  delivery_term: string | null
  trade_term: string | null
  price_list_group: string | null
  subtotal: number
  discount_amt: number
  vat_pct: number
  vat_amt: number
  currency: string
  approved_at: string | null
  sent_at: string | null
}

export type Employee = {
  id: number
  emp_code: string
  username: string
  full_name: string
  email: string | null
  is_active: number
  role_code: string
  role_th: string
  manager_name: string | null
}

export type Role = { id: number; code: string; name_th: string; name_en: string; description: string }
export type RolePerm = { role_code: string; permission_code: string; module: string; name_th: string }

export type ReportCoverage = {
  catalogs: number
  products: number
  groups_n: number
  types_n: number
  models: number
  offers: number
  model_offer_links: number
  price_rows: number
  product_offer_links: number
  models_no_type: number
  offers_no_price: number
  products_no_offer: number
  report_rows: number
}

export type ReportRow = {
  group_id?: number | null
  type_group: string | null
  type_id: number | string | null
  type_code?: string | null
  type_th: string | null
  type_en: string | null
  model_id?: number | null
  sig_hash?: string
  model_name: string | null
  model_name_en: string | null
  model_status: string | null
  price_source: string | null
  offer_id?: number | null
  offer_code: string | null
  offer_th: string | null
  offer_en: string | null
  offer_kind: string | null
  offer_status: string | null
  branding: string | null
  origin: string | null
  product_id?: number | null
  catalog_rmb: number | null
  price_min: number | null
  price_max: number | null
  price_vat_min: number | null
  price_vat_max: number | null
  price_tier_count: number
}

export type ReportByGroup = {
  type_group: string
  group_id?: number | null
  type_count: number
  model_count: number
  offer_count: number
  offers_with_price: number
  price_min: number | null
  price_max: number | null
}

export type ReportByType = {
  type_group: string
  type_id: number | string
  type_code?: string
  type_label: string
  model_count: number
  offer_count: number
  offers_with_price: number
  price_min: number | null
  price_max: number | null
}

export type SalesPeriod = {
  id: number
  period_code: string
  label_th: string
  year_num: number
  month_num: number
  quota_pre_vat: number
  is_current: number
  note?: string | null
}

export type SalesQuotaSplit = {
  source_id: number
  source_code: string
  source_th: string
  color_hex: string | null
  amount: number
  pct: number
}

export type SalesKpi = {
  kpi_id: number
  kpi_code: string
  kpi_th: string
  unit: string | null
  direction: string
  target_value: number | null
  target_op: string
  actual_value: number | null
  actual_note: string | null
  measure_note: string | null
}

export type SalesWeek = {
  week_plan_id: number
  week_no: number
  theme_th: string
  date_range: string | null
  revenue_goal: number | null
  tasks: { task_id: number; task_th: string; is_done: boolean }[]
}
