import os
import sys
import shutil
import subprocess
import importlib.util

# ---------------- Ensure PyInstaller is installed ----------------
if importlib.util.find_spec("PyInstaller") is None:
    print("PyInstaller not found. Installing it now...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller==6.19.0"], check=True)

# ---------------- Debug info ----------------
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# ---------------- Directories ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")
RELEASE_DIR = os.path.join(BASE_DIR, "release")
APP_DIR = os.path.join(BASE_DIR, "AppDir")

# ---------------- Clean old builds ----------------
for folder in [DIST_DIR, BUILD_DIR, RELEASE_DIR, APP_DIR]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
os.makedirs(RELEASE_DIR, exist_ok=True)

# ---------------- PyInstaller options ----------------
APP_NAME = "CSVtoJSON"
ENTRY_POINT = os.path.join(BASE_DIR, "app", "main.py")

PYINSTALLER_ARGS = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    f"--name={APP_NAME}",
    "--paths", os.path.join(BASE_DIR, "app"),  # ensures package imports work
    ENTRY_POINT
]

print("Building executable with PyInstaller...")
subprocess.run(PYINSTALLER_ARGS, check=True)

# ---------------- Copy artifacts to release folder ----------------
if sys.platform.startswith("win"):
    exe_name = f"{APP_NAME}.exe"
    src_path = os.path.join(DIST_DIR, exe_name)
    dst_path = os.path.join(RELEASE_DIR, exe_name)
    shutil.copy(src_path, dst_path)
    print(f"Windows build complete: {dst_path}")

elif sys.platform.startswith("darwin"):
    src_path = os.path.join(DIST_DIR, APP_NAME)
    dst_path = os.path.join(RELEASE_DIR, f"{APP_NAME}-macOS")
    shutil.copy(src_path, dst_path)
    print(f"macOS build complete: {dst_path}")

elif sys.platform.startswith("linux"):
    print("Preparing AppDir for AppImage...")
    bin_dir = os.path.join(APP_DIR, "usr/bin")
    os.makedirs(bin_dir, exist_ok=True)
    binary_path = os.path.join(bin_dir, APP_NAME)
    shutil.copy(os.path.join(DIST_DIR, APP_NAME), binary_path)

    # AppRun symlink
    app_run_path = os.path.join(APP_DIR, "AppRun")
    if os.path.exists(app_run_path):
        os.remove(app_run_path)
    os.symlink(os.path.join("usr/bin", APP_NAME), app_run_path)
    os.chmod(app_run_path, 0o755)

    # Desktop file
    applications_dir = os.path.join(APP_DIR, "usr/share/applications")
    os.makedirs(applications_dir, exist_ok=True)
    desktop_file_path = os.path.join(applications_dir, f"{APP_NAME}.desktop")
    with open(desktop_file_path, "w") as f:
        f.write(f"""[Desktop Entry]
Name={APP_NAME}
Exec={APP_NAME}
Icon={APP_NAME}
Terminal=true
Type=Application
Categories=Utility;
""")

    # Icon
    icon_dir = os.path.join(APP_DIR, "usr/share/icons/hicolor/256x256/apps")
    os.makedirs(icon_dir, exist_ok=True)
    shutil.copy(os.path.join(BASE_DIR, "assets", f"{APP_NAME}.png"), icon_dir)

    # Build AppImage
    print("Downloading linuxdeploy AppImage...")
    linuxdeploy_path = os.path.join(BASE_DIR, "linuxdeploy-x86_64.AppImage")
    if not os.path.exists(linuxdeploy_path):
        subprocess.run([
            "wget",
            "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage",
            "-O",
            linuxdeploy_path
        ], check=True)
        subprocess.run(["chmod", "+x", linuxdeploy_path], check=True)

    print("Building AppImage...")
    subprocess.run([
        linuxdeploy_path,
        "--appdir", APP_DIR,
        "--output", "appimage"
    ], check=True)

    # Make AppImage executable
    for file in os.listdir(BASE_DIR):
        if file.startswith(APP_NAME) and file.endswith(".AppImage"):
            appimage_path = os.path.join(BASE_DIR, file)
            os.chmod(appimage_path, 0o755)
            shutil.move(appimage_path, os.path.join(RELEASE_DIR, f"{APP_NAME}-Linux.AppImage"))

    print(f"Linux AppImage build complete: {os.path.join(RELEASE_DIR, f'{APP_NAME}-Linux.AppImage')}")

print(f"\nAll builds complete! Artifacts are in: {RELEASE_DIR}")