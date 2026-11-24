def parse_int(value):
    """Convierte un parámetro de la URL a int; devuelve None si no es válido."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
