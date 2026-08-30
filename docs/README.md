# เอกสาร Price Boss / SmartGift

## Interactive (แนะนำ)

ในแอป SPA หลัง login:

- เมนู **เอกสาร / DataDict** → `/docs`
- แท็บ **Data Dictionary** — ค้นตาราง/คอลัมน์, กรองโดเมน, ดู FK คลิกข้ามตาราง
- แท็บ **Workflow** — ขั้นตอนละเอียด + transition + permission matrix + checklist สถานะใบ

แหล่งข้อมูล interactive:

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `web/src/data/schemaCatalog.json` | schema จาก MySQL จริง (46 tables/views) |
| `web/src/data/workflows.json` | workflow 7 เส้น + สิทธิ์ |
| `scripts/export_schema_catalog.py` | regenerate schema JSON |

```powershell
python D:\price_boss\scripts\export_schema_catalog.py
```

## Markdown อ้างอิง (CRM / Quote)

- [data-dictionary-crm.md](./data-dictionary-crm.md) — คอลัมน์ CRM/RBAC/ใบเสนอราคา
- [workflow-quotation.md](./workflow-quotation.md) — lifecycle ใบเสนอราคา

## โดเมนใน DB `smartgift`

1. **rbac** — roles, permissions, employees  
2. **crm** — customers, contacts  
3. **quote** — quotations, items, breaks, status logs  
4. **catalog** — catalogs, products, tags  
5. **pricelist** — group/type/model/offer/price + junction  
6. **sourcing** — china RFQ  
7. **sales** — Quota & Plan (Sales Command)  
8. **views** — รายงานและสรุป
