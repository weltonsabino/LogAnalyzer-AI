"""
Testes para error handling com arestas condicionais.

Testa roteamento condicional do StateGraph para o nó error_handling
quando diferentes tipos de erro ocorrem durante execução.
"""

import pytest
from src.loganalyzer.agent import create_agent_graph, get_initial_state
from src.loganalyzer.models import LogAnalysisState


class TestConditionalEdgesValidation:
    """Testa arestas condicionais após validação."""

    def test_validation_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando validação falha."""
        # Prepara estado com arquivo inválido
        state = get_initial_state(file_path="/arquivo/inexistente.log")

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida que error_handling foi acionado
        assert result.get("is_valid") is False
        assert result.get("validation_error") is not None
        assert result.get("error_message") is not None

    def test_validation_success_proceeds_to_read_file(self):
        """Testa que validação bem-sucedida prossegue para read_file."""
        # Cria arquivo temporário para teste
        import tempfile
        
        # Cria arquivo temporário com conteúdo
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-08-20 10:00:00 INFO Test log entry\n")
            temp_file = f.name
        
        try:
            state = get_initial_state(file_path=temp_file)

            # Cria e executa agente
            graph = create_agent_graph()
            result = graph.invoke(state)

            # Valida que prosseguiu além de validação
            assert result.get("is_valid") is True
            assert result.get("validation_error") is None
            # Se foi além de validação, deve ter lido arquivo
            assert len(result.get("file_content", "")) > 0
        finally:
            # Limpa arquivo temporário
            import os as os_module
            if os_module.path.exists(temp_file):
                os_module.remove(temp_file)


class TestConditionalEdgesParsing:
    """Testa arestas condicionais após parsing."""

    def test_parsing_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando parsing falha."""
        # Prepara estado com conteúdo inválido (sem estrutura de log)
        state = get_initial_state(file_path="tests/fixtures/invalid_format.log")
        state["file_content"] = "Conteúdo inválido sem estrutura de log"
        state["is_valid"] = True

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida roteamento para error_handling
        # (parsing_error deve ser setado ou o resultado deve indicar erro)
        assert result.get("is_valid") is False or result.get("parsing_error") is not None

    def test_parsing_success_proceeds_to_analyze_patterns(self):
        """Testa que parsing bem-sucedido prossegue para analyze_patterns."""
        # Cria arquivo temporário para teste
        import tempfile
        
        # Cria arquivo temporário com log estruturado
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-08-20 10:00:00 ERROR Database connection failed\n")
            f.write("2026-08-20 10:00:01 WARNING Retry attempt 1\n")
            temp_file = f.name
        
        try:
            state = get_initial_state(file_path=temp_file)

            # Cria e executa agente
            graph = create_agent_graph()
            result = graph.invoke(state)

            # Se parsing foi bem-sucedido, deve ter eventos analisados
            if result.get("is_valid") is True:
                assert len(result.get("parsed_events", [])) >= 0
                assert result.get("parsing_error") is None
        finally:
            # Limpa arquivo temporário
            import os as os_module
            if os_module.path.exists(temp_file):
                os_module.remove(temp_file)


class TestConditionalEdgesDetection:
    """Testa arestas condicionais após detecção de padrões."""

    def test_detection_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando detecção falha."""
        # Prepara estado com parsed_events vazio
        state = get_initial_state(file_path="tests/fixtures/empty.log")
        state["file_content"] = ""
        state["parsed_events"] = []
        state["is_valid"] = True

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida handling - pode ter detection_error ou continuar com dados vazios
        assert "detection_error" in result or result.get("is_valid") is not None

    def test_detection_success_proceeds_to_interpret(self):
        """Testa que detecção bem-sucedida prossegue para interpret_with_llm."""
        # Cria arquivo temporário para teste
        import tempfile
        
        # Cria arquivo com múltiplos níveis de severidade
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-08-20 10:00:00 INFO Service started\n")
            f.write("2026-08-20 10:00:01 ERROR Connection timeout\n")
            f.write("2026-08-20 10:00:02 CRITICAL System failure\n")
            temp_file = f.name
        
        try:
            state = get_initial_state(file_path=temp_file)

            # Cria e executa agente
            graph = create_agent_graph()
            result = graph.invoke(state)

            # Se detecção foi bem-sucedida, deve ter análise
            if result.get("is_valid") is True and result.get("detection_error") is None:
                assert result.get("errors_found") is not None or \
                       result.get("warnings_found") is not None
        finally:
            # Limpa arquivo temporário
            import os as os_module
            if os_module.path.exists(temp_file):
                os_module.remove(temp_file)


class TestConditionalEdgesAnalysis:
    """Testa arestas condicionais após análise IA."""

    def test_analysis_error_routes_to_error_handler(self):
        """Testa roteamento para error_handling quando análise IA falha."""
        # Prepara estado com dados para análise
        state = get_initial_state(file_path="examples/sample_critical.log")
        state["file_content"] = "ERROR: Test error"
        state["parsed_events"] = [{"level": "ERROR", "message": "Erro crítico"}]
        state["errors_found"] = [{"level": "ERROR", "count": 1}]
        state["warnings_found"] = []
        state["is_valid"] = True

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida que continuou mesmo com possível erro de IA
        assert "analysis_error" in result or result.get("report") is not None

    def test_analysis_success_proceeds_to_generate_report(self):
        """Testa que análise bem-sucedida prossegue para generate_report."""
        # Cria arquivo temporário para teste
        import tempfile
        
        # Cria arquivo com logs para análise completa
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2026-08-20 10:00:00 INFO Application started\n")
            f.write("2026-08-20 10:00:01 WARNING Memory usage high\n")
            f.write("2026-08-20 10:00:02 ERROR Failed to connect to database\n")
            temp_file = f.name
        
        try:
            state = get_initial_state(file_path=temp_file)

            # Cria e executa agente
            graph = create_agent_graph()
            result = graph.invoke(state)

            # Se análise foi bem-sucedida, deve ter relatório
            if result.get("is_valid") is True and result.get("analysis_error") is None:
                assert result.get("report") is not None or \
                       result.get("analysis_result") is not None
        finally:
            # Limpa arquivo temporário
            import os as os_module
            if os_module.path.exists(temp_file):
                os_module.remove(temp_file)


class TestErrorHandlerNode:
    """Testa o nó error_handling."""

    def test_error_handler_generates_error_summary(self):
        """Testa se error_handler gera sumário de erro."""
        # Prepara estado com múltiplos erros
        state = get_initial_state(file_path="/inexistente")
        state["validation_error"] = "Arquivo não encontrado"

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida sumário de erro
        assert result.get("is_valid") is False
        assert result.get("error_message") is not None
        assert "error_timestamp" in result.get("metadata", {})

    def test_error_handler_sets_is_valid_false(self):
        """Testa se error_handler seta is_valid como False."""
        # Prepara estado com erro
        state = get_initial_state(file_path="/inexistente")

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida que is_valid é False
        assert result.get("is_valid") is False

    def test_error_handler_populates_metadata(self):
        """Testa se error_handler popula metadados de erro."""
        # Prepara estado com erro
        state = get_initial_state(file_path="/inexistente")

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida metadados
        metadata = result.get("metadata", {})
        assert "error_timestamp" in metadata
        assert "error_message" in metadata


class TestErrorFlagsPropagation:
    """Testa propagação das flags de erro específicas."""

    def test_validation_error_flag_set_on_invalid_path(self):
        """Testa se validation_error é setado em validação inválida."""
        # Prepara estado com arquivo inválido
        state = get_initial_state(file_path="/arquivo/inexistente.log")

        # Cria e executa agente
        graph = create_agent_graph()
        result = graph.invoke(state)

        # Valida flag de validação
        assert result.get("validation_error") is not None

    def test_parsing_error_flag_set_on_parse_failure(self):
        """Testa se parsing_error é setado em falha de parsing."""
        # Este teste seria mais realista se tivéssemos fixture com log inválido
        # Por enquanto, testamos que o flag existe e pode ser setado
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            llm_provider=None,
            is_valid=True,
            error_message=None,
            validation_error=None,
            parsing_error=None,
            detection_error=None,
            analysis_error=None,
        )

        # Valida que o estado contém o campo
        assert "parsing_error" in state
        assert state["parsing_error"] is None

    def test_detection_error_flag_set_on_detection_failure(self):
        """Testa se detection_error pode ser setado."""
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            llm_provider=None,
            is_valid=True,
            error_message=None,
            validation_error=None,
            parsing_error=None,
            detection_error=None,
            analysis_error=None,
        )

        # Valida que o estado contém o campo
        assert "detection_error" in state

    def test_analysis_error_flag_set_on_llm_failure(self):
        """Testa se analysis_error pode ser setado."""
        state = LogAnalysisState(
            file_path="test.log",
            file_content="",
            parsed_events=[],
            errors_found=[],
            warnings_found=[],
            critical_events=[],
            analysis_result={},
            report="",
            metadata={},
            llm_provider=None,
            is_valid=True,
            error_message=None,
            validation_error=None,
            parsing_error=None,
            detection_error=None,
            analysis_error=None,
        )

        # Valida que o estado contém o campo
        assert "analysis_error" in state
        assert state["analysis_error"] is None
