---
inclusion: manual
description: "Solicita o número da task, busca dados no GitHub para determinar o tipo e nome da branch, sugere nome descritivo baseado no título da issue, garante padrão gitflow (feature/<nome>_task<N> ou bugfix/<nome>_task<N>), solicita descrição das alterações e realiza o commit seguindo conventional commits em português."
---

Execute o fluxo de commit seguindo as etapas abaixo:

1. Verifique a branch atual com `git branch --show-current`

2. Se a branch não seguir o padrão `feature/<nome>_task<N>` ou `bugfix/<nome>_task<N>`:
   a. Pergunte ao desenvolvedor: "Qual o número da task (issue) que você está trabalhando?"
   b. Com o número informado, busque os dados da issue no GitHub com `gh issue view <número> --repo weltonsabino/LogAnalyzer-AI`
   c. A partir do título da issue, gere um slug curto e descritivo em português:
      - Remova o prefixo entre colchetes (ex: `[STORY]`, `[TECH]`, `[DOCS]`, `[EPIC]`)
      - Resuma o título em no máximo 3 palavras-chave que capturam a essência da tarefa
      - Converta para lowercase
      - Substitua espaços e caracteres especiais por hífens
      - Limite a 30 caracteres
      - Exemplos:
        - `[STORY] Configurar estrutura inicial do projeto` → slug `configurar-estrutura-projeto`
        - `[TECH] Implementar análise de logs com LangGraph` → slug `implementar-analise-langgraph`
        - `[DOCS] Criar specs de planejamento funcional LogAnalyzer` → slug `specs-planejamento-loganalyzer`
   d. Analise o campo `type` da issue:
      - Se o tipo for `Feature` → prefixo `feature/`
      - Se o tipo for `Bug` → prefixo `bugfix/`
      - Se não houver tipo definido → pergunte ao desenvolvedor: "As implementações se tratam de uma nova funcionalidade ou correção de bug?"
        - Nova funcionalidade → prefixo `feature/`
        - Correção de bug → prefixo `bugfix/`
   e. Monte o nome sugerido da branch: `<prefixo><slug>_task<número>`
      - Exemplo: `feature/implementar-statengraph-loganalyzer_task2`
   f. Apresente ao desenvolvedor: "Sugiro o nome de branch: `<nome-sugerido>`. Deseja usar esse nome ou prefere outro?"
      - Se o desenvolvedor aprovar → use o nome sugerido
      - Se o desenvolvedor informar outro nome → use o nome informado, mas garanta que termina com `_task<número>`
   g. Crie e mude para a nova branch com `git checkout -b <nome-da-branch>`

3. Pergunte ao desenvolvedor: "Do que se tratam as alterações realizadas? Descreva brevemente para que eu possa criar a mensagem de commit."

4. Com base nas alterações realizadas, determine o tipo de commit:
   - `feat:` → Novas funcionalidades do produto: novos arquivos Python em src/loganalyzer/, novos testes, alterações em requirements.txt que adicionam capacidades
   - `fix:` → Correções de funcionalidades do produto: correções em código Python, ajustes em requirements.txt que resolvem problemas
   - `refactor:` → Refatoração de código Python sem alteração de comportamento
   - `docs:` → Modificações em documentos, guias, arquivos steerings, hooks, skills ou exemplos — qualquer alteração que NÃO modifique o código-fonte da aplicação

5. Execute `git add .` e `git commit -m "<tipo>: <descrição curta em português>"`

Regras:
- Nunca commitar diretamente na branch `main`
- Manter commits atômicos e mensagens claras em português
- O nome da branch deve SEMPRE terminar com `_task<N>`
- O slug deve ser gerado a partir do título da issue — nunca inventado

Padrões de branch: `feature/<nome-descritivo>_task<número>` ou `bugfix/<nome-descritivo>_task<número>`
Padrões de commit: `feat:`, `fix:`, `refactor:`, `docs:`
