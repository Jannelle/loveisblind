
# Love Is Blind Fantasy League

A full-stack web application for managing **fantasy leagues based on the Netflix show *Love Is Blind***.

This project allows users to create leagues, draft contestants, track episode events, and view evolving leaderboards as the show unfolds. I built this project independently as a way to deepen my full‑stack engineering skills and explore how relational data models can power dynamic scoring systems.

---

# Overview

The application enables users to:

- Create and manage fantasy leagues
- Draft contestants onto teams
- Track scoring events across episodes
- View leaderboards and team performance
- Update scores as the season progresses

The system models the relationships between leagues, teams, contestants, and scoring events using a relational database.

---

# Architecture

The application follows a **modular Flask architecture** using the application factory pattern.

```
loveisblind/
│
├── run.py                 # Application entry point
├── config.py              # Configuration
├── requirements.txt
│
└── app/
    ├── __init__.py        # Flask app factory
    ├── extensions.py      # Database + extensions
    │
    ├── models/            # Data models
    │   └── league.py
    │
    ├── main/              # Application routes
    │   ├── routes.py
    │   ├── events.py
    │   └── template_globals.py
    │
    ├── templates/         # HTML templates
    └── static/            # JS / CSS / assets
```

---

# Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy
- Flask‑SocketIO

### Frontend
- HTML
- JavaScript
- Jinja templates

### Database
- Relational database via SQLAlchemy ORM

---

# Data Model

The application models several core entities:

### League
Represents a fantasy league.

### Owner
Represents a participant in the league.

### Team
Each owner drafts contestants onto a team.

### Cast Member
Contestants from the show.

### Activity / Event
Scoring events tied to episodes.

Example conceptual relationships:

```
League
 ├── Owners
 │     └── Teams
 │           └── Cast Members
 │
 └── Activities (episode events)
```

This relational structure allows scoring events to dynamically update league standings.

---

# System Design

The system is structured around event-driven updates when episode activities occur.

```
User Action / Episode Event
            │
            ▼
      Activity Recorded
            │
            ▼
      Score Calculation
            │
            ▼
     Database Update
            │
            ▼
      Leaderboard Update
            │
            ▼
     Real‑time UI Update (SocketIO)
```

This architecture allows multiple users to see scoring updates without needing to refresh the page.

---

# Key Features

## League Management
Users can create leagues and manage participants.

## Team Drafting
Owners draft contestants onto their teams.

## Episode Event Scoring
Events from each episode trigger score changes.

Examples:
- engagements
- breakups
- conflicts
- major show moments

## Leaderboard Tracking
Scores update as events are recorded, allowing league standings to evolve across episodes.

## Real-Time Updates
SocketIO support allows updates to propagate across clients.

---

# API Design (Conceptual)

While the current implementation is server‑rendered, the system naturally supports REST-style endpoints such as:

```
GET /leagues
GET /league/<id>
GET /teams
GET /scores
POST /activity
```

These endpoints would allow the frontend or other systems to query league data programmatically.

---

# Running the Project

Clone the repository:

```
git clone https://github.com/Jannelle/loveisblind.git
cd loveisblind
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the server:

```
python run.py
```

Open:

```
http://localhost:5000
```

---

# Learning Goals

This project was built to explore:

- Full‑stack web application design
- Flask application architecture
- Relational data modeling
- Event-driven updates
- Managing application state in multi-user systems

---

# Future Improvements

Possible enhancements include:

- Adding a formal REST API layer
- Improving draft UI
- Automated episode event ingestion
- Advanced analytics and statistics
- User authentication
- Cloud deployment

---

# Author

Jannelle Zapanta
