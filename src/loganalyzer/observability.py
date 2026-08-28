"""
Módulo de observabilidade avançada para rastreamento de execução.

Fornece TraceCollector centralizado com execution_id único e middleware
para instrumentar nós do agente LangGraph.
"""

import uuid
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
from functools import wraps


# ============================================
# Constantes de Observabilidade
# ============================================

TRACE_EVENTS = [
    "node_start",
    "node_end",
    "error",
    "warning",
    "timeout",
    "retry"
]

TRACE_LEVELS = {
    "DEBUG": 0,
    "INFO": 1,
    "WARN": 2,
    "ERROR": 3
}


# ============================================
# Classe TraceCollector
# ============================================

class TraceCollector:
    """
    Centraliza coleta de traces e correlação de execução.

    Responsável por:
    - Gerar execution_id único (UUID) para cada execução
    - Armazenar traces com timestamp em ordem cronológica
    - Correlacionar traces por execution_id
    - Gerar resumo de correlação com duração total
    """

    def __init__(self, execution_id: Optional[str] = None):
        """
        Inicializa TraceCollector com ID único de execução.

        Argumentos:
            execution_id: ID de execução (gerado se None)
        """
        # Gera ou usa execution_id fornecido
        self.execution_id = execution_id or self._generate_execution_id()
        # Lista de traces ordenada por timestamp
        self.traces: List[Dict[str, Any]] = []
        # Timestamp de início da execução
        self.start_time = time.time()

    def _generate_execution_id(self) -> str:
        """
        Gera UUID único para execução.

        Retorno:
            String UUID no formato padrão
        """
        return str(uuid.uuid4())

    def add_trace(self, node_name: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        Adiciona trace com timestamp automático.

        Argumentos:
            node_name: Nome do nó que gerou o trace
            event_type: Tipo de evento (node_start, node_end, error, warning)
            data: Dados adicionais do trace
        """
        # Cria trace com timestamp ISO
        trace = {
            "execution_id": self.execution_id,
            "node_name": node_name,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        # Adiciona à lista de traces
        self.traces.append(trace)

    def get_traces(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de traces ordenada por timestamp.

        Retorno:
            Lista de traces em ordem cronológica
        """
        # Retorna todos os traces armazenados
        return self.traces

    def get_correlation_summary(self) -> Dict[str, Any]:
        """
        Retorna sumário correlacionado de execução.

        Retorno:
            Dicionário com execution_id, trace_count, duration, status
        """
        # Calcula duração total em segundos
        end_time = time.time()
        duration = end_time - self.start_time

        # Conta eventos por tipo
        event_counts = {}
        for trace in self.traces:
            event_type = trace.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Determina status geral (ERROR se houve error, warning se houve warning, OK senão)
        status = "OK"
        if event_counts.get("error", 0) > 0:
            status = "ERROR"
        elif event_counts.get("warning", 0) > 0:
            status = "WARNING"

        # Retorna sumário estruturado
        return {
            "execution_id": self.execution_id,
            "trace_count": len(self.traces),
            "duration_seconds": round(duration, 3),
            "event_counts": event_counts,
            "status": status,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(end_time).isoformat()
        }


# ============================================
# Decorators para Observabilidade
# ============================================

def with_timeout(seconds: int = 30) -> Callable:
    """
    Decorator que limita tempo de execução de função.

    Argumentos:
        seconds: Tempo máximo em segundos

    Retorno:
        Função decorada com timeout
    """
    def decorator(func: Callable) -> Callable:
        """Aplica timeout a uma função."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Executa função com limite de tempo."""
            import signal

            def timeout_handler(signum, frame):
                """Handler para timeout."""
                raise TimeoutError(f"Função {func.__name__} excedeu {seconds}s")

            # Configurar signal para timeout (funciona em Unix/Linux)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancela alarm
                return result
            except (AttributeError, ValueError):
                # Em Windows, signal.SIGALRM não existe
                # Apenas executa função sem timeout
                return func(*args, **kwargs)

        return wrapper
    return decorator


def with_retry(max_attempts: int = 3, backoff: float = 1.5) -> Callable:
    """
    Decorator que implementa retry automático com backoff exponencial.

    Argumentos:
        max_attempts: Número máximo de tentativas
        backoff: Fator de backoff exponencial

    Retorno:
        Função decorada com retry
    """
    def decorator(func: Callable) -> Callable:
        """Aplica retry a uma função."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Executa função com retry automático."""
            attempt = 0
            wait_time = 1

            while attempt < max_attempts:
                try:
                    # Tenta executar função
                    return func(*args, **kwargs)
                except (TimeoutError, PermissionError, OSError):
                    # Erros transientes que justificam retry
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    # Aguarda antes de próxima tentativa
                    time.sleep(wait_time)
                    wait_time *= backoff
            return None

        return wrapper
    return decorator


def observability_middleware(collector: Optional['TraceCollector'] = None) -> Callable:
    """
    Decorator que instrumenta função com observabilidade.

    Argumentos:
        collector: TraceCollector para registrar traces

    Retorno:
        Função decorada com observabilidade
    """
    def decorator(func: Callable) -> Callable:
        """Aplica observabilidade a uma função."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Executa função com instrumentação."""
            if collector is None:
                # Se sem collector, apenas executa função
                return func(*args, **kwargs)

            # Registra início de execução
            collector.add_trace(
                node_name=func.__name__,
                event_type="node_start",
                data={"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
            )

            start = time.time()
            try:
                # Executa função
                result = func(*args, **kwargs)
                # Registra fim bem-sucedido
                duration = time.time() - start
                collector.add_trace(
                    node_name=func.__name__,
                    event_type="node_end",
                    data={"duration_seconds": round(duration, 3), "success": True}
                )
                return result
            except Exception as e:
                # Registra erro
                duration = time.time() - start
                collector.add_trace(
                    node_name=func.__name__,
                    event_type="error",
                    data={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "duration_seconds": round(duration, 3)
                    }
                )
                raise

        return wrapper
    return decorator
