const router = require("express").Router();

router.post("/", (req, res) => {
  res.json({ reply: "Eat balanced meals and drink water" });
});

module.exports = router;