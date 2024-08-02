import os
import re

def create_file_in_parent_directory(prompt):
    parent_directory = os.path.dirname(os.getcwd())

    # Extract file name and extension using regex
    match = re.search(r'create\s+file\s+([^\s]+)', prompt, re.IGNORECASE)
    if not match:
        return "Please specify the file name in the format 'create file <filename.extension>'."

    file_name = match.group(1).strip()

    # Ensure file name is not empty and valid
    if not file_name:
        return "File name cannot be empty."

    # Check if file already exists
    file_path = os.path.join(parent_directory, file_name)
    if os.path.exists(file_path):
        return f"File {file_name} already exists in the parent directory."

    try:
        with open(file_path, 'w') as file:
            pass  # Create an empty file
        return f"File {file_name} created in the parent directory."
    except Exception as e:
        return f"Error creating file: {str(e)}"

def delete_file_from_parent_directory(prompt):
    parent_directory = os.path.dirname(os.getcwd())

    # Extract file name and extension using regex
    match = re.search(r'delete\s+file\s+([^\s]+)', prompt, re.IGNORECASE)
    if not match:
        return "Please specify the file name in the format 'delete file <filename.extension>'."

    file_name = match.group(1).strip()

    # Ensure file name is not empty and valid
    if not file_name:
        return "File name cannot be empty."

    # Construct the file path
    file_path = os.path.join(parent_directory, file_name)
    if not os.path.exists(file_path):
        return f"File {file_name} does not exist in the parent directory."

    try:
        os.remove(file_path)
        return f"File {file_name} deleted from the parent directory."
    except Exception as e:
        return f"Error deleting file: {str(e)}"
