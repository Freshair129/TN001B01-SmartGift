/** Checklist ก่อนออกใบเสนอราคา — ใช้ร่วม list / form / quote */
export type CustomerLike = {
  customer_code?: string | null
  name_th?: string | null
  customer_type?: string | null
  status?: string | null
  tax_id?: string | null
  branch?: string | null
  billing_address?: string | null
  shipping_address?: string | null
  province?: string | null
  phone?: string | null
  contact_name?: string | null
  contact_phone?: string | null
  email?: string | null
  contact_email?: string | null
  price_list_group?: string | null
}

export type Readiness = {
  ready: boolean
  quoteReady: boolean
  missing: string[]
  warnings: string[]
  labels: string[]
}

const LABEL: Record<string, string> = {
  name_th: 'ชื่อลูกค้า',
  customer_code: 'รหัสลูกค้า',
  status_active: 'สถานะต้องเป็น active',
  tax_id: 'เลขผู้เสียภาษี',
  billing_address: 'ที่อยู่เรียกเก็บเงิน',
  branch: 'สาขา / สำนักงานใหญ่',
  phone: 'เบอร์โทร',
  contact_name: 'ชื่อผู้ติดต่อ',
  province: 'จังหวัด',
  shipping_or_billing: 'ที่อยู่จัดส่งหรือเรียกเก็บ',
  price_list_group: 'กลุ่มราคา',
}

export function customerReadiness(c: CustomerLike): Readiness {
  const missing: string[] = []
  const warnings: string[] = []
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
  if (!c.price_list_group) warnings.push('price_list_group')

  const labels = [...missing, ...warnings].map((k) => LABEL[k] || k)
  return {
    ready: missing.length === 0 && warnings.length === 0,
    quoteReady: missing.length === 0,
    missing,
    warnings,
    labels,
  }
}

export function readinessTone(r: Readiness): 'good' | 'warn' | 'crit' {
  if (r.ready) return 'good'
  if (r.quoteReady) return 'warn'
  return 'crit'
}
