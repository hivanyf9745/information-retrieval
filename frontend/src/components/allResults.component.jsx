import ArrowCircleLeftIcon from "@mui/icons-material/ArrowCircleLeft";
import Highlighter from "react-highlight-words";
import "./allResults.styles.scss";
import { Fragment, useState } from "react";
import { useNavigate } from "react-router-dom";

const AllResults = ({ query }) => {
  const [shrink, setShrink] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState("");
  const [detail, setDetail] = useState({});
  const [keywords, setKeywords] = useState("");

  const navigate = useNavigate();
  const results = JSON.parse(localStorage.getItem("searchedResults"));

  console.log(detail);
  console.log(results);

  if (typeof results !== "string") {
    return (
      <Fragment>
        <div className='translated-result'>
          Translated Result: <span>{results.translatedResult}</span>
          <div className='MeSH-container'>
            <div>
              <input
                type='checkbox'
                id='vehicle1'
                name='vehicle1'
                value='Bike'
              />
              <label for='vehicle1'> I have a bike</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='vehicle2'
                name='vehicle2'
                value='Car'
              />
              <label for='vehicle2'> I have a car</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='vehicle3'
                name='vehicle3'
                value='Boat'
              />
              <label for='vehicle3'> I have a boat</label>
              <br />
            </div>
          </div>
        </div>

        <div
          className='expand-button'
          onClick={() => {
            navigate("/pseudo");
          }}>
          Not satisfied? Show more results
        </div>

        {shrink === false ? (
          <div className='results-container'>
            <div className='MeSH-container'></div>

            {results.initialDocs.map((ele, idx) => {
              const authorsArr = ele.authors.split(", ");
              const firstAuthor = authorsArr[0];
              return (
                <div
                  className='result-container'
                  key={idx}
                  onClick={() => {
                    setShrink(true);
                    setSelectedDoc(idx);
                    setDetail(ele);
                  }}>
                  {ele.score > 0.5 && <div className='score-color-green' />}
                  {ele.score < 0.5 && ele.score > 0.1 && (
                    <div className='score-color-yellow' />
                  )}
                  {ele.score >= 0 && ele.score <= 0.1 && (
                    <div className='score-color-red' />
                  )}

                  <div className='result-detail'>
                    <div className='result-header'>
                      <div className='result-title'>{ele.title}</div>
                      <div className='author-date'>
                        <div>
                          Author: <span>{firstAuthor}</span>...
                        </div>
                        <div>
                          Date: <span>{ele.releaseDate}</span>
                        </div>
                      </div>
                    </div>
                    <div className='result abstract'>{ele.snippet}</div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className='expanded-results'>
            <div className='expanded-resultList'>
              {results.initialDocs.map((ele, idx) => {
                const authorsArr = ele.authors.split(", ");
                const firstAuthor = authorsArr[0];

                return (
                  <div
                    className='shrinked-container'
                    key={idx}
                    style={
                      selectedDoc === idx
                        ? { backgroundColor: "#0099FF", color: "#fff" }
                        : { backgroundColor: "#f1f1f1", color: "#000" }
                    }
                    onClick={() => {
                      setSelectedDoc(idx);
                      setDetail(ele);
                    }}>
                    {ele.score > 0.5 && <div className='score-color-green' />}
                    {ele.score < 0.5 && ele.score > 0.1 && (
                      <div className='score-color-yellow' />
                    )}
                    {ele.score >= 0 && ele.score <= 0.1 && (
                      <div className='score-color-red' />
                    )}

                    <div className='expanded-preview'>
                      <div className='expanded-header'>
                        <div className='expanded-title'>{ele.title}</div>
                        <span className='addition'>...</span>
                      </div>
                      <div className='expanded-info'>
                        <div>
                          <strong>Author: </strong>
                          {firstAuthor} et al.
                        </div>
                        <div>
                          <strong>Date: </strong>
                          {ele.releaseDate}
                        </div>
                        <div className='keywords'>
                          <div
                            onMouseEnter={() => setKeywords(ele.docid)}
                            onMouseLeave={() => {
                              setKeywords("");
                            }}>
                            <strong>Keywords</strong>
                          </div>
                          <div
                            className='keywords-detail'
                            style={
                              keywords === ele.docid
                                ? { display: "block" }
                                : { display: "none" }
                            }>
                            {ele.keywords.join(", ")}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className='result-page'>
              {detail.score > 0.5 && <div className='score-color-green' />}
              {detail.score < 0.5 && detail.score > 0.1 && (
                <div className='score-color-yellow' />
              )}
              {detail.score >= 0 && detail.score <= 0.1 && (
                <div className='score-color-red' />
              )}

              <div className='page-detail'>
                <div
                  className='detail-arrow'
                  onClick={() => {
                    setShrink(false);
                  }}>
                  <ArrowCircleLeftIcon />
                </div>
                <div className='detail-title'>{detail.title}</div>
                <div className='detail-authors'>{detail.authors}</div>
                <div className='detail-date'>{detail.releaseDate}</div>
                <div className='detail-abstract'>
                  {detail.docLanguage == "english" ? (
                    <Highlighter
                      highlightClassName='YourHighlightClass'
                      searchWords={query.split(" ")}
                      autoEscape={true}
                      textToHighlight={detail.abstract}
                    />
                  ) : (
                    <Highlighter
                      highlightClassName='YourHighlightClass'
                      searchWords={results.translatedResult.split(" ")}
                      autoEscape={true}
                      textToHighlight={detail.abstract}
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </Fragment>
    );
  } else {
    return (
      <div className='error-container'>
        <h1>{results}</h1>
      </div>
    );
  }
};

export default AllResults;
