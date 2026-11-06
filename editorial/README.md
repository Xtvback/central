# Estúdio Editorial — André M. Fernandes

Painel editorial estático para acompanhar o crescimento do Threads **@andre.f.m.fernandes** e a identidade pública de escritor.

## O que já está implementado

- **Visão geral**: próximos posts, checklist do dia e marcos editoriais.
- **Calendário navegável**: publicações agendadas no Metricool (fotografia de 06/11/2026), tarefas e planos locais.
- **Publicações**: texto completo dos 17 posts de novembro e sete propostas editoriais distintas, **não aplicadas** ao Metricool.
- **O meu dia**: tarefas por data, validação do agendamento, acompanhamento de comentários e revisão de resultados.
- **Resultados**: referência dos seis posts iniciais e registo manual de novos dados.
- **Exportação**: cópia JSON para transferir notas e checklists entre dispositivos; calendário ICS para importar datas.
- **Rascunhos locais**: criar novos planos sem os confundir com publicações efetivamente agendadas.

## Publicação

Este painel encontra-se na pasta `editorial/` do repositório [Xtvback/central](https://github.com/Xtvback/central).

Se o GitHub Pages estiver configurado para publicar a branch `main` a partir da raiz do repositório, o endereço é:

https://xtvback.github.io/central/editorial/

## Importante: o que NÃO faz

- Não inicia sessão nem escreve no Metricool.
- Não publica, cancela nem altera posts na rede social.
- Não recebe dados em tempo real do Metricool. Os posts são um instantâneo de **6 de novembro de 2026**.
- Não sincroniza checklists/rascunhos entre dispositivos: usam `localStorage` do navegador.
- Não envia notificações push. Para lembretes, pode ser importado o calendário `.ics` numa agenda.
- O repositório é **público**: os textos agendados constantes em `data.js` também ficam visíveis no GitHub.

As propostas de revisão precisam de validação editorial e de atualização **separada** no Metricool antes de poderem ser tratadas como texto agendado.

## Atualizar o calendário

Editar `editorial/data.js` com uma nova exportação/lista de posts do Metricool. Evitar colocar neste repositório chaves de API, senhas ou informações pessoais sensíveis.

Os ficheiros `index.html`, `style.css` e `app.js` funcionam sem compilação, instalação ou backend.

## Próximos passos opcionais

Uma sincronização automática e segura com o Metricool, bem como login e dados partilhados entre dispositivos, exigiria um backend autenticado. Não se deve publicar qualquer token do Metricool num site estático público.
