def convertir_rango(limite_inferior_entrada, limite_superior_entrada, limite_inferior_salida, limite_superior_salida, valor_entrada):
    """
    Convierte un valor de entrada de un rango a otro.

    Args:
      limite_inferior_entrada: El limite inferior del rango de entrada.
      limite_superior_entrada: El limite superior del rango de entrada.
      limite_inferior_salida: El limite inferior del rango de salida.
      limite_superior_salida: El limite superior del rango de salida.
      valor_entrada: El valor de entrada a convertir.

    Returns:
      El valor de entrada convertido.
    """

    # Calculamos el factor de escala.

    factor_escala = (limite_superior_salida - limite_inferior_salida) / \
        (limite_superior_entrada - limite_inferior_entrada)

    # Convertimos el valor de entrada.

    valor_convertido = limite_inferior_salida + \
        factor_escala * (valor_entrada - limite_inferior_entrada)

    return valor_convertido


print(convertir_rango(0, 10, 20, 0, 1))
