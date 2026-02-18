# Roll & Ride API

This repository contains the **Flask + Postgres** back end for **Roll & Ride** (JWT auth + saved directions).

For the full product overview, UI, and usage details, see the front-end repository:
https://github.com/wolnoid/roll-and-ride-front-end

### Deployed API
- https://roll-and-ride-7a172a20dd22.herokuapp.com/

---

## ✅ What this API provides
- **JWT authentication**
  - `POST /auth/sign-up`
  - `POST /auth/sign-in`
- **Saved directions (JWT required)**
  - `GET /saved-directions`
  - `POST /saved-directions`
  - `PUT /saved-directions/:id`
  - `DELETE /saved-directions/:id`

> Note: The front end stores “saved directions” as the **raw URL querystring** (e.g. `?v=1&o=...&d=...&mode=...&when=now&via=...`) so opening a bookmark can rerun routing with up-to-date times.

---

## 💻 Run locally

### 1) Setup environment
1. Fork and clone this repository.
2. Install dependencies:
   ```bash
   pipenv install
   ```
3. Create a `.env` file in the project root. Minimum required:
   ```bash
   JWT_SECRET=your_secret_here
   ```

### 2) Configure Postgres
You can use **either** a single `DATABASE_URL` **or** discrete Postgres variables.

**Option A: DATABASE_URL**
```bash
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

**Option B: discrete Postgres env vars**
```bash
POSTGRES_HOST=localhost
POSTGRES_DATABASE=roll_and_ride
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your_password
```

Create tables:
```bash
psql -f schema.sql
```

### 3) Start the server
```bash
pipenv run python app.py
```

---

## 🧩 Technologies used
- **Python 3**
- **Flask**
- **PostgreSQL** (psycopg2)
- **PyJWT** + **bcrypt**
- **Gunicorn** (deployment)
- **flask-cors** (CORS)

---

## 📌 CORS
CORS is configured to allow local dev origins (Vite) and the deployed Netlify domain. If you deploy to a different front-end domain, update the allowed origins in `app.py`.
