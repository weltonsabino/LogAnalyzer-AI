"""
Módulo de governança e segurança do LogAnalyzer AI.

Define limites de autonomia, políticas de validação e proteção contra
entradas adversariais (prompt injection, path traversal, command injection).

Implementação: Task #32 (Segurança Avançada)
"""

import os
import re
from enum import Enum
from typing import List, Optional, Tuple


# ============================================
# CONSTANTES DE SEGURANÇA
# ============================================

# Tamanho máximo de entrada permitido (10MB)
MAX_INPUT_SIZE = 10 * 1024 * 1024

# Extensões de arquivo permitidas para análise
ALLOWED_FILE_EXTENSIONS = [".log", ".txt", ".csv", ".json"]

# Padrões bloqueados (regex) — detectam entradas maliciosas
BLOCKED_PATTERNS = [
    # Prompt injection
    r"(?i)ignore\s+(previous|all)\s+(instructions|rules)",
    r"(?i)system\s*:\s*(ignore|override|bypass)",
    r"(?i)you\s+are\s+now\s+(a|an)\s+",
    r"(?i)forget\s+(everything|all|previous)",
    r"(?i)new\s+instructions?\s*:",
    # SQL injection
    r";\s*DROP\s+",
    r";\s*DELETE\s+FROM",
    r";\s*INSERT\s+INTO",
    r"'\s*OR\s+'1'\s*=\s*'1",
    r"--\s*$",
    # Command injection
    r"\$\(",
    r"`[^`]+`",
    r"\|\s*rm\s+",
    r"\|\s*del\s+",
    r"&&\s*(rm|del|format|shutdown)",
    r";\s*(rm|del|format|shutdown)",
    # Path traversal
    r"\.\./",
    r"\.\.\.",
    r"/etc/(passwd|shadow|hosts)",
    r"C:\\Windows\\System32",
    r"%00",  # Null byte injection
]


# ============================================
# ENUMERAÇÃO DE NÍVEIS DE AUTONOMIA
# ============================================

class AutonomyLevel(Enum):
    """
    Níveis de autonomia do agente LogAnalyzer AI.

    Define o que o agente pode fazer em cada nível:
    - READ_ONLY: Apenas leitura de dados
    - ANALYZE: Leitura + análise (padrão)
    - RECOMMEND: Análise + recomendações de ação
    - EXECUTE: Execução de ações (requer aprovação humana)
    """

    READ_ONLY = "read_only"
    ANALYZE = "analyze"
    RECOMMEND = "recommend"
    EXECUTE = "execute"


# Mapeamento de ações permitidas por nível
ACTIONS_BY_LEVEL = {
    AutonomyLevel.READ_ONLY: ["read_file", "list_files"],
    AutonomyLevel.ANALYZE: ["read_file", "list_files", "parse_log", "detect_patterns", "analyze"],
    AutonomyLevel.RECOMMEND: [
        "read_file", "list_files", "parse_log", "detect_patterns",
        "analyze", "generate_report", "recommend",
    ],
    AutonomyLevel.EXECUTE: [
        "read_file", "list_files", "parse_log", "detect_patterns",
        "analyze", "generate_report", "recommend",
        "write_file", "delete_file", "execute_command",
    ],
}

# Ações que sempre requerem aprovação humana
ACTIONS_REQUIRING_APPROVAL = [
    "write_file",
    "delete_file",
    "execute_command",
    "modify_config",
    "send_notification",
]


# ============================================
# VALIDADOR DE ENTRADAS
# ============================================

class InputValidator:
    """
    Valida e sanitiza entradas contra padrões adversariais.

    Detecta e bloqueia:
    - Prompt injection
    - Path traversal
    - Command injection
    - SQL injection
    - Entradas excessivamente grandes
    - Extensões de arquivo não permitidas
    """

    def __init__(
        self,
        blocked_patterns: Optional[List[str]] = None,
        max_input_size: int = MAX_INPUT_SIZE,
        allowed_extensions: Optional[List[str]] = None,
    ):
        """
        Inicializa validador com padrões de bloqueio.

        Argumentos:
            blocked_patterns: Lista de regex para bloquear (padrão: BLOCKED_PATTERNS)
            max_input_size: Tamanho máximo de entrada em bytes
            allowed_extensions: Extensões de arquivo permitidas
        """
        # Compila padrões regex para performance
        self.blocked_patterns = blocked_patterns or BLOCKED_PATTERNS
        self._compiled_patterns = [
            re.compile(pattern) for pattern in self.blocked_patterns
        ]
        self.max_input_size = max_input_size
        self.allowed_extensions = allowed_extensions or ALLOWED_FILE_EXTENSIONS

    def validate_input(self, input_data: str) -> Tuple[bool, str]:
        """
        Valida entrada contra todos os padrões de segurança.

        Argumentos:
            input_data: Dados de entrada a validar

        Retorno:
            Tupla (is_safe, message):
            - is_safe: True se entrada é segura
            - message: Descrição do resultado ou motivo de rejeição
        """
        # Verifica tamanho da entrada
        if len(input_data.encode("utf-8")) > self.max_input_size:
            return False, (
                f"Entrada excede tamanho máximo permitido "
                f"({self.max_input_size} bytes)"
            )

        # Verifica padrões adversariais
        for pattern in self._compiled_patterns:
            match = pattern.search(input_data)
            if match:
                return False, (
                    f"Padrão adversarial detectado: '{match.group()}' "
                    f"(regra: {pattern.pattern})"
                )

        return True, "Entrada validada com sucesso"

    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Valida caminho de arquivo contra padrões de segurança.

        Argumentos:
            file_path: Caminho do arquivo a validar

        Retorno:
            Tupla (is_safe, message)
        """
        # Verifica se caminho está vazio
        if not file_path or not file_path.strip():
            return False, "Caminho de arquivo vazio"

        # Verifica tamanho do caminho
        if len(file_path) > 1024:
            return False, "Caminho de arquivo excede tamanho máximo (1024 chars)"

        # Verifica path traversal
        if ".." in file_path:
            return False, f"Path traversal detectado no caminho: {file_path}"

        # Verifica null byte injection
        if "\x00" in file_path or "%00" in file_path:
            return False, "Null byte injection detectado no caminho"

        # Verifica extensão permitida
        _, extension = os.path.splitext(file_path)
        if extension.lower() not in self.allowed_extensions:
            return False, (
                f"Extensão não permitida: '{extension}'. "
                f"Permitidas: {self.allowed_extensions}"
            )

        # Verifica padrões adversariais no caminho
        is_safe, message = self.validate_input(file_path)
        if not is_safe:
            return False, f"Caminho contém padrão adversarial: {message}"

        return True, "Caminho de arquivo validado com sucesso"

    def sanitize_input(self, raw_input: str) -> str:
        """
        Sanitiza entrada removendo padrões perigosos.

        Argumentos:
            raw_input: Entrada bruta a sanitizar

        Retorno:
            Entrada limpa com padrões perigosos removidos
        """
        # Remove padrões adversariais
        sanitized = raw_input
        for pattern in self._compiled_patterns:
            sanitized = pattern.sub("[BLOCKED]", sanitized)

        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")

        # Remove caracteres de controle (exceto newline e tab)
        sanitized = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)

        return sanitized


# ============================================
# POLÍTICA DE GOVERNANÇA
# ============================================

class GovernancePolicy:
    """
    Define políticas de autonomia e controle de ações do agente.

    Determina:
    - Quais ações são permitidas no nível atual
    - Quais ações requerem aprovação humana
    - Validação de entradas contra padrões adversariais
    """

    def __init__(
        self,
        autonomy_level: AutonomyLevel = AutonomyLevel.ANALYZE,
        allowed_actions: Optional[List[str]] = None,
        blocked_patterns: Optional[List[str]] = None,
    ):
        """
        Inicializa política de governança.

        Argumentos:
            autonomy_level: Nível de autonomia do agente
            allowed_actions: Lista customizada de ações permitidas (sobrescreve padrão)
            blocked_patterns: Padrões adicionais a bloquear
        """
        self.autonomy_level = autonomy_level

        # Define ações permitidas baseado no nível
        if allowed_actions is not None:
            self.allowed_actions = allowed_actions
        else:
            self.allowed_actions = ACTIONS_BY_LEVEL.get(
                autonomy_level, ACTIONS_BY_LEVEL[AutonomyLevel.READ_ONLY]
            )

        # Inicializa validador de entrada
        self.input_validator = InputValidator(blocked_patterns=blocked_patterns)

    def can_execute_action(self, action_name: str) -> bool:
        """
        Verifica se uma ação é permitida no nível atual de autonomia.

        Argumentos:
            action_name: Nome da ação a verificar

        Retorno:
            True se ação é permitida, False caso contrário
        """
        return action_name in self.allowed_actions

    def requires_human_approval(self, action_name: str) -> bool:
        """
        Verifica se uma ação requer aprovação humana antes de execução.

        Argumentos:
            action_name: Nome da ação a verificar

        Retorno:
            True se ação requer aprovação, False caso contrário
        """
        return action_name in ACTIONS_REQUIRING_APPROVAL

    def validate_input(self, input_data: str) -> Tuple[bool, str]:
        """
        Valida entrada contra padrões adversariais usando InputValidator.

        Argumentos:
            input_data: Dados de entrada a validar

        Retorno:
            Tupla (is_safe, message)
        """
        return self.input_validator.validate_input(input_data)

    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Valida caminho de arquivo contra padrões de segurança.

        Argumentos:
            file_path: Caminho a validar

        Retorno:
            Tupla (is_safe, message)
        """
        return self.input_validator.validate_file_path(file_path)

    def sanitize_input(self, raw_input: str) -> str:
        """
        Sanitiza entrada removendo padrões perigosos.

        Argumentos:
            raw_input: Entrada bruta

        Retorno:
            Entrada limpa
        """
        return self.input_validator.sanitize_input(raw_input)

    def get_policy_summary(self) -> dict:
        """
        Retorna resumo da política atual para metadados/auditoria.

        Retorno:
            Dicionário com resumo da política ativa
        """
        return {
            "autonomy_level": self.autonomy_level.value,
            "allowed_actions": self.allowed_actions,
            "blocked_patterns_count": len(self.input_validator.blocked_patterns),
            "max_input_size": self.input_validator.max_input_size,
            "allowed_extensions": self.input_validator.allowed_extensions,
        }
