import React, { useState } from "react";
import QueryForm from "./components/QueryForm";
import Results from "./components/Results";

function App() {
  const [results, setResults] = useState(null);
  return (
    <div className="App">
      <h1>Information Retrieval System</h1>
      <QueryForm setResults={setResults} />
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
