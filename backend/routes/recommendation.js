const router = require("express").Router();

let meals = require("./meals"); // just logic reference

router.get("/:userId", (req, res) => {
  const allMeals = global.meals || [];
  const userMeals = allMeals.filter(m => m.userId == req.params.userId);

  const total = userMeals.reduce((s, m) => s + Number(m.calories), 0);

  const rec = total < 1800 ? "High Protein Meal" : "Light Meal";

  res.json({ total, rec });
});

module.exports = router;