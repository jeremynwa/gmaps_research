"""Fix Python import paths - Add this to your project root."""
import sys
from pathlib import Path

# Get the folder where this file is located
project_root = Path(__file__).parent.absolute()

# Add all the folders Python needs to find your code
folders = [
    project_root,
    project_root / "src",
    project_root / "src" / "analyzers",
    project_root / "src" / "scrapers",
    project_root / "src" / "processors",
    project_root / "src" / "exporters",
    project_root / "src" / "utils",
    project_root / "config",
    project_root / "cli",
]

# Add each folder to Python's search path
for folder in folders:
    path_str = str(folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

print("✅ Import paths configured!")
print(f"📁 Project root: {project_root}")