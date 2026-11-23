from abc import ABC, abstractmethod
import logging
from typing import List, Optional

from excepciones import ErrorReserva, ErrorServicio, ErrorValidacion

logger = logging.getLogger("SoftwareFJ")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("sistema_fj.log", mode="a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class EntidadGeneral(ABC):
    """Clase abstracta general que representa entidades del sistema."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ErrorValidacion("El identificador de la entidad es obligatorio.")
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @abstractmethod
    def resumen(self) -> str:
        """Retorna una descripción resumida de la entidad."""


class Cliente(EntidadGeneral):
    """Representa un cliente de Software FJ con datos encapsulados y validados."""

    def __init__(self, id_entidad: str, nombre: str, documento: str, correo: str):
        super().__init__(id_entidad)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorValidacion(f"Nombre inválido ('{valor}'): debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str):
        doc_limpio = str(valor).strip()
        if not doc_limpio.isdigit() or len(doc_limpio) < 6:
            raise ErrorValidacion(f"Documento inválido ('{valor}'): debe tener al menos 6 dígitos numéricos.")
        self.__documento = doc_limpio

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ErrorValidacion(f"Correo electrónico inválido ('{valor}').")
        self.__correo = valor.strip()

    def resumen(self) -> str:
        return f"[{self.id_entidad}] Cliente: {self.__nombre} | Doc: {self.__documento} | Correo: {self.__correo}"


class Servicio(EntidadGeneral, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo: str, nombre_servicio: str, tarifa_base: float, disponible: bool = True):
        super().__init__(codigo)
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def nombre_servicio(self) -> str:
        return self.__nombre_servicio

    @nombre_servicio.setter
    def nombre_servicio(self, valor: str):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorValidacion(f"Nombre de servicio inválido ('{valor}').")
        self.__nombre_servicio = valor.strip()

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float):
        try:
            monto = float(valor)
        except (TypeError, ValueError) as exc:
            raise ErrorServicio("La tarifa base debe ser numérica.") from exc
        if monto <= 0:
            raise ErrorServicio(f"La tarifa base ({monto}) debe ser mayor que cero.")
        self.__tarifa_base = monto

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ErrorServicio(f"El servicio '{self.nombre_servicio}' ({self.id_entidad}) no está disponible.")

    @abstractmethod
    def calcular_costo(
        self,
        unidades: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        extra_fijo: float = 0.0,
    ) -> float:
        """Calcula el costo total con soporte a parámetros opcionales."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe las características específicas del servicio."""

    def resumen(self) -> str:
        estado_disp = "Disponible" if self.disponible else "No disponible"
        return f"{self.describir_servicio()} | Tarifa base: ${self.tarifa_base:.2f} | {estado_disp}"


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas."""

    def __init__(self, codigo: str, nombre_servicio: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        super().__init__(codigo, nombre_servicio, tarifa_base, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorValidacion("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad

    def calcular_costo(
        self,
        unidades: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        extra_fijo: float = 0.0,
    ) -> float:
        try:
            if not isinstance(unidades, int) or unidades <= 0:
                raise ValueError("Las horas de sala deben ser un entero mayor a 0.")
            if not (0 <= descuento_pct <= 100) or impuesto_pct < 0 or extra_fijo < 0:
                raise ValueError("Descuento, impuesto o cargo extra fuera de rango válido.")

            subtotal = (self.tarifa_base * unidades) + extra_fijo
            con_descuento = subtotal * (1 - descuento_pct / 100.0)
            total = con_descuento * (1 + impuesto_pct / 100.0)
            return round(total, 2)
        except Exception as exc:
            logger.error(f"Error calculando costo en ReservaSala ({self.id_entidad}): {exc}")
            raise ErrorServicio("No fue posible calcular el costo de la reserva de sala.") from exc

    def describir_servicio(self) -> str:
        return f"Sala '{self.nombre_servicio}' (Capacidad: {self.capacidad})"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos."""

    def __init__(self, codigo: str, nombre_servicio: str, tarifa_base: float, categoria_equipo: str, disponible: bool = True):
        super().__init__(codigo, nombre_servicio, tarifa_base, disponible)
        if not categoria_equipo or not categoria_equipo.strip():
            raise ErrorValidacion("La categoría del equipo es obligatoria.")
        self.categoria_equipo = categoria_equipo.strip()

    def calcular_costo(
        self,
        unidades: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        extra_fijo: float = 0.0,
    ) -> float:
        try:
            if not isinstance(unidades, int) or unidades <= 0:
                raise ValueError("Los días de alquiler deben ser un entero mayor a 0.")
            if not (0 <= descuento_pct <= 100) or impuesto_pct < 0 or extra_fijo < 0:
                raise ValueError("Parámetros financieros inválidos en alquiler de equipo.")

            subtotal = (self.tarifa_base * unidades) + extra_fijo
            con_descuento = subtotal * (1 - descuento_pct / 100.0)
            total = con_descuento * (1 + impuesto_pct / 100.0)
            return round(total, 2)
        except Exception as exc:
            logger.error(f"Error calculando costo en AlquilerEquipo ({self.id_entidad}): {exc}")
            raise ErrorServicio("No fue posible calcular el costo del alquiler de equipo.") from exc

    def describir_servicio(self) -> str:
        return f"Equipo '{self.nombre_servicio}' (Categoría: {self.categoria_equipo})"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o consultorías."""

    def __init__(self, codigo: str, nombre_servicio: str, tarifa_base: float, especialidad: str, disponible: bool = True):
        super().__init__(codigo, nombre_servicio, tarifa_base, disponible)
        if not especialidad or not especialidad.strip():
            raise ErrorValidacion("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    def calcular_costo(
        self,
        unidades: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        extra_fijo: float = 0.0,
    ) -> float:
        try:
            if not isinstance(unidades, int) or unidades <= 0:
                raise ValueError("El número de sesiones debe ser un entero mayor a 0.")
            if not (0 <= descuento_pct <= 100) or impuesto_pct < 0 or extra_fijo < 0:
                raise ValueError("Parámetros financieros inválidos en asesoría especializada.")

            subtotal = (self.tarifa_base * unidades) + extra_fijo
            con_descuento = subtotal * (1 - descuento_pct / 100.0)
            total = con_descuento * (1 + impuesto_pct / 100.0)
            return round(total, 2)
        except Exception as exc:
            logger.error(f"Error calculando costo en AsesoriaEspecializada ({self.id_entidad}): {exc}")
            raise ErrorServicio("No fue posible calcular el costo de la asesoría especializada.") from exc

    def describir_servicio(self) -> str:
        return f"Asesoría '{self.nombre_servicio}' (Especialidad: {self.especialidad})"


class Reserva(EntidadGeneral):
    """Integra cliente, servicio, duración y estado con control de ciclo de vida."""

    ESTADOS_VALIDOS = {"CREADA", "CONFIRMADA", "CANCELADA"}

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ErrorReserva("Debe asociarse una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ErrorReserva("Debe asociarse una instancia válida de Servicio.")
        if not isinstance(duracion, int) or duracion <= 0:
            raise ErrorReserva("La duración de la reserva debe ser un entero positivo.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "CREADA"
        self.costo_calculado: Optional[float] = None

    def confirmar(
        self,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        extra_fijo: float = 0.0,
    ) -> float:
        try:
            if self.estado == "CANCELADA":
                raise ErrorReserva(f"La reserva {self.id_entidad} está cancelada y no puede confirmarse.")
            self.servicio.validar_disponibilidad()
            costo = self.servicio.calcular_costo(
                self.duracion,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
                extra_fijo=extra_fijo,
            )
        except ErrorServicio as exc:
            logger.error(f"Fallo de servicio al confirmar reserva {self.id_entidad}: {exc}")
            raise ErrorReserva(f"Error al confirmar reserva {self.id_entidad} por fallo en servicio.") from exc
        except ErrorReserva:
            logger.error(f"Estado inválido al confirmar reserva {self.id_entidad}.")
            raise
        except Exception as exc:
            logger.error(f"Error inesperado al confirmar reserva {self.id_entidad}: {exc}")
            raise ErrorReserva(f"No fue posible confirmar la reserva {self.id_entidad}.") from exc
        else:
            self.costo_calculado = costo
            self.estado = "CONFIRMADA"
            logger.info(f"Reserva {self.id_entidad} confirmada para {self.cliente.nombre}. Total: ${costo:.2f}")
            return costo
        finally:
            logger.info(f"Auditoría reserva {self.id_entidad}: estado actual='{self.estado}'.")

    def cancelar(self):
        try:
            if self.estado == "CANCELADA":
                raise ErrorReserva(f"La reserva {self.id_entidad} ya se encuentra cancelada.")
            self.estado = "CANCELADA"
            logger.info(f"Reserva {self.id_entidad} cancelada correctamente.")
        except Exception as exc:
            logger.error(f"Error al cancelar reserva {self.id_entidad}: {exc}")
            raise ErrorReserva(f"Operación de cancelación rechazada para {self.id_entidad}.") from exc

    def resumen(self) -> str:
        costo_str = f"${self.costo_calculado:.2f}" if self.costo_calculado is not None else "Pendiente"
        return (
            f"Reserva {self.id_entidad} | Estado: {self.estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
            f"Duración: {self.duracion} | Costo: {costo_str}"
        )


class GestorSoftwareFJ:
    """Administra colecciones en memoria mediante listas sin utilizar bases de datos."""

    def __init__(self):
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []

    def registrar_cliente(self, cliente: Cliente):
        if any(c.documento == cliente.documento for c in self.clientes):
            raise ErrorValidacion(f"Ya existe un cliente registrado con el documento {cliente.documento}.")
        self.clientes.append(cliente)
        logger.info(f"Cliente registrado: {cliente.resumen()}")

    def registrar_servicio(self, servicio: Servicio):
        if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
            raise ErrorServicio(f"Ya existe un servicio con el código {servicio.id_entidad}.")
        self.servicios.append(servicio)
        logger.info(f"Servicio registrado: {servicio.resumen()}")

    def crear_y_procesar_reserva(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        extra_fijo: float = 0.0,
    ) -> Reserva:
        reserva = Reserva(id_reserva, cliente, servicio, duracion)
        reserva.confirmar(
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
            extra_fijo=extra_fijo,
        )
        self.reservas.append(reserva)
        return reserva