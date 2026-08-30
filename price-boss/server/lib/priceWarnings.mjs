/**
 * Sanity warnings for a price ladder, derived from what a saved quotation line
 * or offer's price tiers actually persist: (qty, unit_price) pairs. This is a
 * strict subset of the full pricing-engine warning set (pricing.html / the
 * SmartGift Python calculator) — those also check floor-driven pricing,
 * profit inversion, shipping mode, small-order factor, and logo cost, none of
 * which survive into quotation_line_breaks / smartgift_price.
 */
export function priceTierWarnings(tiers) {
  const rows = tiers
    .filter((t) => t.qty != null && t.unit_price != null)
    .map((t) => ({ qty: Number(t.qty), unit_price: Number(t.unit_price) }))
    .sort((a, b) => a.qty - b.qty)

  const warnings = []
  for (let i = 1; i < rows.length; i++) {
    const prev = rows[i - 1]
    const cur = rows[i]

    if (cur.unit_price > prev.unit_price) {
      warnings.push({
        level: 'crit',
        message: `สั่ง ${cur.qty} ชุดแพงกว่าสั่ง ${prev.qty} ชุด — ตรวจการบรรจุกล่อง`,
      })
    }

    if (prev.unit_price > 0) {
      const drop = 1 - cur.unit_price / prev.unit_price
      if (drop > 0.25) {
        warnings.push({
          level: 'warn',
          message: `ราคาตกลง ${Math.round(drop * 100)}% ระหว่าง ${prev.qty} กับ ${cur.qty} ชุด — ควรเสนอขั้นนี้เมื่อลูกค้าถาม ไม่ใช่พิมพ์ไว้ข้าง ๆ กัน`,
        })
      }
    }
  }
  return warnings
}
