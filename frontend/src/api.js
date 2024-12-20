import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"; // Update if backend runs on a different port

export const getQueryResults = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/query`, { query });
    return response.data;
  } catch (error) {
    console.error("Error fetching query results:", error);
    return null;
  }
};
