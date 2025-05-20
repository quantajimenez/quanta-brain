import os

with open("repo_file_list.txt", "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk('.'):
        for fname in files:
            fpath = os.path.join(root, fname)
            outfile.write(f"{fpath}\n")
            # Optional: preview the first 5 lines of code for .py files
            if fname.endswith('.py'):
                try:
                    with open(fpath, encoding="utf-8") as codefile:
                        for i, line in enumerate(codefile):
                            if i >= 5: break
                            outfile.write(f"    {line.rstrip()}\n")
                except Exception as e:
                    outfile.write(f"    [Error reading file: {e}]\n")
            outfile.write("\n")
print("Export complete. Upload repo_file_list.txt to ChatGPT.")
