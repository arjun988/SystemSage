# Features
1. Volume Control: Adjust the system volume on Windows and Linux.
2. File Operations: Create and delete files in the current directory.
3. Conversational AI: Chat with the agent using natural language.
# Installation
1. Clone the Repository:

2. Create and Activate a Virtual Environment (optional but recommended):

```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install Dependencies:

```
pip install -r requirements.txt
```
4. Set Up Environment Variables:

Create a .env file in the root directory and add the necessary environment variables, such as:

```
LLM_MODEL=phi3
```
5. Install ollama and run command in cmd
```
ollama pull model_name
```
# Run the Application:
1. Backend
```
python a.py
```
2. application
```
npm start
```

# Example Commands:

1. Adjust Volume:
Increase Volume: "Increase the volume"
Decrease Volume: "Decrease the volume"
2. Create File:
Create File: "Create file example.txt"
3. Delete File:
Delete File: "Delete file example.txt"
    