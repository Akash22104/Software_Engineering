const router = require("express").Router();

let meals = [];

router.post("/add", (req, res) => {
  meals.push(req.body);
  res.json({ message: "Meal added" });
});

router.get("/:userId", (req, res) => {
  const userMeals = meals.filter(m => m.userId == req.params.userId);
  res.json(userMeals);
});

module.exports = router;