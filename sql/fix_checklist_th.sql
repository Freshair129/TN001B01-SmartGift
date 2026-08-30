USE price_db;
SET NAMES utf8mb4;

UPDATE china_request_checklist SET ask_th = 'ราคา 100 / 500 / 1,000 / 3,000 ชิ้น', group_label = 'Unit Price' WHERE group_code = 'unit_price';
UPDATE china_request_checklist SET ask_th = 'ขั้นต่ำต่อรุ่น ต่อสี และต่อโลโก้', group_label = 'MOQ' WHERE group_code = 'moq';
UPDATE china_request_checklist SET ask_th = 'ราคาตัวอย่างและค่าขนส่ง', group_label = 'Sample' WHERE group_code = 'sample';
UPDATE china_request_checklist SET ask_th = 'Silk Screen, UV Print, Laser หรือ Full Color', group_label = 'OEM Logo' WHERE group_code = 'oem_logo';
UPDATE china_request_checklist SET ask_th = 'MOQ และค่าทำสี Pantone', group_label = 'Custom Color' WHERE group_code = 'custom_color';
UPDATE china_request_checklist SET ask_th = 'กล่องธรรมดา กล่องพรีเมียม คู่มือ และอุปกรณ์ในกล่อง', group_label = 'Packaging' WHERE group_code = 'packaging';
UPDATE china_request_checklist SET ask_th = 'ระยะเวลาผลิตหลังอนุมัติตัวอย่าง', group_label = 'Production Lead Time' WHERE group_code = 'lead_time';
UPDATE china_request_checklist SET ask_th = 'จำนวนต่อกล่อง, ขนาดกล่อง, NW, GW และ CBM', group_label = 'Carton Data' WHERE group_code = 'carton';
UPDATE china_request_checklist SET ask_th = 'ผู้ผลิตเซลล์ รุ่นเซลล์ ความจุจริง และ Cycle Life', group_label = 'Battery Data' WHERE group_code = 'battery';
UPDATE china_request_checklist SET ask_th = 'เอกสารทดสอบแบตเตอรี่ ความปลอดภัย และการขนส่ง', group_label = 'Test Documents' WHERE group_code = 'test_docs';
UPDATE china_request_checklist SET ask_th = 'ระยะรับประกันและเงื่อนไขสินค้ามีปัญหา', group_label = 'Warranty' WHERE group_code = 'warranty';
UPDATE china_request_checklist SET ask_th = 'EXW, FOB หรือ DDP Bangkok', group_label = 'Trade Term' WHERE group_code = 'trade';
UPDATE china_request_checklist SET ask_th = 'เงินมัดจำและยอดชำระก่อนส่งสินค้า', group_label = 'Payment' WHERE group_code = 'payment';

SELECT group_code, group_label, ask_th FROM china_request_checklist ORDER BY sort_order;