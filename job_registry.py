import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

class JobRegistry:
    """Gestor de registro de trabajos de impresión en base de datos SQLite"""
    
    def __init__(self, db_path: str = "job_registry.db"):
        """
        Inicializa el registro de trabajos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Crea la tabla de registro si no existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                timestamp_arrival TIMESTAMP NOT NULL,
                printer_id TEXT NOT NULL,
                num_pages INTEGER NOT NULL,
                exit_time TIMESTAMP NOT NULL,
                pdf_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def register_job(self, job_id: str, filename: str, timestamp_arrival: datetime,
                    printer_id: str, num_pages: int, exit_time: datetime, 
                    pdf_path: str) -> bool:
        """
        Registra un trabajo completado en la base de datos
        
        Args:
            job_id: ID único del trabajo
            filename: Nombre original del archivo
            timestamp_arrival: Timestamp de llegada del trabajo
            printer_id: ID de la impresora que procesó el trabajo
            num_pages: Número de páginas imprimidas
            exit_time: Timestamp de finalización
            pdf_path: Ruta relativa del PDF guardado
            
        Returns:
            True si se registró correctamente, False en caso contrario
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO job_registry 
                (job_id, filename, timestamp_arrival, printer_id, num_pages, exit_time, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, 
                filename, 
                timestamp_arrival.isoformat() if isinstance(timestamp_arrival, datetime) else timestamp_arrival,
                printer_id, 
                num_pages, 
                exit_time.isoformat() if isinstance(exit_time, datetime) else exit_time,
                pdf_path
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print(f"Error: El trabajo {job_id} ya está registrado")
            return False
        except Exception as e:
            print(f"Error al registrar trabajo: {e}")
            return False
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene los datos de un trabajo del registro
        
        Args:
            job_id: ID del trabajo a buscar
            
        Returns:
            Diccionario con los datos del trabajo o None si no existe
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM job_registry WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_jobs(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene todos los trabajos registrados
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Número de registros a saltar desde el inicio
            
        Returns:
            Lista de diccionarios con los datos de los trabajos
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if limit:
            cursor.execute("""
                SELECT * FROM job_registry 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
        else:
            cursor.execute("SELECT * FROM job_registry ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_jobs_by_printer(self, printer_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los trabajos procesados por una impresora específica
        
        Args:
            printer_id: ID de la impresora
            
        Returns:
            Lista de diccionarios con los datos de los trabajos
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM job_registry 
            WHERE printer_id = ? 
            ORDER BY created_at DESC
        """, (printer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del registro
        
        Returns:
            Diccionario con estadísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de trabajos
        cursor.execute("SELECT COUNT(*) as total FROM job_registry")
        total_jobs = cursor.fetchone()[0]
        
        # Total de páginas impresas
        cursor.execute("SELECT SUM(num_pages) as total_pages FROM job_registry")
        total_pages = cursor.fetchone()[0] or 0
        
        # Trabajos por impresora
        cursor.execute("""
            SELECT printer_id, COUNT(*) as count, SUM(num_pages) as total_pages
            FROM job_registry
            GROUP BY printer_id
        """)
        printer_stats = []
        for row in cursor.fetchall():
            printer_stats.append({
                "printer_id": row[0],
                "job_count": row[1],
                "total_pages": row[2]
            })
        
        conn.close()
        
        return {
            "total_jobs": total_jobs,
            "total_pages": total_pages,
            "printer_statistics": printer_stats
        }
    
    def delete_job(self, job_id: str) -> bool:
        """
        Elimina un trabajo del registro
        
        Args:
            job_id: ID del trabajo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM job_registry WHERE job_id = ?", (job_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error al eliminar trabajo: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Elimina todos los registros (uso con cuidado)
        
        Returns:
            True si se limpió correctamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM job_registry")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al limpiar registro: {e}")
            return False


# Instancia global del registro
_job_registry = None

def get_job_registry(db_path: str = "job_registry.db") -> JobRegistry:
    """
    Obtiene la instancia global del registro de trabajos
    
    Args:
        db_path: Ruta al archivo de base de datos SQLite
        
    Returns:
        Instancia de JobRegistry
    """
    global _job_registry
    if _job_registry is None:
        _job_registry = JobRegistry(db_path)
    return _job_registry
