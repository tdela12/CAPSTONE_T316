import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePredict } from "../api";
import { taskFeatures } from "../../config/features";
import { featureMeta } from "../../config/featureMeta";


export default function DataEntry() {
  const [taskType, setTaskType] = useState("");
  const [features, setFeatures] = useState({
    make: "",
    model: "",
    taskName: "",
    odometer: "",
    year: "",
    engineSize: "",
    distance: "",
    months: "",
    adjustedPrice: "",
    fuelType: "",
    transmission: "",
    driveType: "",
  });

  const { predict } = usePredict();
  const navigate = useNavigate();

  const handleChange = (key, value) => {
    setFeatures((prev) => ({ ...prev, [key]: value }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    const result = await predict(
      taskType,
      features.taskName,
      features.odometer,
      features.make,
      features.model,
      features.year,
      features.fuelType,
      features.engineSize,
      features.transmission,
      features.driveType,
      features.distance,
      features.months,
      features.adjustedPrice
    );

    if (result) {
      navigate("/Results", { state: { data: result } });
    } else {
      navigate("/Results", { state: { error: "Prediction failed" } });
    }
  };

  return (
    <div className="MainPage">
      <form onSubmit={handlePredict} className="featureForm">
        {/* Task type dropdown */}
        <label htmlFor="taskType">Select task type to predict:</label>
        <select
          id="taskType"
          value={taskType}
          onChange={(e) => setTaskType(e.target.value)}
        >
          <option value="">-- Choose a task --</option>
          {Object.keys(taskFeatures).map((task) => (
            <option key={task} value={task}>
              {task}
            </option>
          ))}
        </select>

        {/* Conditionally render features */}
        {taskFeatures[taskType]?.map((field) => {
          const meta = featureMeta[field];

          if (meta.type === "select") {
            return (
              <div key={field}>
                <label htmlFor={field}>{meta.label}:</label>
                <select
                  id={field}
                  value={features[field]}
                  onChange={(e) => handleChange(field, e.target.value)}
                >
                  <option value="">-- Choose --</option>
                  {meta.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
            );
          }

          return (
            <div key={field}>
              <label htmlFor={field}>{meta.label}:</label>
              <input
                type={meta.type}
                id={field}
                value={features[field]}
                onChange={(e) => handleChange(field, e.target.value)}
              />
            </div>
          );
        })}

        <button type="submit" id="predictBtn">
          Predict
        </button>
      </form>
    </div>
  );
}
