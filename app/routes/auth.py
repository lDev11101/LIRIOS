import bcrypt
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    current_app,
    flash,
)

# Blueprint de autenticación
bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


# Obtener la conexión configurada en app.config
# Se asume que en create_app se definió app.config['db_conexion']
def get_db_connection():
    return current_app.config["db_conexion"]


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    # Si el usuario ya está en sesión, redirigimos al dashboard
    if "username" in session:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT u.user_id, u.username, u.userpass, u.nomb_usu, r.role_name FROM usuarios u JOIN roles r ON u.role_id = r.role_id WHERE u.username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user["userpass"].encode("utf-8")
        ):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["nomb_usu"] = user["nomb_usu"]  # <-- Agrega esto
            session["user_role"] = user["role_name"]
            session["is_admin"] = (
                user["role_name"] == "admin"
            )  # Establecer bandera de administrador

            # Redirigir al dashboard según el rol del usuario
            if user["role_name"] == "admin":
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        else:
            flash("Credenciales inválidas. Por favor, inténtalo de nuevo.", "error")
            return redirect(url_for("auth.login"))

    # GET: renderizar formulario de login
    return render_template("auth/login.html")


@bp_auth.route("/logout")
def logout():
    # Limpiar toda la sesión y volver al login
    session.clear()
    return redirect(url_for("auth.login"))
