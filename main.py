import uuid, os, shutil, asyncio, time
from multiprocessing import Process, freeze_support, Queue, Manager
from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from PyPDF2 import PdfReader 

from models import PrintJob
from printer_process import printer_process
from websocket_manager import job_subscribers, subscribers_lock, broadcast
from queue_manager import put_job, get_job, peek_queue
from job_registry import get_job_registry

# Variables globales para colas y estado compartido
job_queue = None
event_queue = None
queue_state = None
printer_state = None
system_config = None
manager = None

UPLOAD_DIR="uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

NUM_PRINTERS = 3
printer_processes = []
monitor_clients = set()

def init_queues():
    """Inicializar colas y estado compartido"""
    global job_queue, event_queue, queue_state, printer_state, system_config, manager
    
    event_queue = Queue()
    manager = Manager()
    queue_state = manager.list()
    printer_state = manager.dict()
    system_config = manager.dict()
    
    # Configuración por defecto
    system_config["queue_type"] = "fifo"  # "fifo" o "priority"
    
    # Crear cola única
    job_queue = Queue()

@app.on_event("startup")
async def startup():
    """Iniciar el listener de eventos cuando la app inicia"""
    asyncio.create_task(event_listener())

async def event_listener():
    print("[EventListener] Iniciado", flush=True)
    while True:
        print("[EventListener] Esperando evento...", flush=True)
        data = await asyncio.to_thread(event_queue.get)
        print(f"[EventListener] Evento recibido: {data}", flush=True)

        if data.get("type") == "printer" and data.get("status") == "printing":
            if data["job_id"] in queue_state:
                queue_state.remove(data["job_id"])
                print(f"[EventListener] Job {data['job_id']} removido de la cola", flush=True)

        await broadcast(data)
        print(f"[EventListener] Broadcast enviado", flush=True)
        await broadcast_monitor()

async def broadcast_monitor():
    queue_data = peek_queue(job_queue, queue_type=system_config["queue_type"])
    payload = {
        "queue": queue_data,
        "printers": dict(printer_state),
        "config": dict(system_config)
    }

    for ws in list(monitor_clients):
        try:
            await ws.send_json(payload)
        except:
            pass

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), priority: int = Form(1)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse({"error":"only PDF"}, status_code=400)
    job_id=str(uuid.uuid4())
    print(f"[Upload] Nuevo trabajo: {job_id} (prioridad: {priority})", flush=True)
    path=os.path.join(UPLOAD_DIR,f"{job_id}.pdf")
    with open(path,"wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        reader=PdfReader(path)
        total_pages=len(reader.pages)
    except:
        total_pages=1
    job=PrintJob(id=job_id, filename=file.filename, path=path, priority=priority, total_pages=total_pages)
    queue_state.append(job_id)
    print(f"[Upload] Job agregado a queue_state. Enviando a job_queue...", flush=True)
    
    # Usar put_job para respetar el tipo de cola
    put_job(job_queue, job, priority=priority, queue_type=system_config["queue_type"])
    print(f"[Upload] Job enviado a job_queue ({system_config['queue_type']}). Total de páginas: {total_pages}", flush=True)
    return {"job_id":job_id,"total_pages":total_pages}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/monitor", response_class=HTMLResponse)
async def monitor(request: Request):
    return templates.TemplateResponse("monitor.html",{"request":request})

@app.get("/batch", response_class=HTMLResponse)
async def batch_upload(request: Request):
    return templates.TemplateResponse("batch_upload.html",{"request":request})

@app.get("/registry", response_class=HTMLResponse)
async def registry(request: Request):
    """Página para consultar el registro de trabajos"""
    return templates.TemplateResponse("registry.html",{"request":request})

@app.get("/download/{job_id}")
async def download_file(job_id: str):
    path = os.path.join(UPLOAD_DIR, f"{job_id}.pdf")
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path, media_type="application/pdf", filename=f"printed_{job_id}.pdf")

@app.post("/config/queue-type")
async def set_queue_type(queue_type: str = Query("fifo")):
    """Cambiar el tipo de cola (fifo o priority)"""
    if queue_type not in ["fifo", "priority"]:
        return JSONResponse({"error": "Invalid queue type"}, status_code=400)
    
    system_config["queue_type"] = queue_type
    print(f"[Config] Tipo de cola cambiado a: {queue_type}", flush=True)
    
    # Notificar a los clientes del monitor
    await broadcast_monitor()
    #ordenamos la fia si se camvio a prioridad
    
    
    return {"message": f"Queue type changed to {queue_type}", "queue_type": queue_type}

@app.get("/config/queue-type")
async def get_queue_type():
    """Obtener el tipo de cola actual"""
    return {"queue_type": system_config["queue_type"]}

# ========== ENDPOINTS DE REGISTRO DE TRABAJOS ==========

@app.get("/registry/jobs")
async def get_all_jobs(limit: int = Query(50), offset: int = Query(0)):
    """Obtiene todos los trabajos registrados con paginación"""
    registry = get_job_registry()
    jobs = registry.get_all_jobs(limit=limit, offset=offset)
    return {"jobs": jobs, "limit": limit, "offset": offset}

@app.get("/registry/job/{job_id}")
async def get_job_details(job_id: str):
    """Obtiene los detalles de un trabajo específico"""
    registry = get_job_registry()
    job = registry.get_job(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return job

@app.get("/registry/printer/{printer_id}")
async def get_printer_jobs(printer_id: str):
    """Obtiene todos los trabajos procesados por una impresora específica"""
    registry = get_job_registry()
    jobs = registry.get_jobs_by_printer(printer_id)
    return {"printer_id": printer_id, "jobs": jobs}

@app.get("/registry/statistics")
async def get_registry_statistics():
    """Obtiene estadísticas del registro de trabajos"""
    registry = get_job_registry()
    stats = registry.get_statistics()
    return stats

@app.delete("/registry/job/{job_id}")
async def delete_job_record(job_id: str):
    """Elimina un trabajo del registro"""
    registry = get_job_registry()
    success = registry.delete_job(job_id)
    if not success:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return {"message": f"Job {job_id} deleted successfully"}

@app.post("/registry/clear")
async def clear_registry():
    """Limpia todo el registro (uso con cuidado)"""
    registry = get_job_registry()
    success = registry.clear_all()
    if success:
        return {"message": "Registry cleared successfully"}
    return JSONResponse({"error": "Failed to clear registry"}, status_code=500)

# ========== FIN ENDPOINTS DE REGISTRO ==========

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    async with subscribers_lock:
        if job_id not in job_subscribers:
            job_subscribers[job_id]=set()
        job_subscribers[job_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        async with subscribers_lock:
            job_subscribers.get(job_id,set()).discard(websocket)

@app.websocket("/ws-monitor")
async def ws_monitor(websocket: WebSocket):
    await websocket.accept()
    monitor_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        pass
    finally:
        monitor_clients.remove(websocket)



if __name__ == "__main__":
    freeze_support()
    
    # Inicializar colas y estado compartido
    init_queues()

    # Lanzar procesos de impresoras
    for i in range(NUM_PRINTERS):
        p = Process(target=printer_process, args=(i, job_queue, event_queue, system_config, printer_state), daemon=True)
        p.start()
        printer_processes.append(p)

    # Iniciar servidor
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
