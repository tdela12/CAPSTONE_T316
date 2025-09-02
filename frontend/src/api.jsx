import { useEffect, useState } from "react";

export function usePredict(taskType, taskName, odometer, make, model, year, fuelType, engineSize, transmission, driveType, distance, months, adjustedPrice) {
  const predict = (taskType, taskName, odometer, make, model, year, fuelType, engineSize, transmission, driveType, distance, months, adjustedPrice) => {
    const url = 'http://127.0.0.1:8000'
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

    const jsonBody = JSON.stringify(body);

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: jsonBody,
    })
      .then((res) =>
        res.json())
      .catch((error) => {
        console.log(error)
      })
  }
  return {
    predict,
  };
}