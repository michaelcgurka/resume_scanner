import React, { useState, useEffect } from "react";
import Loader from "./Loader";
import ScoreVisualizer from "./ScoreVisualizer";
import InsightsPanel from "./InsightsPanel";
import Toast from "./Toast";

// Same-origin when not set (Docker/single-service); explicit URL for dev or separate frontend
function getApiBase() {
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  // Use same host as the page so 127.0.0.1 and localhost both work (e.g. WSL + Windows browser)
  if (typeof window !== "undefined" && window.location.port === "3000") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return ""; // same origin (e.g. production backend serving frontend)
}
const API_BASE = getApiBase();

function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lastResult, setLastResult] = useState(null);
    const [viewingScore, setViewingScore] = useState(false);
    const [description, setDescription] = useState("");
    const [warmupDone, setWarmupDone] = useState(false);
    const [warmupLoading, setWarmupLoading] = useState(true);
    const [toastMessage, setToastMessage] = useState(null);

    // Preload the ML model when the page loads so the first upload is fast
    useEffect(() => {
        let cancelled = false;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10 * 60 * 1000); // 10 min for first-time download
        fetch(`${API_BASE}/warmup`, { signal: controller.signal })
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
            const response = await fetch(`${API_BASE}/upload`, {
                method: "POST",
                body: formData,
                signal: controller.signal,
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 429) {
                    alert("Too many requests. Please wait a minute and try again.");
                    return;
                }
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
            setToastMessage(`Uploaded ${result.filename} — ${result.name}`);
        } catch (error) {
            console.error("Unable to upload file:", error);
            const isTimeout = error.name === "AbortError";
            const isNetwork = !error.response && (error.message === "Failed to fetch" || error.name === "TypeError");
            let msg;
            if (isTimeout) {
                msg = "Request took too long (over 15 minutes). The first upload downloads and loads the scoring model—this can take 5–15 min on slow connections or disk. Next time, wait until the page shows \"Scorer ready\" before uploading, or check backend.log for timing details.";
            } else if (isNetwork) {
                msg = `Could not reach the backend (Failed to fetch). From the project root run: ./start.sh (or npm start). Open ${API_BASE || "http://localhost:8000"}/health in your browser to check. If that works but upload still fails, set REACT_APP_API_URL in frontend/.env (e.g. REACT_APP_API_URL=http://127.0.0.1:8000) and restart the frontend.`;
            } else {
                msg = `Error: Unable to upload file. ${error.message}`;
            }
            alert(msg);
        } finally {
            setLoading(false);
        }
    };

    if (viewingScore && lastResult) {
        return (
            <div className="max-w-xl w-full mx-auto p-6 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <p className="text-gray-900 dark:text-gray-100 text-center"><strong>Name:</strong> {lastResult.name}</p>
                <div className="mt-4 flex flex-col items-center">
                    <ScoreVisualizer
                        score={lastResult.score}
                        breakdown={lastResult.breakdown}
                    />
                </div>
                <InsightsPanel
                    recommendations={lastResult.recommendations}
                    missing_keywords={lastResult.missing_keywords}
                    missing_keywords_by_category={lastResult.missing_keywords_by_category}
                    section_scores={lastResult.section_scores}
                />
                <div className="text-center mt-4">
                    <button
                        type="button"
                        onClick={() => setViewingScore(false)}
                        className="text-sm text-gray-600 dark:text-gray-400 hover:underline"
                    >
                        Back
                    </button>
                </div>
                <Toast
                    message={toastMessage}
                    visible={!!toastMessage}
                    onDismiss={() => setToastMessage(null)}
                />
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
            {API_BASE && (
                <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                    Backend: <a href={API_BASE + "/health"} target="_blank" rel="noopener noreferrer" className="underline">{API_BASE}</a>
                </p>
            )}
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
            <Toast
                message={toastMessage}
                visible={!!toastMessage}
                onDismiss={() => setToastMessage(null)}
            />
        </div>
    );
}

export default Upload;
