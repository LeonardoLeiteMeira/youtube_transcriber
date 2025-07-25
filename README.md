# YouTube Transcriber

Este projeto baixa o áudio de um vídeo público do YouTube, normaliza a gravação e gera um arquivo `.srt` utilizando o modelo [Whisper](https://github.com/openai/whisper) localmente.

## Requisitos

- Python 3.12
- [FFmpeg](https://ffmpeg.org/) instalado e disponível no `PATH`
- [Poetry](https://python-poetry.org/) para gerenciamento das dependências

## Instalação

```bash
poetry install
```

## Uso

Execute o transcritor informando a URL do vídeo no YouTube:

```bash
poetry run python main.py <URL do vídeo>
```

O script gera um arquivo `.srt` dentro de `/tmp/subs` contendo as legendas.

## Variáveis de ambiente

A transcrição usa o pacote `openai-whisper` localmente e **não** requer chave de API. Nenhuma variável de ambiente é necessária por padrão.

## Testes

Para rodar os testes (necessita acesso à internet para baixar um clipe de exemplo):

```bash
poetry run pytest
```

## Docker

Opcionalmente, é possível construir uma imagem Docker:

```bash
docker build -t transcritor .
```

## Tradução de arquivos TXT

O repositório inclui um script auxiliar `translate_txt.py` para traduzir
arquivos de texto longos utilizando a API da OpenAI sem depender do SDK
oficial. Defina a chave em `OPENAI_API_KEY` no topo do arquivo e execute:

```bash
poetry run python translate_txt.py
```

O script lerá o arquivo especificado em `SOURCE_FILENAME`, enviará o conteúdo
em partes para o modelo selecionado e escreverá o resultado traduzido em um novo
arquivo com sufixo `.translated.<idioma>.txt`.


