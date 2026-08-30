const { serveCustomerSafe } = require("./_public_data");

module.exports = function catalog(req, res) {
  serveCustomerSafe(req, res);
};
