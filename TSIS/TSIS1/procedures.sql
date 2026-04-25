-- ============================================================
-- PhoneBook Stored Procedures & Functions (TSIS1 additions)
-- Do NOT duplicate procedures already defined in Practice 8.
-- ============================================================

-- ------------------------------------------------------------
-- 1. add_phone
--    Adds a new phone number (with type) to an existing contact.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM   contacts
    WHERE  username = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Validate type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home, work or mobile.', p_type;
    END IF;

    -- Avoid exact duplicates for the same contact
    IF EXISTS (
        SELECT 1 FROM phones
        WHERE  contact_id = v_contact_id AND phone = p_phone
    ) THEN
        RAISE NOTICE 'Phone % already exists for contact %.', p_phone, p_contact_name;
        RETURN;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact %.', p_phone, p_type, p_contact_name;
END;
$$;


-- ------------------------------------------------------------
-- 2. move_to_group
--    Moves a contact to a group; creates the group if missing.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM   contacts
    WHERE  username = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Upsert group
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM   groups
    WHERE  name = p_group_name;

    -- Move contact
    UPDATE contacts
    SET    group_id = v_group_id
    WHERE  id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- ------------------------------------------------------------
-- 3. search_contacts  (extends the Practice-8 pattern search)
--    Matches username, email, and ALL phone numbers.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    username   VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,       -- comma-separated "number(type)" list
    created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id                                                   AS contact_id,
        c.username,
        c.email,
        c.birthday,
        g.name                                                 AS group_name,
        STRING_AGG(p.phone || '(' || COALESCE(p.type,'?') || ')', ', '
                   ORDER BY p.id)                             AS phones,
        c.created_at
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    LEFT   JOIN phones p ON p.contact_id = c.id
    WHERE
        c.username ILIKE '%' || p_query || '%'
        OR c.email  ILIKE '%' || p_query || '%'
        OR EXISTS (
            SELECT 1 FROM phones ph
            WHERE  ph.contact_id = c.id
              AND  ph.phone ILIKE '%' || p_query || '%'
        )
    GROUP  BY c.id, g.name
    ORDER  BY c.username;
END;
$$;


-- ------------------------------------------------------------
-- 4. get_contacts_page  (pagination helper used by console)
--    Returns one page of the full contact list.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit  INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0,
    p_sort   VARCHAR DEFAULT 'username'   -- 'username' | 'birthday' | 'created_at'
)
RETURNS TABLE (
    contact_id INTEGER,
    username   VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Dynamic sort via CASE to stay injection-safe
    RETURN QUERY
    SELECT
        c.id,
        c.username,
        c.email,
        c.birthday,
        g.name,
        STRING_AGG(p.phone || '(' || COALESCE(p.type,'?') || ')', ', '
                   ORDER BY p.id),
        c.created_at
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    LEFT   JOIN phones p ON p.contact_id = c.id
    GROUP  BY c.id, g.name
    ORDER  BY
        CASE WHEN p_sort = 'birthday'    THEN c.birthday::TEXT    END ASC NULLS LAST,
        CASE WHEN p_sort = 'created_at'  THEN c.created_at::TEXT  END ASC NULLS LAST,
        c.username ASC
    LIMIT  p_limit
    OFFSET p_offset;
END;
$$;
