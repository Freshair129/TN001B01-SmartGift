import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

const BINDING_PATH = process.env.GENESIS_BINDING_PATH || '@freshair129/gks-genesis-block-native';
const DB_PATH = process.env.GENESIS_DB_PATH || './vaults/vlt-catalog-product/genesis-db';
const CATALOG_PATH = process.env.CATALOG_PATH || './data-pipeline/02_prepared/smartgift_catalog_master.json';
const OLLAMA_EMBED_URL = 'http://localhost:11434/api/embeddings';

async function getEmbedding(text) {
  try {
    const res = await fetch(OLLAMA_EMBED_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'bge-m3:latest',
        prompt: text
      })
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.embedding || null;
  } catch (err) {
    return null;
  }
}

async function main() {
  console.log('=== Step 1: Loading GenesisBlockDB Native Addon ===');
  const binding = require(BINDING_PATH);
  const { GenesisDatabase } = binding;

  console.log('=== Step 2: Opening GenesisDatabase Instance ===');
  const db = GenesisDatabase.open({
    path: DB_PATH,
    vectorDim: 1024
  });
  console.log(`Database opened at '${DB_PATH}' with vectorDim: 1024`);

  console.log('=== Step 3: Loading Catalog Master Dataset ===');
  const rawCatalog = fs.readFileSync(CATALOG_PATH, 'utf-8');
  const catalog = JSON.parse(rawCatalog);

  console.log('=== Step 4: Seeding Categories, Tiers & Segments ===');
  // Top-Level 4 Main Categories (Interest Themes 2026 Blueprint)
  const categories = [
    { id: 'cat:pastel-series', name: 'Pastel Series (Soft & Friendly)', name_th: 'ชุดธีมสีพาสเทล', slug: 'pastel-series', vibe: 'Soft & Friendly' },
    { id: 'cat:classic-oriental', name: 'Classic Oriental (Mindfulness & Craft)', name_th: 'ชุดศิลปะร่วมสมัยและตะวันออก', slug: 'classic-oriental', vibe: 'Mindfulness & Craft' },
    { id: 'cat:novelty-self-care', name: 'Novelty & Self-Care (Warm & Wellness)', name_th: 'ชุด Novelty & Self-Care', slug: 'novelty-self-care', vibe: 'Warm & Wellness' },
    { id: 'cat:executive-smart-tech', name: 'Executive Smart Tech (Modern & Work)', name_th: 'ชุดนวัตกรรมทางการทำงานอัจฉริยะ', slug: 'executive-smart-tech', vibe: 'Modern & Work' }
  ];
  for (const c of categories) {
    await db.addNode({
      id: c.id,
      labels: ['Category'],
      props: { name: c.name, name_th: c.name_th, slug: c.slug, vibe: c.vibe }
    });
  }

  // Gift Tiers
  const tiers = [
    { id: 'tier:Reach', name: 'Reach', budget_tier: 'Mass/Team' },
    { id: 'tier:Select', name: 'Select', budget_tier: 'Standard' },
    { id: 'tier:Signature', name: 'Signature', budget_tier: 'Premium/Executive' },
    { id: 'tier:Bespoke', name: 'Bespoke', budget_tier: 'Ultra-VIP/Board' }
  ];
  for (const t of tiers) {
    await db.addNode({
      id: t.id,
      labels: ['GiftTier'],
      props: { name: t.name, budget_tier: t.budget_tier }
    });
  }

  // Recipient Segments
  const segments = [
    { id: 'seg:VIP', name: 'VIP & Board of Directors', tier: 'tier:Bespoke' },
    { id: 'seg:Executive', name: 'Executives & Managers', tier: 'tier:Signature' },
    { id: 'seg:Staff', name: 'General Staff & Event Attendees', tier: 'tier:Reach' }
  ];
  for (const s of segments) {
    await db.addNode({
      id: s.id,
      labels: ['RecipientSegment'],
      props: { name: s.name }
    });
    await db.addEdge({
      from: s.id,
      to: s.tier,
      rel: 'RECOMMENDED_TIER'
    });
  }

  console.log('=== Step 5: Seeding Canonical Product Masters ===');
  for (const p of catalog.canonical_products) {
    const pId = `pm:${p.code}`;
    await db.addNode({
      id: pId,
      labels: ['ProductMaster'],
      props: {
        code: p.code,
        name_th: p.name_th,
        name_en: p.name_en,
        category: p.category,
        base_cost: p.base_cost
      }
    });

    // Link product to top-level category
    let catSlug = p.category_slug || 'executive-smart-tech';
    if (!p.category_slug) {
      if (p.category.includes('Pastel')) catSlug = 'pastel-series';
      else if (p.category.includes('Oriental')) catSlug = 'classic-oriental';
      else if (p.category.includes('Self-Care') || p.category.includes('Wellness')) catSlug = 'novelty-self-care';
      else catSlug = 'executive-smart-tech';
    }
    const catId = `cat:${catSlug}`;

    await db.addEdge({
      from: pId,
      to: catId,
      rel: 'IN_CATEGORY'
    });
  }

  console.log(`=== Step 6: Seeding Catalog Offers (Sample & High-Value Sets) with Vector Embeddings ===`);
  const sampleOffers = catalog.catalog_offers.slice(0, 50); // Seed 50 curated offers
  let embeddedCount = 0;

  for (const offer of sampleOffers) {
    const offerId = `offer:${offer.offer_code}`;
    const sensoryText = `${offer.name}. ${offer.unboxing_experience}. ${offer.gift_tier} Tier.`;

    // Fetch bge-m3 embedding for semantic/sensory search
    let embedding = null;
    if (embeddedCount < 15) { // Embed first 15 for fast startup
      embedding = await getEmbedding(sensoryText);
      if (embedding) embeddedCount++;
    }

    const nodeInput = {
      id: offerId,
      labels: ['CatalogOffer', `${offer.gift_tier}Tier`],
      props: {
        code: offer.offer_code,
        name: offer.name,
        gift_tier: offer.gift_tier,
        unboxing: offer.unboxing_experience,
        price_tiers: JSON.stringify(offer.price_tiers)
      }
    };
    if (embedding && embedding.length === 1024) {
      nodeInput.embedding = embedding;
    }

    await db.addNode(nodeInput);

    // Link offer to tier
    await db.addEdge({
      from: offerId,
      to: `tier:${offer.gift_tier}`,
      rel: 'BELONGS_TO_TIER'
    });

    // Link offer components to canonical products
    for (const comp of offer.components) {
      await db.addEdge({
        from: offerId,
        to: `pm:${comp.product_code}`,
        rel: 'CONTAINS',
        props: { qty: comp.qty || 1 }
      });
    }
  }
  console.log(`Seeded ${sampleOffers.length} Catalog Offers (${embeddedCount} with 1024-dim Vector Embeddings).`);

  console.log('=== Step 7: Seeding Corporate Bundles ===');
  for (const bundle of catalog.corporate_bundles) {
    const bId = `bundle:${bundle.bundle_code}`;
    await db.addNode({
      id: bId,
      labels: ['BundleOffer', 'CorporateMetaBundle'],
      props: {
        code: bundle.bundle_code,
        name: bundle.name,
        target_recipients: bundle.target_recipients,
        total_price: bundle.total_price,
        description: bundle.description,
        tier_breakdown: JSON.stringify(bundle.tier_breakdown)
      }
    });

    for (const inc of bundle.included_offers) {
      await db.addEdge({
        from: bId,
        to: `offer:${inc.offer_code}`,
        rel: 'INCLUDES_OFFER',
        props: { qty: inc.qty }
      });
    }
  }

  console.log('=== Step 8: Flushing HNSW Index & Saving State ===');
  await db.flushIndex();
  await db.saveState();
  console.log('GenesisBlockDB state snapshot persisted successfully!');

  console.log('\n=== Step 9: Running Test Traversal & Context Queries ===');
  const sampleOffer = sampleOffers[0].offer_code;
  const context = await db.executeHql(`TRAVERSE FROM "offer:${sampleOffer}" DEPTH 1 REL ANY`);
  console.log(`HQL Traverse result for offer:${sampleOffer}:`, JSON.stringify(context, null, 2));

  console.log('\nGenesisBlockDB Seeding Completed Successfully!');
}

main().catch(err => {
  console.error('Seeding failed:', err);
  process.exit(1);
});
