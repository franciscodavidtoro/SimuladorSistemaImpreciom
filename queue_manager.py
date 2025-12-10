from multiprocessing import Queue, Manager
import time

def init_queues_and_state():
    """Initialize all the queues and shared state. Must be called in the main process."""
    event_queue = Queue()
    job_queue = Queue()  # Cola única que almacena (prioridad, timestamp, job_data)
    
    manager = Manager()
    queue_state = manager.list()
    printer_state = manager.dict()
    system_config = manager.dict()
    
    # Configuración por defecto
    system_config["queue_type"] = "fifo"  # "fifo" o "priority"
    
    return event_queue, queue_state, printer_state, system_config, job_queue

def put_job(job_queue, job_data, priority=1, queue_type="fifo"):
    """Insertar un trabajo en la cola considerando el tipo"""
    timestamp = time.time()
    # Siempre guardar como tupla (prioridad, timestamp, job_data)
    job_queue.put((priority, timestamp, job_data))
    print(f"[Queue] Job {job_data.id} agregado (prioridad: {priority}, tipo: {queue_type})", flush=True)

def get_job(job_queue, queue_type="fifo"):
    """Obtener un trabajo de la cola considerando el tipo"""
    # Extraer todos los items de la cola
    jobs = []
    while not job_queue.empty():
        try:
            jobs.append(job_queue.get_nowait())
        except:
            break
    
    if not jobs:
        # Si la cola está vacía, esperar a que llegue uno
        priority, timestamp, job_data = job_queue.get()
        print(f"[Queue] Job {job_data.id} obtenido (prioridad: {priority}, tipo: {queue_type})", flush=True)
        return job_data, priority
    
    # Si estamos en modo priority, ordenar por prioridad y timestamp
    if queue_type == "priority":
        jobs.sort(key=lambda x: (x[0], x[1]))  # Ordena por (prioridad, timestamp)
    # En FIFO, mantienen el orden que tenían
    
    # Obtener el primero (mayor prioridad o primero en llegar)
    priority, timestamp, job_data = jobs[0]
    
    # Devolver el resto a la cola
    for i in range(1, len(jobs)):
        job_queue.put(jobs[i])
    
    print(f"[Queue] Job {job_data.id} obtenido (prioridad: {priority}, tipo: {queue_type})", flush=True)
    return job_data, priority

def peek_queue(job_queue, queue_type="fifo"):
    """Obtener todos los trabajos sin remover ninguno, ordenados según el tipo"""
    # Extraer todos los items de la cola
    jobs = []
    while not job_queue.empty():
        try:
            jobs.append(job_queue.get_nowait())
        except:
            break
    
    # Si estamos en modo priority, ordenar por prioridad y timestamp
    if queue_type == "priority":
        jobs.sort(key=lambda x: (x[0], x[1]))  # Ordena por (prioridad, timestamp)
    
    # Devolver todos a la cola
    for job in jobs:
        job_queue.put(job)
    
    # Retornar información de los trabajos
    result = []
    for priority, timestamp, job_data in jobs:
        result.append({
            "job_id": job_data.id,
            "priority": priority,
            "timestamp": timestamp,
            "filename": job_data.filename
        })
    
    return result
