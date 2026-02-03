import React, { useState, useEffect } from "react";
import Loader from "./Loader";

function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lastResult, setLastResult] = useState(null);
    const [viewingScore, setViewingScore] = useState(false);
    const [description, setDescription] = useState("");
    const [warmupDone, setWarmupDone] = useState(false);
    const [warmupLoading, setWarmupLoading] = useState(true);

    // Preload the ML model when the page loads so the first upload is fast
    useEffect(() => {
        let cancelled = false;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10 * 60 * 1000); // 10 min for first-time download
        fetch("http://localhost:8000/warmup", { signal: controller.signal })
            .then((r) => (cancelled ? null : r.json()))
            .then((data) => {
                if (!cancelled && data) {
                    setWarmupDone(true);
                }
            })
            .catch(() => { if (!cancelled) setWarmupDone(true); }) // consider ready even on timeout so upload can still be tried
            .finally(() => {
                clearTimeout(timeoutId);
                if (!cancelled) setWarmupLoading(false);
            });
        return () => {
            cancelled = true;
            controller.abort();
        };
    }, []);

    const handleFileChange = (e) => setFile(e.target.files[0]);
    const handleDescriptionChange = (e) => setDescription(e.target.value);

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
            // First upload may load the ML model (download + load can take 5–15 min); use a long timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15 * 60 * 1000); // 15 min
            const response = await fetch("http://localhost:8000/upload", {
                method: "POST",
                body: formData,
                signal: controller.signal,
            });
            clearTimeout(timeoutId);

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
            const isTimeout = error.name === "AbortError";
            const msg = isTimeout
                ? "Request took too long (over 15 minutes). The first upload downloads and loads the scoring model—this can take 5–15 min on slow connections or disk. Next time, wait until the page shows \"Scorer ready\" before uploading, or check backend.log for timing details."
                : `Error: Unable to upload file. ${error.message}`;
            alert(msg);
        } finally {
            setLoading(false);
        }
    };

    if (viewingScore && lastResult) {
        return (
            <div className="max-w-xl w-full mx-auto p-6 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-center">
                <p className="text-gray-900 dark:text-gray-100"><strong>Name:</strong> {lastResult.name}</p>
                <p className="text-gray-900 dark:text-gray-100 mt-2"><strong>Score:</strong> {lastResult.score != null ? Number(lastResult.score).toFixed(4) : "—"}</p>
                <button
                    type="button"
                    onClick={() => setViewingScore(false)}
                    className="mt-4 text-sm text-gray-600 dark:text-gray-400 hover:underline"
                >
                    Back
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-xl w-full mx-auto p-6 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                disabled={loading}
                className="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-gray-100 file:text-gray-700 dark:file:bg-gray-700 dark:file:text-gray-200"
            />
            <p className="mt-4 text-sm font-medium text-gray-700 dark:text-gray-300">Insert Job Description Below</p>
            <textarea
                id="description"
                value={description || ""}
                onChange={handleDescriptionChange}
                placeholder="Paste job description here"
                disabled={loading}
                className="w-full mt-2 p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 min-h-[120px]"
            />
            <button
                type="button"
                onClick={handleUpload}
                disabled={loading}
                className="mt-4 px-4 py-2 rounded-lg bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {loading ? "Uploading..." : "Upload Resume and Job Description"}
            </button>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {warmupLoading ? "Preparing scorer (first time can take 1–5 min: downloading/loading model)…" : warmupDone ? "Scorer ready. Upload should be quick." : "First upload may take 1–5 min while the model loads."}
            </p>
            {lastResult && (
                <div className="mt-4">
                    <button
                        type="button"
                        onClick={() => setViewingScore(true)}
                        className="text-sm text-gray-600 dark:text-gray-400 hover:underline"
                    >
                        View Score
                    </button>
                </div>
            )}
            {loading && (
                <div className="mt-5 flex justify-center">
                    <Loader />
                </div>
            )}
        </div>
    );
}

export default Upload;
