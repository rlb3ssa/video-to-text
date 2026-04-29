#!/usr/bin/env python3
"""
Transcreve vídeos do YouTube, TikTok e outros para texto.
Uso: python transcribe.py <URL> [opções]
"""
import sys
import argparse
import subprocess
import json
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcreve vídeos do YouTube, TikTok e outros para texto."
    )
    parser.add_argument("url", help="URL do vídeo (YouTube, TikTok, etc.)")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Modelo Whisper (padrão: base)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Idioma do áudio, ex: pt, en (padrão: detecção automática)",
    )
    parser.add_argument(
        "--output-format",
        default="text",
        choices=["text", "srt", "json"],
        help="Formato de saída (padrão: text)",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Não deletar o arquivo de áudio após a transcrição",
    )
    parser.add_argument(
        "--temp-dir",
        default="temp",
        help="Diretório para arquivos temporários (padrão: ./temp)",
    )
    parser.add_argument(
        "--output-file",
        metavar="ARQUIVO",
        help="Salvar transcrição em arquivo (ex: transcricao.txt)",
    )
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="Usar cookies do navegador para autenticação, ex: chrome, firefox",
    )
    return parser.parse_args()


def validate_url(url: str) -> bool:
    return bool(re.match(r"^https?://", url))


def download_audio(url: str, output_dir: Path, cookies_browser: str | None) -> Path:
    output_template = str(output_dir / "%(id)s.%(ext)s")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-x",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", output_template,
        "--no-playlist",
        "--print", "after_move:filepath",
        "--no-warnings",
        url,
    ]
    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]

    print("Baixando áudio...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Falha no download:\n{error}")

    # yt-dlp --print filepath imprime o caminho do arquivo na última linha
    lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
    if not lines:
        raise RuntimeError("yt-dlp não retornou o caminho do arquivo.")

    audio_path = Path(lines[-1])
    if not audio_path.exists():
        # fallback: procurar o wav mais recente no diretório
        wavs = sorted(output_dir.glob("*.wav"), key=lambda p: p.stat().st_mtime)
        if not wavs:
            raise RuntimeError("Arquivo de áudio não encontrado após o download.")
        audio_path = wavs[-1]

    print(f"Áudio salvo em: {audio_path}", file=sys.stderr)
    return audio_path


def transcribe_audio(
    audio_path: Path, model_name: str, language: str | None
) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print(
            "Erro: faster-whisper não está instalado.\n"
            "Execute: pip install faster-whisper",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Carregando modelo '{model_name}'...", file=sys.stderr)
    model = WhisperModel(model_name, device="cpu", compute_type="int8")

    print("Transcrevendo...", file=sys.stderr)
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    detected = info.language
    prob = info.language_probability
    print(f"Idioma detectado: {detected} (confiança: {prob:.0%})", file=sys.stderr)

    result = []
    for seg in segments:
        result.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})

    return result


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_output(segments: list[dict], fmt: str) -> str:
    if fmt == "text":
        return " ".join(s["text"] for s in segments)

    if fmt == "srt":
        lines = []
        for i, seg in enumerate(segments, 1):
            start = format_srt_time(seg["start"])
            end = format_srt_time(seg["end"])
            lines.append(f"{i}\n{start} --> {end}\n{seg['text']}\n")
        return "\n".join(lines)

    if fmt == "json":
        return json.dumps(segments, ensure_ascii=False, indent=2)

    return ""


def main():
    args = parse_args()

    if not validate_url(args.url):
        print("Erro: URL inválida. Deve começar com http:// ou https://", file=sys.stderr)
        sys.exit(1)

    temp_dir = Path(args.temp_dir)
    temp_dir.mkdir(exist_ok=True)

    audio_path = None
    try:
        audio_path = download_audio(args.url, temp_dir, args.cookies_from_browser)

        if audio_path.stat().st_size == 0:
            raise RuntimeError("Arquivo de áudio está vazio.")

        segments = transcribe_audio(audio_path, args.model, args.language)

        if not segments:
            print("Aviso: nenhum trecho de fala detectado no áudio.", file=sys.stderr)
            sys.exit(0)

        result = format_output(segments, args.output_format)

        if args.output_file:
            output_path = Path(args.output_file)
            output_path.write_text(result, encoding="utf-8")
            print(f"Transcrição salva em: {output_path}", file=sys.stderr)
        else:
            print(result)

    except RuntimeError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.", file=sys.stderr)
        sys.exit(130)
    finally:
        if audio_path and audio_path.exists() and not args.keep_audio:
            audio_path.unlink()


if __name__ == "__main__":
    main()
