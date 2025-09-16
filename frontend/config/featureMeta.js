// config/featureMeta.js
export const featureMeta = {
  Make: { label: "Make", type: "text" },
  Model: { label: "Model", type: "text" },
  TaskName: { label: "Task Name", type: "text" },
  Odometer: { label: "Odometer", type: "number" },
  Year: { label: "Year", type: "number" },
  EngineSize: { label: "Engine Size", type: "number" },
  Distance: { label: "Distance", type: "number" },
  Months: { label: "Months", type: "number" },
  AdjustedPrice: { label: "Adjusted Price", type: "number" },

  FuelType: {
    label: "Fuel Type",
    type: "select",
    options: ["Petrol", "Diesel", "Electric", "LPG", "nan"],
  },
  Transmission: {
    label: "Transmission",
    type: "select",
    options: ["Auto", "Manual", "Electric"],
  },
  DriveType: {
    label: "Drive Type",
    type: "select",
    options: ["2WD", "4WD", "nan"],
  },
};
