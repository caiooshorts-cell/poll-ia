# DevPilot PC

Um assistente de IA desktop, feito para tarefas de programação no computador: explicar código, encontrar bugs, sugerir melhorias e gerar arquivos. Ele usa o **Ollama** localmente, então o seu código não precisa sair do PC.

## O que já faz

- conversa com modelos locais de código (ex.: `qwen2.5-coder`, `deepseek-coder`);
- adiciona arquivos ou uma pasta inteira como contexto;
- tem modos rápidos: Explicar, Corrigir e Revisar;
- transmite a resposta enquanto ela é gerada;
- salva a conversa durante a sessão.

## Como executar

1. Instale o [Python 3.11+](https://www.python.org/downloads/).
2. Instale o [Ollama](https://ollama.com/) e baixe um modelo de programação:

   ```powershell
   ollama pull qwen2.5-coder:7b
   ```

3. Na pasta do projeto, execute:

   ```powershell
   python app.py
   ```

O Ollama deve estar aberto (normalmente ele inicia automaticamente). No DevPilot, escolha o modelo e uma pasta de projeto, se quiser.

## Próximos passos

- edição/aplicação de patches com confirmação;
- integração com terminal e Git;
- perfis de modelo por linguagem;
- empacotamento em `.exe` com PyInstaller.

> O projeto não executa comandos nem altera arquivos automaticamente: as respostas são sugestões que você revisa antes de aplicar.
