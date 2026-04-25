-- ============================================================
-- PhoneBook Extended Schema
-- Extends the base schema from Practice 7-8
-- ============================================================

-- Groups / Categories table
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name) VALUES
    ('Family'),
    ('Work'),
    ('Friend'),
    ('Other')
ON CONFLICT (name) DO NOTHING;

-- Contacts table (base from Practice 7, extended here)
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR(50)  UNIQUE NOT NULL,
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Multiple phones per contact
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_contacts_username  ON contacts (username);
CREATE INDEX IF NOT EXISTS idx_contacts_email     ON contacts (email);
CREATE INDEX IF NOT EXISTS idx_contacts_group_id  ON contacts (group_id);
CREATE INDEX IF NOT EXISTS idx_phones_contact_id  ON phones   (contact_id);
CREATE INDEX IF NOT EXISTS idx_phones_phone       ON phones   (phone);
