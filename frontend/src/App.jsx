import axios from "axios";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import SearchIcon from "@mui/icons-material/Search";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { useState } from "react";

import "./App.scss";

const App = () => {
  const baseURL = "http://localhost:8080";

  const [language, setLanguage] = useState("EN");
  const [query, setQuery] = useState("");

  const handleChange = (event, newLanguage) => {
    setLanguage(newLanguage);
  };

  const handleQuery = event => {
    setQuery(event.target.value);
  };

  const submitQuery = async () => {
    try {
      await axios
        .post(`${baseURL}/query`, {
          title: "Hello World",
          body: `{"query": "${query}", "type": "${language}"}`,
        })
        .then(response => {
          console.log("user query: ----->", response.data);
        });
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className='search-bar-container'>
      <Paper
        component='form'
        sx={{
          p: "2px 4px",
          display: "flex",
          alignItems: "center",
          width: 700,
          margin: "0 auto",
        }}>
        <InputBase
          sx={{ ml: 1, flex: 1 }}
          placeholder='Input French/English Query'
          inputProps={{ "aria-label": "Input French/English Query" }}
          onChange={handleQuery}
        />
        <IconButton
          type='button'
          sx={{ p: "10px" }}
          aria-label='search'
          onClick={submitQuery}>
          <SearchIcon />
        </IconButton>
        <Divider sx={{ height: 28, m: 0.5 }} orientation='vertical' />
        <ToggleButtonGroup
          color='primary'
          value={language}
          exclusive
          onChange={handleChange}
          aria-label='Platform'>
          <ToggleButton value='EN'>EN</ToggleButton>
          <ToggleButton value='FR'>FR</ToggleButton>
        </ToggleButtonGroup>
      </Paper>
    </div>
  );
};

export default App;
