@echo off
REM QABuddy.ai - local (no-Docker) launcher: Qdrant binary + Streamlit app.
REM Embeddings come from the local Ollama server (see .env).
setlocal
cd /d "%~dp0.."

if not exist ".tools\qdrant\qdrant.exe" (
  echo [!] Qdrant binary not found at .tools\qdrant\qdrant.exe
  echo     Download qdrant-x86_64-pc-windows-msvc.zip from
  echo     https://github.com/qdrant/qdrant/releases and extract it there.
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [!] venv not found. Run: python -m venv .venv ^&^& .venv\Scripts\python.exe -m pip install -r requirements-local.txt
  exit /b 1
)

echo Starting Qdrant on 127.0.0.1:6333 ...
pushd .tools\qdrant
start "qdrant" /min cmd /c "set QDRANT__SERVICE__HOST=127.0.0.1&& qdrant.exe"
popd

echo Starting QABuddy at http://localhost:8501/ ...
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
endlocal
