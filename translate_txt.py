OPENAI_API_KEY = "COLOQUE_SUA_CHAVE_AQUI"
SOURCE_FILENAME = "meu_arquivo.txt"
TARGET_LANGUAGE = "en"
CONTEXT_DESCRIPTION = """Texto livre descrevendo o contexto do documento a ser traduzido
(ex.: contrato de software B2B, termos legais, termos financeiros etc.)."""
MODEL = "gpt-4.1"
TEMPERATURE = 0.0
MAX_CHARS_PER_CHUNK = 8000
OUTPUT_FILENAME = ""
MAX_RETRIES = 5
RETRY_BASE_SECONDS = 2

import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
from tqdm import tqdm

API_URL = "https://api.openai.com/v1/responses"


def read_api_key() -> str:
    key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
    if not key:
        print("Erro: OPENAI_API_KEY não definido", file=sys.stderr)
        sys.exit(1)
    return key


def generate_output_name() -> str:
    if OUTPUT_FILENAME:
        return OUTPUT_FILENAME
    src = Path(SOURCE_FILENAME)
    return f"{src.stem}.translated.{TARGET_LANGUAGE}.txt"


SENTENCE_RE = re.compile(r"(?<=[.!?…][\"'”’)?]*)\s+", re.MULTILINE)


def split_sentences(text: str) -> list[str]:
    sentences = SENTENCE_RE.split(text)
    return [s for s in sentences if s]


def chunk_sentences(sentences: list[str]) -> list[str]:
    chunks: list[str] = []
    buffer = ""
    for s in sentences:
        if len(buffer) + len(s) <= MAX_CHARS_PER_CHUNK:
            buffer += s
        else:
            if buffer:
                chunks.append(buffer)
            if len(s) > MAX_CHARS_PER_CHUNK:
                chunks.append(s)
                buffer = ""
            else:
                buffer = s
    if buffer:
        chunks.append(buffer)
    return chunks


def build_input_message(chunk: str) -> str:
    return (
        f"Traduza o seguinte trecho para {TARGET_LANGUAGE}. Responda somente com o texto traduzido, sem explicações adicionais.\n\n"
        "<<<TRECHO_INÍCIO\n"
        f"{chunk}\n"
        "TRECHO_FIM>>>"
    )


def extract_text(resp_json: dict) -> str:
    parts = []
    for item in resp_json.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))
    if parts:
        return "".join(parts).strip()
    if "output_text" in resp_json:
        return str(resp_json["output_text"]).strip()
    raise ValueError("Texto traduzido não encontrado na resposta")


def translate_chunk(client: httpx.Client, api_key: str, instructions: str, user_message: str) -> str:
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_message,
                    }
                ],
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = client.post(API_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return extract_text(resp.json())
            if resp.status_code in {429} or resp.status_code >= 500:
                wait = min(RETRY_BASE_SECONDS * 2 ** attempt, 30)
                time.sleep(wait)
                continue
            resp.raise_for_status()
        except Exception as err:  # noqa: BLE001
            if attempt >= MAX_RETRIES:
                raise RuntimeError(f"Erro ao traduzir chunk: {err}") from err
            wait = min(RETRY_BASE_SECONDS * 2 ** attempt, 30)
            time.sleep(wait)
    raise RuntimeError("Falha após várias tentativas")


def main() -> None:
    api_key = read_api_key()
    src_path = Path(SOURCE_FILENAME)
    if not src_path.exists():
        print(f"Arquivo {src_path} não encontrado", file=sys.stderr)
        sys.exit(1)

    out_path = Path(generate_output_name())
    text = src_path.read_text(encoding="utf-8")
    sentences = split_sentences(text)
    chunks = chunk_sentences(sentences)

    instructions = (
        "Você é um tradutor profissional. Traduza o texto enviado para "
        f"{TARGET_LANGUAGE} com máxima fidelidade sem omitir informações.\n"
        "Mantenha o sentido técnico e a terminologia com consistência.\n"
        "Adapte unidades, formatação de números e datas apenas quando isso melhorar a clareza no idioma de destino.\n"
        "Se encontrar trechos confusos, escolha a tradução mais natural e fluida, preservando o significado.\n\n"
        "Contexto do documento (para guiar a tradução):\n"
        f"{CONTEXT_DESCRIPTION}"
    )

    with out_path.open("w", encoding="utf-8") as f_out:
        f_out.write(
            f"# Tradução gerada em {datetime.now().isoformat()} usando modelo {MODEL}\n"
        )
        f_out.write(f"# Idioma alvo: {TARGET_LANGUAGE}\n\n")
        f_out.flush()

    with httpx.Client() as client, out_path.open("a", encoding="utf-8") as f_out:
        for i, chunk in enumerate(tqdm(chunks, desc="Traduzindo"), start=1):
            user_msg = build_input_message(chunk)
            translated = translate_chunk(client, api_key, instructions, user_msg)
            f_out.write(translated)
            f_out.write("\n\n")
            f_out.flush()

    print(f"Arquivo traduzido salvo em {out_path}")


if __name__ == "__main__":
    main()
