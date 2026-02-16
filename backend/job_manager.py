import threading
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ExportJobManager:
    """Manages a single background export job with status and locking."""

    def __init__(self, db_handler, data_exporter, active_sessions: Dict[str, Any]):
        self._db = db_handler
        self._exporter = data_exporter
        self._sessions = active_sessions

        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._status: Dict[str, Any] = self._make_idle_status()

    def _make_idle_status(self) -> Dict[str, Any]:
        return {
            'job_id': None,
            'state': 'idle',  # idle, running, completed, failed, cancelled
            'started_at': None,
            'finished_at': None,
            'current_table': None,
            'tables_total': 0,
            'tables_done': 0,
            'table_rows_exported': 0,
            'total_rows_exported': 0,
            'error': None,
            'cancel_requested': False
        }

    def start_export(self, session_id: str, tables: List[str], options: Dict[str, Any]):
        """Start export in background. Raises RuntimeError if another job is running."""
        if not self._lock.acquire(blocking=False):
            raise RuntimeError('An export job is already running')

        # validate session
        if session_id not in self._sessions:
            self._lock.release()
            raise RuntimeError('Session not found')

        access_conn = self._sessions[session_id].get('access_connection')
        mysql_conn = self._sessions[session_id].get('mysql_connection')

        if not access_conn or not mysql_conn:
            self._lock.release()
            raise RuntimeError('Missing database connections in session')

        # initialize status
        self._status = self._make_idle_status()
        self._status.update({
            'job_id': str(uuid.uuid4()),
            'state': 'running',
            'started_at': datetime.now().isoformat(),
            'tables_total': len(tables),
            'tables_done': 0,
            'total_rows_exported': 0,
            'cancel_requested': False
        })

        # start thread
        self._thread = threading.Thread(
            target=self._run_export,
            args=(session_id, tables, options),
            daemon=True
        )
        self._thread.start()

        return self._status['job_id']

    def request_cancel(self):
        self._status['cancel_requested'] = True

    def get_status(self) -> Dict[str, Any]:
        return dict(self._status)

    def _run_export(self, session_id: str, tables: List[str], options: Dict[str, Any]):
        try:
            access_conn = self._sessions[session_id]['access_connection']
            mysql_conn = self._sessions[session_id]['mysql_connection']

            override_data = options.get('override_data', True)
            create_tables = options.get('create_tables', True)
            batch_size = int(options.get('batch_size', 1000))

            for idx, table_name in enumerate(tables, start=1):
                if self._status['cancel_requested']:
                    self._status['state'] = 'cancelled'
                    logger.info('Export cancelled by request')
                    break

                self._status['current_table'] = table_name
                self._status['table_rows_exported'] = 0

                # create table if requested
                if create_tables:
                    try:
                        self._exporter._create_mysql_table(mysql_conn, table_name,
                                                           self._db.get_table_schema(access_conn, table_name, 'access'),
                                                           drop_if_exists=False)
                    except Exception as e:
                        logger.warning(f"Could not create table {table_name}: {e}")

                # clear data if override
                if override_data:
                    try:
                        self._exporter._clear_mysql_table(mysql_conn, table_name)
                    except Exception:
                        pass

                # stream data from Access and insert to MySQL
                for chunk in self._db.read_table_data(access_conn, table_name, 'access', batch_size):
                    if self._status['cancel_requested']:
                        break

                    if not chunk.empty:
                        rows_inserted = self._exporter._insert_batch(mysql_conn, table_name, chunk)
                        self._status['table_rows_exported'] += rows_inserted
                        self._status['total_rows_exported'] += rows_inserted

                # table finished
                self._status['tables_done'] = idx

            if self._status['state'] != 'cancelled':
                self._status['state'] = 'completed'
                self._status['finished_at'] = datetime.now().isoformat()
                logger.info('Export job completed')

        except Exception as e:
            logger.exception('Export job failed')
            self._status['state'] = 'failed'
            self._status['error'] = str(e)
            self._status['finished_at'] = datetime.now().isoformat()

        finally:
            # release lock so another job can run
            try:
                self._lock.release()
            except RuntimeError:
                pass
