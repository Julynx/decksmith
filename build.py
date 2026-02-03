import shutil
import subprocess
from pathlib import Path


def get_dependencies():
    """Extract dependencies from uv export."""
    print("Extracting dependencies from uv...")
    try:
        # Run uv export to get requirements.txt content
        result = subprocess.run(
            ["uv", "export", "--no-dev", "--format", "requirements-txt"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout

        dependencies = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-e"):
                continue

            # Handle lines with hashes or comments
            if " ;" in line:
                line = line.split(" ;")[0]
            if " #" in line:
                line = line.split(" #")[0]

            # Remove backslashes used for line continuation
            line = line.replace("\\", "").strip()

            # Skip hash lines
            if line.startswith("--hash"):
                continue

            if line:
                dependencies.append(line)

        return dependencies

    except subprocess.CalledProcessError as e:
        print(f"Error running uv export: {e}")
        print("Falling back to hardcoded dependencies (WARNING: might be outdated)")
        return [
            "click==8.2.1",
            "flask==3.1.2",
            "werkzeug==3.1.5",
            "jinja2==3.1.6",
            "markupsafe==3.0.3",
            "itsdangerous==2.2.0",
            "blinker==1.9.0",
            "colorama==0.4.6",
            "jval==1.0.6",
            "pandas==2.3.1",
            "numpy==2.3.2",
            "python-dateutil==2.9.0.post0",
            "pytz==2025.2",
            "tzdata==2025.2",
            "six==1.17.0",
            "pillow==11.3.0",
            "reportlab==4.4.3",
            "ruamel.yaml==0.19.1",
            "crossfiledialog==1.1.0",
            "pywin32==311",
            "waitress==3.0.2",
        ]


def main():
    # 1. Generate installer.cfg
    python_version = "3.11.0"

    dependencies = get_dependencies()
    pypi_wheels_str = "\n    ".join(dependencies)

    cfg_content = f"""[Application]
name=DeckSmith
version=0.9.3
entry_point=decksmith.gui.app:main
icon=docs/assets/decksmith.ico
console=false

[Python]
version={python_version}
bitness=64

[Include]
pypi_wheels = {pypi_wheels_str}

packages = decksmith

[Build]
directory=build_nsis
installer_name=DeckSmith_Setup.exe
"""

    with open("installer.cfg", "w") as installer_file:
        installer_file.write(cfg_content)

    print("Generated installer.cfg")

    # 2. Run Pynsist (prepare only)
    print("Running Pynsist (prepare)...")
    subprocess.check_call(["pynsist", "--no-makensis", "installer.cfg"])

    # 3. Run Makensis
    print("Running Makensis...")
    makensis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis",  # In PATH
    ]

    makensis_exe = None
    for makensis_path in makensis_paths:
        if shutil.which(makensis_path) or Path(makensis_path).exists():
            makensis_exe = makensis_path
            break

    if makensis_exe:
        subprocess.check_call([makensis_exe, str(Path("build_nsis") / "installer.nsi")])
        print("Build complete!")
    else:
        print(
            "WARNING: makensis.exe not found. Please install NSIS and run makensis manually on build_nsis/installer.nsi"
        )


if __name__ == "__main__":
    main()
