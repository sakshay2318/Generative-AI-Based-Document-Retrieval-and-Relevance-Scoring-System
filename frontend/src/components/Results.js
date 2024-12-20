import React from "react";
import './Results.css';

function Results({ results }) {
  return (
    <div>
      <h2>Results</h2>
      <p><center><strong>Best Performing Algorithm:</strong> {results.best_algorithm}</center></p>
      <br />

      {/* Generative Output Card */}
      <div className="generative-output-card">
        <h3>Generative Model Output:</h3>
        <br />
          {results.generative_output}
      </div>

      <img src={`data:image/png;base64,${results.graph}`} alt="Algorithm Performance" />

      <div className="results-container">
        {results.documents.map((doc, idx) => (
          <div key={idx} className="card">
            <div className="card-header">Document {idx + 1}</div>
            <div className="card-body">
              <p>{doc.substring(0, 300)}...</p> {/* Show the first 300 characters */}
            </div>
            <div className="scores">
              <p><strong>Naive Bayes:</strong> {results.naive_bayes_scores[idx]}</p>
              <p><strong>BM25:</strong> {results.bm25_scores[idx]}</p>
              <p><strong>BSBI:</strong> {results.bsbi_scores[idx]}</p>
            </div>
            <div className="card-footer">
              <a href={results.links[idx]} target="_blank" rel="noopener noreferrer">
                Read Full Document
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Results;
