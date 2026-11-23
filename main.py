from excepciones import ErrorSistemaFJ
from modelos import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    GestorSoftwareFJ,
    ReservaSala,
    logger,
)


def ejecutar_simulacion():
    gestor = GestorSoftwareFJ()
    print("=== INICIO DE SIMULACIÓN SOFTWARE FJ (10 OPERACIONES) ===\n")

    cliente_base = Cliente("CL-001", "Laura Méndez", "1020304050", "laura.mendez@correo.com")
    sala_base = ReservaSala("SV-SALA-1", "Sala Reuniones Norte", 80.0, capacidad=10, disponible=True)
    equipo_base = AlquilerEquipo("SV-EQ-1", "Portátil Ingeniería", 45.0, categoria_equipo="Cómputo", disponible=True)
    asesoria_base = AsesoriaEspecializada("SV-AS-1", "Auditoría de Software", 150.0, especialidad="Calidad", disponible=True)
    sala_no_disp = ReservaSala("SV-SALA-2", "Auditorio Principal", 200.0, capacidad=60, disponible=False)

    operaciones = [
        ("1. Registro válido de cliente", lambda: gestor.registrar_cliente(cliente_base)),
        ("2. Registro inválido de cliente (documento)", lambda: gestor.registrar_cliente(
            Cliente("CL-002", "Andrés Ruiz", "ABC-123", "andres@correo.com")
        )),
        ("3. Creación válida de servicio (ReservaSala)", lambda: gestor.registrar_servicio(sala_base)),
        ("4. Creación inválida de servicio (tarifa <= 0)", lambda: gestor.registrar_servicio(
            AlquilerEquipo("SV-EQ-ERR", "Proyector HD", -25.0, "Video")
        )),
        ("5. Reserva exitosa con descuento e impuesto", lambda: gestor.crear_y_procesar_reserva(
            "RS-101", cliente_base, sala_base, duracion=4, descuento_pct=10.0, impuesto_pct=19.0
        )),
        ("6. Reserva exitosa de alquiler de equipo", lambda: gestor.crear_y_procesar_reserva(
            "RS-102", cliente_base, equipo_base, duracion=3, extra_fijo=15.0
        )),
        ("7. Reserva exitosa de asesoría especializada", lambda: gestor.crear_y_procesar_reserva(
            "RS-103", cliente_base, asesoria_base, duracion=2
        )),
        ("8. Reserva fallida (servicio no disponible)", lambda: gestor.crear_y_procesar_reserva(
            "RS-104", cliente_base, sala_no_disp, duracion=2
        )),
        ("9. Reserva fallida (duración inválida)", lambda: gestor.crear_y_procesar_reserva(
            "RS-105", cliente_base, equipo_base, duracion=0
        )),
        ("10. Cancelación válida y doble cancelación fallida", lambda: (
            r := gestor.crear_y_procesar_reserva("RS-106", cliente_base, sala_base, duracion=1),
            r.cancelar(),
            r.cancelar(),
        )),
    ]

    for descripcion, accion in operaciones:
        try:
            accion()
            print(f"[OK] {descripcion}")
        except ErrorSistemaFJ as exc:
            causa = f" | Causa raíz: {exc.__cause__}" if exc.__cause__ else ""
            print(f"[EXCEPCIÓN CONTROLADA] {descripcion} -> {exc}{causa}")
        except Exception as exc:
            logger.critical(f"Error no controlado en '{descripcion}': {exc}")
            print(f"[ERROR INESPERADO] {descripcion} -> {exc}")

    print("\n=== SIMULACIÓN COMPLETADA SIN DETENER EL SISTEMA ===")
    print(f"Clientes en lista: {len(gestor.clientes)} | Servicios en lista: {len(gestor.servicios)} | Reservas en lista: {len(gestor.reservas)}")


if __name__ == "__main__":
    ejecutar_simulacion()