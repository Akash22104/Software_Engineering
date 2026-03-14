const router = require("express").Router();

router.post("/detect", (req, res) => {
  res.json({ food: "Apple", calories: 95 });
});

module.exports = router;