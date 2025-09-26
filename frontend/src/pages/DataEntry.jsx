import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePredict } from "../api";
import { getRegistration } from "../api";
import { taskFeatures } from "../../config/features";
import { featureMeta } from "../../config/featureMeta";


export default function DataEntry() {
  const [taskType, setTaskType] = useState("");
  const [features, setFeatures] = useState({
    Registration: "",
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

  const handleRegistrationLookup = async () => {
    const reg = features.Registration?.trim();
    if (!reg) return;

    const data = await getRegistration(reg);
    if (!data) return alert("Could not find vehicle for this registration.");

    const autofillFields = [
      "Make",
      "Model",
      "Year",
      "FuelType",
      "EngineSize",
      "Transmission",
      "DriveType",
    ];

    // Use functional state update to ensure the latest state
    setFeatures((prevFeatures) => {
      const newFeatures = { ...prevFeatures };
      autofillFields.forEach((field) => {
        if (data[field] !== undefined && data[field] !== null) {
          newFeatures[field] = String(data[field]); // force string
        }
      });
      return newFeatures;
    });

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
        <div className="formGroup">
          <label htmlFor="registration">Vehicle Registration:</label>
          <input
            type="text"
            id="registration"
            placeholder="Please enter a valid vehicle registration."
            className="enterBar"
            value={features.Registration || ""}
            onChange={(e) => handleChange("Registration", e.target.value)}
            onBlur={handleRegistrationLookup} // call API when input loses focus
          />
        </div>

        {/* Task type dropdown */}
        <div className="formGroup">
          <label htmlFor="taskType">Select task type to predict:</label>
          <select
            id="taskType"
            className="enterBar"
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
        </div>


        {/* Render relevant fields dynamically */}
        {taskFeatures[taskType]?.map((field) => {
          const meta = featureMeta[field];

          if (!meta) return null; // safety check

          if (meta.type === "select") {
            return (
              <div className="formGroup" key={field}>
                <label htmlFor={field}>{meta.label}:</label>
                <select
                  id={field}
                  className="enterBar"
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
            <div className="formGroup" key={field}>
              <label htmlFor={field}>{meta.label}:</label>
              <input
                type={meta.type}
                placeholder={`Please enter ${meta.type}`}
                className="enterBar"
                id={field}
                value={features[field]}
                onChange={(e) => handleChange(field, e.target.value)}
              />
            </div>
          );
        })}

        <div className="formActions">
          <button type="submit" id="predictBtn">
            Predict
          </button>
        </div>
      </form>
    </div>
  );
}
