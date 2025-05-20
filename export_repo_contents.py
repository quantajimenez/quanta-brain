import os

def get_all_files(directory, extensions=None):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not extensions or file.endswith(tuple(extensions)):
                yield os.path.join(root, file)

output_file = "repo_full_contents.txt"
repo_root = os.getcwd()

with open(output_file, "w", encoding="utf-8") as out:
    for file_path in get_all_files(repo_root, extensions=['.py', '.txt', '.md', '.yaml', '.yml', '.json']):
        rel_path = os.path.relpath(file_path, repo_root)
        out.write(f"\n{'='*80}\n# {rel_path}\n{'='*80}\n")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                out.write(f.read())
        except Exception as e:
            out.write(f"\n[Could not read file: {e}]\n")
