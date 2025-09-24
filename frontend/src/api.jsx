import { useState } from "react";
import axios from "axios";

// Generic hook for API calls
const useApi = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const callApi = async ({ method = "get", url, payload, params }) => {
    try {
      const res = await axios({
        method,
        url,
        data: payload,
        params,
      });

      setData(res.data);
      setError(null);
      return res.data;
    } catch (err) {
      console.error(err);
      setError(err.response?.data || err.message || "API request failed");
      return null;
    }
  };

  return { data, error, callApi };
};

// Specific hooks
export const usePredict = () => {
  const { data, error, callApi } = useApi();

  const predict = (taskType, features) =>
    callApi({
      method: "post",
      url: "http://127.0.0.1:8000/predict",
      payload: { model_name: taskType, features },
    });

  return { data, error, predict };
};

export const useHistoricalSummary = () => {
  const { data, error, callApi } = useApi();

  const fetchHistorical = (taskType, features, prediction, months, distance) =>
    callApi({
      method: "post",
      url: "http://127.0.0.1:8000/historical/summary",
      payload: { model_name: taskType, features, prediction, months, distance },
    });

  return { data, error, fetchHistorical };
};

// Standalone API function
export const getRegistration = async (registration) => {
  if (!registration) return null;

  try {
    const res = await axios.get("http://127.0.0.1:8000/registration/lookup", {
      params: { registration },
    });
    return res.data;
  } catch (err) {
    console.error(err);
    return null;
  }
};
