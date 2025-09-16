import { useState } from "react";

export const usePredict = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const predict = async (taskType, features) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model_name: taskType,
          features: features
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Prediction failed");
      }

      const resData = await res.json();
      setData(resData);
      setError(null);
      return resData;
    } catch (err) {
      console.error(err);
      setError(err.message || "Prediction failed");
      return null;
    }
  };

  return { data, error, predict };
};

export const useHistoricalSummary = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchHistorical = async (taskType, features, prediction) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/historical_summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model_name: taskType,
          features: features,
          prediction: prediction
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Failed to fetch historical data");
      }

      const resData = await res.json();
      setData(resData);
      setError(null);
      return resData;
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to fetch historical data");
      return null;
    }
  };

  return { data, error, fetchHistorical };
};

