#  ResQNet

**Disaster communication and resource management platform with role-based emergency dispatch.**

ResQNet helps coordinate emergency response by routing incoming incident reports to the right responders, tracking resource availability in real time, and automatically dispatching calls to on-duty personnel — all from a single command dashboard.

> Built as a college project, designed like a production system.

<!-- 📸 PLACEHOLDER: Replace with a hero screenshot or GIF of the Admin Command Center dashboard -->
![ResQNet Dashboard](docs/screenshots/dashboard-hero.png)

---

##  Key Features

- **Voice-to-incident pipeline** — callers report emergencies by voice; audio is transcribed via **OpenAI Whisper** and converted into a structured incident automatically
- **Automated responder dispatch** — once an incident is created, **Twilio** places live calls to on-duty responders for the required resource type and records their response (confirmed / unavailable / no answer)
- **Role-based dashboards** — Admins get a full command center; Police, Ambulance, Fire & Rescue, and Doctor responders each see only the incidents and resources relevant to their unit
- **Live resource tracking** — see available vs. deployed resources by type, in real time, with the ability to dispatch additional units to an already-active incident
- **Auto-generated incident reports** — closing an incident triggers a background job that compiles a PDF report of the response timeline
- **Supabase Auth + Postgres** — secure authentication with row-level security and an auto-provisioned profile/role on signup

<!-- 📸 PLACEHOLDER: Replace with a screenshot of the responder-specific dashboard (e.g. Ambulance Hub) -->
![Responder Dashboard](docs/screenshots/responder-dashboard.png)

---

#  ResQNet

**Disaster communication and resource management platform with role-based emergency dispatch.**

ResQNet helps coordinate emergency response by routing incoming incident reports to the right responders, tracking resource availability in real time, and automatically dispatching calls to on-duty personnel — all from a single command dashboard.


<!-- 📸 PLACEHOLDER: Replace with a hero screenshot or GIF of the Admin Command Center dashboard -->
![ResQNet Dashboard](docs/screenshots/dashboard-hero.png)

---

##  Key Features

- **Voice-to-incident pipeline** — callers report emergencies by voice; audio is transcribed via **OpenAI Whisper** and converted into a structured incident automatically
- **Automated responder dispatch** — once an incident is created, **Twilio** places live calls to on-duty responders for the required resource type and records their response (confirmed / unavailable / no answer)
- **Role-based dashboards** — Admins get a full command center; Police, Ambulance, Fire & Rescue, and Doctor responders each see only the incidents and resources relevant to their unit
- **Live resource tracking** — see available vs. deployed resources by type, in real time, with the ability to dispatch additional units to an already-active incident
- **Auto-generated incident reports** — closing an incident triggers a background job that compiles a PDF report of the response timeline
- **Supabase Auth + Postgres** — secure authentication with row-level security and an auto-provisioned profile/role on signup

<!-- 📸 PLACEHOLDER: Replace with a screenshot of the responder-specific dashboard (e.g. Ambulance Hub) -->
![Responder Dashboard](docs/screenshots/responder-dashboard.png)

---

##  Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Caller    │─────▶│  Whisper STT │─────▶│  Flask Backend   │
│  (voice)    │      │ (transcribe) │      │  /api/speech     │
└─────────────┘      └──────────────┘      └────────┬─────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │   Incident Created     │
                                          │  (priority + location) │
                                          └───────────┬─────────────┘
                                                      │
                                ┌─────────────────────┼─────────────────────┐
                                ▼                                           ▼
                      ┌──────────────────┐                       ┌──────────────────┐
                      │ Resource Engine    │                       │  Twilio Dispatch   │
                      │ (rule-based match) │──────────────────────▶│  (live phone call) │
                      └──────────────────┘                       └─────────┬──────────┘
                                                                            │
                                                                            ▼
                                                                  ┌──────────────────┐
                                                                  │  Webhook updates   │
                                                                  │  call_logs in DB   │
                                                                  └──────────────────┘
                                                                            │
                                                                            ▼
                                                          ┌──────────────────────────────┐
                                                          │   Role-filtered Dashboards     │
                                                          │  (Admin / Police / Ambulance /  │
                                                          │   Fire & Rescue / Doctor)        │
                                                          └──────────────────────────────┘
```

---

##  Components

In the interest of being upfront about the engineering here:

| Component | How it works |
|---|---|
| **Speech-to-text** | OpenAI **Whisper** transcribes the caller's voice report into text — this is the genuine AI/ML component |
| **Priority classification** | Rule-based keyword matching against a curated severity dictionary (`Critical` / `High` / `Medium` / `Low`) — fast, deterministic, and explainable, which matters a lot when triaging emergencies |
| **Resource allocation** | Rule-based lookup table mapping incident priority → required responder types and counts |
| **Dispatch & call tracking** | **Twilio** Programmable Voice places calls and webhooks record responder replies in real time |
| **Report generation** | Backend aggregation of incident timeline data, rendered to PDF |

We chose deterministic logic over an LLM for priority and resource decisions on purpose — in an emergency-response context, predictable, auditable behavior is more valuable than generative flexibility. Whisper is used where AI provides genuine leverage: turning unstructured speech into usable data.

---

## 🛠️ Tech Stack

**Frontend**
- React (Vite)
- React Router
- Recharts (data visualization)
- Axios

**Backend**
- Flask (Python)
- Supabase (Postgres + Auth + Row-Level Security)
- Twilio (Programmable Voice + Webhooks)
- OpenAI Whisper (speech-to-text)

**Infra**
- Supabase-hosted Postgres database
- Threaded background jobs for delayed report generation

---

## 👥 Role-Based Access

| Role | Dashboard shows |
|---|---|
| **Admin** | Full platform — all incidents, all resources, system-wide analytics, reports |
| **Police** | Only incidents with a police unit assigned, police resource availability |
| **Ambulance** | Only incidents with an ambulance assigned, ambulance fleet status |
| **Fire & Rescue** | Only incidents with a fire truck assigned, fire unit availability |
| **Doctor** | Only incidents with a doctor assigned, medical team status |

Role is selected at sign-up and stored in a `profiles` table linked to Supabase Auth via a database trigger. Every API route validates the requester's role server-side — responders cannot query incidents outside their assigned resource type, even via direct API calls.

<!-- 📸 PLACEHOLDER: Replace with a screenshot of the role-selection signup screen -->
![Role-based Signup](docs/screenshots/signup-roles.png)

---

## 📂 Project Structure

```
resqnet/
├── backend/
│   ├── agents/              # Priority, resource, report, and dispatch logic
│   ├── routes/               # Flask blueprints (incidents, resources, dashboard, reports, auth)
│   ├── services/              # Supabase queries, business logic
│   ├── middleware/            # Auth + role verification
│   └── app.py
├── frontend/
│   └── src/
│       ├── pages/             # Dashboard, IncidentView, Signup, Login
│       ├── components/         # AddResourcesModal, Navbar, PriorityBadge
│       ├── context/            # AuthContext (role-aware session)
│       └── api/                 # Axios client + endpoint wrappers
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Supabase project
- A Twilio account with a phone number
- OpenAI API key (Whisper)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # add Supabase, Twilio, OpenAI keys
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env          # add VITE_API_BASE_URL, Supabase keys
npm run dev
```

### Database Setup

Run the SQL migration in `backend/migrations/` via the Supabase SQL Editor to create the `profiles`, `incidents`, `resources`, `incident_resources`, `call_logs`, and `reports` tables, along with the auto-profile-creation trigger.

---

## 🗺️ Roadmap

- [ ] Live map view of active incidents and resource locations
- [ ] SMS fallback for responders who miss a call
- [ ] Test suite (pytest + Vitest)
- [ ] Docker Compose for one-command local setup
- [ ] CI pipeline for automated checks on PRs

---



<p align="center">Built with care for faster, smarter emergency response.</p>
---
