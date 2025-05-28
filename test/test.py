import pytest
from app import create_app
import io
import openpyxl
import os


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False  # Desactivar protección CSRF para pruebas
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username, password):
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    # Asegurarse de que el login fue exitoso antes de continuar
    assert response.status_code == 302  # O el código de redirección esperado después del login
    return client


def test_admin_export_excel(client):
    # Primero, inicia sesión como administrador
    client = login(client, "admin", "1230")
    
    # Preparar los datos para la exportación (simulando el formulario de filtros)
    data = {
        "usuario": "",  # Sin filtro de usuario
        "ingreso": "on",  # Incluir ingresos
        "egreso": "on",  # Incluir egresos
        "fecha_inicio": "",  # Sin filtro de fecha inicial
        "fecha_final": ""  # Sin filtro de fecha final
    }
    
    # Realizar la solicitud POST a la ruta correcta
    response = client.post("/admin/dashboard/exportar_excel", data=data)
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    
    # Verificar el tipo de contenido de Excel
    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Verificar que el archivo tenga contenido
    assert len(response.data) > 100
    
    # Verificar que el archivo sea un Excel válido
    excel_file = io.BytesIO(response.data)
    try:
        workbook = openpyxl.load_workbook(excel_file)
        worksheet = workbook.active
        # Verificar que tenga las columnas esperadas
        headers = [cell.value for cell in worksheet[1]]
        expected_headers = [
            "Fecha", "Usuario", "Tipo", "Descripción", 
            "Cantidad", "Precio Unitario", "Precio Total"
        ]
        assert headers == expected_headers
    except Exception as e:
        assert False, f"No se pudo abrir el archivo Excel: {str(e)}"
    
    # Guardar el archivo Excel si la prueba es exitosa (opcional, para depuración)
    if response.status_code == 200:
        export_dir = "temp_exports"
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, "export_sin_filtros.xlsx")
        with open(file_path, "wb") as f:
            f.write(response.data)
        print(f"Archivo Excel guardado en: {file_path}")


def test_admin_export_excel_with_filters(client):
    # Inicia sesión como administrador
    client = login(client, "admin", "1230")
    
    # Preparar los datos para la exportación con filtros
    data = {
        "usuario": "admin",  # Filtrar por usuario admin
        "ingreso": "on",  # Solo ingresos
        "egreso": "",  # Sin egresos
        "fecha_inicio": "2023-01-01",  # Desde esta fecha
        "fecha_final": "2023-12-31"  # Hasta esta fecha
    }
    
    # Realizar la solicitud POST a la ruta correcta
    response = client.post("/admin/dashboard/exportar_excel", data=data)
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    
    # Verificar el tipo de contenido de Excel
    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Verificar que el archivo tenga contenido
    assert len(response.data) > 100
    
    # Guardar el archivo Excel si la prueba es exitosa (opcional, para depuración)
    if response.status_code == 200:
        export_dir = "temp_exports"
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, "export_con_filtros.xlsx")
        with open(file_path, "wb") as f:
            f.write(response.data)
        print(f"Archivo Excel guardado en: {file_path}")
