const router = require("express").Router();

let users = [];

router.post("/register", (req, res) => {
  const user = { id: users.length + 1, ...req.body };
  users.push(user);
  res.json(user);
});

router.post("/login", (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  res.json(user);
});

module.exports = router;