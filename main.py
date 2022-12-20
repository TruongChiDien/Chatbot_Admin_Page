from flask import Flask, render_template, url_for, g, redirect, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import *
import os


app = Flask(__name__, instance_relative_config = True)
app.config.from_mapping(
    SECRET_KEY="dev",
    # store the database in the instance folder
    DATABASE=os.path.join(app.instance_path, "admin.sqlite"),
)
print(app.instance_path)
init_app(app)


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@app.route('/', methods = ('GET', 'POST'))
def index():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('collect/index.html')


@app.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template('login.html')


@app.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
        else:
            return redirect(url_for("login"))

    return render_template('auth/register.html')




@app.route('/logout', methods = ('GET', 'POST'))
def logout():
    session.clear()
    return redirect(url_for('index'))



@app.route('/collect', methods = ('GET', 'POST'))
def collect():
    if request.method == 'POST':
        intent = request.form["intent"]
        message = request.form["message"]
        print(intent, message)
        redirect(url_for('index'))

    return render_template('collect/collect.html')


@app.route('/dashboard', methods = ('GET', 'POST'))
def dashboard():
    pass


app.add_url_rule("/", endpoint="index")


if __name__ == '__main__':
    app.run(port=5000, debug=True)