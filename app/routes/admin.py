from flask import render_template, Blueprint, session, redirect, url_for, abort, request, flash, current_app
from functools import wraps
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("auth.login"))
        if not session.get("is_admin"):
            abort(403)  # Forbidden
        return f(*args, **kwargs)

    return decorated_function


@bp_admin.route("/dashboard")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@bp_admin.route("/dashboard/ingreso", methods=["GET", "POST"])
@admin_required
def ingreso():
    if request.method == "POST":
        conn = None
        cursor = None
        try:
            # Obtener los datos del formulario
            descripcion = request.form.get("descripcion")
            cantidad = int(request.form.get("cantidad"))
            precio_unitario = float(request.form.get("precio_unitario"))
            precio_total = float(request.form.get("precio_total"))
            fecha_hora = request.form.get("fecha_hora")
            usuario = request.form.get("usuario")
            
            # Obtener una nueva conexión
            conn = get_db_connection()
            if not conn:
                flash("Error: No se pudo conectar a la base de datos", "error")
                return redirect(url_for("admin.ingreso"))
                
            cursor = conn.cursor(buffered=True)  # Usar cursor con buffer
            
            # Verificar la conexión antes de cada operación
            cursor.execute("SELECT 1")
            cursor.fetchone()  # Consumir el resultado
            
            # Obtener el user_id
            cursor.execute("SELECT user_id FROM usuarios WHERE username = %s", (usuario,))
            user_result = cursor.fetchone()
            
            if not user_result:
                flash("Error: Usuario no encontrado", "error")
                return redirect(url_for("admin.ingreso"))
            
            user_id = user_result[0]
            
            # Insertar en la tabla de ingresos
            cursor.execute("""
                INSERT INTO ingresos (descripcion, cantidad, precio_unitario, 
                                   precio_total, fecha_hora, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (descripcion, cantidad, precio_unitario, 
                  precio_total, fecha_hora, user_id))
            
            conn.commit()
            
            ingreso_id = cursor.lastrowid
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
            # Obtener los datos del formulario
            descripcion = request.form.get("descripcion")
            cantidad = int(request.form.get("cantidad"))
            precio_unitario = float(request.form.get("precio_unitario"))
            precio_total = float(request.form.get("precio_total"))
            fecha_hora = request.form.get("fecha_hora")
            usuario = request.form.get("usuario")
            
            # Obtener una nueva conexión
            conn = get_db_connection()
            if not conn:
                flash("Error: No se pudo conectar a la base de datos", "error")
                return redirect(url_for("admin.egreso"))
                
            cursor = conn.cursor(buffered=True)  # Usar cursor con buffer
            
            # Verificar la conexión antes de cada operación
            cursor.execute("SELECT 1")
            cursor.fetchone()  # Consumir el resultado
            
            # Obtener el user_id
            cursor.execute("SELECT user_id FROM usuarios WHERE username = %s", (usuario,))
            user_result = cursor.fetchone()
            
            if not user_result:
                flash("Error: Usuario no encontrado", "error")
                return redirect(url_for("admin.egreso"))
            
            user_id = user_result[0]
            
            # Insertar en la tabla de egresos
            cursor.execute("""
                INSERT INTO egresos (descripcion, cantidad, precio_unitario, 
                                   precio_total, fecha_hora, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (descripcion, cantidad, precio_unitario, 
                  precio_total, fecha_hora, user_id))
            
            conn.commit()
            
            egreso_id = cursor.lastrowid
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


def get_db_connection():
    try:
        load_dotenv()
        # Crear una nueva conexión usando variables de entorno
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except mysql.connector.Error as db_err:
        flash(f"Error de conexión MySQL: {str(db_err)}", "error")
        return None
    except Exception as e:
        flash(f"Error inesperado en la conexión: {str(e)}", "error")
        return None