import os

def generate_file_structure(directory, output_file):
    with open(output_file, "w") as f:
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ and specific database directories
            dirs[:] = [d for d in dirs if d not in ["__pycache__"] and not root.endswith("chroma_db")]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * level
            f.write(f"{indent}|-- {os.path.basename(root)}\n")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                if "__pycache__" not in file:
                    f.write(f"{sub_indent}|-- {file}\n")

def main():
    # Specify the path of the folder you want to get the structure of
    directory = "ui"  # Change '.' to your desired directory path if needed
    output_file = "ui_structure.txt"
    
    generate_file_structure(directory, output_file)
    print(f"File structure saved to '{output_file}'")

if __name__ == "__main__":
    main()