# Resume Scanner

Resume Scanner is a web app that scores resumes against job descriptions using ML, similar to applicant-tracking systems (ATS) used in tech hiring. Upload a PDF resume and a job description to get a match score and insights.

---

## Use the app

**[Resume Scanner](https://resume-scanner-hltc.onrender.com/)** — open the link, upload a PDF resume, paste a job description, and get your score. No account required. The first load (or after the app has been idle) may take 30–60 seconds while the service wakes up.


---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Security](#security)
- [License](#license)

---

## Features

- **Upload & parse** — Upload a PDF resume; the backend extracts text and stores it with an optional job description.
- **ML-based scoring** — Score resumes against job descriptions using a sentence-transformers model (embedding similarity).
- **Single-page UI** — React frontend with dark/light theme; results and insights on the same page.
- **Rate limiting & validation** — Uploads limited by IP; only PDFs allowed, with size and length limits to reduce abuse.
- **Production-ready** — Health checks, CORS config, security headers; deployable to Render, Fly.io, or any Docker host.

---

## Tech Stack

| Frontend | React 19, Create React App, Tailwind CSS |
| Backend  | Python 3.11, FastAPI, Uvicorn |
| Database | PostgreSQL (SQLAlchemy ORM) |
| ML       | sentence-transformers, scikit-learn, PyTorch |
| PDF      | pdfplumber, PyPDF2, pdfminer.six |

---

## Project Structure

```
resume_scanner/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, routes, static serving
│   │   ├── database.py      # DB connection
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── resume_parser.py  # PDF text extraction
│   │   ├── scoring_logic.py  # ML scoring
│   │   ├── ml_model/        # Embedding model loading & processing
│   │   └── ...
│   ├── migrate_job_columns.py
│   └── tests/
├── frontend/
│   ├── public/              # index.html, favicon, manifest
│   └── src/                 # React app (App.js, Upload.js, etc.)
├── Dockerfile               # Multi-stage: Node build + Python serve
├── requirements.txt
├── render.yaml              # Render Blueprint (optional)
└── README.md
```

---

## Deployment

This app is built to run as a single web service (e.g. on [Render](https://render.com) or [Fly.io](https://fly.io)) with a managed PostgreSQL database.

---

## License

ISC — see [package.json](package.json).
