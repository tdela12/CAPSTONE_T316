import { useState } from "react";

export function usePredict() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const predict = async (
    taskType, taskName, odometer, make, model, year,
    fuelType, engineSize, transmission, driveType,
    distance, months, adjustedPrice
  ) => {
    const url = "http://127.0.0.1:8000/predict";
    const body = {
      model_name: taskType,
      features: {
        TaskName: taskName,
        Odometer: odometer,
        Make: make,
        Model: model,
        Year: year,
        FuelType: fuelType,
        Transmission: transmission,
        EngineSize: engineSize,
        DriveType: driveType,
        Distance: distance,
        Months: months,
        AdjustedPrice: adjustedPrice,
      },
    };

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const resData = await res.json();
      console.log("API response:", resData);

      setData(resData);
      setError(null);

      return resData;
    } catch (err) {
      console.error("Error fetching prediction:", err);
      setError("Error fetching prediction");
      setData(null);
      return null; 
    }
  };

  return { data, error, predict };
}
