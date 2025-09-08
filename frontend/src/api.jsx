import { useState } from "react";

export function usePredict(
  taskType, taskName, odometer, make, model, year,
  fuelType, engineSize, transmission, driveType,
  distance, months, adjustedPrice
) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const predict = (
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

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then((res) => res.json())
      .then((resData) => {
        console.log("API response:", resData);
        setData(resData);     // store full API response
        setError(null);
      })
      .catch((err) => {
        console.error("Error fetching prediction:", err);
        setError("Error fetching prediction");
      });
  };

  return { data, error, predict };
}
