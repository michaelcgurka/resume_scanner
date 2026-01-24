import React, { useState } from "react";
import Loader from "./Loader";

function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lastResult, setLastResult] = useState(null);
    const [viewingScore, setViewingScore] = useState(false);
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

        setLoading(true);
        setLastResult(null);

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
                    const detail = errorData.detail ?? errorData.error;
                    errorMsg = typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((x) => x?.msg ?? x).join("; ") : errorMsg;
                    alert(`Error: ${errorMsg}`);
                } catch (e) {
                    alert(`Error: ${errorMsg}`);
                }
                return;
            }

            const result = await response.json();
            setLastResult(result);
            alert(`Successfully uploaded: ${result.filename}\nName: ${result.name}`);
        } catch (error) {
            console.error("Unable to upload file:", error);
            alert(`Error: Unable to upload file. ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (viewingScore && lastResult) {
        return (
            <div>
                <p><strong>Name:</strong> {lastResult.name}</p>
                <p><strong>Score:</strong> {lastResult.score != null ? Number(lastResult.score).toFixed(4) : "—"}</p>
                <button onClick={() => setViewingScore(false)}>Back</button>
            </div>
        );
    }

    return (
        <div>
            <input type="file" accept=".pdf,application/pdf" onChange={handleFileChange} disabled={loading} />
            <br /><p>Insert Job Description Below</p><br />
            <textarea style={{ textAlign: "center" }} id="description" value={description || ""} onChange={handleDescriptionChange} placeholder="Paste job description here" disabled={loading} />
            <button onClick={handleUpload} disabled={loading}>{loading ? "Uploading..." : "Upload Resume and Job Description"}</button>
            {lastResult && (
                <div style={{ marginTop: "1rem" }}>
                    <button onClick={() => setViewingScore(true)}>View Score</button>
                </div>
            )}
            {loading && (
                <div style={{ marginTop: "20px", display: "flex", justifyContent: "center" }}>
                    <Loader />
                </div>
            )}
        </div>
    );
}

export default Upload;