const router = require("express").Router();

router.post("/", (req, res) => {
  if (req.body.condition === "diabetes")
    res.json({ diet: "Low Sugar Diet" });
  else
    res.json({ diet: "Normal Diet" });
});

module.exports = router;