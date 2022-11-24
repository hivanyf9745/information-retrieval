import axios from "axios";
import Button from "@mui/material/Button";
import Rating from "@mui/material/Rating";
import Box from "@mui/material/Box";
import StarIcon from "@mui/icons-material/Star";
import { useState } from "react";
import Checkbox from "@mui/material/Checkbox";
import "./allResults.styles.scss";

const label = { inputProps: { "aria-label": "Checkbox demo" } };

const labels = {
  1: "Useless",
  2: "Poor",
  3: "Ok",
  4: "Good",
  5: "Excellent",
};

function getLabelText(value) {
  return `${value} Star${value !== 1 ? "s" : ""}, ${labels[value]}`;
}

const AllResults = ({ results, query, language }) => {
  const baseURL = "http://localhost:8080";

  const [expand, setExpand] = useState("none");
  const [displayUser, setDisplayUser] = useState("none");
  const [checked, setChecked] = useState([]);

  // For user ratings
  const [value, setValue] = useState(
    new Array(results.returnedDocs.length).fill(0)
  );
  const [hover, setHover] = useState(-1);

  const [feedback, setFeedback] = useState([]);

  const [response, setResponse] = useState("{}");

  console.log("rating feedback: ---->", feedback);
  console.log("box checked: ---->", checked);
  console.log("value: ---->", value);
  console.log("user-based response: ---->", response);

  const checkHandler = e => {
    if (e.target.checked && !checked.includes(e.target.value)) {
      const newChecked = [...checked, e.target.value];
      setChecked(newChecked);
    } else if (!e.target.checked && checked.includes(e.target.value)) {
      const newChecked = checked.filter(item => item !== e.target.value);
      setChecked(newChecked);
    }
  };

  const submitUserFeedback = async () => {
    console.log("post body format: ----> ", JSON.stringify(checked));
    try {
      await axios
        .post(`${baseURL}/userBased`, {
          title: "user-based feedback",
          body: `{"query": "${query}", "type": "${language}", "userFeedback": ${JSON.stringify(
            checked
          )}}`,
        })
        .then(response => {
          setResponse(response.data);
          setDisplayUser("block");
        });
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className='results-container'>
      <div className='option-flex'>
        <div>Translated Result: {results.translatedResult}</div>
        <div>
          <Button
            variant='contained'
            onClick={() => {
              expand === "none" ? setExpand("block") : setExpand("none");
            }}>
            For Pseudo Relevance Results
          </Button>
        </div>
      </div>
      <div className='returned-docs'>
        {results.returnedDocs.map((ele, index) => {
          return (
            <div key={index} className='docs-container'>
              <div className='result-checkbox'>
                <div>Do you find this document relevant?</div>
                <Checkbox
                  {...label}
                  value={`${ele.docid}, ${ele.docLanguage}`}
                  onClick={checkHandler}
                />
              </div>
              <div className='result-details'>
                <div>{ele.title}</div>
                <div>{ele.authors}</div>
                <div>{ele.releaseDate}</div>
                <div>{ele.abstract}</div>
              </div>
              <div className='result-ratings'>
                <div>Your Rating?</div>
                <Box
                  sx={{
                    width: 200,
                    display: "flex",
                    alignItems: "center",
                  }}>
                  <Rating
                    name='hover-feedback'
                    value={value[index]}
                    precision={1}
                    getLabelText={getLabelText}
                    onChange={event => {
                      const newFeedback = [
                        ...feedback,
                        JSON.stringify({
                          docid: ele.docid,
                          docLanguage: ele.docLanguage,
                          docRating: parseInt(event.target.value),
                        }),
                      ];
                      let newValueArr = [...value];
                      newValueArr[index] = parseInt(event.target.value);
                      setFeedback(newFeedback);
                      setValue(newValueArr);
                    }}
                    onChangeActive={(event, newHover) => {
                      setHover(newHover);
                    }}
                    emptyIcon={
                      <StarIcon style={{ opacity: 0.55 }} fontSize='inherit' />
                    }
                  />
                  {value !== null && (
                    <Box sx={{ ml: 2 }}>
                      {labels[hover !== -1 ? hover : value]}
                    </Box>
                  )}
                </Box>
              </div>
            </div>
          );
        })}
        <Button variant='contained' onClick={submitUserFeedback}>
          USER-BASED Relevance
        </Button>

        <div className='userBased-results' style={{ display: displayUser }}>
          <Button
            variant='contained'
            onClick={() => {
              displayUser === "none"
                ? setDisplayUser("block")
                : setDisplayUser("none");
            }}>
            Fold User-Based Feedback
          </Button>
          {response.userbasedDocs.map((ele, index) => {
            return (
              <div key={index} className='results-container'>
                <div>{ele.title}</div>
                <div>{ele.authors}</div>
                <div>{ele.releaseDate}</div>
                <div>{ele.abstract}</div>
              </div>
            );
          })}
        </div>
      </div>
      <div className='expanded-results' style={{ display: expand }}>
        <Button
          variant='contained'
          onClick={() => {
            expand === "none" ? setExpand("block") : setExpand("none");
          }}>
          Fold Expand Query
        </Button>
        {results.expandedDocs.map((ele, index) => {
          return (
            <div key={index} className='results-container'>
              <div>{ele.title}</div>
              <div>{ele.authors}</div>
              <div>{ele.releaseDate}</div>
              <div>{ele.abstract}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AllResults;
