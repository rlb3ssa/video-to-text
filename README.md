# video-to-text

Transcreve vídeos do YouTube, TikTok e centenas de outras plataformas para texto, usando ferramentas 100% gratuitas e open-source que rodam localmente em computadores mais antigos ou com limitações.
Não é necessário GPU.

**Ferramentas utilizadas:**
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — download de vídeo/áudio
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — transcrição de áudio para texto (baseado no Whisper da OpenAI)
- [ffmpeg](https://ffmpeg.org/) — processamento de áudio

---

## Pré-requisitos

Antes de instalar o projeto, você precisa ter os seguintes programas instalados:

### 1. Python 3.8 ou superior

Verifique se já está instalado:
```bash
python3 --version   # Linux / macOS
python --version    # Windows
```

Caso não tenha, baixe em: https://www.python.org/downloads/

> **Windows:** durante a instalação, marque a opção **"Add Python to PATH"**.

---

### 2. ffmpeg

O ffmpeg é necessário para a conversão de áudio.

**Ubuntu / Debian:**
```bash
sudo apt install -y ffmpeg
```

**Fedora / RHEL:**
```bash
sudo dnf install -y ffmpeg
```

**Arch Linux:**
```bash
sudo pacman -S ffmpeg
```

**macOS (com Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**

Usando o gerenciador de pacotes `winget` (disponível no Windows 10/11):
```powershell
winget install --id Gyan.FFmpeg -e
```

Ou baixe manualmente em https://ffmpeg.org/download.html e adicione a pasta `bin/` ao PATH do sistema.

Verifique a instalação:
```bash
ffmpeg -version
```

---

## Instalação

### 1. Clone ou baixe o repositório

```bash
git clone <url-do-repositório>
cd video_to_text
```

Ou baixe e extraia o arquivo ZIP e entre na pasta.

### 2. Crie o ambiente virtual

O ambiente virtual isola as dependências do projeto do restante do sistema.

**Linux / macOS:**
```bash
python3 -m venv .venv
```

**Windows:**
```powershell
python -m venv .venv
```

### 3. Ative o ambiente virtual

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Prompt de Comando):**
```cmd
.venv\Scripts\activate.bat
```

> O prompt do terminal mudará para mostrar `(.venv)` indicando que o ambiente está ativo.

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

A instalação pode levar alguns minutos na primeira vez.

---

## Uso

### Ativar o ambiente virtual (sempre que abrir um novo terminal)

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
```

### Transcrever um vídeo

```bash
python transcribe.py "https://www.youtube.com/watch?v=XXXX"
python transcribe.py "https://www.tiktok.com/@usuario/video/123"
python transcribe.py "https://vt.tiktok.com/XXXXX/"
```

### Salvar a transcrição em arquivo

```bash
python transcribe.py "URL" --output-file transcricao.txt
```

Ou usando redirecionamento de saída do terminal:

```bash
python transcribe.py "URL" > transcricao.txt
```

---

## Opções disponíveis

| Opção | Padrão | Descrição |
|---|---|---|
| `--model` | `base` | Modelo Whisper: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3` |
| `--language` | auto | Idioma do áudio: `pt`, `en`, `es`, etc. |
| `--output-format` | `text` | Formato de saída: `text`, `srt`, `json` |
| `--keep-audio` | — | Não apagar o arquivo de áudio após transcrição |
| `--temp-dir` | `./temp` | Pasta para arquivos temporários |
| `--cookies-from-browser` | — | Usar cookies do navegador: `chrome`, `firefox` |

### Exemplos com opções

```bash
# Modelo melhor para português
python transcribe.py "URL" --model small --language pt

# Saída no formato de legenda SRT
python transcribe.py "URL" --output-format srt

# Saída em JSON (com timestamps por segmento)
python transcribe.py "URL" --output-format json

# Salvar áudio após transcrição
python transcribe.py "URL" --keep-audio

# Vídeo que exige login (ex: conteúdo restrito)
python transcribe.py "URL" --cookies-from-browser chrome
```

---

## Escolha do modelo

Na **primeira execução** com cada modelo, os pesos são baixados automaticamente e ficam em cache — não é preciso baixar novamente.

| Modelo | Download | RAM usada | Velocidade (CPU) | Qualidade |
|---|---|---|---|---|
| `tiny` | 75 MB | ~150 MB | Muito rápida | Baixa |
| `base` | 145 MB | ~290 MB | Rápida | Boa |
| `small` | 461 MB | ~920 MB | Moderada | Muito boa |
| `medium` | 1.5 GB | ~3 GB | Lenta | Excelente |
| `large-v3` | 3.1 GB | ~6 GB | Muito lenta | Máxima |

**Recomendação:** comece com `base`. Para português com sotaque regional ou áudio de baixa qualidade, use `small` ou `medium`.

---

## Solução de problemas

**Erro: `ffmpeg` não encontrado**
Verifique se o ffmpeg está instalado e no PATH: `ffmpeg -version`

**TikTok ou YouTube retorna erro de autenticação**
Faça login no site no seu navegador e use a opção `--cookies-from-browser`:
```bash
python transcribe.py "URL" --cookies-from-browser chrome
```

**Windows: erro ao ativar o ambiente virtual (`Execution Policy`)**
Execute no PowerShell como administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Transcrição muito lenta**
Use um modelo menor com `--model tiny` ou `--model base`.

**Pouca memória RAM**
Use `--model tiny`. O modelo `tiny` usa apenas ~150 MB de RAM.

---

## Instalação com comando único

### Linux / macOS (Ubuntu, Debian e derivados)

Copie e cole no terminal dentro da pasta do projeto:

```bash
sudo apt install -y ffmpeg && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && echo "Ambiente pronto. Execute: python transcribe.py <URL>"
```

> Para outras distribuições, substitua `sudo apt install -y ffmpeg` pelo comando equivalente do seu gerenciador de pacotes (`dnf`, `pacman`, `brew`, etc.).

### Windows (PowerShell)

Copie e cole no PowerShell dentro da pasta do projeto:

```powershell
winget install --id Gyan.FFmpeg -e --silent; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; Write-Host "Ambiente pronto. Execute: python transcribe.py <URL>"
```

> Se aparecer erro de política de execução, rode primeiro:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Após a instalação, sempre que abrir um novo terminal, ative o ambiente antes de usar:

```bash
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\Activate.ps1    # Windows
```
