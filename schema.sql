-- Roll & Ride minimal schema (users + saved directions)
--
-- Usage:
--   createdb <your_db>
--   psql <your_db> -f schema.sql

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS saved_directions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  name TEXT NOT NULL,
  description TEXT,

  origin_label TEXT,
  destination_label TEXT,
  mode TEXT,

  -- The canonical bookmark (querystring), e.g. "?v=1&o=...&d=...&mode=...&when=now&hill=...&via=..."
  search TEXT NOT NULL,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS saved_directions_user_id_idx ON saved_directions(user_id);
