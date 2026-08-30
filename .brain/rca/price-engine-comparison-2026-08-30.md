---
version: "0.1.3b"
created_at: "2026-08-30T09:43:56+07:00,ATHER,uncommitted"
last_update: "2026-08-30T09:54:02+07:00,ATHER"
status: "need review"
superseded_by: null
attributes:
  domain: pricing
  scope: Price Boss and SmartGift read-only comparison
  language: th
---

# RCA — เปรียบเทียบ Price Engine: Price Boss vs SmartGift

## คำตัดสิน

**ผลล่าสุด: สูตรแกนกลางที่รับ input เทียบกันได้ให้ผลตรงกันในชุดปกติ จึงไม่มีหลักฐานให้ประกาศว่าฝ่ายใดถูกต้องกว่าทั้งระบบ** ข้อได้เปรียบของ Price Boss เรื่องต้นทุนโลโก้ใน snapshotแรกถูกลดลง เพราะงานอื่นแก้ SmartGift และตรวจซ้ำผ่านแล้ว อย่างไรก็ตาม **ยังไม่ผ่านทั้งคู่สำหรับการออกใบเสนอราคาอัตโนมัติที่เชื่อถือได้ end-to-end**: SmartGift ยังมี config/input/missing-cost gates ที่ไม่ครบ ส่วน Price Boss เก็บ/พิมพ์ราคาคนละชุดและมี state เก่าหลัง input invalid

### ตรวจซ้ำหลังมีการแก้จากงานอื่นระหว่าง audit

เวลา09:50พบ SmartGift calculator/tests/service เปลี่ยนโดยงานอื่น ไม่ใช่ทีม audit นี้ จึงตรวจซ้ำถึง **09:54:02 ICT** ไม่ใช้ข้อสรุป snapshotเก่าปะปน:

- **แก้แล้วใน Python calculator และ service:** ส่ง flat/UV rate, positions และสีโลโก้เข้า landed/quote; รับ USD FX ผ่าน constructorของcalculator; ป้องกัน float noise ก่อน ceil10
- **SG-01 custom_logo_thb แก้แล้ว:** ล่าสุดส่งเข้า single_landed และ quoted tiers ครบ; inputเดิมได้ landed442.40/sell600/profit15,760 ตรงกับ Price Boss
- **ยังไม่แก้:** config schema mismatch/input validation/shared rates/missing-cost handling; ROUND-01 และ Price Boss findings ยังเปิด
- Tests ล่าสุด **20/20** (pricing10 + service6 + inventory4) ผ่าน; initial snapshot ก่อนงานอื่นแก้ผ่าน9/9
- รัน parity ใหม่กับ hashล่าสุดแล้ว: 1,728 inputs/9,504 breaks ตรงกัน; boundary100 inputs/550 breaks ยังต่างราคาขาย12 และ landed/profit210 เช่นเดิม
- เพิ่มเทียบ flat/UV/silk/none × profiles2 × custom cost0/100 =16inputs/88breaks หลังแก้ ได้ landed/selling priceตรงกันทุกbreak
- Latest calculator SHA256 `86030E388753E0047EC05E660CAC6717BFDD9C149DAA401160A3E4F267654717`; service SHA256 `19D567B5536A00029CF07395205D2E44AA5E6438077BDDFCFA548E0696834076` (stableก่อน/หลังทดสอบ)
- Catalogก็ถูกแก้ภายนอกแต่ counts/cost-provenance checksข้างล่างถูกตรวจซ้ำ ณ09:51:28; แยก timestampนี้จาก engine refresh

ไม่ได้ตัดสินว่าราคาที่สูงกว่าหรือต่ำกว่าคือราคาที่ถูกต้อง และไม่ได้ใช้คำประกาศ authority หรือ tests ผ่านแทนหลักฐานธุรกิจ

- งานวิเคราะห์: C-2, read-only ต่อ application code/config/data; ไม่รัน pipeline, LLM หรือบริการภายนอก
- อนุมัติในรอบนี้ครอบคลุมการตั้งค่า MySQL ตามเอกสารเดิม ไม่ใช่การแก้ price engine
- รายงานนี้เป็น diagnostic/RCA และข้อเสนอป้องกัน ยังไม่ใช่การอนุมัติเปลี่ยนสูตร
- ตรวจ 2026-08-30 ICT; ขอบเขตเครื่อง local ไม่ใช่ production/UAT
- `O:/price-boss` ไม่มี Git; SmartGift HEAD `326576d9496f155796341767c5fd895d8d752059`, main ahead origin/main 8 commits
- Snapshot ระหว่างตรวจพบ SmartGift มีงานนอกขอบเขต `package.json`, `public/`, CR-006 และต่อมามี calculator/tests เปลี่ยน; ไม่แตะงานเหล่านี้

## 1. เทียบสิ่งเดียวกันก่อน

| เส้นทาง | Price Boss | SmartGift | ข้อสรุป |
|---|---|---|---|
| Calculator standalone | `pricing.html`: freight → landed → ladder/floor → ceil10 | `src/cascade_engine/pricing_calculator.py`: โครงเดียวกัน | เป็นสูตรตระกูลเดียวกัน ไม่ใช่สองอัลกอริทึมอิสระ |
| ต้นทุนเพิ่มเติม | ส่ง flat/UV rate, colors, inland, unit/order cost เข้า quote | calculator/service ล่าสุดส่ง flat/UV/colors/custom costครบในกรณีที่ทดสอบ | parity16inputs/88breaksผ่าน; ไม่ใช้ข้อบกพร่องเก่าตัดสิน |
| ออกใบที่บันทึก | React SPA → Express → MySQL; รับราคากับ breaks จาก client | AutoQuote service → Python; รับ factory cost จาก caller | ต้องตรวจความสอดคล้องที่ caller ไม่ใช่เฉพาะ engine |
| GraphRAG/BOM | ไม่ใช่ขอบเขต calculator นี้ | อีกเส้นทางใช้ InventoryCascadeEngine + ราคา JSON | ไม่ได้ใช้ Python ladder engine เดียวกันทุกเส้นทาง |
| แหล่งราคาเดิม | SQL snapshot มี source_ref, group, price_missing | ประกาศ FlowAccount authority แต่ต้นทุน master ปัจจุบันตรงกับ seed literals | ตรวจ lineage ของราคาขายแยกจากต้นทุน |
| สถานะพร้อมใช้งานจริง | ไม่ผ่าน end-to-end pricing gates | ไม่ผ่าน cost/config/input gates | ยังรับรองผู้ชนะทั้งระบบไม่ได้ |

หลักฐานเส้นทาง Price Boss: [App.tsx](O:/price-boss/web/src/App.tsx), [Dockerfile](O:/price-boss/docker/web/Dockerfile) build/copy เฉพาะ web app; ไม่พบ route/copy/import เชื่อม root `pricing.html` เข้า deployed SPA ดังนั้นผล calculator ไม่ได้พิสูจน์เส้นทาง API/ใบพิมพ์โดยอัตโนมัติ

หลักฐาน SmartGift: [auto_quote_service.py](O:/Org-EtohGroup/SmartGift/pipeline/auto_quote_service.py:48), [smartgift_graphrag_agent.py](O:/Org-EtohGroup/SmartGift/src/graphrag_agent/smartgift_graphrag_agent.py:26). CR-005 ยัง `status: proposed`; ไม่ยืนยัน LINE/MCP live

## 2. สูตรที่ทั้งคู่ใช้

- Factory/unit = RMB × FX × small-order factor
- Landed/unit = factory + international freight/order ÷ qty + logo/order ÷ qty + China inland/unit + extra unit cost (เมื่อ caller ส่งครบ)
- Standard: anchor 500 ชุด, markup ตามช่วง **factory cost**: 3.00 / 2.73 / 2.62 / 2.45 / 2.14
- Corporate: anchor 1,000 ชุด, markup 1.47 × **landed cost** อ้างอิง freight class electronic_tisi
- Ladder = anchor price × factor ของขั้น ÷ factor ของ anchor
- Profit floor price = landed/unit + (minimum profit + order cost) ÷ qty
- Sell/unit = ปัดขึ้นหลักสิบของ max(ladder, floor)
- Profit = (sell − landed) × qty − order cost; margin = profit ÷ sales

สูตรคณิตศาสตร์ส่วนนี้สอดคล้องกันเมื่อ input และ rounding ตรงกัน แต่ไม่พิสูจน์ว่าค่า freight/FX/factors เป็นต้นทุนที่อนุมัติและเป็นปัจจุบัน

## 3. ผลทดสอบเปรียบเทียบจริง

ใช้ JavaScript engine ที่ extract จากไฟล์จริงผ่าน Node vm และ import Python module จริงแบบ `-B`; ไม่ rewrite สูตรจำลองใหม่

| ชุดตรวจ | ขอบเขต | ผล |
|---|---|---|
| Compatible-default parity | 1,728 inputs / 9,504 quantity breaks | ราคาขาย, landed แบบเต็มความละเอียด, profit ตรงกันทุก break ภายใน tolerance ที่ระบุ |
| Rounding boundary | 100 inputs / 550 breaks | ราคาขายต่าง 12 breaks; landed/profit ต่าง 210 breaks |
| Price Boss state/input probes | render/addToSheet จริงใน mock DOM | ยืนยัน stale quote, deadline ผิดขั้น และ negative extra cost ผ่าน validation |
| Price Boss API probes | 9 actual-handler scenarios, mock DB/access | ยืนยัน qty0, negative/missing price, missing break, excessive discount, decimal precision และ submit gate |
| Price Boss SPA probes | 3 actual-function scenarios | missing price, manual-price divergence, snapshot group collision |
| Price Boss SQL snapshot audit | parse 669/669 price rows | missing price 102; duplicate eligible offer+qty 19 keys, ราคาต่าง 5 keys |
| SmartGift unit tests | ล่าสุด pricing 10 + service 6 + inventory 4 | 20/20 ผ่าน; initial snapshot 9/9; config/invalid-input gaps ยังไม่ครอบคลุม |
| SmartGift diagnostic probes | actual methods + in-memory mocks | ยืนยันต้นทุนหล่น, config ไม่ใช้, invalid inputs, missing-cost และ shared state |

Parity base: RMB50, FX5, upc20, CBM.08/carton, inland2RMB/unit, extra costs0. Cross product:
profiles standard/corporate × warehouses2 × modes truck/sea/auto × months8/11 × goods2 × tiers4 × kg(null/12/40) × logo(none/silk/engrave, positions2/colors1).
Compared selling price exactly, landed tolerance 1e-7, profit tolerance .011. ไม่เทียบ margin display precision เพราะ JS แสดง1ตำแหน่ง vs Python2ตำแหน่ง

Boundary matrix: profiles2 × RMB(1,32,50,85,130) × CBM(.015,.025,.075,.085,.105,.125,.145,.155,.205,.225); gold/truck/general/month8/kg12/upc20/FX5/logo none

ตัวอย่าง baseline corporate (RMB50/upc20/CBM.08/kg12/gold/truck/general/FX5): 100/300/500/1000 ชุด → **470/450/440/430 บาทต่อชุด** เหมือนกันทั้งคู่

### ROUND-01 — parity แตกที่การปัดเศษ (P2)

- Symptom: input เดียวกันได้ราคาขายไม่เท่ากันที่ boundary
- Evidence: standard, RMB1, FX5, upc20, CBM.125, kg12, gold/truck/general, qty10 → Price Boss landed100.70 / sell610; SmartGift landed94.30 / sell600
- Root Cause: [pricing.html:650](O:/price-boss/pricing.html:650) ใช้ JS Math.round + epsilon; [pricing_calculator.py:170](O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py:170) ใช้ Python round. .125 CBM กลายเป็น .13 vs .12; freight832 vs768 บาทก่อนหารจำนวน
- Why escaped: ไม่มี shared decimal boundary oracle; smoke tests ไม่กดจุดกึ่งกลาง
- Proposed prevention: ให้เจ้าของอนุมัติวิธี round CBM, money, per-unit cost และ ceil10 แล้วใช้ golden fixtures ร่วมกัน ไม่เลือก Python/JS ว่าเป็น business truth โดยอัตโนมัติ
- ผล 9,504 breaks ที่ตรงกันจึงไม่รองรับคำว่า parity100% สำหรับ input ทุกแบบ

## 4. SmartGift RCA

### SG-01 — custom logo/extra cost ไม่เข้าใบราคา (P1 เดิม; RESOLVED ใน snapshot09:54)

**สถานะล่าสุด:** งานอื่นเพิ่ม custom_ucostในgenerate_quoteและส่งจากservice [บรรทัด70](O:/Org-EtohGroup/SmartGift/pipeline/auto_quote_service.py:70)/84/98แล้ว; ตรวจซ้ำได้single/quoted landed442.4เท่ากัน, selling600/profit15,760. รายการต่อไปนี้เก็บ RCAของsnapshotก่อนแก้ ไม่ใช่defectที่ยังเปิด

- Symptom: แสดงต้นทุนใหม่แต่ราคาขาย/กำไรยังคำนวณจากต้นทุนเก่า
- Evidence ล่าสุด: [service:60](O:/Org-EtohGroup/SmartGift/pipeline/auto_quote_service.py:60), [:73](O:/Org-EtohGroup/SmartGift/pipeline/auto_quote_service.py:73), [:96](O:/Org-EtohGroup/SmartGift/pipeline/auto_quote_service.py:96)
- Repro: product_code AUDIT, factory_cny50, qty100, CBM.05, kg10, upc50, member SILVER, custom_logo_thb100
- Actual: single landed442.40/unit แต่ corporate quote landed342.40, sell440, reported profit9,760; เมื่อใช้ต้นทุนที่ caller ส่งจริง profit **−240 บาท**
- Cross-check Price Boss input เดียวกันโดยใส่ extra unit cost100: landed442.40, corporate sell600, profit15,760; ตัวเลข600เป็นผลสูตรเดิมที่รวมต้นทุนครบ ไม่ใช่การรับรองราคา commercial ที่เจ้าของอนุมัติ
- Root Cause: custom_logo_thb ส่งเข้าเฉพาะ single_landed ไม่ส่งเข้า corporate/standard quote; generate_quote API ไม่มี custom unit cost parameter
- Why escaped: service test ตรวจ SUCCESS/keys/tier ไม่ตรวจ cost conservation
- Proposed prevention: cost context เดียวกันทุก call; quoted margin/floor ต้องใช้ต้นทุนครบชุด
- Related initial defect **แก้แล้วทั้ง calculator/service**: เดิม landed ไม่ส่ง rate/uv_rate จึงได้0; ตอนตรวจซ้ำ [calculator:234](O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py:234) และ serviceส่งค่าแล้ว มีregression tests. อย่านับจุดนี้เป็น defectที่ยังเปิด; custom_logo_thbเป็นอีกparameterซึ่งยังตกหล่น

### SG-02 — config เก็บไว้แต่ไม่ได้ใช้จริง (P1)

- Symptom: เปลี่ยนค่าใน schema ปัจจุบันแล้ว engine ยังใช้ค่าเดิม
- Evidence: YAML ใช้ `currency_exchange_rates` และ `shipping_rate_matrix`; [loader:120](O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py:120) รอ `currency_fx`, `shipping_rates`, `rates`, แล้ว break ที่129 แม้ยังไม่ได้ apply
- Repro: mock file read ใน memory เป็น schema ปัจจุบัน FX10 / GOLD9999; ได้ FX5 / GOLD6400 เหมือนเดิม
- Actual config consequence: cosmetic_fda GOLD truck 100ชุด/upc50/CBM.05/kg10 ได้ freight640; ระบุ legacy shipping YAML ตรง ๆ ได้750 ซึ่งตรง matrix7500/CBM
- Root Cause: schema mismatch + stop-on-parse แทน stop-on-valid-effective-config; [fallback:177](O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py:177) ให้ rate6400/16 แก่ค่าที่ไม่รู้จัก
- Why escaped: test ตรวจ tier ต่างกัน แต่ไม่ได้พิสูจน์ config changes มีผล หรือ unsupported category fail
- Proposed prevention: schema validation, effective config version/hash, reject unknown keys/categories และ no silent invented rate
- Related SG-02b P2: `self.rates = RATES` ที่94 แชร์ mutable state; custom config9999 ใน instance2 เปลี่ยน instance1 และ instance3 ด้วย. ใช้ isolation test ก่อนแก้

### SG-03 — invalid input ยัง SUCCESS (P1)

- Symptom: negative quotation พร้อมกำไรบวก
- Evidence: [auto_quote_service.py:25](O:/Org-EtohGroup/SmartGift/pipeline/auto_quote_service.py:25), [calculator:167](O:/Org-EtohGroup/SmartGift/src/cascade_engine/pricing_calculator.py:167)
- Repro: factory_cny−50, qty100 → SUCCESS, corporate landed−307.60, sell−270, total−27,000, gross profit3,760
- qty−10 ยัง SUCCESS; qty0 raw ZeroDivisionError; upc0 ถูกแทนด้วย1
- Root Cause: ไม่มี validation ก่อน pricing; minimum/coercion ถูกใช้แทนการ reject
- Why escaped: tests มีแต่ valid happy path
- Proposed prevention: finite/nonnegative costs, positive quantities/dimensions, valid enums; structured error และไม่สร้าง quote เมื่อ input ไม่ครบ

### SG-04 — missing cost กลายเป็น margin100% (P1/P2)

- Symptom: ไม่รู้ต้นทุนแต่แสดงเหมือนรู้กำไร
- Evidence: [inventory_cascade_engine.py:73](O:/Org-EtohGroup/SmartGift/src/cascade_engine/inventory_cascade_engine.py:73) default base_cost0; profit ที่152–164
- Repro: ลบ base_cost เฉพาะ object ใน memory แล้ว decompose PKG-SME-ELITE → cost0, sale46,250, profit46,250, margin100%; ไม่ได้แก้ catalog บนดิสก์
- Root Cause: ไม่มี unknown-cost state; missing ถูกแทนด้วย zero
- Why escaped: fixture มี base_cost จึงไม่ทดสอบ absence
- Proposed prevention: แยก known zero / unknown cost, block margin เมื่อ lineage/cost ไม่ครบ
- Current data distinction: master ปัจจุบันมี16 products ที่ base_costเป็นบวก ไม่ใช่ต้นทุนปัจจุบันทั้งหมดเป็น0; ทั้ง16คู่ code/cost ตรง hard-coded legacy seed literals ที่ [extract_catalog_dataset.py:87](O:/Org-EtohGroup/SmartGift/pipeline/legacy_prototypes/extract_catalog_dataset.py:87). จึงยังไม่พิสูจน์ actual landed COGS
- Catalog มี357 offers แต่107มี price tiers และไม่มี price_missing field ใน357 offers; bundle margin เป็น arithmetic against loaded costs ไม่ใช่ verified business profit

## 5. Price Boss RCA

### PB-01 — manual price กับตารางพิมพ์คนละราคา (P1)

- Symptom: ยอดสุทธิใช้ราคา80 แต่ใบราคาบันไดใช้100
- Evidence: [QuotationsPage.tsx:449](O:/price-boss/web/src/pages/QuotationsPage.tsx:449) เปลี่ยน unitPrice; [:160](O:/price-boss/web/src/pages/QuotationsPage.tsx:160) ยังคัดลอก breaks จาก tiers เดิม; [server:692](O:/price-boss/server/index.mjs:692) คำนวณจาก unitPrice; [print:557](O:/price-boss/web/src/pages/QuotationDetailPage.tsx:557) แสดง break price
- Repro: source100, แก้เป็น80, qty100 → main pre-VAT8,000 แต่ displayed tier100×100=10,000
- Root Cause: ราคา main line กับ ladder ไม่มี invariant ให้ selected break ตรงกัน
- Why escaped: ไม่มี cross-path test calculator/basket/API/print ใน package scripts ที่ตรวจ
- Proposed prevention: monetary snapshot เดียวกันหรือ explicit manual override/discount; ตรวจ selected tier กับ totals ก่อน persist/submit

### PB-02 — รวมคนละ price group / variant เป็น break เดียว (P1)

- Symptom: มีจำนวน10ซ้ำสองราคาใน item เดียว
- Evidence: [API:190](O:/price-boss/server/index.mjs:190) filter แค่ offer code; [SPA:164](O:/price-boss/web/src/pages/QuotationsPage.tsx:164) นำทุก tier เข้า breaks
- ข้อมูลจริง snapshot TSQ01-2: [SQL:1994](O:/price-boss/sql/smartgiftpricelist.postgres.sql:1994) P-02/10=1,180 และ [SQL:2085](O:/price-boss/sql/smartgiftpricelist.postgres.sql:2085) P-05/10=940; description ต่างกันด้วย
- Actual-function probe ได้ duplicate qty10 breaks1180/940
- Root Cause: identity/group ถูกตัดเหลือ offer code ก่อนเลือกราคา; customer price_list_group ไม่ได้กำกับ query
- DDL [migrate_crm_auth_quote.sql:227](O:/price-boss/sql/migrate_crm_auth_quote.sql:227) UNIQUE(item,qty) คาดว่าจะ reject save แต่รอบ audit ไม่รัน DB write เพื่อยืนยัน failure จริง
- Why escaped: ไม่มี fixture หลายกลุ่ม/variant ในเส้นทางเลือก→บันทึก
- Proposed prevention: owner ยืนยัน identity และ price authority แล้ว select ด้วย group/variant ที่ถูกต้อง; ห้าม dedupe ด้วย first-row เงียบ ๆ

### PB-03 — ใช้ quote เก่าหลัง input invalid (P1)

- Symptom: เปลี่ยน SKU แล้วล้างต้นทุนจน validation fail ยังเพิ่มใบราคาเก่าให้ SKU ใหม่ได้
- Evidence: [render:1303](O:/price-boss/pricing.html:1303) clear DOM/return แต่ไม่ invalidate lastQuote; [addToSheet:1366](O:/price-boss/pricing.html:1366) อ่าน SKU ปัจจุบันแต่ใช้ lastQuote.breaks
- Repro actual functions/mock DOM: valid AUDIT-VALID/RMB50 → เปลี่ยน AUDIT-INVALID/RMBว่าง → render + addToSheet ได้ SKUใหม่กับ breaks1000/900/850/800/770/750/730จาก inputเก่า
- Root Cause: cached quote ไม่ผูกกับ validated input snapshot
- Why escaped: ไม่มี transition test valid→invalid→add
- Proposed prevention: invalidate quote เมื่อ validation fail และ add ต้องตรวจ fingerprint/validation ของ input ชุดเดียวกัน

### PB-04 — deadline ตัดสินจาก500ชุดแล้วใช้ทั้ง ladder (P2)

- Symptom: คิดค่าขนส่งเรือให้1,000ชุดทั้งที่ deadline ไม่พอ
- Evidence: [renderLeadTime:1286](O:/price-boss/pricing.html:1286) qty hard-coded500; [render:1312](O:/price-boss/pricing.html:1312) apply mode ทั้ง quote
- Repro corporate/deadline44: แจ้งเรือ33–44วันสำหรับ500ชุด แล้ว quote1000ใช้sea แต่ leadTimeFor1000/sea ต้อง41–52วัน; same function at1000 เลือกtruckแทน
- Root Cause: lead-time quantity ไม่ตรงกับแต่ละ price break
- Why escaped: ไม่ทดสอบ deadline ที่ข้าม production threshold500
- Proposed prevention: resolve fulfillment mode ต่อ break; infeasible deadline ไม่ควรออก quote ที่เหมือนพร้อมส่งได้

### PB-05 — missing price / invalid quantity / submit gate (P1/P2)

- Symptom: ไม่มีราคาแล้วยังสร้างและส่งอนุมัติได้
- Evidence: [SPA:154](O:/price-boss/web/src/pages/QuotationsPage.tsx:154) missing→0; [server:692](O:/price-boss/server/index.mjs:692) qty0→1; [submit:848](O:/price-boss/server/index.mjs:848) ตรวจเฉพาะ state/owner ไม่มี item/break/total guards
- Actual-handler mocked-DB probes: qty0/price100 → grand107; negative price accepted; missing qty/break→201; submit→200แม้ไม่มี break; discount200กับsubtotal100ถูก clamp เป็น total0
- ขัด [workflow §2.4](O:/price-boss/docs/workflow-quotation.md) ที่ต้องมี≥1 item และ≥1 break/item
- Precision probe0.335×3ส่ง line_total1.0050000000000001 เข้า DECIMAL(...,2); ยังไม่พิสูจน์ MySQL round จริง
- Root Cause: input defaults/coercion และแยก transition จาก price readiness
- Why escaped: ไม่มี negative/missing/precision cases ที่เส้นทาง API/submit ใน checks ที่พบ
- Proposed prevention: validate typed monetary inputs, approved price readiness, discount bounds และ consistency ก่อน submit
- Related standalone: negative ucost−1000 ผ่าน validate(readForm()) และทำ landed100=−609.4 ใน probe; HTML min attributes ไม่แทน engine validation

### PB-06 — small-order assumption warning ไม่ทำงาน (P2)

- Symptom: factor1.5ถูกคิดจริง แต่ warning โรงงาน/สมมติฐานไม่แสดง
- Evidence: [return:719](O:/price-boss/pricing.html:719) ไม่คืน sof แต่ [warning:739](O:/price-boss/pricing.html:739) filter b.sof>1
- Root Cause: field ตกหล่นระหว่าง landed→break DTO
- Why escaped: ไม่ตรวจ output warning เทียบ SOF
- Proposed prevention: ส่ง factor/provenance ครบและ test warning; ข้อความที่กล่าวว่า small-order schedule เป็น assumption ต้องปรากฏเมื่อใช้จริง
- Related: [SHEET_NOTES:1402](O:/price-boss/pricing.html:1402) ระบุรวม full-color logo/กล่อง/ถุงคงที่ แม้เลือก none/UVไม่มีrate; ยังต้อง owner ยืนยัน inclusion policy ไม่ใช่รับรองว่า option ทุกแบบรวมจริง

## 6. ประเด็นที่ต้องเจ้าของตัดสิน ไม่ควรแก้สูตรเอง

1. China inland: Price Boss comment/form และ SmartGift runtimeใช้2RMB/ชุด; YAML SmartGiftใช้150RMB/CBMขั้นต่ำ50RMB/order. ตัวอย่าง100ชุด/5กล่อง×.08CBM/FX5: runtime10บาทต่อชุด vs YAML3บาทต่อชุด → ต่าง7บาทต่อชุด เป็น policy conflict ที่ยืนยันได้ ไม่ใช่พิสูจน์ว่า YAMLใหม่ถูกกว่า/ถูกต้องกว่า
2. CBM/currency rounding: half-up, half-even หรือ billable ceil ต้องมีสัญญาเดียวกัน
3. SOFตามqtyและfactorขั้น300/1000: Price Bossระบุว่าเป็น assumption/estimate; ต้องยืนยันกับเจ้าของ/ต้นทางก่อนใช้เป็น published price
4. Price authority: แยก factory quote, actual landed cost, approved commercial price, FlowAccount snapshot และ imported offer identity; SQLเก็บราคาขายไม่ได้พิสูจน์ COGS
5. Package floor20,000/target30,000ใน SmartGift YAML ไม่เท่ากับ core floor5,000/3,000; ยังไม่ควรเปลี่ยนโดยตีความเอง
6. Freight ratesที่ตรวจเป็น local snapshot; ไม่ได้ตรวจเรทขนส่งหรือFXปัจจุบันจากผู้ให้บริการ

## 7. ข้อเสนอแก้เป็นลำดับ (ยังไม่ implement)

- ก่อนใช้เสนอราคาอัตโนมัติ: SG-03, PB-01/PB-02/PB-03/PB-05; SG-01แก้แล้วโดยงานอื่นและมีผลตรวจซ้ำ
- จากนั้นกำหนด monetary/config contract ร่วม: SG-02, ROUND-01 และ policy decisions
- รักษา unknown-cost/provenance gate: SG-04
- เพิ่ม golden tests ที่ผ่านทั้ง calculator→caller→persist/print และ tests ของ warning/deadline
- ไม่จำเป็นต้อง rewrite ทั้งระบบหรือย้าย framework เพื่อแก้ defect เหล่านี้

## 8. ขอบเขตการพิสูจน์

- ราคากับ profit ที่ยกมาเป็นผล deterministic local code/probe ไม่ใช่คำแนะนำทางบัญชี ภาษี หรือรับรองกำไรธุรกิจ
- ไม่ได้เปิดbrowser/พิมพ์จริง; DOM/React probesเป็น in-memory function execution
- ไม่สร้างใบราคาใน DB จริง; SQL constraint failure ยังเป็น inference ที่ระบุไว้
- ไม่รัน full SmartGift discovery เพราะ archiver/E2Eบางชุดเขียน registry/archiveจริง; selected testsล่าสุด20ชุดใช้เฉพาะ memory
- ไม่ตรวจ external FlowAccount export หรือ live deployment; declared authority ไม่เท่ากับ verified lineage
- Tests ผ่านที่กล่าวถึงไม่ได้รวม production/UAT และไม่ได้รับรองไม่มี bugอื่น

## 9. Source fingerprints (SHA-256)

| File | SHA-256 |
|---|---|
| Price Boss pricing.html | FF24C373A8520405A9D4958AE03D34875B274C319C7FE4C41AD022B195979BBA |
| Price Boss server/index.mjs | F8E29DA17F15AA15721BDB16C57B6BB03C82DD67EC6C8B4967CB87B8F28D7CF9 |
| Price Boss QuotationsPage.tsx | 68F43897FDAE39E9F663B3E79AB478FD5E7A52B61EBD00233C02B8D54D9A0604 |
| Price Boss smartgiftpricelist.postgres.sql | E003439A2D3C54ADF6BEA106E6081639B44ECC32270F8A4D9F76230148088ED3 |
| SmartGift pricing_calculator.py (initial snapshot) | EF0DBC9A71F1AE439AF6D6BAC1AC6C7EF934CC54BBC859A41F4878C682274E25 |
| SmartGift pricing_calculator.py (09:50 refresh) | 778F45ED14FE75DC5BAD842CE63B759EB05B5E78A144CB514DD473BDA7922C9B |
| SmartGift pricing_calculator.py (09:54 refresh) | 86030E388753E0047EC05E660CAC6717BFDD9C149DAA401160A3E4F267654717 |
| SmartGift auto_quote_service.py (initial snapshot) | CACA1B2C848E8B37BE788C9A228EA9F5BA3B22D03B55A1EAE9DE1A03B69520FF |
| SmartGift auto_quote_service.py (09:51 refresh) | 8A8F68B70D8B457A3395F973F57B63E312F58F1D39843B6EFC1D83F3D57FB31A |
| SmartGift auto_quote_service.py (09:54 refresh) | 19D567B5536A00029CF07395205D2E44AA5E6438077BDDFCFA548E0696834076 |
| SmartGift smartgift_catalog_master.json (09:51 refresh) | 35DB6255E4D5CDA04557F7DCE06E55BC9030377DCFDC6BC4F95AB0316F2605D7 |
| SmartGift pricing_rules_formula.yaml | F4473230F10B59133936974A0CACF84BBE84865D61DB76553D8CC2A58BA635FC |

## Version diff

ไม่มีรายงาน → 0.1.0b → 0.1.3b: เพิ่มผลเปรียบเทียบ, RCA และตรวจซ้ำหลังพบงานอื่นแก้ SmartGift calculator/service รวมcustom cost; **งาน audit นี้ไม่ได้แก้ engine/code/config ของทั้งคู่**

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.3b | 2026-08-30 | need review | Custom cost resolved externally; refresh20tests and verdict without stale defect ranking | uncommitted | ATHER + audit agents |
| 0.1.2b | 2026-08-30 | need review | Refresh service logo fixes and 18 passing tests; custom cost defect remains | uncommitted | ATHER + audit agents |
| 0.1.1b | 2026-08-30 | need review | Refresh live SmartGift changes; direct-logo fixes separated from remaining service/config defects | uncommitted | ATHER + audit agents |
| 0.1.0b | 2026-08-30 | need review | Read-only comparative pricing RCA, parity and counterexamples | uncommitted | ATHER + audit agents |
