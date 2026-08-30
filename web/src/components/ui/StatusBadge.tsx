const STATUS_TH: Record<string, string> = {
  draft: 'ร่าง',
  submitted: 'รออนุมัติ',
  approved: 'อนุมัติแล้ว',
  rejected: 'ตีกลับ',
  sent: 'ส่งลูกค้าแล้ว',
  accepted: 'ลูกค้ารับ',
  expired: 'หมดอายุ',
  cancelled: 'ยกเลิก',
}

const STATUS_CLASS: Record<string, string> = {
  draft: 'bg-paper-3 text-ink-2',
  submitted: 'bg-[#f3e5cc] text-warn',
  approved: 'bg-[#dcebe1] text-good',
  rejected: 'bg-[#f3dcdc] text-crit',
  sent: 'bg-brass-soft text-brass',
  accepted: 'bg-[#dcebe1] text-good',
  expired: 'bg-paper-3 text-ink-3',
  cancelled: 'bg-paper-3 text-ink-3',
}

export function statusLabel(status: string) {
  return STATUS_TH[status] || status
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-[2px] px-2 py-0.5 text-xs font-medium ${STATUS_CLASS[status] || 'bg-paper-3'}`}
    >
      <span className="font-mono opacity-70">{status}</span>
      {statusLabel(status)}
    </span>
  )
}

export { STATUS_TH }
