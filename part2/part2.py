import os
from pathlib import Path

from sqlalchemy import create_engine, text

DB_DIR = Path(__file__).resolve().parent.parent / "db"
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/conference_db")
engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1))

TABLES = ["app_user", "author", "author_research_area", "reviewer", "reviewer_expertise",
          "conference", "conference_host", "conference_reviewer", "track",
          "conference_session", "paper", "paper_keyword", "paper_author",
          "paper_version", "review"]


def heading(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_table(result):
    columns = list(result.keys())
    rows = [["NULL" if v is None else str(v) for v in row] for row in result]
    widths = [max([len(c)] + [len(r[i]) for r in rows]) for i, c in enumerate(columns)]
    print(" | ".join(c.ljust(w) for c, w in zip(columns, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"({len(rows)} rows)")


def query(conn, sql, params=None, label=None):
    if label:
        print(f"\n{label}:")
    print(sql.strip())
    if params:
        print("Parameters:", params)
    print_table(conn.execute(text(sql), params or {}))


def execute(conn, sql, params=None):
    print()
    print(sql.strip())
    if params:
        print("Parameters:", params)
    print("Rows affected:", conn.execute(text(sql), params or {}).rowcount)


def task_1():
    heading("TASK 1")
    sql = (DB_DIR / "schema.sql").read_text(encoding="utf-8")
    print(sql)
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)


def task_2():
    heading("TASK 2")
    sql = (DB_DIR / "seed.sql").read_text(encoding="utf-8")
    print(sql)
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
        query(conn, "\nUNION ALL\n".join(
            f"SELECT '{t}' AS table_name, COUNT(*) AS row_count FROM {t}" for t in TABLES))


def task_3_1():
    heading("TASK 3.1")
    select = "SELECT user_id, given_name, surname, email, phone_number FROM app_user WHERE email = :email"
    email = {"email": "arman.armanov@example.com"}
    with engine.connect() as conn:
        trans = conn.begin()
        query(conn, select, email, "Before")
        execute(conn, "UPDATE app_user SET phone_number = :phone WHERE email = :email",
                {"email": "arman.armanov@example.com", "phone": "+77773414141"})
        query(conn, select, email, "After")
        trans.rollback()
        print("\nRolled back.")


def task_3_2():
    heading("TASK 3.2")
    select = "SELECT conference_id, acronym, city, review_deadline FROM conference ORDER BY conference_id"
    with engine.connect() as conn:
        trans = conn.begin()
        query(conn, select, label="Before")
        execute(conn, """
UPDATE conference
SET review_deadline = review_deadline + CASE WHEN city = :city THEN 7 ELSE 3 END""",
                {"city": "Astana"})
        query(conn, select, label="After")
        trans.rollback()
        print("\nRolled back.")


def task_4_1():
    heading("TASK 4.1")
    email = {"email": "amina.aminova@example.com"}
    target = """
SELECT p.paper_id, p.title, p.status
FROM paper p
JOIN paper_author pa ON pa.paper_id = p.paper_id AND pa.is_corresponding
JOIN app_user u ON u.user_id = pa.author_id
WHERE p.status = 'withdrawn' AND u.email = :email"""
    counts = """
SELECT (SELECT COUNT(*) FROM paper) AS papers,
       (SELECT COUNT(*) FROM paper_author) AS paper_authors,
       (SELECT COUNT(*) FROM paper_keyword) AS keywords,
       (SELECT COUNT(*) FROM paper_version) AS versions,
       (SELECT COUNT(*) FROM review) AS reviews,
       (SELECT COUNT(*) FROM app_user) AS users,
       (SELECT COUNT(*) FROM track) AS tracks,
       (SELECT COUNT(*) FROM conference) AS conferences"""
    with engine.connect() as conn:
        trans = conn.begin()
        query(conn, target, email, "Before")
        query(conn, counts)
        execute(conn, """
DELETE FROM paper
WHERE status = 'withdrawn'
  AND paper_id IN (SELECT pa.paper_id
                   FROM paper_author pa
                   JOIN app_user u ON u.user_id = pa.author_id
                   WHERE pa.is_corresponding AND u.email = :email)""", email)
        query(conn, target, email, "After")
        query(conn, counts)
        trans.rollback()
        print("\nRolled back.")


def task_4_2():
    heading("TASK 4.2")
    select = """
SELECT s.session_id, s.title, c.city,
       (SELECT COUNT(*) FROM paper p WHERE p.session_id = s.session_id) AS papers
FROM conference_session s
JOIN conference c ON c.conference_id = s.conference_id
ORDER BY s.session_id"""
    with engine.connect() as conn:
        trans = conn.begin()
        query(conn, select, label="Before")
        execute(conn, """
DELETE FROM conference_session s
USING conference c
WHERE c.conference_id = s.conference_id
  AND c.city = :city
  AND NOT EXISTS (SELECT 1 FROM paper p WHERE p.session_id = s.session_id)""",
                {"city": "Astana"})
        query(conn, select, label="After")
        trans.rollback()
        print("\nRolled back.")


def task_5():
    with engine.connect() as conn:
        heading("TASK 5.1")
        query(conn, """
SELECT p.paper_id, p.title,
       u.given_name || ' ' || u.surname AS corresponding_author, u.email,
       t.name AS track_name, c.conference_id, c.acronym
FROM paper p
JOIN track t ON t.track_id = p.track_id
JOIN conference c ON c.conference_id = t.conference_id
JOIN paper_author pa ON pa.paper_id = p.paper_id AND pa.is_corresponding
JOIN app_user u ON u.user_id = pa.author_id
WHERE p.status = 'accepted'
ORDER BY p.paper_id""")

        heading("TASK 5.2")
        query(conn, "SELECT paper_id, title FROM paper WHERE abstract ILIKE :pattern ORDER BY paper_id",
              {"pattern": "%machine learning%"})

        heading("TASK 5.3")
        query(conn, """
SELECT version_no, file_location, uploaded_at
FROM paper_version
WHERE paper_id = :paper_id
ORDER BY version_no DESC""", {"paper_id": 2})

        heading("TASK 5.4")
        query(conn, """
SELECT u.user_id, u.given_name || ' ' || u.surname AS full_name, u.email
FROM conference_reviewer cr
JOIN reviewer r ON r.reviewer_id = cr.reviewer_id
JOIN app_user u ON u.user_id = r.reviewer_id
WHERE cr.conference_id = :conference_id
  AND r.years_experience >= :years
  AND EXISTS (SELECT 1 FROM reviewer_expertise e
              WHERE e.reviewer_id = r.reviewer_id AND e.area_label = :area)
ORDER BY u.user_id""", {"conference_id": 1, "area": "Databases", "years": 3})


def task_6():
    with engine.connect() as conn:
        heading("TASK 6.1")
        query(conn, """
SELECT t.track_id, t.name, t.conference_id,
       COUNT(DISTINCT p.paper_id) AS papers,
       COUNT(DISTINCT pa.author_id) AS authors
FROM track t
LEFT JOIN paper p ON p.track_id = t.track_id
LEFT JOIN paper_author pa ON pa.paper_id = p.paper_id
GROUP BY t.track_id, t.name, t.conference_id
ORDER BY t.track_id""")

        heading("TASK 6.2")
        query(conn, """
SELECT r.reviewer_id, u.given_name || ' ' || u.surname AS full_name,
       COUNT(rv.review_id) AS reviews,
       AVG(rv.overall_score) AS average_score
FROM reviewer r
JOIN app_user u ON u.user_id = r.reviewer_id
LEFT JOIN review rv ON rv.reviewer_id = r.reviewer_id
GROUP BY r.reviewer_id, u.given_name, u.surname
ORDER BY r.reviewer_id""")

        heading("TASK 6.3")
        query(conn, """
SELECT c.conference_id, c.acronym,
       (SELECT COUNT(*) FROM paper p JOIN track t ON t.track_id = p.track_id
        WHERE t.conference_id = c.conference_id) AS papers,
       (SELECT COUNT(*) FROM paper p JOIN track t ON t.track_id = p.track_id
        WHERE t.conference_id = c.conference_id AND p.status = 'accepted') AS accepted_papers,
       (SELECT AVG(rv.overall_score) FROM review rv
        JOIN paper p ON p.paper_id = rv.paper_id
        JOIN track t ON t.track_id = p.track_id
        WHERE t.conference_id = c.conference_id) AS average_score
FROM conference c
ORDER BY c.conference_id""")

        heading("TASK 6.4")
        query(conn, """
WITH counts AS (
    SELECT r.reviewer_id, COUNT(rv.review_id) AS reviews
    FROM reviewer r
    LEFT JOIN review rv ON rv.reviewer_id = r.reviewer_id
    GROUP BY r.reviewer_id
)
SELECT c.reviewer_id, u.given_name || ' ' || u.surname AS full_name, c.reviews,
       (SELECT AVG(reviews) FROM counts) AS average_reviews
FROM counts c
JOIN app_user u ON u.user_id = c.reviewer_id
WHERE c.reviews > (SELECT AVG(reviews) FROM counts)
ORDER BY c.reviewer_id""")


def task_7():
    with engine.connect() as conn:
        heading("TASK 7")
        query(conn, """
SELECT c.conference_id, c.acronym,
       COUNT(p.paper_id) FILTER (WHERE p.status = 'accepted') AS accepted,
       COUNT(p.paper_id) FILTER (WHERE p.status = 'rejected') AS rejected,
       ROUND(100.0 * COUNT(p.paper_id) FILTER (WHERE p.status = 'accepted')
             / NULLIF(COUNT(p.paper_id) FILTER (WHERE p.status IN ('accepted', 'rejected')), 0),
             2) AS acceptance_rate
FROM conference c
LEFT JOIN track t ON t.conference_id = c.conference_id
LEFT JOIN paper p ON p.track_id = t.track_id
GROUP BY c.conference_id, c.acronym
ORDER BY c.conference_id""")


def task_8():
    heading("TASK 8")
    view = """
CREATE OR REPLACE VIEW accepted_paper_schedule AS
SELECT p.paper_id, p.title,
       c.conference_id, c.acronym,
       t.name AS track_name,
       s.session_id, s.title AS session_title, s.session_date,
       s.start_time, s.end_time, s.room_label,
       ch.given_name || ' ' || ch.surname AS chair_name,
       ca.given_name || ' ' || ca.surname AS corresponding_author,
       ca.email AS corresponding_email
FROM paper p
JOIN track t ON t.track_id = p.track_id
JOIN conference_session s ON s.session_id = p.session_id
JOIN conference c ON c.conference_id = s.conference_id
JOIN app_user ch ON ch.user_id = s.chair_id
JOIN paper_author pa ON pa.paper_id = p.paper_id AND pa.is_corresponding
JOIN app_user ca ON ca.user_id = pa.author_id"""
    with engine.begin() as conn:
        print(view.strip())
        conn.execute(text(view))
        print()
        query(conn, """
SELECT * FROM accepted_paper_schedule
ORDER BY conference_id, session_date, start_time, session_id, paper_id""")


task_1()
task_2()
task_3_1()
task_3_2()
task_4_1()
task_4_2()
task_5()
task_6()
task_7()
task_8()
