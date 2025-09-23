import { useState } from "react";
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // Replace with server backend URL if different
  headers: { "Content-Type": "application/json" },
});

export const usePredict = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const predict = async (taskType, features) => {
    try {
      const res = await api.post("/predict", {
        model_name: taskType,
        features: features,
      });

      setData(res.data);
      setError(null);
      return res.data;
    } catch (err) {
      console.error(err);
      setError(err.response?.data || err.message || "Prediction failed");
      return null;
    }
  };

  return { data, error, predict };
};

export const useHistoricalSummary = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchHistorical = async (
    taskType,
    features,
    prediction,
    months,
    distance
  ) => {
    try {
      const res = await api.post("/historical_summary", {
        model_name: taskType,
        features: features,
        prediction: prediction,
        months: months,
        distance: distance,
      });

      setData(res.data);
      setError(null);
      return res.data;
    } catch (err) {
      console.error(err);
      setError(err.response?.data || err.message || "Failed to fetch historical data");
      return null;
    }
  };

  return { data, error, fetchHistorical };
};

export const getRegistration = async (registration) => {
  if (!registration) return null;

  try {
    const res = await api.get(`/registration_lookup`, {
      params: { Registration: registration },
    });
    return res.data;
  } catch (err) {
    console.error(err);
    return null;
  }
};
