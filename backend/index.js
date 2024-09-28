const express = require("express");
const dotenv = require("dotenv").config();
const cors = require("cors");
const connectionToDB = require("./DB/dbconnection");
const router = require("./routes/userRoutes");
const cookieParser = require("cookie-parser");

const corsOptions = {
  origin: "http://localhost:5173", // Replace with your frontend domain
  methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
  credentials: true, // Allow cookies to be sent
  optionsSuccessStatus: 204
};
const app = express();
app.use(cors(corsOptions));
app.use(express.json());
app.use(cookieParser(process.env.COOKIE_NAME));
app.use(router);


try {
  connectionToDB();

  app.listen(process.env.PORT, () => {
    console.log(`Server is running on port ${process.env.PORT}`);
  });
} catch (error) {
  console.log("Error connecting to the database");
}