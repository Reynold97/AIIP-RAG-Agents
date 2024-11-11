import os

# Root folder of your repository
root_folder_path = 'ui'  # Replace with the actual root folder path

# Output .txt file path
output_file = 'ui_code.txt'  # Replace with desired output file location

# Open the output file in write mode
with open(output_file, 'w') as outfile:
    # Walk through all directories and subdirectories
    for dirpath, dirnames, filenames in os.walk(root_folder_path):
        for filename in filenames:
            # Check if the file ends with .py
            if filename.endswith(".py"):
                # Full path to the Python script
                file_path = os.path.join(dirpath, filename)
                
                # Write the file path (relative to root) to the output file
                relative_path = os.path.relpath(file_path, root_folder_path)
                outfile.write(f"File Name: {relative_path}\n")
                outfile.write("=" * 40 + "\n")
                
                # Read and write the content of the script
                with open(file_path, 'r') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write("\n" + "=" * 40 + "\n\n")  # Separate each script by a line

print(f"All Python scripts have been written to {output_file}")

