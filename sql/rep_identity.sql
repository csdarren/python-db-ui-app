
    CREATE TABLE IF NOT EXISTS public.rep_identity
    (
        rep_id SERIAL PRIMARY KEY,
        rep_num BIGINT UNIQUE NOT NULL,
        rep_name TEXT
    );
    