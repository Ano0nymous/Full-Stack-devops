const express = require("express");
const app = express();
const PORT = process.env.PORT || 8080;
const ENV = process.env.APP_MESSAGE || "No env set";
const DB_PASSWORD = process.env.DB_PASSWORD || "No DB password set";
const HOSTNAME = process.env.HOSTNAME || require('os').hostname();

app.get("/pt", (req, res) => {
  res.json({
    message: "Hello from Simple App (Node)",
    env: ENV, 
    container: HOSTNAME,
    dbPassword: DB_PASSWORD
    
  });
});

app.listen(PORT, () => console.log(`Node Hello listening on ${PORT}`));
