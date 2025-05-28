from flask import (
    render_template,
    Blueprint,
    session,
    redirect,
    url_for,
    abort,
    request,
    flash,
    current_app,
    send_file,
)
from functools import wraps
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import io
import openpyxl

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("auth.login"))
        if not session.get("is_admin"):
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def get_db_connection():
    try:
        load_dotenv()
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT"),
        )
        return conn
    except mysql.connector.Error as db_err:
        flash(f"Error de conexión MySQL: {str(db_err)}", "error")
        return None
    except Exception as e:
        flash(f"Error inesperado en la conexión: {str(e)}", "error")
        return None


def construir_filtros(usuario, fecha_inicio, fecha_final, tabla_alias):
    where = []
    params = []
    if usuario:
        where.append(f"u.username = %s")
        params.append(usuario)
    if fecha_inicio:
        where.append(f"{tabla_alias}.fecha_hora >= %s")
        params.append(fecha_inicio + " 00:00:00")
    if fecha_final:
        where.append(f"{tabla_alias}.fecha_hora <= %s")
        params.append(fecha_final + " 23:59:59")
    return where, params


def obtener_consultas(usuario, ingreso, egreso, fecha_inicio, fecha_final):
    mostrar_ingresos = ingreso == "on"
    mostrar_egresos = egreso == "on"
    if not mostrar_ingresos and not mostrar_egresos:
        mostrar_ingresos = True
        mostrar_egresos = True

    consultas = []
    if mostrar_ingresos:
        where_ingreso, params_ingreso = construir_filtros(
            usuario, fecha_inicio, fecha_final, "i"
        )
        sql_ingresos = """
            SELECT i.fecha_hora, u.username, 'Ingreso' as tipo, i.descripcion, i.cantidad, i.precio_unitario, i.precio_total
            FROM ingresos i
            JOIN usuarios u ON i.usuario_id = u.user_id
        """
        if where_ingreso:
            sql_ingresos += " WHERE " + " AND ".join(where_ingreso)
        consultas.append((sql_ingresos, params_ingreso))
    if mostrar_egresos:
        where_egreso, params_egreso = construir_filtros(
            usuario, fecha_inicio, fecha_final, "e"
        )
        sql_egresos = """
            SELECT e.fecha_hora, u.username, 'Egreso' as tipo, e.descripcion, e.cantidad, e.precio_unitario, e.precio_total
            FROM egresos e
            JOIN usuarios u ON e.usuario_id = u.user_id
        """
        if where_egreso:
            sql_egresos += " WHERE " + " AND ".join(where_egreso)
        consultas.append((sql_egresos, params_egreso))
    return consultas


def ejecutar_consultas(cursor, consultas):
    resultados = []
    for sql, params in consultas:
        cursor.execute(sql, tuple(params))
        resultados.extend(cursor.fetchall())
    resultados.sort(key=lambda x: x[0], reverse=True)
    return resultados


def crear_excel(resultados):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reportes"
    headers = [
        "Fecha",
        "Usuario",
        "Tipo",
        "Descripción",
        "Cantidad",
        "Precio Unitario",
        "Precio Total",
    ]
    ws.append(headers)
    for row in resultados:
        ws.append(row)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def obtener_usuarios(cursor):
    cursor.execute("SELECT username FROM usuarios")
    return [row[0] for row in cursor.fetchall()]


def obtener_user_id(cursor, usuario):
    cursor.execute("SELECT user_id FROM usuarios WHERE username = %s", (usuario,))
    user_result = cursor.fetchone()
    return user_result[0] if user_result else None


def insertar_movimiento(
    cursor,
    tabla,
    descripcion,
    cantidad,
    precio_unitario,
    precio_total,
    fecha_hora,
    user_id,
):
    cursor.execute(
        f"""
        INSERT INTO {tabla} (descripcion, cantidad, precio_unitario, 
                           precio_total, fecha_hora, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (descripcion, cantidad, precio_unitario, precio_total, fecha_hora, user_id),
    )
    return cursor.lastrowid


def print_filtros_formulario(usuario, ingreso, egreso, fecha_inicio, fecha_final):
    print("=== FILTROS DEL FORMULARIO ===")
    print(f"Usuario: {usuario}")
    print(f"Ingreso: {ingreso}")
    print(f"Egreso: {egreso}")
    print(f"Fecha inicio: {fecha_inicio}")
    print(f"Fecha final: {fecha_final}")
    print("==============================")


@bp_admin.route("/dashboard")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@bp_admin.route("/dashboard/exportar_excel", methods=["POST"])
@admin_required
def exportar_excel():
    usuario = request.form.get("usuario")
    ingreso = request.form.get("ingreso")
    egreso = request.form.get("egreso")
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_final = request.form.get("fecha_final")

    conn = get_db_connection()
    cursor = conn.cursor()
    consultas = obtener_consultas(usuario, ingreso, egreso, fecha_inicio, fecha_final)
    resultados = ejecutar_consultas(cursor, consultas)
    output = crear_excel(resultados)
    cursor.close()
    conn.close()

    return send_file(
        output,
        as_attachment=True,
        download_name="reporte.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp_admin.route("/dashboard/ingreso", methods=["GET", "POST"])
@admin_required
def ingreso():
    if request.method == "POST":
        conn = None
        cursor = None
        try:
            descripcion = request.form.get("descripcion")
            cantidad = int(request.form.get("cantidad"))
            precio_unitario = float(request.form.get("precio_unitario"))
            precio_total = float(request.form.get("precio_total"))
            fecha_hora = request.form.get("fecha_hora")
            usuario = request.form.get("usuario")

            conn = get_db_connection()
            if not conn:
                flash("Error: No se pudo conectar a la base de datos", "error")
                return redirect(url_for("admin.ingreso"))

            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT 1")
            cursor.fetchone()

            user_id = obtener_user_id(cursor, usuario)
            if not user_id:
                flash("Error: Usuario no encontrado", "error")
                return redirect(url_for("admin.ingreso"))

            ingreso_id = insertar_movimiento(
                cursor,
                "ingresos",
                descripcion,
                cantidad,
                precio_unitario,
                precio_total,
                fecha_hora,
                user_id,
            )
            conn.commit()
            flash(f"Ingreso registrado exitosamente. ID: {ingreso_id}", "success")

        except mysql.connector.Error as db_err:
            if conn:
                conn.rollback()
            flash(f"Error de base de datos: {str(db_err)}", "error")
        except ValueError as ve:
            flash(f"Error en los datos ingresados: {str(ve)}", "error")
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f"Error inesperado: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for("admin.ingreso"))
    return render_template("admin/ingreso.html")


@bp_admin.route("/dashboard/egreso", methods=["GET", "POST"])
@admin_required
def egreso():
    if request.method == "POST":
        conn = None
        cursor = None
        try:
            descripcion = request.form.get("descripcion")
            cantidad = int(request.form.get("cantidad"))
            precio_unitario = float(request.form.get("precio_unitario"))
            precio_total = float(request.form.get("precio_total"))
            fecha_hora = request.form.get("fecha_hora")
            usuario = request.form.get("usuario")

            conn = get_db_connection()
            if not conn:
                flash("Error: No se pudo conectar a la base de datos", "error")
                return redirect(url_for("admin.egreso"))

            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT 1")
            cursor.fetchone()

            user_id = obtener_user_id(cursor, usuario)
            if not user_id:
                flash("Error: Usuario no encontrado", "error")
                return redirect(url_for("admin.egreso"))

            egreso_id = insertar_movimiento(
                cursor,
                "egresos",
                descripcion,
                cantidad,
                precio_unitario,
                precio_total,
                fecha_hora,
                user_id,
            )
            conn.commit()
            flash(f"Egreso registrado exitosamente. ID: {egreso_id}", "success")

        except mysql.connector.Error as db_err:
            if conn:
                conn.rollback()
            flash(f"Error de base de datos: {str(db_err)}", "error")
        except ValueError as ve:
            flash(f"Error en los datos ingresados: {str(ve)}", "error")
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f"Error inesperado: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return redirect(url_for("admin.egreso"))
    return render_template("admin/egreso.html")


@bp_admin.route("/dashboard/reportes", methods=["GET", "POST"])
@admin_required
def reportes():
    conn = None
    cursor = None
    usuarios = []
    resultados = []
    filtros = {
        "usuario": "",
        "ingreso": False,
        "egreso": False,
        "fecha_inicio": "",
        "fecha_final": "",
    }
    try:
        conn = get_db_connection()
        if not conn:
            flash("Error: No se pudo conectar a la base de datos", "error")
            return render_template(
                "admin/reportes.html",
                usuarios=usuarios,
                resultados=resultados,
                filtros=filtros,
            )
        cursor = conn.cursor()
        usuarios = obtener_usuarios(cursor)

        if request.method == "POST":
            usuario = request.form.get("usuario")
            ingreso = request.form.get("ingreso")
            egreso = request.form.get("egreso")
            fecha_inicio = request.form.get("fecha_inicio")
            fecha_final = request.form.get("fecha_final")

            print_filtros_formulario(
                usuario, ingreso, egreso, fecha_inicio, fecha_final
            )

            filtros = {
                "usuario": usuario,
                "ingreso": ingreso == "on",
                "egreso": egreso == "on",
                "fecha_inicio": fecha_inicio,
                "fecha_final": fecha_final,
            }
        else:
            usuario = ""
            ingreso = "on"
            egreso = "on"
            fecha_inicio = ""
            fecha_final = ""

        consultas = obtener_consultas(
            usuario, ingreso, egreso, fecha_inicio, fecha_final
        )
        resultados = ejecutar_consultas(cursor, consultas)

    except Exception as e:
        flash(f"Error al obtener reportes: {str(e)}", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    print("RESULTADOS:", resultados)
    return render_template(
        "admin/reportes.html", usuarios=usuarios, resultados=resultados, filtros=filtros
    )
