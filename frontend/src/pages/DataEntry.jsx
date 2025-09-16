import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePredict } from "../api";
import { taskFeatures } from "../../config/features";
import { featureMeta } from "../../config/featureMeta";

export default function DataEntry() {
  const [taskType, setTaskType] = useState("");
  const [features, setFeatures] = useState({
    Make: "",
    Model: "",
    TaskName: "",
    Odometer: "",
    Year: "",
    EngineSize: "",
    Distance: "",
    Months: "",
    AdjustedPrice: "",
    FuelType: "",
    Transmission: "",
    DriveType: "",
  });

  const { predict } = usePredict();
  const navigate = useNavigate();

  // Update feature value
  const handleChange = (key, value) => {
    setFeatures((prev) => ({ ...prev, [key]: value }));
  };

  // Handle form submission
  const handlePredict = async (e) => {
  e.preventDefault();

  if (!taskType) return alert("Please select a task type");

  // Build payload with all features, fill unused ones with null
  const payloadFeatures = {};
  Object.keys(features).forEach((key) => {
    let value = features[key] || null;

    // Convert numeric fields
    if (["odometer", "year", "engineSize", "distance", "months", "adjustedPrice"].includes(key)) {
      value = value !== null ? Number(value) : null;
    }

    payloadFeatures[key] = value;
  });

  const result = await predict(taskType, payloadFeatures);

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

        {/* Render relevant fields dynamically */}
        {taskFeatures[taskType]?.map((field) => {
          const meta = featureMeta[field];

          if (!meta) return null; // safety check

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
