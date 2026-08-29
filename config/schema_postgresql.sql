-- ============================================================================
-- SmartGift B2B E-commerce & Inventory Architecture
-- Supabase PostgreSQL DDL, pgvector Extension & Inventory Cascade Functions
-- ============================================================================

-- 0. Enable pgvector & pgcrypto Extensions (Supabase Vector Search & Vault UUID Support)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;



-- 1. Categories (หมวดหมู่สินค้าหลัก 4 หมวดหลัก ตาม SmartGift 2026 Portfolio Blueprint)
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    name_th VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    vibe VARCHAR(255),
    target_recipient VARCHAR(255),
    guardrail TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed Data: Top Level 4 Main Categories
INSERT INTO categories (name_th, name_en, slug, vibe, target_recipient, guardrail, description) VALUES
('ชุดธีมสีพาสเทล (Pastel Series)', 'Pastel Series (Soft & Friendly)', 'pastel-series', 'อ่อนหวาน ละมุน เป็นมิตร', 'กลุ่มวัยรุ่น, แคมเปญเข้าถึงง่าย', 'คุมโทนสีให้เป็นเฉดเดียวกันทั้งกล่อง', 'การคุมโทนเฉดสีอ่อนหวาน ละมุน และเป็นมิตร (ฟ้าพาสเทล, ส้มสว่าง, ชมพู)'),
('ชุดศิลปะร่วมสมัยและตะวันออก (Classic Oriental)', 'Classic Oriental (Mindfulness & Craft)', 'classic-oriental', 'ประณีต ทรงคุณค่า คลาสสิก', 'ผู้ใหญ่, แขก VIP ต่างชาติ', 'ตรวจเช็คความหมายมงคลของลวดลาย', 'ผสมผสานความร่วมสมัยสไตล์จีนคลาสสิก (Classical Chinese Craft) ประณีต ทรงคุณค่า และมีเอกลักษณ์'),
('ชุด Novelty & Self-Care', 'Novelty & Self-Care (Warm & Wellness)', 'novelty-self-care', 'ผ่อนคลาย อบอุ่น ใส่ใจ', 'กลุ่มผู้หญิง, พนักงานสาย Wellness', 'ห้ามเคลมสรรพคุณ Medical โดยไม่มีหลักฐาน', 'ชุดของขวัญที่เน้นความรู้สึกผ่อนคลาย อบอุ่น เหมาะสำหรับแคมเปญสาย Wellness ของกลุ่มผู้หญิงหรือพนักงาน'),
('ชุดนวัตกรรมทางการทำงานอัจฉริยะ (Executive Smart Tech)', 'Executive Smart Tech (Modern & Work)', 'executive-smart-tech', 'ทันสมัย นวัตกรรม เป็นมืออาชีพ', 'ผู้บริหาร, กลุ่มนักธุรกิจยุคใหม่', 'ตรวจสเปกแบตเตอรี่และการรับรองความปลอดภัย', 'เซ็ตไอทีพรีเมียมที่เน้นความทันสมัย ตอบสนองไลฟ์สไตล์การทำงานยุคใหม่ของระดับบริหาร')
ON CONFLICT (slug) DO UPDATE SET 
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    vibe = EXCLUDED.vibe,
    target_recipient = EXCLUDED.target_recipient,
    guardrail = EXCLUDED.guardrail,
    description = EXCLUDED.description;


-- 2. ProductMasters (สินค้าจริงหลักทางกายภาพ)
CREATE TABLE IF NOT EXISTS product_masters (
    product_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    name_th VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    model_code VARCHAR(50) UNIQUE,
    description TEXT,
    unboxing_experience TEXT, -- รายละเอียด Sensory / Unboxing เช่น เสียงเปิดแม่เหล็ก กลิ่นหอม
    specs JSONB DEFAULT '{}'::jsonb, -- ข้อมูลสเปกกลางแบบ Flexible JSONB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Attributes (ประเภทคุณสมบัติ เช่น สี, ความจุ, วัสดุ)
CREATE TABLE IF NOT EXISTS attributes (
    attribute_id SERIAL PRIMARY KEY,
    name_th VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL
);

-- 4. ProductVariants (สต็อกชิ้นส่วนจริงรายชิ้น - Granular Stock Level)
CREATE TABLE IF NOT EXISTS product_variants (
    variant_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES product_masters(product_id) ON DELETE CASCADE,
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    inventory_qty INT NOT NULL DEFAULT 0 CHECK (inventory_qty >= 0),
    safety_stock INT NOT NULL DEFAULT 10,
    cost_price NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    extra_features JSONB DEFAULT '{}'::jsonb, -- รายละเอียดเฉพาะชิ้น
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. VariantValues (ตารางสะพานจับคู่คุณสมบัติย่อย)
CREATE TABLE IF NOT EXISTS variant_values (
    variant_id INT NOT NULL REFERENCES product_variants(variant_id) ON DELETE CASCADE,
    attribute_id INT NOT NULL REFERENCES attributes(attribute_id) ON DELETE RESTRICT,
    attribute_value VARCHAR(255) NOT NULL,
    PRIMARY KEY (variant_id, attribute_id)
);

-- 6. CatalogOffers (รายการเสนอขาย / เซ็ตของขวัญสำเร็จรูป)
CREATE TYPE gift_tier_enum AS ENUM ('Reach', 'Select', 'Signature', 'Bespoke');

CREATE TABLE IF NOT EXISTS catalog_offers (
    offer_id SERIAL PRIMARY KEY,
    offer_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    gift_tier gift_tier_enum NOT NULL,
    is_set BOOLEAN NOT NULL DEFAULT FALSE,
    variant_id INT REFERENCES product_variants(variant_id) ON DELETE SET NULL, -- สำหรับสินค้าเดี่ยว (is_set = FALSE)
    base_description TEXT,
    packaging_details JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. SetComponents (โครงสร้างส่วนประกอบของเซ็ต - Set Decomposition)
CREATE TABLE IF NOT EXISTS set_components (
    set_offer_id INT NOT NULL REFERENCES catalog_offers(offer_id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES product_variants(variant_id) ON DELETE RESTRICT,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    PRIMARY KEY (set_offer_id, variant_id)
);

-- 8. BundleOffers (แพ็กเกจขายองค์กรเหมาแคมเปญ - Meta-Bundle)
CREATE TABLE IF NOT EXISTS bundle_offers (
    bundle_id SERIAL PRIMARY KEY,
    bundle_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    total_price NUMERIC(12, 2) NOT NULL,
    target_recipients_count INT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. BundleComponents (ส่วนประกอบระดับเซ็ตในแพ็กเกจองค์กร)
CREATE TABLE IF NOT EXISTS bundle_components (
    bundle_id INT NOT NULL REFERENCES bundle_offers(bundle_id) ON DELETE CASCADE,
    offer_id INT NOT NULL REFERENCES catalog_offers(offer_id) ON DELETE RESTRICT,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    PRIMARY KEY (bundle_id, offer_id)
);

-- 10. PriceTiers (ขั้นบันไดราคาส่งตาม MOQ)
CREATE TABLE IF NOT EXISTS price_tiers (
    price_id SERIAL PRIMARY KEY,
    offer_id INT NOT NULL REFERENCES catalog_offers(offer_id) ON DELETE CASCADE,
    min_qty INT NOT NULL CHECK (min_qty > 0),
    max_qty INT CHECK (max_qty IS NULL OR max_qty >= min_qty),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    CONSTRAINT unique_offer_tier UNIQUE (offer_id, min_qty)
);

-- 11. Orders & OrderItems (บันทึกคำสั่งซื้อ)
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(100) UNIQUE NOT NULL,
    corporate_client_name VARCHAR(255) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    delivery_plan JSONB DEFAULT '[]'::jsonb, -- แผนกระจายจุดจัดส่งตามกลุ่มผู้รับ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    bundle_id INT REFERENCES bundle_offers(bundle_id) ON DELETE RESTRICT,
    offer_id INT REFERENCES catalog_offers(offer_id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    total_price NUMERIC(12, 2) NOT NULL
);

-- ============================================================================
-- INDEXES FOR MAXIMUM QUERY PERFORMANCE
-- ============================================================================
CREATE INDEX idx_pv_product ON product_variants(product_id);
CREATE INDEX idx_pv_sku ON product_variants(sku_code);
CREATE INDEX idx_co_tier ON catalog_offers(gift_tier);
CREATE INDEX idx_co_is_set ON catalog_offers(is_set);
CREATE INDEX idx_sc_set ON set_components(set_offer_id);
CREATE INDEX idx_bc_bundle ON bundle_components(bundle_id);
CREATE INDEX idx_pt_offer ON price_tiers(offer_id);
CREATE INDEX idx_pm_specs ON product_masters USING gin (specs);

-- ============================================================================
-- STORED PROCEDURES & INVENTORY CASCADE WATERFALL LOGIC
-- ============================================================================

-- Function: ตัดสต็อกระดับเซ็ต (Decompose Set to SKU Inventory)
CREATE OR REPLACE FUNCTION deduct_set_inventory(
    p_offer_id INT,
    p_order_qty INT
) RETURNS VOID AS $$
DECLARE
    v_is_set BOOLEAN;
    v_single_variant_id INT;
    v_comp RECORD;
BEGIN
    SELECT is_set, variant_id INTO v_is_set, v_single_variant_id
    FROM catalog_offers
    WHERE offer_id = p_offer_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Offer ID % not found.', p_offer_id;
    END IF;

    IF v_is_set THEN
        -- แตกตัวประกอบเซ็ตแล้วตัดสต็อกทีละชิ้น
        FOR v_comp IN
            SELECT variant_id, quantity
            FROM set_components
            WHERE set_offer_id = p_offer_id
        LOOP
            UPDATE product_variants
            SET inventory_qty = inventory_qty - (v_comp.quantity * p_order_qty)
            WHERE variant_id = v_comp.variant_id;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Variant ID % not found during set decomposition.', v_comp.variant_id;
            END IF;
        END LOOP;
    ELSE
        -- สินค้าเดี่ยว ตัดตรงเข้า Variant
        UPDATE product_variants
        SET inventory_qty = inventory_qty - p_order_qty
        WHERE variant_id = v_single_variant_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function: ตัดสต็อกระดับ Meta-Bundle (Cascade Bundle -> Sets -> SKUs)
CREATE OR REPLACE FUNCTION deduct_bundle_inventory(
    p_bundle_id INT,
    p_bundle_order_qty INT
) RETURNS VOID AS $$
DECLARE
    v_item RECORD;
BEGIN
    FOR v_item IN
        SELECT offer_id, quantity
        FROM bundle_components
        WHERE bundle_id = p_bundle_id
    LOOP
        -- เรียกใช้ฟังก์ชันย่อยตัดสต็อกเซ็ตตามจำนวนที่กำหนดในแพ็กเกจ
        PERFORM deduct_set_inventory(v_item.offer_id, v_item.quantity * p_bundle_order_qty);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
