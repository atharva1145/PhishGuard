"""
Unified cross-platform launcher for PhishGuard.
Starts both the FastAPI backend and Vite frontend concurrently.
"""
import subprocess
import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def main():
    print("=" * 60)
    print(" Starting PhishGuard Full-Stack Platform")
    print("=" * 60)
    
    # Check if models exist
    url_model = ROOT_DIR / "ml" / "models" / "url_detector.joblib"
    email_model = ROOT_DIR / "ml" / "models" / "email_detector.joblib"
    if not url_model.exists() or not email_model.exists():
        print("[!] Models not detected. Running training pipeline first...")
        subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "train_models.py")], check=True)
        print("[✓] Model artifacts ready.\n")

    print("[*] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT_DIR)
    )

    print("[*] Starting Vite React Frontend on http://localhost:5173 ...")
    frontend_dir = ROOT_DIR / "frontend"
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(frontend_dir)
    )

    print("\n" + "=" * 60)
    print(" [✓] PhishGuard is running!")
    print(" -> Frontend Dashboard: http://localhost:5173")
    print(" -> Backend API Docs:   http://127.0.0.1:8000/docs")
    print(" Press Ctrl+C in this terminal to stop both servers.")
    print("=" * 60 + "\n")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n[*] Stopping PhishGuard servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=3)
            frontend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
            frontend_proc.kill()
        print("[✓] All servers stopped gracefully.")

if __name__ == "__main__":
    main()
