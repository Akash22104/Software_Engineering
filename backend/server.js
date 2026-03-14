const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// Routes
app.use("/api/auth", require("./routes/auth"));
app.use("/api/meals", require("./routes/meals"));
app.use("/api/recommend", require("./routes/recommendation"));
app.use("/api/analytics", require("./routes/analytics"));
app.use("/api/image", require("./routes/image"));
app.use("/api/coach", require("./routes/coach"));
app.use("/api/health", require("./routes/health"));
app.use("/api/gamify", require("./routes/gamify"));

app.listen(5000, () => console.log("Server running on 5000"));