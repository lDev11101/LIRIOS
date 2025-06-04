document.addEventListener('DOMContentLoaded', function () {
    // Cambiar Rol
    document.querySelectorAll('.cambiar-rol-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.id;
            const username = this.dataset.username;
            const rolActual = this.dataset.rol;
            Swal.fire({
                title: 'Cambiar Rol',
                html: `
          <label class="block mb-2 text-[#F0B000]">Selecciona el nuevo rol para <b>${username}</b>:</label>
          <select id="nuevoRol" class="swal2-input">
            <option value="1" ${rolActual == 1 ? 'selected' : ''}>Administrador</option>
            <option value="2" ${rolActual == 2 ? 'selected' : ''}>Usuario</option>
          </select>
        `,
                showCancelButton: true,
                confirmButtonText: 'Continuar',
                cancelButtonText: 'Cancelar',
                preConfirm: () => {
                    const nuevoRol = document.getElementById('nuevoRol').value;
                    return nuevoRol;
                }
            }).then(result => {
                if (result.isConfirmed) {
                    // Segunda ventana: pedir contraseña
                    Swal.fire({
                        title: 'Confirmar acción',
                        html: `
              <p>Ingresa tu contraseña para confirmar el cambio de rol:</p>
              <input type="password" id="passwordConfirm" class="swal2-input" placeholder="Contraseña">
            `,
                        inputAttributes: { autocapitalize: "off" },
                        showCancelButton: true,
                        confirmButtonText: 'Confirmar',
                        cancelButtonText: 'Cancelar',
                        preConfirm: () => {
                            const password = document.getElementById('passwordConfirm').value;
                            if (!password) {
                                Swal.showValidationMessage('Debes ingresar tu contraseña');
                            }
                            return password;
                        }
                    }).then(confirmResult => {
                        if (confirmResult.isConfirmed) {
                            // Enviar petición AJAX para cambiar el rol
                            fetch('/admin/dashboard/cambiar_rol_usuario', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    user_id: userId,
                                    nuevo_rol: result.value,
                                    password: confirmResult.value
                                })
                            })
                                .then(res => res.json())
                                .then(data => {
                                    Swal.fire({
                                        icon: data.success ? 'success' : 'error',
                                        title: data.success ? '¡Rol actualizado!' : 'Error',
                                        text: data.message
                                    }).then(() => { if (data.success) location.reload(); });
                                });
                        }
                    });
                }
            });
        });
    });

    // Eliminar usuario
    document.querySelectorAll('.eliminar-usuario-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.id;
            const username = this.dataset.username;
            Swal.fire({
                title: '¿Eliminar usuario?',
                html: `<b>${username}</b> será eliminado permanentemente.<br><span class="text-red-500">¡Esta acción no se puede deshacer!</span>`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#232b3b',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then(result => {
                if (result.isConfirmed) {
                    fetch('/admin/dashboard/eliminar_usuario', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ user_id: userId })
                    })
                        .then(res => res.json())
                        .then(data => {
                            Swal.fire({
                                icon: data.success ? 'success' : 'error',
                                title: data.success ? '¡Eliminado!' : 'Error',
                                text: data.message
                            }).then(() => { if (data.success) location.reload(); });
                        });
                }
            });
        });
    });

    // Enviar reporte
    document.querySelectorAll('.enviar-reporte-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.id;
            const username = this.dataset.username;
            const nombre = this.dataset.nombre;
            Swal.fire({
                title: 'Enviar reporte',
                text: `¿Enviar el reporte de hoy a ${nombre} (${username})?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Enviar',
                cancelButtonText: 'Cancelar'
            }).then(result => {
                if (result.isConfirmed) {
                    fetch('/admin/dashboard/enviar_reporte_usuario', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ user_id: userId })
                    })
                        .then(res => res.json())
                        .then(data => {
                            Swal.fire({
                                icon: data.success ? 'success' : 'error',
                                title: data.success ? '¡Enviado!' : 'Error',
                                text: data.message
                            });
                        });
                }
            });
        });
    });

    // Mostrar y ocultar modal de agregar usuario
    document.addEventListener("DOMContentLoaded", function () {
        const abrirModal = document.getElementById("abrir-modal-agregar");
        const cerrarModal = document.getElementById("cerrar-modal-agregar");
        const modal = document.getElementById("modal-agregar-usuario");
        const form = document.getElementById("form-agregar-usuario");

        if (abrirModal && cerrarModal && modal && form) {
            abrirModal.onclick = function () {
                modal.classList.remove("hidden");
            };
            cerrarModal.onclick = function () {
                modal.classList.add("hidden");
            };

            // Cerrar modal al hacer click fuera del contenido
            modal.addEventListener("click", function (e) {
                if (e.target === modal) {
                    modal.classList.add("hidden");
                }
            });

            // Enviar formulario por AJAX
            form.onsubmit = async function (e) {
                e.preventDefault();
                const datos = Object.fromEntries(new FormData(form).entries());
                const res = await fetch(form.getAttribute("data-url"), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(datos),
                });
                const data = await res.json();
                if (data.success) {
                    Swal.fire("¡Éxito!", data.message, "success").then(() => location.reload());
                } else {
                    Swal.fire("Error", data.message, "error");
                }
            };
        }
    });
});