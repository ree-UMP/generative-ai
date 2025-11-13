import os
import sys
import json
import subprocess
from pathlib import Path

def safe_repo_name(url):
    """Extract a clean repo name from the GitHub URL."""
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name

def git_clone(url, target_dir):
    """Clone the repo or pull latest if already exists."""
    if os.path.exists(target_dir):
        print(f"[repo_mapper] Target exists, pulling latest changes in {target_dir}")
        subprocess.run(["git", "-C", target_dir, "pull"], check=False)
        return
    print(f"[repo_mapper] Cloning {url} -> {target_dir}")
    subprocess.run(["git", "clone", url, target_dir], check=True)

def scan_tree(path: Path, ignore_dirs=(".git", "node_modules", "__pycache__")):
    """Recursively scan directory structure and return a nested dict."""
    tree = {}
    for p in sorted(path.iterdir(), key=lambda p: p.name.lower()):
        if p.is_dir():
            if p.name in ignore_dirs:
                continue
            tree[p.name] = scan_tree(p, ignore_dirs)
        else:
            tree[p.name] = "file"
    return tree

def summarize_readme(repo_path: Path):
    """Extract a simple summary from the README file."""
    readme_files = ["README.md", "README.rst", "README.txt"]
    for rf in readme_files:
        f = repo_path / rf
        if f.exists():
            text = f.read_text(encoding="utf-8", errors="ignore")
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            summary = ""
            if paragraphs:
                summary = "\n\n".join(paragraphs[:3])
            else:
                summary = text[:400]
            return {"found": True, "name": rf, "summary": summary.strip()}
    return {"found": False, "summary": ""}

def main():
    if len(sys.argv) < 2:
        print("Usage: python BE/repo_mapper.py <git_repo_url>")
        sys.exit(1)

    url = sys.argv[1]
    base = Path.cwd()
    repos_dir = base / "repos"
    repos_dir.mkdir(exist_ok=True)

    repo_name = safe_repo_name(url)
    target = repos_dir / repo_name

    try:
        git_clone(url, str(target))
    except Exception as e:
        print(f"[repo_mapper] Error cloning repository: {e}")
        sys.exit(2)

    tree = scan_tree(target)

    # Create output folder
    outputs_dir = base / "outputs" / repo_name
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Save file tree
    with open(outputs_dir / "file_tree.json", "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)

    # Summarize README
    readme_info = summarize_readme(target)
    with open(outputs_dir / "readme_summary.json", "w", encoding="utf-8") as f:
        json.dump(readme_info, f, indent=2)

    print(f"[repo_mapper] ✅ Completed. Outputs saved in: {outputs_dir.resolve()}")

if __name__ == "__main__":
    main()
 
