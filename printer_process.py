import time
import sys
from queue_manager import get_job

def printer_process(printer_id, job_queue, event_queue, system_config, printer_state):
    print(f"[Printer {printer_id}] Iniciado", flush=True)
    printer_state[printer_id] = "idle"
    
    while True:
        print(f"[Printer {printer_id}] Esperando trabajo...", flush=True)
        
        # Obtener trabajo respetando el tipo de cola
        job, priority = get_job(job_queue, queue_type=system_config["queue_type"])
        print(f"[Printer {printer_id}] Trabajo recibido: {job.id} (prioridad: {priority})", flush=True)
        
        printer_state[printer_id] = f"printing {job.id}"
        event_queue.put({"type":"printer","printer_id":printer_id,"status":"printing","job_id":job.id})
        print(f"[Printer {printer_id}] Iniciando impresión de {job.total_pages} páginas", flush=True)
        
        for p in range(1, job.total_pages+1):
            time.sleep(10)
            print(f"[Printer {printer_id}] Página {p}/{job.total_pages}", flush=True)
            event_queue.put({"type":"progress","job_id":job.id,"printer_id":printer_id,"pages_printed":p,"total_pages":job.total_pages})
        
        print(f"[Printer {printer_id}] Impresión completada", flush=True)
        event_queue.put({"type":"printer","printer_id":printer_id,"status":"idle","job_id":job.id})
        printer_state[printer_id] = "idle"