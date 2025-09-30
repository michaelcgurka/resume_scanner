import React, { useState } from "react";

function Upload() {
    const [file, setFile] = useState(null);
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        console.log(result);
        alert(`Uploaded: ${result.filename}`);
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload Resume (PDF)</button>
        </div>
    );
}

export default Upload;