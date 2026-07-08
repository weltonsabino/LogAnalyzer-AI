# Padrão de Títulos para Issues no GitHub

Este documento define o padrão de nomenclatura para títulos de issues no projeto CineRank AI.

> **Referência**: Este arquivo documenta os prefixos de título utilizados na seção `title` dos seguintes templates:
> - `title: "[STORY] "` → [`user_story_template.yml`](../assets/user_story_template.yml)
> - `title: "[EPIC] "` → [`epic_template.yml`](../assets/epic_template.yml)
> - `title: "[TECH] "` → [`tech_template.yml`](../assets/tech_template.yml)
> - `title: "[DOCS] "` → [`docs_template.yml`](../assets/docs_template.yml)

## Estrutura dos Títulos

Os títulos das issues devem seguir o formato:

```
[TIPO] Descrição clara e objetiva da issue
```

## Tipos de Issues

### [EPIC]
- **Quando usar**: Issues marcadas com a label `epic`
- **Propósito**: Agrupa múltiplas issues relacionadas (stories, tasks, bugs)
- **Características**: 
  - Issue pai que organiza outras issues
  - Representa uma iniciativa maior ou tema de trabalho
  - Pode conter múltiplas stories e tasks
- **Exemplo**: `[EPIC] Implementação do sistema de avaliação de filmes`

### [STORY]
- **Quando usar**: Issues marcadas com a label `story`
- **Propósito**: Criação de uma nova funcionalidade
- **Características**:
  - Representa uma user story
  - Descreve valor para o usuário final
  - Pode estar vinculada a um EPIC
- **Exemplo**: `[STORY] Como usuário, quero cadastrar um filme para avaliá-lo posteriormente`

### [DOCS]
- **Quando usar**: Issues marcadas com a label `docs`
- **Propósito**: Criação ou atualização de documentação
- **Características**:
  - Documentos de detalhamento do projeto (README, CONTRIBUTING, PRD)
  - Arquivos que auxiliam na utilização de IA (steerings, specs, skills)
  - Documentação técnica e guias
- **Exemplo**: `[DOCS] Atualizar README com instruções de instalação e execução da API`

### [TECH]
- **Quando usar**: Issues marcadas com a label `tech`
- **Propósito**: Tarefas técnicas que não entregam valor direto ao usuário
- **Características**:
  - Configuração de infraestrutura e pipelines
  - Refatoração de código
  - Setup de ferramentas e dependências
  - Ajustes de configuração
- **Exemplo**: `[TECH] Configurar pipeline de CI/CD com GitHub Actions para testes automatizados`

## Boas Práticas

1. **Clareza**: O título deve ser autoexplicativo
2. **Objetividade**: Evite títulos muito longos ou vagos
3. **Português**: Todos os títulos devem estar em português
4. **Consistência**: Sempre use o prefixo apropriado baseado na label

## Exemplos Completos

```
[EPIC] Implementação do módulo de avaliação e ranking de filmes
[STORY] Como usuário, quero atribuir uma nota a um filme para contribuir com o ranking
[STORY] Como usuário, quero listar os filmes mais bem avaliados para descobrir boas opções
[TECH] Configurar pipeline de CI/CD com GitHub Actions para build e testes
[TECH] Configurar banco de dados H2 em memória para ambiente de desenvolvimento
[DOCS] Criar documentação arquitetural do projeto com estrutura de pacotes e camadas
```
