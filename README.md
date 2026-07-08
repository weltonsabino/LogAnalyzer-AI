# LogAnalyzer AI

> Um agente de IA para automatizar análise de arquivos de log usando LangGraph

## 📋 Visão Geral

**LogAnalyzer AI** é um agente inteligente que analisa automaticamente arquivos de log, identificando padrões importantes (erros, avisos, exceções) e gerando relatórios técnicos estruturados.

### Objetivo

Demonstrar o uso de agentes LangGraph em um caso real de análise de logs, com componentes como:
- Estado compartilhado
- Nós e fluxo de execução
- Ferramentas integradas
- Validações e contexto
- Respostas estruturadas

### Stack

- **Python** 3.10+
- **LangGraph** para construção do agente
- **LangChain** para integrações
- **Pytest** para testes

---

## 🚀 Setup

### 1. Clonar Repositório
```bash
git clone <seu-repositorio>
cd mini-projeto-LogAnalyzer-AI
```

### 2. Criar Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

---

## 📖 Como Usar

### Executar o Agente
```bash
python src/loganalyzer/main.py --file /caminho/para/log.log
```

### Executar Testes
```bash
pytest tests/ -v
```

### Linter e Formatter
```bash
pylint src/
black src/
```

---

## 📝 Exemplos

### Entrada
```
arquivo: /home/user/app.log
```

### Saída Esperada
```
Relatório de Análise de Log
===========================
Total de eventos: 245
Erros encontrados: 12
Avisos encontrados: 34
Exceções críticas: 3

Principais problemas:
1. NullPointerException em UserService.java:45
2. OutOfMemory no módulo de cache
3. Timeout em conexão com banco de dados

Recomendações:
- Revisar tratamento de nulos em UserService
- Aumentar heap memory
- Otimizar queries ao banco
```

---

## 🏗️ Arquitetura

### Estrutura do Projeto
```
src/loganalyzer/
├── main.py              # Entrypoint
├── agent.py             # StateGraph
├── models.py            # Modelos (State)
├── nodes.py             # Funções dos nós
├── tools/               # Ferramentas
├── analysis/            # Análise
└── utils/               # Utilitários

tests/                  # Testes
examples/               # Exemplos
docs/                   # Documentação
```

### Fluxo do Agente
```
Entrada → Validação → Leitura → Análise → Processamento → Relatório
```

---

## 🔐 Segurança

- ✅ Credenciais em `.env` (não versionado)
- ✅ `.gitignore` configurado
- ✅ `.env.example` sem valores reais
- ✅ Validações de entrada

---

## 📚 Documentação

- [Pré-requisitos](.kiro/steering/project-guidelines.md)
- [Requisitos Completos](docs/PROJECT_REQUIREMENTS.md)
- [Arquitetura do Agente](docs/ARCHITECTURE.md)
- [Prompts Utilizados](docs/prompts.md)

---

## 🤝 Contribuição

Em projetos em grupo, cada integrante deve:
- Fazer commits frequentes com autoria clara
- Implementar funcionalidades específicas
- Documentar suas contribuições
- Revisar código de colegas

---

## ✅ Checklist de Entrega

- [ ] Repositório público no GitHub
- [ ] Código do agente implementado
- [ ] Ferramenta integrada e funcional
- [ ] README.md completo
- [ ] prompts.md preenchido
- [ ] Exemplos de entrada/saída
- [ ] Apresentação (2 slides)
- [ ] Testes básicos
- [ ] Commits semânticos
- [ ] Sem credenciais versionadas

---

## 📞 Contato

**Projeto:** LogAnalyzer AI  
**Disciplina:** IA para Desenvolvedores [T2]  
**Prazo:** 20/07/2026 às 22h  
**Avaliação:** 30% do módulo

---

**Última atualização:** Junho 2026
