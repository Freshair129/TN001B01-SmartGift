const { customerSafeMaster } = require("./_public_data");

module.exports = function health(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    res.status(405).json({ error: "method_not_allowed" });
    return;
  }
  const master = customerSafeMaster();
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.status(200).json({
    status: "ok",
    data_classification: "customer-safe",
    schema_version: master.metadata.schema_version,
    counts: master.metadata.counts,
  });
};
