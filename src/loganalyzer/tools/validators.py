"""
Ferramentas de validação para o LogAnalyzer AI.

Fornece funções para validar entrada, arquivo e dados de processamento.
"""

import os
from typing import Tuple


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Valida se o caminho do arquivo é acessível e legível.

    Argumentos:
        file_path: Caminho do arquivo de log a validar

    Retorno:
        Tupla (is_valid, message) onde:
        - is_valid: True se arquivo existe e é legível
        - message: Descrição do resultado ou erro
    """
    # Valida se file_path foi fornecido
    if not file_path:
        return False, "Caminho do arquivo não foi fornecido"

    # Valida se arquivo existe
    if not os.path.exists(file_path):
        return False, f"Arquivo não encontrado: {file_path}"

    # Valida se é arquivo (não diretório)
    if not os.path.isfile(file_path):
        return False, f"Caminho não é um arquivo: {file_path}"

    # Valida permissões de leitura
    if not os.access(file_path, os.R_OK):
        return False, f"Sem permissão de leitura: {file_path}"

    return True, f"Arquivo validado: {file_path}"


def validate_file_content(content: str) -> Tuple[bool, str]:
    """
    Valida se o conteúdo do arquivo é válido para processamento.

    Argumentos:
        content: Conteúdo do arquivo a validar

    Retorno:
        Tupla (is_valid, message)
    """
    # Valida se conteúdo não está vazio
    if not content or len(content.strip()) == 0:
        return False, "Conteúdo do arquivo está vazio"

    return True, f"Conteúdo validado ({len(content)} caracteres)"
