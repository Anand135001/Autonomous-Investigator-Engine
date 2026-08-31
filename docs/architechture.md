# Investigation Fleet Architecture

## 1. System Architecture

```mermaid
flowchart TB

    U[Operator / Browser]

    CR[Google Cloud Run<br/>FastAPI]

    FC[Fleet Commander<br/>Google ADK]

    CI[Code Investigator]
    RI[Runtime Investigator]
    CA[Cache Investigator]

    GIT[Git Diagnostic Tool]
    PY[Python Runtime Benchmark]
    FS[Filesystem / Metrics Tools]

    EV[Evidence Verifier]

    DB[(Cloud Firestore)]

    SM[Secret Manager]

    GEM[Gemini API]

    U --> CR

    CR --> FC

    FC --> CI
    FC --> RI
    FC --> CA

    CI --> GIT
    RI --> PY
    CA --> FS

    CI --> EV
    RI --> EV
    CA --> EV

    EV --> DB

    SM --> CR
    CR --> GEM