import React, { useState } from "react";

function Upload() {
    const [file, setFile] = useState(null);
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const [description, setDescription] = useState(null);
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

            const result = await response.json();
            console.log("Server response: ", result);

            if (result.error) {
                alert(`Error: ${result.error}\nDetails: ${result.details || ""}`)
            }

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
            <br></br><p>Insert Job Description Below</p><br></br>
            <textarea id='description' value={description || ""} onChange={handleDescriptionChange} placeholder="Paste job description here"></textarea>
            <button onClick={handleUpload}>Upload Resume and Job Description</button>
        </div>
    );
}

export default Upload;