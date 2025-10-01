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
        try {
            const formData = new FormData();
            formData.append("file", file);
            const response = await fetch("http://localhost:8000/upload", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();

            console.log(result);
            alert(`Uploaded: ${result.filename}`);
            
        } catch (error) {
            console.log("Unable to upload file. See error message.")
            console.error(error.message);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload Resume (PDF)</button>
        </div>
    );
}

export default Upload;