import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePredict } from "../api";
import { usePrefilter } from "../api";
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
  const { filteredData, error, prefilter } = usePrefilter();
  const [loading, setLoading] = useState(false);
  const [dynamicOptions, setDynamicOptions] = useState({});

  const navigate = useNavigate();

  const stringUIFields = ["Registration", "Make", "Model"];


  // Update feature value
  const handleChange = (key, value) => {
    if (stringUIFields.includes(key) && typeof value === "string") {
      value = value.toUpperCase();
    }
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

  const handlePrefilter = async () => {
    setLoading(true);
    
    await new Promise((resolve) => setTimeout(resolve, 0));

    
    
    try {
      const payloadFeatures = {};

      Object.keys(features).forEach((key) => {
        let value = features[key] || null;
        if (["odometer", "year", "engineSize", "distance", "months", "adjustedPrice"].includes(key)) {
          value = value !== null ? Number(value) : null;
        }
        payloadFeatures[key] = value;
      });

      const response = await prefilter(taskType, payloadFeatures);

      if (response) {
        setDynamicOptions((prev) => ({
          ...prev,
          ...Object.fromEntries(
            Object.entries(response).map(([key, values]) => [key, values || []])
          ),
        }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }

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
      <div className={`blurContents ${loading ? "blurred" : ""}`}>
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
              onBlur={handlePrefilter}
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

            if (!meta) return null;

            const options = dynamicOptions[field] || meta.options;
            const isTypeable = ["Make", "Model", "Year", "EngineSize", "Distance", "Months", "TaskName"].includes(field);

            return (
              <div className="formGroup" key={field}>
                <label htmlFor={field}>{meta.label}:</label>
                {isTypeable ? (
                  <>
                    <input
                      list={`${field}-options`}
                      id={field}
                      name={field}
                      className="enterBar"
                      value={features[field] || ""}
                      placeholder={`Enter or select ${meta.label.toLowerCase()}`}
                      onChange={(e) => handleChange(field, e.target.value)}
                      onBlur={handlePrefilter}
                    />
                    <datalist id={`${field}-options`}>
                      {options.map((opt) => (
                        <option key={opt} value={opt} />
                      ))}
                    </datalist>
                  </>
                ) : (
                  <select
                    className="enterBar"
                    id={field}
                    value={features[field]}
                    onChange={(e) => handleChange(field, e.target.value)}
                    onBlur={handlePrefilter}
                  >
                    <option value="">-- Choose --</option>
                    {options.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                )}
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

      {loading && (
        <div className="loadingContainer">
          <div className="loadingText">Loading...</div>
        </div>
      )}

    </div>
  );
}
