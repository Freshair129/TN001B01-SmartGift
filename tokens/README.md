# Design tokens

`smartgift-color.tokens.json` — W3C Design Tokens Community Group format
สีหลักสุ่มจากไฟล์โลโก้จริง (IMG_4363.jpeg) ขั้นกลางของ scale เป็นส่วนขยายสำหรับใช้ใน UI

ไฟล์นี้เป็น source of truth ของสีทั้งระบบ
`scripts/brand_kit.py` อ่านไฟล์นี้ resolve alias `{color.x.y}` แล้ว emit เป็น CSS custom properties
แก้สีที่นี่ที่เดียว แล้วรัน `python scripts/build_catalog_pages.py`
