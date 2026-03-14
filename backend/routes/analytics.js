const router = require("express").Router();

let meals = [];

router.get("/:userId", (req, res) => {
  const userMeals = meals.filter(m => m.userId == req.params.userId);
  res.json(userMeals);
});

module.exports = router;