from enum import Enum

class Motif(str, Enum):
    """
    Enum representing tactical motifs in chess.
    """
    CLAVADA = "Clavada"
    DOBLE_ATAQUE = "Doble Ataque"
    JAQUE_DESCUBIERTO = "Jaque Descubierto"
    DESVIACION = "Desviación"
    ATRACCION = "Atracción"
    INTERCEPCION = "Intercepción"
    ELIMINACION_DEFENSA = "Eliminación de la Defensa"
    RAYOS_X = "Rayos X"
    ZUGZWANG = "Zugzwang"
    PIEZA_SOBRECARGADA = "Pieza Sobrecargada"
    MATE_PASILLO = "Mate del Pasillo"
    SACRIFICIO = "Sacrificio"
    ATAQUE_DESCUBIERTO = "Ataque Descubierto"
    BLOQUEO = "Bloqueo"
    PROMOCION = "Promoción"
    AHOGADO = "Ahogado"
    JAQUE_PERPETUO = "Jaque Perpetuo"
