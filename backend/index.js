const express = require("express");
const app = express();
const cors = require("cors");

let queryValue;

// CORS policy to allow frontend calls backend API
app.use(
  cors({
    origin: "http://localhost:5173",
  })
);
// make sure the req.body of the post method would not be undefined
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Hello from the main page!");
});

app.get("/ir", (req, res) => {
  let spawn = require("child_process").spawn;

  let stdout = '';
  let data = '';
  let process = spawn(
    "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3",
    ["Assignment4.py", req.query.inputQuery]
  );
  process.stderr.on("data", data => {
    console.log("stderr ---->:", data.toString());
  });
  process.stdout.on("data", data => {
    stdout += data.toString()
  });
  process.stdout.on('end',(data) => {
    res.send(stdout)
});
  // process.stdout.on('end', data => {
  //   try{
  //     let artifact_array = JSON.parse(stdout);
  //     log.debug(artifact_array);
  //     if (!artifact_array) {
  //       res.status(200).send({status: 'success', message: artifact_array})
  //     } else {
  //       res.status(400).send({ status: 'error', message: 'In else :: somthing went wrong' })
  //     }
  //   }catch(error){
  //     res.status(400).send({ status: 'error', message: 'somthing went wrong' });
  //   }
  // })
});

app.post("/query", (req, res) => {
  queryValue = req.body.body;
  res.redirect(`/ir?inputQuery=${queryValue}`);
});

const PORT = process.env.PORT || 8080;

app.listen(PORT, console.log(`Server started on PORT ${PORT}`));
