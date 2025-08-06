
    CREATE TABLE IF NOT EXISTS public.call_log
    (
        log_id SERIAL PRIMARY KEY,
        rep_num BIGINT REFERENCES public.rep_identity(rep_num),
        date DATE NOT NULL,
        time TIME WITHOUT TIME ZONE NOT NULL,
        customer_num BIGINT NOT NULL,
        mins_on_phone SMALLINT NOT NULL,
        caller_location TEXT NOT NULL
    );
    