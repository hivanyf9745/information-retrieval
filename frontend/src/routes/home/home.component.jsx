import axios from "axios";
import Paper from "@mui/material/Paper";
import InputBase from "@mui/material/InputBase";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import SearchIcon from "@mui/icons-material/Search";
import ClearIcon from "@mui/icons-material/Clear";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { useEffect, useState } from "react";

import "./home.styles.scss";
import AllResults from "../../components/allResults.component";

const Home = () => {
  const baseURL = "http://localhost:8080";

  const [language, setLanguage] = useState("EN");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [focus, setFocus] = useState(false);

  console.log("results: -->", typeof results);

  const handleChange = (event, newLanguage) => {
    setLanguage(newLanguage);
  };

  const handleQuery = event => {
    setQuery(event.target.value);
  };

  const submitQuery = async () => {
    try {
      const result = !!query.match(/^[.,:;!?@#$%&*]/);
      if (query !== "" && !result) {
        await axios
          .post(`${baseURL}/query`, {
            title: "Hello World",
            body: `{"query": "${query}", "type": "${language}"}`,
          })
          .then(response => {
            localStorage.setItem(
              "searchedResults",
              JSON.stringify(response.data)
            );
            setResults(JSON.parse(localStorage.getItem("searchedResults")));
          });
      } else {
        alert("Please put in a valid query!");
      }
    } catch (error) {
      alert("Something went wrong!\n" + error);
    }
  };
  const enterKeyDownHandler = e => {
    if (e.key === "Enter") {
      e.preventDefault();
      submitQuery();
    }
  };
  console.log(results);

  return (
    <div>
      <div className='search-bar-container'>
        <div className='searchBar'>
          <Paper
            component='form'
            sx={
              !focus
                ? {
                    p: "2px 4px",
                    display: "flex",
                    alignItems: "center",
                    width: 700,
                    margin: "0 auto",
                    borderRadius: "1000px",
                    boxShadow: "none",
                    backgroundColor: "#F6F5F5",
                  }
                : {
                    p: "2px 4px",
                    display: "flex",
                    alignItems: "center",
                    width: 700,
                    margin: "0 auto",
                    borderRadius: "1000px",
                    boxShadow: "none",
                    backgroundColor: "#fff",
                    outline: "#445FEA solid 3px",
                  }
            }>
            <IconButton
              type='button'
              sx={{ p: "10px" }}
              aria-label='search'
              onClick={submitQuery}>
              <SearchIcon />
            </IconButton>
            <InputBase
              sx={{ ml: 1, flex: 1 }}
              placeholder='Input French/English Query'
              inputProps={{ "aria-label": "Input French/English Query" }}
              onChange={handleQuery}
              onFocus={() => setFocus(true)}
              onKeyDown={enterKeyDownHandler}
            />
            <IconButton type='button' sx={{ p: "10px" }} aria-label='search'>
              <ClearIcon />
            </IconButton>
            <Divider sx={{ height: 28, m: 0.5 }} orientation='vertical' />
            <ToggleButtonGroup
              color='primary'
              value={language}
              exclusive
              onChange={handleChange}
              aria-label='Platform'>
              <ToggleButton value='EN' sx={{ border: "none" }}>
                EN
              </ToggleButton>
              <ToggleButton value='FR' sx={{ border: "none" }}>
                FR
              </ToggleButton>
            </ToggleButtonGroup>
          </Paper>

          <div
            className='clear-results'
            onClick={() => {
              localStorage.removeItem("searchedResults");
              window.location.reload();
            }}>
            clear all results
          </div>
        </div>

        {localStorage.getItem("searchedResults") ? (
          <AllResults query={query} onClick={() => setFocus(false)} />
        ) : (
          <div
            className='results-container-null'
            onClick={() => setFocus(false)}>
            <h1>Please input some queries 📝</h1>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
