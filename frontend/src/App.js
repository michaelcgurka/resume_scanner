import React from "react";
import Upload from "./Upload";  // import Upload component
import Loader from "./Loader";  // import Loader component

function App() {
  return (
    <div className="App">
      <h1>Resume Uploader</h1>
      <Upload />  {/* render the Upload component */}
    </div>
  );
}

export default App;