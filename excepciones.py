class ErrorSistemaFJ(Exception):
    """Excepción base para errores controlados del sistema Software FJ."""


class ErrorValidacion(ErrorSistemaFJ):
    """Excepción lanzada cuando los datos de entrada o parámetros no son válidos."""


class ErrorServicio(ErrorSistemaFJ):
    """Excepción lanzada por fallos en servicios o cálculos de costos."""


class ErrorReserva(ErrorSistemaFJ):
    """Excepción lanzada al crear, confirmar o cancelar una reserva."""