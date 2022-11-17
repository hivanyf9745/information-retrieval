import Button from "@mui/material/Button";
import { useState } from "react";

const AllResults = ({ results }) => {
  const [expand, setExpand] = useState("none");
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
            Expand Query
          </Button>
        </div>
      </div>
      <div className='returned-docs'>
        {results.returnedDocs.map((ele, index) => {
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
