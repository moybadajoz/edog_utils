import threading
import queue
import time

# Función que encola mensajes


def productor(cola, evento, close):
    for i in range(20):
        mensaje = f"Mensaje {i}"
        cola.put(mensaje)
        print(f"Productor: Enviado '{mensaje}' a la cola")
        evento.set()  # Establecer el evento para notificar al consumidor
        time.sleep(0.02)
    print('fin')
    time.sleep(3)
    close.set()

# Función que desencola mensajes


def consumidor(cola, evento, close):
    mensaje = ''
    while not close.is_set():
        while not cola.empty():
            mensaje = cola.get()
        evento.clear()  # Limpiar el evento para la próxima notificación
        print(f"Consumidor: Recibido '{mensaje}' de la cola cada segundo")
        time.sleep(0.5)


# Crear una cola
mi_cola = queue.Queue(5)

# Crear un evento para la comunicación entre el productor y el consumidor
mi_evento = threading.Event()
close = threading.Event()

# Crear hilos para el productor y el consumidor y pasarles la cola y el evento
hilo_productor = threading.Thread(
    target=productor, args=(mi_cola, mi_evento, close))
hilo_consumidor = threading.Thread(
    target=consumidor, args=(mi_cola, mi_evento, close))

# Iniciar los hilos
hilo_productor.start()
hilo_consumidor.start()

# Esperar a que los hilos terminen (esto podría no ocurrir en este caso ya que los hilos se ejecutan indefinidamente)
hilo_productor.join()
hilo_consumidor.join()
