# LogAnalyzer AI — Pré-Requisitos de Implementação

**Documento Base:** IA para Desenvolvedores [T2] - M2S05-06 - Mini-Projeto Avaliativo  
**Atualizado:** 3 de julho de 2026  
**Criado por:** Wanderson Souza

---

## 📋 Resumo Executivo

Este documento centraliza todos os pré-requisitos, critérios de avaliação e checklist de entrega para o desenvolvimento do **LogAnalyzer AI** — um agente de IA utilizando LangGraph para automatizar análise de arquivos de log.

---

## 1. CONTEXTO E OBJETIVO

<cite index="1-14,1-15">O foco é aplicar os conceitos de agentes de IA em um projeto prático, por meio da construção de uma solução funcional e bem documentada que automatize um processo real com apoio de IA.</cite>

<cite index="1-16,1-17">O projeto poderá ser desenvolvido individualmente ou em grupos de até 3 alunos. A proposta é criar um agente usando LangGraph, demonstrando o uso de componentes como objetivo, estado, memória, ferramentas, chamadas a APIs ou arquivos, validações e geração de respostas estruturadas.</cite>

---

## 2. DESAFIO DO PROJETO

<cite index="1-23,1-24">Desenvolver um agente funcional, demonstrável e documentado, capaz de automatizar um processo real relacionado ao desenvolvimento de software ou à temática escolhida para o projeto. A solução deve apresentar uma entrada definida, um fluxo de execução organizado, uso de ferramenta, tratamento de contexto e uma saída útil para o usuário final.</cite>

---

## 3. PRAZOS E ENTREGA

- **Data Limite:** 20/07/2026 às 22h
- **Plataforma:** AVA (envio do link do repositório GitHub)
- **Peso:** 30% da nota do módulo
- **Formato:** Individual ou grupos de até 3 alunos

---

## 4. REQUISITOS OBRIGATÓRIOS DA APLICAÇÃO

<cite index="1-48,1-49,1-50,1-51,1-52,1-53,1-54,1-55,1-56,1-57,1-58,1-59,1-60,1-61,1-62">
1. Definir um processo real a ser automatizado, descrevendo o objetivo do agente, a entrada esperada, as etapas principais e a saída produzida.
2. Implementar o agente com LangGraph, utilizando um fluxo organizado com estado, nós e conexões entre as etapas.
3. Integrar pelo menos uma ferramenta ao agente, como leitura de arquivo, escrita de relatório, chamada a API, consulta a dados ou execução de função controlada.
4. Utilizar memória ou contexto durante a execução, mantendo informações relevantes no estado do agente ou em uma estrutura simples de apoio.
5. Registrar os principais prompts utilizados em arquivo .md, incluindo prompts usados para planejar, implementar, corrigir ou melhorar o agente.
6. Documentar no README.md como o agente funciona, como executar o projeto e quais decisões principais foram tomadas.
7. Manter o projeto versionado no GitHub. Em projetos em grupo, cada integrante deverá apresentar contribuição rastreável.
</cite>

---

## 5. OBJETIVOS DE APRENDIZAGEM

Ao construir o agente, o aluno estará praticando:

<cite index="1-25,1-26,1-27,1-28,1-29,1-30,1-31">
- Definir um agente com objetivo claro, explicando qual processo será automatizado, qual entrada será recebida e qual resultado será entregue ao usuário.
- Implementar um fluxo funcional com LangGraph, utilizando estado, nós e conexões para organizar as etapas de execução do agente.
- Aplicar, de forma simples, conceitos de arquitetura de agentes, como separação entre planejamento, execução, uso de ferramentas e geração da resposta final.
- Integrar pelo menos uma ferramenta ao agente, como leitura ou escrita de arquivos, chamada a uma API, consulta a dados, análise de logs ou execução de uma função controlada.
- Utilizar memória ou contexto durante a execução, mantendo informações relevantes no estado do agente para apoiar o processamento e a resposta final.
- Aplicar cuidados básicos de segurança e validação, como controle das entradas recebidas, proteção de chaves de API, limitação de ações da ferramenta e geração de saídas verificáveis.
- Documentar o funcionamento do agente, os principais prompts utilizados, exemplos de entrada e saída e manter o projeto versionado no GitHub.
</cite>

---

## 6. CONTEÚDO DO REPOSITÓRIO (OBRIGATÓRIO)

<cite index="1-35">O repositório deverá estar acessível e conter:
- README.md completo;
- código-fonte do agente implementado com LangGraph;
- pelo menos uma ferramenta integrada ao agente;
- exemplos de entrada e saída da execução;
- registro dos principais prompts utilizados em arquivo .md;
- apresentação da ideia do projeto em até 2 slides.
</cite>

---

## 7. ESTRUTURA DO FLUXO RECOMENDADA

<cite index="1-90">Uma estrutura possível de fluxo seria:
```
Entrada do usuário
↓
Preparação do contexto
↓
Análise do agente
↓
Uso de ferramenta
↓
Geração da resposta final
```
O aluno ou grupo poderá adaptar esse fluxo conforme a necessidade do projeto.
</cite>

---

## 8. CONTEÚDO OBRIGATÓRIO DO README.md

<cite index="1-95">O README.md deve conter:
- nome do projeto;
- descrição do problema;
- objetivo do agente;
- explicação do fluxo com LangGraph;
- ferramenta utilizada pelo agente;
- instruções para executar o projeto;
- exemplo de entrada;
- exemplo de saída;
- principais decisões tomadas;
- limitações da solução.
</cite>

---

## 9. REGISTRO DE PROMPTS

<cite index="1-96">Os principais prompts utilizados deverão ser registrados em um arquivo .md, por exemplo: `docs/prompts.md`. Esse arquivo deve conter os prompts mais relevantes usados para planejar, implementar, corrigir ou melhorar o agente.</cite>

---

## 10. EXEMPLOS DE AGENTES POSSÍVEIS

<cite index="1-82">
- agente para revisar trechos de código;
- agente para analisar logs de pipeline;
- agente para classificar issues;
- agente para gerar relatórios técnicos;
- agente para consultar dados de uma API;
- agente para apoiar decisões dentro do case escolhido pelo aluno ou grupo.
</cite>

**Para LogAnalyzer AI:**
- Agente para análise automatizada de arquivos de log
- Identificação de padrões (erros, avisos, exceções)
- Geração de relatório técnico estruturado

---

## 11. EXEMPLOS DE FERRAMENTAS ACEITAS

<cite index="1-88">
- leitura de arquivo;
- escrita de relatório;
- chamada a uma API;
- consulta a dados locais;
- análise de logs;
- processamento de texto;
- execução de uma função controlada;
- busca de informações em documentos do projeto.
</cite>

---

## 12. CRITÉRIOS DE AVALIAÇÃO (TOTAL: 10 PONTOS)

| Nº | Critério | Pontos |
|----|----------|--------|
| 1 | Versionamento com branches e commits semânticos | 1,0 |
| 2 | Contribuição individual e produtividade | 1,0 |
| 3 | Organização dos arquivos, documentação e prompts | 2,0 |
| 4 | Ideia do projeto e apresentação | 1,0 |
| 5 | Implementação do agente com LangGraph | 1,0 |
| 6 | Uso de ferramenta integrada ao agente | 1,0 |
| 7 | Cuidados básicos de segurança | 1,0 |
| 8 | Contexto, memória e validação básica | 2,0 |
| **TOTAL** | | **10,0** |

---

## 13. AVISOS IMPORTANTES

<cite index="1-40,1-41,1-42,1-43">
- Não serão aceitos projetos submetidos após a data limite.
- Teste o link do repositório antes da submissão para garantir que ele está acessível.
- Não modifique o repositório após a entrega até receber a nota.
- Não versione chaves de API, tokens ou informações sensíveis no repositório.
</cite>

<cite index="1-102,1-103">Projetos com plágio de soluções encontradas na internet ou de colegas receberão nota 0. O uso de materiais, documentações e ferramentas de IA é permitido como apoio, desde que a solução entregue seja própria.</cite>

---

## 14. CHECKLIST FINAL DE ENTREGA

### Repositório e Organização
- [ ] Criei o repositório no GitHub e ele está acessível para avaliação
- [ ] O repositório contém o código-fonte do agente
- [ ] O projeto está organizado com histórico de commits compatível
- [ ] Em projetos em grupo, cada integrante possui contribuição rastreável

### Agente e Implementação
- [ ] Defini o processo que será automatizado pelo agente
- [ ] O agente possui objetivo, entrada e saída claramente definidos
- [ ] Implementei o agente usando LangGraph
- [ ] O fluxo utiliza estado, nós e conexões entre etapas
- [ ] O agente executa de forma funcional e gera uma saída estruturada

### Ferramentas, Contexto e Validação
- [ ] O agente utiliza pelo menos uma ferramenta integrada
- [ ] A ferramenta executa uma ação real (ler arquivo, escrever relatório, consultar dados, chamar API, etc.)
- [ ] O agente utiliza contexto ou memória durante a execução
- [ ] A solução possui validação básica de entrada, saída ou uso da ferramenta
- [ ] Não foram versionadas chaves, tokens ou informações sensíveis

### README.md e Prompts
- [ ] O README.md apresenta o problema, o objetivo do agente e o funcionamento geral
- [ ] O README.md explica como executar o projeto
- [ ] O README.md descreve o fluxo com LangGraph e a ferramenta utilizada
- [ ] O README.md apresenta exemplo de entrada e saída
- [ ] Registrei os principais prompts utilizados em arquivo .md

### Apresentação
- [ ] Preparei a apresentação da ideia do projeto em até 2 slides
- [ ] Os slides apresentam o problema, a proposta do agente, entrada, saída, ferramenta e fluxo
- [ ] A apresentação foi submetida via AVA ou versionada no repositório

### Submissão
- [ ] Submeti o link do repositório GitHub no AVA
- [ ] Conferi se o link está acessível antes da submissão
- [ ] Realizei a entrega antes do prazo: 20/07/2026 às 22h
- [ ] Não modificarei o repositório após a entrega até receber a nota

---

## 15. NOTAS IMPORTANTES PARA PROJETOS EM GRUPO

<cite index="1-45,1-46">Em projetos em grupo, a entrega será coletiva, mas a avaliação será individual conforme a contribuição de cada integrante. Por isso, todos os alunos deverão manter evidências rastreáveis de participação no repositório, como commits, implementação, documentação, revisão ou organização da entrega.</cite>

---

## 16. PONTOS-CHAVE A LEMBRAR

✅ **Faça:**
- Usar LangGraph como framework principal
- Implementar StateGraph para controle de fluxo
- Manter estado compartilhado para armazenar informações
- Criar nós responsáveis por etapas principais
- Integrar pelo menos uma ferramenta real
- Validar entradas e saídas
- Documentar tudo (README, prompts, exemplos)
- Usar commits semânticos
- Proteger informações sensíveis (.env, .gitignore)

❌ **Evite:**
- Expor chaves de API ou tokens no repositório
- Copiar soluções prontas (plágio = nota 0)
- Deixar código desorganizado ou sem documentação
- Usar agente sem fluxo claro ou sem ferramenta real
- Submeter após o prazo limite
- Modificar repositório após entrega

---

## 17. REFERÊNCIAS RÁPIDAS

- **Tecnologia:** Python 3.10+, LangGraph, LangChain
- **Entrega:** GitHub + AVA
- **Prazo:** 20/07/2026 às 22h
- **Peso:** 30% da nota do módulo
- **Documentação Base:** Este arquivo (sempre consulte antes de implementar)

---

**Última atualização:** Junho 2026  
**Autor da Compilação:** Análise do documento oficial de requisitos  
**Propósito:** Referência permanente durante desenvolvimento do LogAnalyzer AI
