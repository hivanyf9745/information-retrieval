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

const AllResults = ({ results }) => {
  const [expand, setExpand] = useState("none");
  const [checked, setChecked] = useState([]);

  // For user ratings
  const [value, setValue] = useState(
    new Array(results.returnedDocs.length).fill(0)
  );
  const [hover, setHover] = useState(-1);

  const [feedback, setFeedback] = useState([]);

  console.log("rating feedback: ---->", feedback);
  console.log("box checked: ---->", checked);
  console.log("value: ---->", value);

  const checkHandler = e => {
    if (e.target.checked && !checked.includes(e.target.value)) {
      const newChecked = [...checked, e.target.value];
      setChecked(newChecked);
    } else if (!e.target.checked && checked.includes(e.target.value)) {
      const newChecked = checked.filter(item => item !== e.target.value);
      setChecked(newChecked);
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
                <div>Do you find this is relevant?</div>
                <Checkbox
                  {...label}
                  value={`{"docid": ${ele.docid}, "docLanguage": "${ele.docLanguage}"}`}
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
                    value={JSON.parse(value[index])}
                    precision={1}
                    getLabelText={getLabelText}
                    onChange={(event, newValue) => {
                      const newFeedback = [
                        ...feedback,
                        JSON.stringify({
                          docid: ele.docid,
                          docLanguage: ele.docLanguage,
                          docRating: event.target.value,
                        }),
                      ];
                      let newValueArr = [...value];
                      newValueArr[index] = JSON.stringify({
                        docid: ele.docid,
                        docLanguage: ele.docLanguage,
                        docRating: event.target.value,
                      });
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
        <Button variant='contained' onClick={() => {}}>
          USER-BASED Relevance
        </Button>
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
