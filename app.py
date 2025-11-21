from flask import Flask, render_template, redirect, request, flash, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import secrets

app = Flask(__name__)
# app.secret_key = secrets.token_hex(32)
app.secret_key = "b1f23d8ce91c7e0fd092bb1e4bf74e2d3c9ad81a7d4a5f6ff123e9012a4c7e88"

def ConnPostGresSQL():
    conn =  psycopg2.connect("postgresql://postgres:KrNQFrPPFkKspmRqPWLbvhcGUNhcZsxL@shinkansen.proxy.rlwy.net:25684/railway", cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn

@app.route("/")
def index():
    conn = ConnPostGresSQL()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM publication ORDER BY id DESC")
    posts = cur.fetchall()
    posts = [dict(row) for row in posts]
    return render_template("index.html", posts=posts)

@app.route("/add_post", methods=["POST"])
def add_post():
    cur = ConnPostGresSQL().cursor()

    cur.execute("INSERT INTO publication (title, content, created_at) VALUES (%s, %s, %s)", 
                (request.form["title"], request.form["content"], datetime.datetime.now()))
    ConnPostGresSQL().commit()
    return redirect("/")

@app.route("/edit_post/<int:post_id>", methods=["GET"])
def edit_post(post_id):
    conn = ConnPostGresSQL()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM publication WHERE id = %s", (post_id,))
    post = cur.fetchone()
    conn.close()

    if post is None:
        return "Post not found", 404

    return render_template("edit_post.html", post=post)

@app.route("/edit_post/<int:post_id>", methods=["POST"])
def update_post(post_id):
    new_title = request.form["title"]
    new_content = request.form["content"]

    conn = ConnPostGresSQL()
    cur = conn.cursor()
    cur.execute(
        "UPDATE publication SET title=%s, content=%s WHERE id=%s",
        (new_title, new_content, post_id)
    )
    conn.commit()
    conn.close()

    flash("Publication modifiée avec succès!", "success")
    return redirect(url_for("index"))

@app.route("/delete_post/<int:id>", methods=["GET"])
def delete_post(id):
    conn = ConnPostGresSQL()
    cur = conn.cursor()
    cur.execute("DELETE FROM publication WHERE id=%s", (id,))
    conn.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
