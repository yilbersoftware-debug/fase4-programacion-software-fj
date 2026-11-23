# Sistema Integral de Gestión de Clientes, Servicios y Reservas — Software FJ

Proyecto del componente práctico de la Fase 4 del curso **Programación (213023)** de la UNAD. Implementa programación orientada a objetos y manejo avanzado de excepciones en Python sin bases de datos, usando listas en memoria y registro de eventos/errores en `sistema_fj.log`.

## Estructura del repositorio
- `excepciones.py`: Jerarquía de excepciones personalizadas del sistema.
- `modelos.py`: Clases abstractas, `Cliente`, servicios derivados (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`), `Reserva`, `GestorSoftwareFJ` y configuración de *logs*.
- `main.py`: Simulación de 10 operaciones (válidas y fallidas) manteniendo la ejecución continua.

## Ejecución
```bash
python main.py
```
