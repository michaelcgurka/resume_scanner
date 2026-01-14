import React, { useState } from "react";

function Upload() {
    const [file, setFile] = useState(null);
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const [description, setDescription] = useState("");
    const handleDescriptionChange = (e) => {
        setDescription(e.target.value);
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file.");
            return;
        }
        if (!description) {
            alert("Please add a job description.");
            return;
        }
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("description", description);
            const response = await fetch("http://localhost:8000/upload", {
                method: "POST",
                body: formData,
            });

            // Check if response is ok before parsing JSON
            if (!response.ok) {
                let errorMsg = `Server error: ${response.status} ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorData.error || errorMsg;
                    const details = errorData.details || "";
                    alert(`Error: ${errorMsg}${details ? `\nDetails: ${details}` : ""}`);
                } catch (e) {
                    // If response is not JSON, use status text
                    alert(`Error: ${errorMsg}`);
                }
                return;
            }

            const result = await response.json();
            console.log("Server response: ", result);

            // Check if response contains an error field
            if (result.error) {
                const errorMsg = result.error || `Server error: ${response.status}`;
                const details = result.details || "";
                alert(`Error: ${errorMsg}${details ? `\nDetails: ${details}` : ""}`);
                return;
            }

            // Success case
            console.log(result);
            alert(`Successfully uploaded: ${result.filename}\nName: ${result.name}`);
            
        } catch (error) {
            console.error("Unable to upload file:", error);
            alert(`Error: Unable to upload file. ${error.message}`);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <br></br><p>Insert Job Description Below</p><br></br>
            <textarea id='description' value={description || ""} onChange={handleDescriptionChange} placeholder="Paste job description here"></textarea>
            <button onClick={handleUpload}>Upload Resume and Job Description</button>
        </div>
    );
}

export default Upload;