from app import app, db, User
from hashlib import sha256


password_hash = sha256("admin123".encode("utf-8")).hexdigest()
users_info = [
    ["admin", "", "admin@admin.com", ""],
    ["Sergey", "Gasparyan", "sergey.gasparyan@gmail.com", "+37498164327"],
    ["Lida", "Tsormudyan", "lida.tsormudyan@gmail.com", "+37477112233"],
    ["Karen", "Hakobyan", "karen.hakobyan@gmail.com", "+37455121212"],
    ["Meri", "Mirzoyan", "meri.mirzoyan@gmail.com", "+37493546576"],
    ["Hamlet", "Adamyan", "hamlet.adamyan@gmail.com", "+37498121212"],
    ["David", "Khachatryan", "david.khachatryan@gmail.com", "+37433456789"],
    ["Edik", "Mughdushyan", "edik.mughdushyan@gmail.com", "+37477394672"],
    ["Erik", "Voskanyan", "erik.voskanyan@gmail.com", "+37455667712"],
    ["Yanek", "Hayrapetyan", "yanek.hayrapetyan@gmail.com", "+3777099860"],
    ["Varuzh", "Gevorgyan", "varuzh.gevorgyan@gmail.com", "+37493129885"],
    ["Tatevik", "Avetisyan", "tatevik.avetisyan@gmail.com", "+37477656512"],
    ["Mariam", "Harutyunyan", "mariam.harutyunyan@gmail.com", "+37455982377"],
    ["Maria", "Miskaryan", "maria.miskaryan@gmail.com", "+37477559100"],
    ["Hrayr", "Muradyan", "hrayr.muradyan@gmail.com", "+37455170008"],
    ["Mushex", "Galstyan", "mushex.galstyan@gmail.com", "+37455868612"],
]


with app.app_context():
    db.create_all()

    print("Start...", end="")
    for user_info in users_info:
        new_user = User(
            name=user_info[0],
            lastName=user_info[1],
            email=user_info[2],
            telPhone=user_info[3],
            passwordHash=password_hash,
        )
        db.session.add(new_user)
        db.session.commit()
    print("all users are saved in db")
