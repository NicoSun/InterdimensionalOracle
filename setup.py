import os
import sys
import subprocess
import shutil


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

# Define the venv folder relative to the backend directory
VENV_REL_PATH = "venv"
VENV_DIR = os.path.join(BACKEND_DIR, VENV_REL_PATH)


# Resolve correct python and pip binary paths inside virtual env
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")
    VENV_PIP = os.path.join(VENV_DIR, "Scripts", "pip.exe")
else:
    VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")
    VENV_PIP = os.path.join(VENV_DIR, "bin", "pip")


def run_cmd(cmd, cwd=None, error_msg="Error executing command"):
    """Helper to cleanly run subprocess commands."""
    print(f"Executing: {' '.join(cmd)} (Working Directory: {cwd or ROOT_DIR})")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[Error] {error_msg}")
        print(f"Details: {e}")
        sys.exit(1)


def main():
    print("==================================================")
    print("       Rick & Morty Oracle Installation           ")
    print("==================================================")

    # 1. Check NPM Requirement
    if not shutil.which("npm"):
        print("[Abort] System dependency 'npm' not found. Please install Node.js/NPM before running setup.")
        sys.exit(1)

    # 2. Setup Python Venv inside backend folder
    if not os.path.exists(VENV_DIR):
        print(f"\nCreating Python Virtual Environment in {BACKEND_DIR}...")
        # We run the command with cwd=BACKEND_DIR so 'venv' is created inside it
        run_cmd([sys.executable, "-m", "venv", VENV_REL_PATH], cwd=BACKEND_DIR, error_msg="Failed to create venv.")
    else:
        print("\nVirtual environment exists. Proceeding...")

    # 3. Install Python Dependencies
    reqs_path = os.path.join(BACKEND_DIR, "requirements.txt")
    if os.path.exists(reqs_path):
        print("\nInstalling backend requirements inside Venv...")
        run_cmd([VENV_PIP, "install", "-r", "requirements.txt"], cwd=BACKEND_DIR, error_msg="Failed installing backend dependencies.")
    else:
        print(f"[Error] 'requirements.txt' not found at {reqs_path}")
        sys.exit(1)

    # 4. Download API Data
    api_data_download = os.path.join(BACKEND_DIR, "build_local_data_cache.py")
    if os.path.exists(api_data_download):
        print("\nDownloading Rock & Morty API Data")
        run_cmd([VENV_PYTHON, "build_local_data_cache.py"], cwd=BACKEND_DIR, error_msg="API Download error.")
    else:
        print(f"[Error] at {api_data_download}")
        sys.exit(1)

    # 5. Run Knowledge Base Ingestion Script
    ingest_script = os.path.join(BACKEND_DIR, "ingest.py")
    if os.path.exists(ingest_script):
        print("\nPopulating local Vector DB. This will download API entities and process local embeddings...")
        run_cmd([VENV_PYTHON, "ingest.py"], cwd=BACKEND_DIR, error_msg="Ingestion pipeline crashed.")
    else:
        print(f"[Error] Ingestion script missing at {ingest_script}")
        sys.exit(1)

    # 6. Install Vue.js Frontend Dependencies
    package_json = os.path.join(FRONTEND_DIR, "package.json")
    if os.path.exists(package_json):
        print("\nInstalling Frontend node_modules via 'npm install'...")
        # Resolve 'npm' execution details (especially on Windows)
        npm_cmd = ["npm.cmd" if sys.platform == "win32" else "npm", "install"]
        run_cmd(npm_cmd, cwd=FRONTEND_DIR, error_msg="Failed to install npm dependencies.")
    else:
        print(f"[Error] Frontend structure is missing package.json at {package_json}")
        sys.exit(1)

    print("\n==================================================")
    print("Setup was completed successfully.")
    print("==================================================")
    print("To launch your environment:")
    print("  1) Start Backend (Python FastAPI server):")
    print("     $ cd backend")
    print("     $ source venv/bin/activate")
    print("     $ python app.py")

    print("  2) Start Frontend (Vite server):")
    print("     open in new terminal in project root")
    print("     $ cd frontend")
    print("     $ npm run dev")
    print("==================================================")


if __name__ == "__main__":
    main()
