---
inclusion: always
---

# Convenções de Estilo de Código — LogAnalyzer AI

Este documento define as regras de estilo de código que DEVEM ser seguidas em TODAS as implementações do projeto.

## 🎯 Regra Fundamental

**TODO CÓDIGO DEVE SEGUIR ESTE PADRÃO:**

- ✅ **Comentários em português**
- ✅ **Variáveis em inglês**
- ✅ **Funções em inglês**
- ✅ **Docstrings em português**
- ✅ **Nomes de classes em inglês**
- ✅ **Nomes de módulos em inglês**

## 📋 Exemplos Corretos

### Python — Arquivo Completo

```python
"""
Descrição do módulo em português.

Explica o propósito e responsabilidade do módulo.
"""

# Importações
from typing import Dict, List, Optional


class DataProcessor:
    """
    Processa dados de entrada e retorna resultados estruturados.
    
    Atributos:
        input_data: Dados de entrada para processamento
        output_format: Formato desejado da saída
    """
    
    def __init__(self, input_data: List[Dict], output_format: str = "json"):
        """
        Inicializa o processador com dados de entrada.
        
        Argumentos:
            input_data: Lista de dicionários com dados brutos
            output_format: Formato de saída (json, xml, csv)
        """
        # Armazena dados de entrada para processamento
        self.input_data = input_data
        # Define formato da saída
        self.output_format = output_format
    
    def process(self) -> Dict:
        """
        Executa o processamento dos dados.
        
        Retorno:
            Dicionário com dados processados no formato especificado
        """
        # Valida dados de entrada antes de processar
        if not self._validate_input():
            raise ValueError("Dados de entrada inválidos")
        
        # Processa cada item dos dados
        result = {}
        for item in self.input_data:
            # Extrai campos relevantes do item
            processed_item = self._extract_fields(item)
            # Adiciona ao resultado
            result[item.get("id")] = processed_item
        
        return result
    
    def _validate_input(self) -> bool:
        """
        Valida se os dados de entrada estão corretos.
        
        Retorno:
            True se válido, False caso contrário
        """
        # Verifica se input_data não está vazio
        return len(self.input_data) > 0
    
    def _extract_fields(self, item: Dict) -> Dict:
        """
        Extrai campos relevantes de um item.
        
        Argumentos:
            item: Dicionário com dados do item
        
        Retorno:
            Dicionário com campos extraídos
        """
        # Define campos que serão extraídos
        fields_to_extract = ["name", "value", "timestamp"]
        
        # Extrai apenas campos definidos
        extracted = {
            field: item.get(field)
            for field in fields_to_extract
            if field in item
        }
        
        return extracted
```

### Testes

```python
"""
Testes para o módulo de processamento de dados.
"""

import pytest
from src.processors import DataProcessor


class TestDataProcessor:
    """Testa a classe DataProcessor."""
    
    def test_initialization_with_valid_data(self):
        """Testa inicialização com dados válidos."""
        # Prepara dados de entrada
        input_data = [{"id": 1, "name": "item1"}]
        
        # Cria instância do processador
        processor = DataProcessor(input_data)
        
        # Valida se foi inicializado corretamente
        assert processor.input_data == input_data
    
    def test_process_returns_dict(self):
        """Testa se processo retorna dicionário."""
        # Prepara dados de teste
        input_data = [{"id": 1, "name": "test", "value": 100}]
        
        # Executa processamento
        processor = DataProcessor(input_data)
        result = processor.process()
        
        # Verifica tipo de retorno
        assert isinstance(result, dict)
    
    def test_validate_input_empty_data(self):
        """Testa validação com dados vazios."""
        # Cria processador com dados vazios
        processor = DataProcessor([])
        
        # Valida se detecção de vazio funciona
        assert not processor._validate_input()
```

## 🔍 Checklist de Implementação

Antes de finalizar qualquer código, verificar:

- [ ] Todos os comentários estão em português
- [ ] Todas as variáveis estão em inglês
- [ ] Todas as funções estão em inglês
- [ ] Todas as docstrings estão em português
- [ ] Nenhuma mistura de idiomas em variáveis ou funções
- [ ] Código segue PEP 8 (para Python)
- [ ] Linter passa (pylint ≥ 8/10)
- [ ] Testes passam 100%

## ❌ Exemplos Incorretos (NÃO FAZER)

```python
# ❌ ERRADO: Comentário em inglês
# This function processes data
def process_data(dados):
    pass

# ❌ ERRADO: Variável em português
arquivo_entrada = "log.txt"

# ❌ ERRADO: Mistura de idiomas
def processar_events():  # Função português + inglês misturados
    pass

# ❌ ERRADO: Docstring em inglês
def analyze_log(file_path):
    """Analyzes a log file and returns results."""
    pass
```

## ✅ Como Verificar

### Verificar Padrão Manualmente

```bash
# Procurar variáveis em português no código
grep -r "variável_em_português" src/

# Procurar comentários em inglês
grep -r "# This" src/
grep -r "# The" src/
```

### Linter com Configuração Recomendada

```bash
# Validar estilo geral
pylint src/ --disable=C0111,C0114,W0511

# Verificar naming conventions
pylint src/ --load-plugins=pylint.extensions.naming
```

## 🎓 Referência Rápida

| Elemento | Idioma | Exemplo |
|----------|--------|---------|
| Comentário | PT | `# Valida dados de entrada` |
| Variável | EN | `input_data = []` |
| Função | EN | `def validate_input()` |
| Classe | EN | `class DataProcessor` |
| Docstring | PT | `"""Processa dados de entrada."""` |
| Constante | EN | `MAX_RETRIES = 3` |
| Argumento | EN | `def process(file_path: str)` |
| Campo de classe | EN | `self.output_format = "json"` |

## 📝 Regras Especiais

### Docstrings em Python

**Formato obrigatório:**

```python
def function_name(param1: str, param2: int) -> str:
    """
    Descrição breve do que a função faz.
    
    Descrição mais longa se necessário, explicando o comportamento,
    casos especiais, e qualquer informação importante.
    
    Argumentos:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro
    
    Retorno:
        Descrição do valor retornado
    
    Levanta:
        ValueError: Se param1 estiver vazio
        TypeError: Se param2 não for inteiro
    """
    pass
```

### Comentários em Bloco

**Formato obrigatório:**

```python
# ============================================
# Seção Principal
# ============================================

# Descrição do que será feito neste bloco
# com múltiplas linhas se necessário
variable = process(data)

# Validação intermediária
if not is_valid(variable):
    raise ValueError("Dados inválidos")
```

## 🚀 Aplicação Automática

Este padrão é **OBRIGATÓRIO** em todas as implementações.

Sempre que novo código for escrito:

1. **Comentários** → Português
2. **Variáveis/Funções** → Inglês
3. **Docstrings** → Português
4. **Testes** → Seguir mesmo padrão

---

**Última atualização:** Julho 2026  
**Versão:** 1.0  
**Status:** ✅ ATIVO E OBRIGATÓRIO

