import os

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/conference_db")
engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1))

app = Flask(__name__)
app.secret_key = "secret"


class CheckError(Exception):
    pass


def rows(conn, sql, **params):
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def run(conn, sql, **params):
    return conn.execute(text(sql), params)


def lines(value):
    return [line.strip() for line in value.splitlines() if line.strip()]


def options(conn, sql):
    return [(str(r["id"]), r["label"]) for r in rows(conn, sql)]


def check_self_review(conn, paper_id):
    if rows(conn, """
SELECT 1 FROM review r
JOIN paper_author pa ON pa.paper_id = r.paper_id AND pa.author_id = r.reviewer_id
WHERE r.paper_id = :paper_id""", paper_id=paper_id):
        raise CheckError("Self-review is not allowed.")


def check_session_assignment(conn, paper_id=None, session_id=None):
    if rows(conn, """
SELECT 1 FROM paper p
JOIN track t ON t.track_id = p.track_id
JOIN conference_session s ON s.session_id = p.session_id
WHERE (p.paper_id = :paper_id OR s.session_id = :session_id)
  AND (p.status <> 'accepted' OR t.conference_id <> s.conference_id)""",
            paper_id=paper_id, session_id=session_id):
        raise CheckError("Invalid session assignment.")



def user_fields(conn):
    return [
        ("given_name", "text", None),
        ("surname", "text", None),
        ("email", "text", None),
        ("affiliation", "text", None),
        ("country", "text", None),
        ("phone_number", "text", None),
        ("author", "checkbox", None),
        ("orcid", "text", None),
        ("research_areas", "textarea", None),
        ("reviewer", "checkbox", None),
        ("years_experience", "number", None),
        ("expertise", "textarea", None),
    ]


def load_user(conn, user_id):
    
    values = rows(conn, "SELECT * FROM app_user WHERE user_id = :id", id=user_id)[0]
    author = rows(conn, "SELECT orcid FROM author WHERE author_id = :id", id=user_id)
    reviewer = rows(conn, "SELECT years_experience FROM reviewer WHERE reviewer_id = :id", id=user_id)
    values["author"] = "on" if author else ""
    values["orcid"] = author[0]["orcid"] if author else ""
    values["research_areas"] = "\n".join(r["area_label"] for r in rows(
        conn, "SELECT area_label FROM author_research_area WHERE author_id = :id", id=user_id))
    values["reviewer"] = "on" if reviewer else ""
    values["years_experience"] = reviewer[0]["years_experience"] if reviewer else ""
    values["expertise"] = "\n".join(r["area_label"] for r in rows(
        conn, "SELECT area_label FROM reviewer_expertise WHERE reviewer_id = :id", id=user_id))
    return values


def save_user(conn, user_id, f):
    params = {k: f[k] for k in ["given_name", "surname", "email", "affiliation", "country", "phone_number"]}
    if user_id is None:
        user_id = run(conn, """
INSERT INTO app_user (given_name, surname, email, affiliation, country, phone_number)
VALUES (:given_name, :surname, :email, :affiliation, :country, :phone_number)
RETURNING user_id""", **params).scalar()
    else:
        run(conn, """
UPDATE app_user SET given_name = :given_name, surname = :surname, email = :email,
       affiliation = :affiliation, country = :country, phone_number = :phone_number
WHERE user_id = :id""", id=user_id, **params)

    if f.get("author"):
        run(conn, """
INSERT INTO author (author_id, orcid) VALUES (:id, :orcid)
ON CONFLICT (author_id) DO UPDATE SET orcid = EXCLUDED.orcid""", id=user_id, orcid=f["orcid"] or None)
        run(conn, "DELETE FROM author_research_area WHERE author_id = :id", id=user_id)
        for area in lines(f["research_areas"]):
            run(conn, "INSERT INTO author_research_area VALUES (:id, :area)", id=user_id, area=area)
    else:
        run(conn, "DELETE FROM author WHERE author_id = :id", id=user_id)

    if f.get("reviewer"):
        run(conn, """
INSERT INTO reviewer (reviewer_id, years_experience) VALUES (:id, :years)
ON CONFLICT (reviewer_id) DO UPDATE SET years_experience = EXCLUDED.years_experience""",
            id=user_id, years=f["years_experience"])
        run(conn, "DELETE FROM reviewer_expertise WHERE reviewer_id = :id", id=user_id)
        for area in lines(f["expertise"]):
            run(conn, "INSERT INTO reviewer_expertise VALUES (:id, :area)", id=user_id, area=area)
    else:
        run(conn, "DELETE FROM reviewer WHERE reviewer_id = :id", id=user_id)


def paper_fields(conn):
    return [
        ("track_id", "select", options(conn, "SELECT track_id AS id, name AS label FROM track ORDER BY 1")),
        ("title", "text", None),
        ("abstract", "textarea", None),
        ("submission_date", "date", None),
        ("status", "select", [(s, s) for s in
                              ["submitted", "under review", "accepted", "rejected", "withdrawn"]]),
        ("session_id", "select", [("", "")] + options(
            conn, "SELECT session_id AS id, title AS label FROM conference_session ORDER BY 1")),
        ("authors (author_id, position, yes/no)", "textarea", None),
        ("keywords", "textarea", None),
        ("versions (version_no, file_location, uploaded_at)", "textarea", None),
    ]


AUTHORS = "authors (author_id, position, yes/no)"
VERSIONS = "versions (version_no, file_location, uploaded_at)"


def load_paper(conn, paper_id):
    values = rows(conn, "SELECT * FROM paper WHERE paper_id = :id", id=paper_id)[0]
    values[AUTHORS] = "\n".join(f"{r['author_id']}, {r['author_position']}, {r['corresponding']}" for r in rows(conn, """
SELECT author_id, author_position, CASE WHEN is_corresponding THEN 'yes' ELSE 'no' END AS corresponding
FROM paper_author WHERE paper_id = :id ORDER BY author_position""", id=paper_id))
    values["keywords"] = "\n".join(r["keyword"] for r in rows(
        conn, "SELECT keyword FROM paper_keyword WHERE paper_id = :id", id=paper_id))
    values[VERSIONS] = "\n".join(f"{r['version_no']}, {r['file_location']}, {r['uploaded_at']}" for r in rows(
        conn, "SELECT * FROM paper_version WHERE paper_id = :id ORDER BY version_no", id=paper_id))
    return values


def save_paper(conn, paper_id, f):
    params = dict(track_id=f["track_id"], title=f["title"], abstract=f["abstract"],
                  submission_date=f["submission_date"], status=f["status"],
                  session_id=f["session_id"] or None)
    if paper_id is None:
        paper_id = run(conn, """
INSERT INTO paper (track_id, title, abstract, submission_date, status, session_id)
VALUES (:track_id, :title, :abstract, :submission_date, :status, :session_id)
RETURNING paper_id""", **params).scalar()
    else:
        run(conn, """
UPDATE paper SET track_id = :track_id, title = :title, abstract = :abstract,
       submission_date = :submission_date, status = :status, session_id = :session_id
WHERE paper_id = :id""", id=paper_id, **params)

    run(conn, "DELETE FROM paper_author WHERE paper_id = :id", id=paper_id)
    for line in lines(f[AUTHORS]):
        author_id, position, corresponding = [p.strip() for p in line.split(",")]
        run(conn, "INSERT INTO paper_author VALUES (:id, :author_id, :position, :corresponding)",
            id=paper_id, author_id=author_id, position=position, corresponding=corresponding == "yes")

    run(conn, "DELETE FROM paper_keyword WHERE paper_id = :id", id=paper_id)
    for keyword in lines(f["keywords"]):
        run(conn, "INSERT INTO paper_keyword VALUES (:id, :keyword)", id=paper_id, keyword=keyword)

    run(conn, "DELETE FROM paper_version WHERE paper_id = :id", id=paper_id)
    for line in lines(f[VERSIONS]):
        version_no, file_location, uploaded_at = [p.strip() for p in line.split(",")]
        run(conn, """
INSERT INTO paper_version (paper_id, version_no, file_location, uploaded_at)
VALUES (:id, :version_no, :file_location, :uploaded_at)""",
            id=paper_id, version_no=version_no, file_location=file_location, uploaded_at=uploaded_at)

    check_self_review(conn, paper_id)
    check_session_assignment(conn, paper_id=paper_id)


REVIEWERS = """
SELECT r.reviewer_id AS id, u.given_name || ' ' || u.surname AS label
FROM reviewer r JOIN app_user u ON u.user_id = r.reviewer_id ORDER BY 1"""


def review_fields(conn):
    return [
        ("paper_id", "select", options(conn, "SELECT paper_id AS id, title AS label FROM paper ORDER BY 1")),
        ("reviewer_id", "select", options(conn, REVIEWERS)),
        ("overall_score", "number", None),
        ("recommendation", "select", [("accept", "accept"), ("reject", "reject")]),
        ("comments_for_authors", "textarea", None),
        ("confidential_comments", "textarea", None),
        ("review_submission_date", "date", None),
    ]


def load_review(conn, review_id):
    return rows(conn, "SELECT * FROM review WHERE review_id = :id", id=review_id)[0]


def save_review(conn, review_id, f):
    params = dict(paper_id=f["paper_id"], reviewer_id=f["reviewer_id"],
                  overall_score=f["overall_score"], recommendation=f["recommendation"],
                  comments_for_authors=f["comments_for_authors"],
                  confidential_comments=f["confidential_comments"] or None,
                  review_submission_date=f["review_submission_date"])
    if review_id is None:
        run(conn, """
INSERT INTO review (paper_id, reviewer_id, overall_score, recommendation,
                    comments_for_authors, confidential_comments, review_submission_date)
VALUES (:paper_id, :reviewer_id, :overall_score, :recommendation,
        :comments_for_authors, :confidential_comments, :review_submission_date)""", **params)
    else:
        run(conn, """
UPDATE review SET paper_id = :paper_id, reviewer_id = :reviewer_id,
       overall_score = :overall_score, recommendation = :recommendation,
       comments_for_authors = :comments_for_authors,
       confidential_comments = :confidential_comments,
       review_submission_date = :review_submission_date
WHERE review_id = :id""", id=review_id, **params)
    check_self_review(conn, f["paper_id"])


def session_fields(conn):
    return [
        ("conference_id", "select", options(
            conn, "SELECT conference_id AS id, acronym AS label FROM conference ORDER BY 1")),
        ("title", "text", None),
        ("session_date", "date", None),
        ("start_time", "time", None),
        ("end_time", "time", None),
        ("room_label", "text", None),
        ("chair_id", "select", options(conn, REVIEWERS)),
    ]


def load_session(conn, session_id):
    return rows(conn, "SELECT * FROM conference_session WHERE session_id = :id", id=session_id)[0]


def save_session(conn, session_id, f):
    params = {k: f[k] for k in ["conference_id", "title", "session_date", "start_time",
                                "end_time", "room_label", "chair_id"]}
    if session_id is None:
        run(conn, """
INSERT INTO conference_session (conference_id, title, session_date, start_time, end_time,
                                room_label, chair_id)
VALUES (:conference_id, :title, :session_date, :start_time, :end_time, :room_label, :chair_id)""",
            **params)
    else:
        run(conn, """
UPDATE conference_session SET conference_id = :conference_id, title = :title,
       session_date = :session_date, start_time = :start_time, end_time = :end_time,
       room_label = :room_label, chair_id = :chair_id
WHERE session_id = :id""", id=session_id, **params)
        check_session_assignment(conn, session_id=session_id)


ENTITIES = {
    "users": dict(key="user_id", table="app_user", fields=user_fields, load=load_user, save=save_user),
    "papers": dict(key="paper_id", table="paper", fields=paper_fields, load=load_paper, save=save_paper),
    "reviews": dict(key="review_id", table="review", fields=review_fields, load=load_review,
                    save=save_review),
    "sessions": dict(key="session_id", table="conference_session", fields=session_fields,
                     load=load_session, save=save_session),
}


def error_text(e):
    if isinstance(e, DBAPIError):
        return str(e.orig).strip().splitlines()[0]
    return str(e)


@app.route("/")
def index():
    return redirect(url_for("list_page", entity="users"))


@app.route("/<entity>")
def list_page(entity):
    e = ENTITIES[entity]
    with engine.connect() as conn:
        result = run(conn, f"SELECT * FROM {e['table']} ORDER BY {e['key']}")
        columns = list(result.keys())
        data = [dict(zip(columns, r)) for r in result]
    return render_template("list.html", entity=entity, key=e["key"], columns=columns, rows=data)


@app.route("/<entity>/new", methods=["GET", "POST"])
@app.route("/<entity>/<int:item_id>/edit", methods=["GET", "POST"])
def form_page(entity, item_id=None):
    e = ENTITIES[entity]
    error = None
    if request.method == "POST":
        values = request.form.to_dict()
        try:
            with engine.begin() as conn:
                e["save"](conn, item_id, values)
            flash("Saved.")
            return redirect(url_for("list_page", entity=entity))
        except (DBAPIError, CheckError, ValueError) as ex:
            error = error_text(ex)
    else:
        values = {}
        if item_id is not None:
            with engine.connect() as conn:
                values = e["load"](conn, item_id)
    with engine.connect() as conn:
        fields = e["fields"](conn)
    values = {k: "" if v is None else str(v) for k, v in values.items()}
    return render_template("form.html", entity=entity, fields=fields, values=values, error=error)


@app.route("/<entity>/<int:item_id>/delete", methods=["POST"])
def delete_page(entity, item_id):
    e = ENTITIES[entity]
    try:
        with engine.begin() as conn:
            run(conn, f"DELETE FROM {e['table']} WHERE {e['key']} = :id", id=item_id)
        flash("Deleted.")
    except DBAPIError as ex:
        flash("Error: " + error_text(ex))
    return redirect(url_for("list_page", entity=entity))
