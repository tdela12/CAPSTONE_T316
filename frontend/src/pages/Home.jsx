import { useState } from "react"


export default function Home() {
  const [taskName, setTaskName] = useState('')
  const [odometer, setOdometer] = useState(0.0)
  const [year, setYear] = useState(0)
  const [model, setModel] = useState('')
  const [make, setMake] = useState('')
  const [fuelType, setFuelType] = useState('')
  const [transmission, setTransmission] = useState('')
  const [engineSize, setEngineSize] = useState(0.0)
  const [driveType, setDriveType] = useState('')
  const [distance, setDistance] = useState(0.0)
  const [months, setMonths] = useState(0.0)
  const [adjustedPrice, setAdjustedPrice] = useState(0.0)
  const [response, setResponse] = useState('');
  const handleLogin = (event) => {
    event.preventDefault();
    setResponse(`Predicting for ${make} ${model}`);
  }
  return (
    <div className="MainPage">
      <div className="login">
        <form onSubmit={handleLogin} className="featureForm">
          {/* Make Input */}
          <label htmlFor="make">Enter Make feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="make"
            id="make"
            value={make}
            onChange={(event) => {
              setMake(event.target.value);
            }}
          />

          {/* Model Input */}
          <label htmlFor="model">Enter Model feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="model"
            id="model"
            value={model}
            onChange={(event) => {
              setModel(event.target.value);
            }}
          />

          {/* taskName Input */}
          <label htmlFor="taskName">Enter taskName feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="taskName"
            id="taskName"
            value={taskName}
            onChange={(event) => {
              setTaskName(event.target.value);
            }}
          />

          {/* odometer Input */}
          <label htmlFor="odometer">Enter odometer feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="odometer"
            id="odometer"
            value={odometer}
            onChange={(event) => {
              setOdometer(event.target.value);
            }}
          />

          {/* year Input */}
          <label htmlFor="year">Enter year feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="year"
            id="year"
            value={year}
            onChange={(event) => {
              setYear(event.target.value);
            }}
          />

          {/* fuelType Input */}
          <label htmlFor="fuelType">Enter fuelType feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="fuelType"
            id="fuelType"
            value={fuelType}
            onChange={(event) => {
              setFuelType(event.target.value);
            }}
          />

          {/* transmission Input */}
          <label htmlFor="transmission">Enter transmission feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="transmission"
            id="transmission"
            value={transmission}
            onChange={(event) => {
              setTransmission(event.target.value);
            }}
          />

          {/* engineSize Input */}
          <label htmlFor="engineSize">Enter engineSize feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="engineSize"
            id="engineSize"
            value={engineSize}
            onChange={(event) => {
              setEngineSize(event.target.value);
            }}
          />

          {/* driveType Input */}
          <label htmlFor="driveType">Enter driveType feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="driveType"
            id="driveType"
            value={driveType}
            onChange={(event) => {
              setDriveType(event.target.value);
            }}
          />

          {/* distance Input */}
          <label htmlFor="distance">Enter distance feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="distance"
            id="distance"
            value={distance}
            onChange={(event) => {
              setDistance(event.target.value);
            }}
          />

          {/* months Input */}
          <label htmlFor="months">Enter months feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="months"
            id="months"
            value={months}
            onChange={(event) => {
              setMonths(event.target.value);
            }}
          />

          {/* adjustedPrice Input */}
          <label htmlFor="adjustedPrice">Enter adjustedPrice feature value:</label>
          <input
            className="enterBar"
            type="text"
            name="adjustedPrice"
            id="adjustedPrice"
            value={model}
            onChange={(event) => {
              setAdjustedPrice(event.target.value);
            }}
          />



          <button type="submit" id="predictBtn">Predict</button>
        </form>


        {response !== '' ? <p id="responseStatus">{response}</p> : null}

      </div>
    </div>
  )
}