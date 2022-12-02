import "./allResults.styles.scss";
import { Fragment } from "react";

const AllResults = ({ results }) => {
  console.log("data did pass through: -->", results);

  return (
    <Fragment>
      <div className='translated-result'>
        Translated Result: <span>{results.translatedResult}</span>
      </div>
      <div className='results-container'>
        {results.expandedDocs.map((ele, idx) => {
          const authorsArr = ele.authors.split(", ");
          const firstAuthor = authorsArr[0];
          return (
            <div className='result-container' key={idx}>
              {ele.score > 0.5 && <div className='score-color-green' />}
              {ele.score < 0.5 && ele.score > 0 && (
                <div className='score-color-yellow' />
              )}
              {ele.score < 0 && <div className='score-color-red' />}

              <div className='result-detail'>
                <div className='result-header'>
                  <div className='result-title'>{ele.title}...</div>
                  <div className='author-date'>
                    <div>
                      Author: <span>{firstAuthor}</span>...
                    </div>
                    <div>
                      Date: <span>{ele.releaseDate}</span>
                    </div>
                  </div>
                </div>
                <div className='result abstract'>
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam
                  eu turpis molestie, dictum est a, mattis tellus. Sed
                  dignissim, metus nec fringilla accumsan, risus sem
                  sollicitudin lacus, ut interdum tellus elit sed risus.
                  Maecenas eget condimentum velit, sit amet feugiat lectus.
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Fragment>
  );
};

export default AllResults;
