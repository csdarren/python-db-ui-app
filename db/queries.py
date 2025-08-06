# INSERT
INSERT_REP_PHONES = """
INSERT INTO rep_identity
(rep_num, rep_name)
VALUES
(%s, %s)
ON CONFLICT DO NOTHING
"""

INSERT_CALL_DATA = """
INSERT INTO call_log
(rep_num, date, time, customer_num, mins_on_phone, caller_location)
VALUES
(%s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

# UPDATE

# SELECT
