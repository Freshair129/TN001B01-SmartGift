const { serveCustomerSafe } = require("./_public_data");

module.exports = function pricelist(req, res) {
  serveCustomerSafe(req, res);
};
