import axios from "axios";
import Button from "@mui/material/Button";
import Rating from "@mui/material/Rating";
import { useState } from "react";
import Checkbox from "@mui/material/Checkbox";
import "./allResults.styles.scss";

const label = { inputProps: { "aria-label": "Checkbox demo" } };

const AllResults = ({ results, query, language }) => {
  const baseURL = "http://localhost:8080";

  const [expand, setExpand] = useState("none");
  const [displayUser, setDisplayUser] = useState("none");
  const [checked, setChecked] = useState([]);

  const [response, setResponse] = useState("{}");
  console.log("box checked: ---->", checked);
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
                <Rating name='half-rating' defaultValue={0} precision={1} />
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
          <div className='userBased-details'>
            {response !== "{}"
              ? response.userbasedDocs.map((ele, index) => {
                  return (
                    <div key={index} className='results-details'>
                      <div className='results-container'>
                        <div>{ele.title}</div>
                        <div>{ele.authors}</div>
                        <div>{ele.releaseDate}</div>
                        <div>{ele.abstract}</div>
                      </div>
                      <div className='userresult-ratings'>
                        <div>Your Rating?</div>
                        <Rating
                          name='half-rating'
                          defaultValue={0}
                          precision={1}
                        />
                      </div>
                    </div>
                  );
                })
              : console.log("no response from users' feedback yet")}
          </div>
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
        <div className=''>
          {results.expandedDocs.map((ele, index) => {
            return (
              <div key={index} className='pseudo-docs-container'>
                <div className='results-container'>
                  <div>{ele.title}</div>
                  <div>{ele.authors}</div>
                  <div>{ele.releaseDate}</div>
                  <div>{ele.abstract}</div>
                </div>
                <div className='pseudoresult-ratings'>
                  <div>Your Rating?</div>
                  <Rating name='half-rating' defaultValue={0} precision={1} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AllResults;
