// config/featureMeta.js
export const featureMeta = {
  Make: { label: "Make", type: "text", options: []},
  Model: { label: "Model", type: "text", options: []},
  TaskName: { label: "Task Name", type: "text", options: []},
  Odometer: { label: "Odometer", type: "number", options: []},
  Year: { label: "Year", type: "number", options: []},
  EngineSize: { label: "Engine Size", type: "number", options: []},
  Distance: { label: "Distance", type: "number", options: []},
  Months: { label: "Months", type: "number", options: []},
  AdjustedPrice: { label: "Adjusted Price", type: "number", options: []},

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
