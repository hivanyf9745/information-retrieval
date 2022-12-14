import ArrowCircleLeftIcon from "@mui/icons-material/ArrowCircleLeft";
import Highlighter from "react-highlight-words";
import "./allResults.styles.scss";
import { Fragment, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const AllResults = ({ query }) => {
  const results = JSON.parse(localStorage.getItem("searchedResults"));

  const [shrink, setShrink] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState("");
  const [detail, setDetail] = useState({});
  const [keywords, setKeywords] = useState("");
  const [mesh, setMesh] = useState([]);
  const [filteredResults, setFilteredResults] = useState(results.initialDocs);

  useEffect(() => {
    let newfilteredResults = [];

    if (mesh.length !== 0) {
      for (let i = 0; i < mesh.length; i++) {
        results.initialDocs.forEach(
          ele =>
            ele.subjectHeadings.includes(mesh[i]) &&
            newfilteredResults.push(ele)
        );
      }
      setFilteredResults(newfilteredResults);
    } else {
      setFilteredResults(results.initialDocs);
    }
  }, [mesh]);

  const navigate = useNavigate();

  console.log(detail);
  console.log(results);
  console.log("mesh: -->", mesh);

  const changeHandler = e => {
    if (e.target.checked && !mesh.includes(e.target.value)) {
      let newMesh = [...mesh, e.target.value];
      setMesh(newMesh);
    } else if (!e.target.checked && mesh.includes(e.target.value)) {
      let newMesh = mesh.filter(ele => ele !== e.target.value);
      setMesh(newMesh);
    }
  };

  if (typeof results !== "string") {
    return (
      <Fragment>
        <div className='translated-result'>
          Translated Result: <span>{results.translatedResult}</span>
          <div className='MeSH-container'>
            <div>
              <input
                type='checkbox'
                id='AD'
                name='anxietyDisorder'
                value='AD'
                onChange={changeHandler}
              />
              <label for='AD'> Anxiety Disorder</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='DP'
                name='depression'
                value='DP'
                onChange={changeHandler}
              />
              <label for='DP'> Depression</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='BD'
                name='bipolarDisorder'
                value='BD'
                onChange={changeHandler}
              />
              <label for='BD'> Bipolar Disorder</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='PTSD'
                name='PTSD'
                value='PTSD'
                onChange={changeHandler}
              />
              <label for='PTSD'> Post-Traumatic Stress Disorder</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='Schizophrenia'
                name='schizophrenia'
                value='Schizophrenia'
                onChange={changeHandler}
              />
              <label for='Schizophrenia'> Schizophrenia</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='ED'
                name='eatingDisorder'
                value='ED'
                onChange={changeHandler}
              />
              <label for='ED'> Eating Disorder</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='DD'
                name='disruptive-dissocial'
                value='DD'
                onChange={changeHandler}
              />
              <label for='DD'>
                {" "}
                Disruptive behaviour and dissocial disorders
              </label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='ND'
                name='neuroDisorder'
                value='ND'
                onChange={changeHandler}
              />
              <label for='ND'> Neurodevelopmental disorders</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='Treatment'
                name='treatment'
                value='Treatment'
                onChange={changeHandler}
              />
              <label for='Treatment'> Treatment</label>
              <br />
            </div>
            <div>
              <input
                type='checkbox'
                id='ADHD'
                name='ADHD'
                value='ADHD'
                onChange={changeHandler}
              />
              <label for='Treatment'>
                {" "}
                Attention-deficit/hyperactivity disorder
              </label>
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
            {filteredResults.map((ele, idx) => {
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
              {filteredResults.map((ele, idx) => {
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
