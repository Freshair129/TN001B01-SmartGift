# Workflow — ใบเสนอราคา Price Boss

**บทบาท:** `administrator` | `manager` | `sale`  
**แหล่งสถานะ:** `quotations.status` + `quotation_status_logs`  
**DDL:** [`sql/migrate_crm_auth_quote.sql`](../sql/migrate_crm_auth_quote.sql)  
**Interactive (แนะนำ):** เมนู **เอกสาร / DataDict** → แท็บ Workflow → «วงจรชีวิตใบเสนอราคา»  
**เอกสารรวมทุกโดเมน:** [`docs/README.md`](README.md) · `web/src/data/workflows.json`

## 1. ภาพรวม lifecycle

```text
draft ──submit──► submitted ──approve──► approved ──send──► sent ──accept──► accepted
                      │                     │
                      └──reject──► rejected ┘ (sale แก้แล้วกลับ draft)
                                         │
                              cancel ──► cancelled
                              expire ──► expired
```

| From | Action | To | Who | Permission |
|---|---|---|---|---|
| — | create | `draft` | sale, manager, admin | `quote.write` |
| `draft` | update lines / breaks | `draft` | owner (หรือ write_all) | `quote.write` |
| `draft` | submit | `submitted` | owner | `quote.submit` |
| `submitted` | approve | `approved` | manager, admin | `quote.approve` |
| `submitted` | reject | `rejected` | manager, admin | `quote.approve` |
| `rejected` | revise | `draft` | owner | `quote.write` |
| `approved` | send | `sent` | owner / manager | `quote.send` |
| `sent` | accept | `accepted` | owner / manager / admin | `quote.write` + note |
| `*` (ไม่ terminal) | cancel | `cancelled` | manager, admin | `quote.cancel` |
| `approved`/`sent` | expire job | `expired` | system / admin | `valid_until < today` |
| any | override | any | **administrator only** | `admin.access` |

Terminal: `accepted`, `expired`, `cancelled` — ห้ามแก้รายการ (ยกเว้น admin override)

---

## 2. Pre / post conditions รายขั้นตอน

### 2.1 สร้างลูกค้า (ก่อนออกใบ)

| | |
|---|---|
| **Actor** | sale (ของตน) / manager / admin |
| **Permission** | `customer.write` (+ `write_all` ถ้าแก้ของคนอื่น) |
| **Pre** | `customer_code` ไม่ซ้ำ; `name_th` ไม่ว่าง |
| **Post** | `customers` แถวใหม่; sale ต้องมี `owner_emp_id = self` |
| **Fail** | code ซ้ำ → 409; blacklist ไม่รับใบใหม่ |

### 2.2 สร้างใบเสนอราคา (draft)

| | |
|---|---|
| **Actor** | sale / manager / admin |
| **Permission** | `quote.write` |
| **Pre** | ลูกค้า `status = active`; มี `quote_no` ไม่ซ้ำ; มี `owner_emp_id` |
| **Required fields** | `quote_no`, `customer_id`, `owner_emp_id`, `quote_date` |
| **Recommended** | `valid_until = quote_date + 30 days`; `currency = THB`; `vat_pct = 7` |
| **Post** | `quotations.status = draft`; log `NULL → draft` |
| **Sale scope** | ลูกค้าต้องเป็นของตน เว้นมี `customer.read_all` |

### 2.3 เพิ่มรายการ + บันไดราคา

| | |
|---|---|
| **Actor** | owner ของใบ (หรือ manager/admin) |
| **Permission** | `quote.write` |
| **Pre** | `status = draft` (หรือ `rejected` หลัง revise เป็น draft) |
| **Required per item** | `item_name`, `qty`, `unit_price`, `line_total` |
| **Required breaks** | ≥1 แถวใน `quotation_line_breaks` ต่อ item ก่อน submit |
| **Post** | อัปเดต `subtotal` / `vat_amt` / `grand_total` บนหัวใบ |

### 2.4 Submit (ส่งอนุมัติ)

| | |
|---|---|
| **Actor** | owner |
| **Permission** | `quote.submit` |
| **Pre** | `status = draft`; มี ≥1 item; ทุก item มี ≥1 break; `grand_total ≥ 0` |
| **Post** | `status = submitted`; log + note optional |
| **Fail** | ไม่มี item/break → 400 |

### 2.5 Approve

| | |
|---|---|
| **Actor** | manager / administrator |
| **Permission** | `quote.approve` |
| **Pre** | `status = submitted`; actor ≠ maker แนะนำ (maker-checker) |
| **Post** | `status = approved`; ตั้ง `approved_by`, `approved_at` |
| **Sale** | **ทำไม่ได้** |

### 2.6 Reject

| | |
|---|---|
| **Actor** | manager / administrator |
| **Permission** | `quote.approve` |
| **Pre** | `status = submitted`; **note บังคับ** (เหตุผล) |
| **Post** | `status = rejected`; log มี note |
| **Next** | sale ใช้ action revise → `draft` แล้วแก้ |

### 2.7 Send (ส่งลูกค้า)

| | |
|---|---|
| **Actor** | owner (sale) หรือ manager |
| **Permission** | `quote.send` |
| **Pre** | `status = approved` |
| **Post** | `status = sent`; ตั้ง `sent_at` |
| **Side effect** | พิมพ์/ส่งอีเมลอยู่นอก DB |

### 2.8 Accept (ลูกค้ารับข้อเสนอ)

| | |
|---|---|
| **Actor** | owner / manager / admin |
| **Pre** | `status = sent` |
| **Post** | `status = accepted` |
| **Note** | ไม่สร้าง SO อัตโนมัติในรอบนี้ |

### 2.9 Cancel

| | |
|---|---|
| **Actor** | manager / administrator |
| **Permission** | `quote.cancel` |
| **Pre** | status ∉ {`accepted`,`expired`,`cancelled`} |
| **Post** | `cancelled`; note บังคับ |

### 2.10 Expire (งานระบบ)

| | |
|---|---|
| **Actor** | batch / admin |
| **Pre** | `status ∈ {approved, sent}` และ `valid_until < CURRENT_DATE` |
| **Post** | `expired` |

---

## 3. สิทธิ์ตามบทบาท (สรุปปฏิบัติการ)

### sale

- สร้าง/แก้ลูกค้าและใบของตน
- submit, send (หลัง approve)
- **ห้าม** approve / cancel / ดูใบคนอื่น / จัดการพนักงาน

### manager

- ดูและแก้ลูกค้า/ใบทุกคน
- approve / reject / cancel / send
- แก้ product / sourcing
- ดูรายชื่อพนักงาน
- **ห้าม** จัดการ role / สร้าง user (ไม่มี `employee.write`, `role.manage`)

### administrator

- ทุกอย่างของ manager
- จัดการพนักงานและสิทธิ์
- override สถานะใดก็ได้ (พร้อมบังคับเขียน log + note)

---

## 4. ฟิลด์บังคับตามสถานะ (checklist)

| สถานะเป้าหมาย | ฟิลด์หัวใบที่ต้องมี | รายการ |
|---|---|---|
| `draft` | quote_no, customer_id, owner_emp_id, quote_date | อนุญาตว่างชั่วคราว |
| `submitted` | + valid_until, currency, totals | ≥1 item + breaks |
| `approved` | + approved_by/at | ไม่แก้ราคาโดย sale |
| `sent` | + sent_at, customer_note แนะนำ | พิมพ์เงื่อนไขมาตรฐานได้ |
| `accepted` | — | ล็อกใบ |
| `rejected` / `cancelled` | + log.note | |

เงื่อนไขพิมพ์มาตรฐาน (อ้าง UI):

1. ราคารวมสกรีนโลโก้ Full Color ทุกชิ้น  
2. ราคารวมชุดกล่องของขวัญและถุงพร้อมสกรีน  
3. ราคาอ้างอิงจำนวนตามตาราง  
4. ยังไม่รวม VAT 7% (ถ้า `vat_pct` แสดงแยก)

---

## 5. ลำดับงานแนะนำ (sale วันต่อวัน)

1. Login เป็น `sale`  
2. สร้าง/เลือกลูกค้าที่เป็น owner ของตน  
3. คำนวณราคา (เครื่องคำนวณ) → ใส่ basket  
4. สร้างใบ `draft` + บันทึก items + line_breaks  
5. Submit → รอ manager  
6. หลัง `approved` → Send / พิมพ์  
7. เมื่อลูกค้าคอนเฟิร์ม → Accept  

Manager เช้า: คิว `submitted` → approve/reject พร้อมเหตุผล
