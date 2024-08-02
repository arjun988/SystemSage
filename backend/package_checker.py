import subprocess
import sys

def check_version(software):
    try:
        if software.lower() == "python":
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        elif software.lower() == "pip":
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True)
        else:
            result = subprocess.run([software, '--version'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error checking {software} version: {str(e)}"

def check_package_installed(package_name):
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], capture_output=True, text=True)
        if result.returncode == 0:
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if line.startswith('Version:'):
                    version = line.split(': ')[1]
                    return f"Package '{package_name}' is installed. Version: {version}"
            return f"Package '{package_name}' is installed, but version information is not available."
        else:
            return f"Package '{package_name}' is not installed."
    except Exception as e:
        return f"An error occurred while checking the package: {str(e)}"
