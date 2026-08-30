const { serveCustomerSafeMedia } = require("./_public_data");

module.exports = function media(req, res) {
  serveCustomerSafeMedia(req, res);
};
