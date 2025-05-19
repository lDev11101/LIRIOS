// Función para calcular el precio total automáticamente
function calcularTotal() {
    const cantidad = document.getElementById('cantidad').value;
    const precioUnitario = document.getElementById('precio_unitario').value;
    const precioTotal = document.getElementById('precio_total');

    if (cantidad && precioUnitario) {
        precioTotal.value = (parseFloat(cantidad) * parseFloat(precioUnitario)).toFixed(2);
    }
}

// Manejador del formulario
document.addEventListener('DOMContentLoaded', function () {
    const ingresoForm = document.getElementById('ingresoForm');
    const cantidad = document.getElementById('cantidad');
    const precioUnitario = document.getElementById('precio_unitario');

    // Eventos para calcular el total
    cantidad.addEventListener('input', calcularTotal);
    precioUnitario.addEventListener('input', calcularTotal);

    // Manejo del envío del formulario
    ingresoForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // Validar que el precio total no sea 0
        const precioTotal = document.getElementById('precio_total').value;
        if (!precioTotal || precioTotal <= 0) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Por favor, ingrese cantidad y precio unitario válidos',
                confirmButtonText: 'Entendido'
            });
            return;
        }

        // Confirmar el envío
        Swal.fire({
            title: '¿Confirmar registro de ingreso?',
            text: `Total a registrar: $${precioTotal}`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#2196f3',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, registrar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Establecer la fecha y hora actual
                function formatearFecha(fecha) {
                    const year = fecha.getFullYear();
                    const month = String(fecha.getMonth() + 1).padStart(2, '0');
                    const day = String(fecha.getDate()).padStart(2, '0');
                    const hours = String(fecha.getHours()).padStart(2, '0');
                    const minutes = String(fecha.getMinutes()).padStart(2, '0');
                    const seconds = String(fecha.getSeconds()).padStart(2, '0');

                    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
                }

                document.getElementById('fecha_hora').value = formatearFecha(new Date());
                // Enviar el formulario
                this.submit();
            }
        });
    });

    // Mostrar mensajes flash con SweetAlert si existen
    if (typeof mensajesFlash !== 'undefined' && mensajesFlash.length > 0) {
        mensajesFlash.forEach(mensaje => {
            Swal.fire({
                icon: mensaje.categoria === 'success' ? 'success' : 'error',
                title: mensaje.categoria === 'success' ? '¡Éxito!' : 'Error',
                text: mensaje.mensaje,
                confirmButtonColor: '#2196f3'
            });
        });
    }
});