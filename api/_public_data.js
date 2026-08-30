const publicMaster = require("../public/data/pricelist_public.json");

function customerSafeMaster() {
  return {
    ...publicMaster,
    canonical_products: publicMaster.product_masters,
    top_level_categories: publicMaster.portfolio_catalogs,
    corporate_bundles: [],
  };
}

function serveCustomerSafe(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    res.status(405).json({ error: "method_not_allowed" });
    return;
  }
  res.setHeader("Cache-Control", "public, max-age=300, s-maxage=300, stale-while-revalidate=86400");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-SmartGift-Data-Classification", "customer-safe");
  res.status(200).json(customerSafeMaster());
}

module.exports = { customerSafeMaster, serveCustomerSafe };
