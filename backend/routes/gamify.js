const router = require("express").Router();

router.get("/:userId", (req, res) => {
  res.json({ points: 100, badge: "Gold" });
});

module.exports = router;