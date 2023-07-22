import os
import shutil
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from time import sleep

import numpy as np
from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

from utils import *

# Globals
app = Flask(__name__)
app.secret_key = "XYZ"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.abspath(
    "database/users_db.db"
)
db = SQLAlchemy(app)

cap = None
ADMIN = "admin"
CURRENT_USER = None
CURRENT_LOGIN_USER_FACE = None
FACE_REID_MODEL = load_model()
CURRENT_USER_FACES_REGISTER = []
DATA_PATH = Path(f"model_training/data/camera_captures/")


class User(db.Model):
    uID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    lastName = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    telPhone = db.Column(db.String(50), unique=True)
    passwordHash = db.Column(db.String(50))
    lastLoginTime = db.Column(db.DateTime, default=datetime.utcnow)


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    telPhone = StringField("Tel. Number", validators=[DataRequired()])
    submit = SubmitField("Submit")
    password = PasswordField(
        validators=[
            Length(min=5, message="The password must be at least 8 lengths long")
        ]
    )
    confirm = PasswordField(
        "Confirm Password", validators=[EqualTo("password", "Password mismatch")]
    )


def init_camera():
    return cv2.VideoCapture(0)


@app.route("/admin")
def admin():
    last_logged_users = User.query.order_by(desc(User.lastLoginTime)).all()[:6]
    login_info = []

    for user in last_logged_users:
        delta = datetime.utcnow() - user.lastLoginTime
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60

        if days > 0:
            if days >= 7:
                weeks = days // 7
                if weeks == 1:
                    time_diff = f"{weeks} week"
                else:
                    time_diff = f"{weeks} weeks"
            else:
                time_diff = f"{days} days"
        elif hours > 0:
            time_diff = f"{hours} hours"
        else:
            if minutes == 0:
                time_diff = f"1 min"
            else:
                time_diff = f"{minutes} mins"

        login_info.append(f"{user.name} {user.lastName} - {time_diff} ago")

    return render_template("admin.html", login_info=login_info)


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        password_hash = sha256(password.encode("utf-8")).hexdigest()
        admin_user = User.query.filter_by(name=name).first()
        if admin_user is not None:
            if password_hash == admin_user.passwordHash:
                return redirect(url_for("admin"))
            else:
                # raise error wrong email/pass
                return render_template("admin_login.html")
        else:
            # raise error wrong email/pass
            return render_template("admin_login.html")

    return render_template("admin_login.html")


@app.route("/user_page")
def user_page():
    return render_template("user_page.html", name=CURRENT_USER)


@app.route("/user_inbox")
def user_inbox():
    return render_template("user_inbox.html")


@app.route("/user_calendar")
def user_calendar():
    return render_template("user_calendar.html")


@app.route("/user_settings", methods=["GET", "POST"])
def user_settings():
    CURRENT_USER = "Sergey"
    user_to_update = User.query.filter_by(name=CURRENT_USER).first()
    form = UserForm()
    pic_filename = url_for("static", filename=f"users/{user_to_update.name}/1.png")

    if request.method == "POST":
        user_to_update.name = request.form["name"]
        user_to_update.lastName = request.form["lastName"]
        user_to_update.email = request.form["email"]
        user_to_update.telPhone = request.form["telPhone"]
        db.session.commit()
        flash("The user's information has been updated successfully")
        return redirect(url_for("user_settings"))

    return render_template(
        "user_settings.html",
        user=user_to_update,
        form=form,
        pic_filename=pic_filename,
    )


@app.route("/admin/profile_users")
def profile_users():
    all_users = User.query.order_by(User.lastLoginTime).all()
    return render_template("admin_profile_users.html", all_users=all_users)


@app.route("/admin/update_user/<int:uID>", methods=["GET", "POST"])
def update_user(uID):
    form = UserForm()
    user_to_update = User.query.get_or_404(uID)
    pic_filename = url_for("static", filename=f"users/{user_to_update.name}/1.png")

    if request.method == "POST":
        user_to_update.name = request.form["name"]
        user_to_update.lastName = request.form["lastName"]
        user_to_update.email = request.form["email"]
        user_to_update.telPhone = request.form["telPhone"]
        db.session.commit()
        flash("The user's information has been updated successfully")
        return redirect(url_for("profile_users"))

    return render_template(
        "admin_update_user.html",
        user=user_to_update,
        form=form,
        pic_filename=pic_filename,
    )


@app.route("/admin/delete_user/<int:uID>", methods=["GET", "POST"])
def delete_user(uID):
    user_to_delete = User.query.get_or_404(uID)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("The user has been successfully deleted")
    return redirect(url_for("profile_users"))


@app.route("/admin/add_user", methods=["GET", "POST"])
def add_user():
    global CURRENT_USER
    form = UserForm()
    if request.method == "POST":
        name = request.form["name"]
        lastname = request.form["lastName"]
        email = request.form["email"]
        phone = request.form["telPhone"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if confirm != password:
            pass  # return back to register
        password_hash = sha256(password.encode("utf-8")).hexdigest()

        new_user = User(
            name=name,
            lastName=lastname,
            email=email,
            telPhone=phone,
            passwordHash=password_hash,
        )
        db.session.add(new_user)
        db.session.commit()

        CURRENT_USER = name
        (DATA_PATH / CURRENT_USER).mkdir(parents=True, exist_ok=True)

        return redirect(url_for("register_face_demo"))

    return render_template("admin_add_user.html", form=form)


@app.route("/login_face")
def login_face():
    return render_template("login_face.html")


@app.route("/register_face_demo")
def register_face_demo():
    return render_template("register_face_demo.html")


@app.route("/")
@app.route("/logout")
def logout():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    global CURRENT_USER
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_by_email = User.query.filter_by(email=email).first()
        password_hash = sha256(password.encode("utf-8")).hexdigest()
        if user_by_email is not None:
            if password_hash == user_by_email.passwordHash:
                CURRENT_USER = user_by_email.name
                user_by_email.lastLoginTime = datetime.utcnow()
                db.session.commit()
                return redirect(url_for("login_face"))
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")

    return render_template("login.html")


@app.route("/video_feed_loop")
def video_feed_loop():
    response = get_rect_frame()
    return Response(response, mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed_scan")
def video_feed_scan():
    response = get_scanned_frame()
    return Response(response, mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/login_process")
def login_process():
    global CURRENT_USER, CURRENT_LOGIN_USER_FACE, cap
    cap.release()
    cap = None

    login_user_encs = FACE_REID_MODEL(CURRENT_LOGIN_USER_FACE)
    CURRENT_LOGIN_USER_FACE = None

    recognized = compare_encodings(login_user_encs, CURRENT_USER)
    if recognized:
        return redirect(url_for("user_page"))
    else:
        flash("Error: Access Denied! You were not authorized by the system!")
        return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    global CURRENT_USER
    if request.method == "POST":
        name = request.form["name"]
        lastname = request.form["lname"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        repeat_password = request.form["repeat_password"]

        if repeat_password != password:
            return redirect(url_for("register"))
        # check email
        # check telephone number
        password_hash = sha256(password.encode("utf-8")).hexdigest()

        new_user = User(
            name=name,
            lastName=lastname,
            email=email,
            telPhone=phone,
            passwordHash=password_hash,
        )
        db.session.add(new_user)
        db.session.commit()

        CURRENT_USER = name
        (DATA_PATH / CURRENT_USER).mkdir(parents=True, exist_ok=True)

        return redirect(url_for("register_face_demo"))
    return render_template("register.html")


@app.route("/register_face", methods=["GET", "POST"])
def register_face():
    global cap
    cap.release()
    cap = None
    return render_template("register_face.html")


@app.route("/register_process")
def register_process():
    global CURRENT_USER, CURRENT_USER_FACES_REGISTER, cap

    cap.release()
    cap = None

    print(f"Extacting features from the user {CURRENT_USER}: ", end="")
    user_encodings = FACE_REID_MODEL(CURRENT_USER_FACES_REGISTER)
    print("done")
    user_encodings = np.array(user_encodings)
    np.save(f"database/user_encodings/{CURRENT_USER}.npy", user_encodings)
    print(f"Features are saved in database/user_encodings/{CURRENT_USER}.npy")
    Path(f"static/users/{CURRENT_USER}").mkdir(parents=True, exist_ok=True)
    shutil.copy(
        (DATA_PATH / CURRENT_USER / "1.png").as_posix(),
        f"static/users/{CURRENT_USER}/1.png",
    )  # dst, src
    CURRENT_USER = ""
    CURRENT_USER_FACES_REGISTER = []

    flash("The new user has been added successfully")
    return redirect(url_for("user_page"))


def get_rect_frame():
    global CURRENT_LOGIN_USER_FACE, cap
    cap = init_camera()
    while True:
        success, frame = cap.read()
        if success:
            face, scanned_frame, _, _ = put_face_rectangle(frame)
            scanned_frame = cv2.flip(scanned_frame, 1)

            CURRENT_LOGIN_USER_FACE = face
            ret, buffer = cv2.imencode(".jpg", scanned_frame)
            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
        else:
            break


def get_scanned_frame():
    global CURRENT_USER_FACES_REGISTER, cap
    cap = init_camera()
    for i in range(1, MAX_SCAN_NUM + 1):
        success, frame = cap.read()
        if success:
            face, scanned_frame = scan_face(frame, i)

            # save faces
            CURRENT_USER_FACES_REGISTER.append(face)

            cv2.imwrite((DATA_PATH / CURRENT_USER / f"{i}.png").as_posix(), face)
            # end saving faces

            ret, buffer = cv2.imencode(".jpg", scanned_frame)
            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
        else:
            break


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
