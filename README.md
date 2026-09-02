# Investigation Fleet
 
**Governed multi-agent incident investigation.**
 
Investigation Fleet delegates operational incident investigation to specialized agents, executes scoped diagnostic tools, collects evidence, and verifies the final root cause — turning a manual, single-engineer debugging process into an autonomous, auditable one.
 
🔗 **Live demo:** https://investigation-fleet-972092482037.asia-south1.run.app
 
---
 
## Table of Contents
 
- [The Problem](#the-problem)
- [Demonstrated Incident](#demonstrated-incident)
- [Architecture](#architecture)
- [How the Fleet Works](#how-the-fleet-works)
- [Core Components](#core-components)
- [Evidence and Verification](#evidence-and-verification)
- [Google Cloud Architecture](#google-cloud-architecture)
- [Persistent Investigation State](#persistent-investigation-state)
- [API](#api)
- [Repository Structure](#repository-structure)
- [Testing](#testing)
- [Security](#security)
- [Design Principles](#design-principles)
- [Why This Matters](#why-this-matters)
- [Future Production Extensions](#future-production-extensions)
- [Project Status](#project-status)
---
 
## The Problem
 
Operational incidents often require several different kinds of investigation at once. A latency regression, for example, might need:
 
- deployment and source inspection
- runtime reproduction
- database analysis
- cache analysis
- evidence comparison
Conventionally, one engineer has to manually coordinate all of this — inspecting code, running diagnostics, and correlating results by hand.
 
**Investigation Fleet turns that workflow into an autonomous investigation process:**
 
```
Incident
   │
   ▼
Fleet Commander
   │
   ├──► Code Investigator
   ├──► Runtime Investigator
   └──► Cache Investigator
          │
          ▼
   Evidence Verifier
          │
          ▼
      Root Cause
```
 
---
 
## Demonstrated Incident
 
**Checkout API Latency Regression**
 
The benchmark incident is a checkout API whose p95 latency increased sharply after the latest deployment:
 
```
180 ms → 1700 ms
```
 
---
 
## Architecture
 
Investigation Fleet is deliberately built as a **fleet of specialized agents** rather than one unrestricted general-purpose agent:
 
```
                    ┌───────────────────┐
                    │  Fleet Commander  │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │    Code     │ │   Runtime   │ │    Cache    │
       │ Investigator│ │ Investigator│ │ Investigator│
       └──────┬──────┘ └──────┬──────┘ └─────────────┘
              │               │
              ▼               ▼
             Git       Python benchmark
              │               │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │   Evidence    │
              │   Verifier    │
              └───────┬───────┘
                      ▼
                 Firestore
```
 
---
 
## How the Fleet Works
 
A typical investigation follows this sequence:
 
1. Incident received
2. Fleet Commander evaluates the incident
3. Commander delegates work to a specialist
4. Specialist executes a scoped diagnostic tool
5. Tool produces evidence
6. Evidence is persisted
7. Additional investigation is performed
8. Independent evidence is collected
9. Evidence Verifier evaluates the evidence
10. Root cause is verified
---
 
## Core Components
 
### Fleet Commander
The orchestration layer. Coordinates the investigation and delegates work to specialist agents.
 
### Code Investigator
Focuses on source and deployment changes.
 
- **Diagnostic:** `inspect_deployment_diff`
- **Finding in the demo incident:** discovers a change from a batched query to a per-item query.
### Runtime Investigator
Focuses on reproducing observed behavior.
 
- **Diagnostic:** `reproduce_performance`
- **Finding in the demo incident:** observes `1 query → 47 queries`, matching the measured latency regression.
### Cache Investigator
A specialized agent for incidents where cache behavior is suspected. Part of the fleet architecture, though not required for the demonstrated incident.
 
---
 
## Evidence and Verification
 
The system enforces a strict separation between observing, evidencing, and concluding:
 
```
Observation → Evidence → Verification → Conclusion
```
 
---
 
## Google Cloud Architecture
 
![Investigation Fleet Architecture](docs/images/architecture.png)
 
The system separates orchestration, specialist investigation, diagnostic tool execution, evidence verification, and persistent state into distinct components. The hosted service runs on Google Cloud.
 
```
                         Operator
                            │
                            ▼
                  ┌──────────────────────┐
                  │      Cloud Run       │
                  │       FastAPI        │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │   Fleet Commander    │
                  │      Google ADK      │
                  └──────────┬───────────┘
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
        Code Investigator  Runtime       Cache
               │          Investigator  Investigator
               ▼             │
              Git       Python benchmark
               │             │
               └──────┬──────┘
                      ▼
             ┌────────────────────┐
             │ Evidence Verifier  │
             └─────────┬──────────┘
                       ▼
                 ┌───────────┐
                 │ Firestore │
                 └───────────┘
 
Secret Manager
      │
      └──► Gemini API credential
```
 
---
 
## Persistent Investigation State
 
Investigation state is persisted separately from the application process. A record includes:
 
```
investigation_id
case_id
status
mode
events
root_cause
confidence
root_cause_verified
updated_at
```
 
**Demo mode** runs with `mode = demo`.
 
---
 
## API
 
### Health check
 
```http
GET /health
```
 
---
 
## Repository Structure
 
```
autonomous-investigation-engine/
│
├── benchmark/
│   ├── cases/
│   │   └── api_latency_regression.json
│   └── demo/
│       └── api_latency_fleet_trace.json
│
├── docs/
│   ├── architecture.md
│   └── architecture.mmd
│
├── investigator/
│   ├── api/
│   │   ├── app.py
│   │   └── static/
│   │       └── index.html
│   ├── domain/
│   ├── evaluation/
│   ├── execution/
│   ├── fleet/
│   ├── investigation/
│   ├── planning/
│   ├── reasoning/
│   └── tools/
│
├── scripts/
├── tests/
│
├── Dockerfile
├── Procfile
├── requirements.txt
└── README.md
```
 
---
 
## Testing
 
The test suite covers:
 
- agent registry
- fleet orchestration
- scoped diagnostic tools
- Git investigation
- runtime investigation
- benchmark evaluation
- API behavior
- Firestore state
- reasoning schemas
- investigation workflow
Run:
 
```powershell
pytest
```
 
---
 
## Security
 
Sensitive credentials are never stored in source code. The Gemini API credential is stored in **Google Secret Manager**.
 
---
 
## Design Principles
 
| Principle | Description |
|---|---|
| **Specialized Agents** | Use specialist agents instead of one unrestricted agent. |
| **Scoped Tools** | Give each specialist only the tools required for its role. |
| **Evidence First** | Prefer concrete diagnostic observations over unsupported assumptions. |
| **Independent Verification** | Separate evidence collection from final verification. |
| **Persistent State** | Store investigation state independently from the process executing the investigation. |
| **Reproducibility** | Benchmark and replay capabilities make investigations reproducible. |
 
---
 
## Why This Matters
 
Investigation Fleet moves incident response from a manual chain:
 
```
Human → manually inspect everything → manually coordinate tools
      → manually correlate evidence → manually decide root cause
```
 
...to an autonomous, evidence-verified pipeline.
 
---
 
## Future Production Extensions
 
The current implementation is optimized for the hackathon demonstration. A production deployment could extend the system with:
 
- durable asynchronous job execution (Cloud Tasks or Pub/Sub)
- stronger authentication and authorization
- richer observability
- additional incident types
- more diagnostic integrations
- policy enforcement
- human approval gates for sensitive actions
---
 
## Demo
 
```
Open hosted application → Start investigation → Fleet Commander
   → Code Investigator → Git evidence → Runtime Investigator
   → Runtime evidence → Evidence Verifier → ROOT CAUSE VERIFIED
```
 
---
 
## Project Status
 
| Component | Status |
|---|---|
| Core investigation engine | ✅ |
| Multi-agent fleet | ✅ |
| Google ADK | ✅ |
| Specialist agents | ✅ |
| Scoped diagnostic tools | ✅ |
| Benchmark suite | ✅ |
| Evidence verification | ✅ |
| Firestore persistence | ✅ |
| Cloud Run deployment | ✅ |
| Secret Manager | ✅ |
| Hosted web console | ✅ |
| Reproducible demo mode | ✅ |
| Automated tests | ✅ |
