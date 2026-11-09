# Central Launcher — Windows 1.1.0

## Instalação noutros computadores

1. Transfere `CentralLauncher_Setup_1.1.0.exe` e executa-o em Windows 64 bits.
2. A instalação cria entrada no menu Iniciar e pode criar atalho no ambiente de trabalho.
3. A aplicação inclui os cartões iniciais dos projetos do repositório [central](https://github.com/Xtvback/central).
4. Para jogos/projetos locais, entra no cartão e clica em **⚙** para indicar a localização dos ficheiros **nesse computador**. O launcher não copia nem instala jogos.
5. Os links online funcionam de imediato; algumas plataformas exigem autenticação.

## Visual 1.1 — baseado no estilo indicado pelo autor

- Interface **dark-glass** azul-escura com cartões, painel lateral e acentos luminosos;
- Painel **Temas**: Auto / Claro / Escuro, nove cores (coral por defeito), densidade e arredondamento;
- Navegação: Biblioteca, Jogos, Música, Escrita, Podcasts, Redes sociais, Desenvolvimento, Temas e Definições;
- Pesquisa e gestão de cartões com adicionar/editar/remover;
- Ícone próprio, um executável autónomo e instalador português, sem necessidade de Python nos PCs de destino.

## Dados e portabilidade

A lista de projetos e as preferências de aparência são gravadas em `%APPDATA%\CentralLauncher\projects.json` e `%APPDATA%\CentralLauncher\theme.json`. A atualização do instalador **preserva estes ficheiros**. As configurações de caminhos locais são independentes em cada computador; não são sincronizadas automaticamente.

## Desenvolvimento

Fontes incluídas no repositório: `launcher.py`, `projects.json`, `setup.iss` e `central_launcher.ico`. Executável gerado com PyInstaller + customtkinter; instalador pelo Inno Setup.

A versão desktop é independente do website público; não altera o conteúdo da landing page `central`.
