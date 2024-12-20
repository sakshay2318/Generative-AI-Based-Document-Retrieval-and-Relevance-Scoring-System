import React, { useState } from "react";
import { getQueryResults } from "../api";

function QueryForm({ setResults }) {
  const [query, setQuery] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = await getQueryResults(query);
    setResults(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your query"
        required
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default QueryForm;
