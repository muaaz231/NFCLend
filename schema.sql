-- NFCLend PostgreSQL schema
-- Reconstructed from the queries in face_server.py. Contains no data.
-- Create the database first:  createdb nfcproject
-- Then load it:               psql nfcproject -f schema.sql

CREATE TABLE users (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    email               TEXT,
    nfc_id              TEXT UNIQUE NOT NULL,      -- UID of the user's NFC card
    role                TEXT DEFAULT 'student',    -- 'student' or 'admin'
    password            TEXT,
    rented_item_uid     TEXT,                      -- nfc_tag of the item currently checked out
    face_encoding_date  TIMESTAMP,
    is_deleted          BOOLEAN DEFAULT FALSE      -- soft delete keeps rental history intact
);

CREATE TABLE equipment (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    category      TEXT,
    nfc_tag       TEXT UNIQUE NOT NULL,            -- UID of the NFC sticker on the item
    status        TEXT DEFAULT 'available',        -- 'available' or 'rented'
    avg_rating    NUMERIC,
    rating_count  INTEGER DEFAULT 0,
    is_deleted    BOOLEAN DEFAULT FALSE
);

CREATE TABLE transactions (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER REFERENCES users(id),
    equipment_id      INTEGER REFERENCES equipment(id),
    checkout_time     TIMESTAMP DEFAULT NOW(),
    return_time       TIMESTAMP,
    face_verified     BOOLEAN,
    rating            INTEGER,                     -- 1-10, given on return
    condition_report  TEXT
);

CREATE TABLE face_logs (
    id                   SERIAL PRIMARY KEY,
    user_id              INTEGER REFERENCES users(id),
    verification_result  BOOLEAN,
    match_confidence     NUMERIC,
    created_at           TIMESTAMP DEFAULT NOW()
);

-- The admin account is created directly in the database (it logs in with card + password, no face check):
-- INSERT INTO users (name, email, nfc_id, role, password) VALUES ('admin', 'admin@example.com', '<admin card uid>', 'admin', '<password>');
