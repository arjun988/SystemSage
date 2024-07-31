import json
import os
import platform
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.llms import Ollama

# Additional imports for volume control
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
        from ctypes import cast, POINTER
    except ImportError as e:
        print(f"Error importing pycaw: {e}")

load_dotenv()

class QA_Agent:
    def __init__(self):
        llm = Ollama(model=os.getenv('LLM_MODEL', 'phi3'))
        print("Model Loaded")

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        q_chain = qa_prompt | llm

        self.chat_history = {}
        self.chat_model = RunnableWithMessageHistory(
            q_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )
        print("Agent Ready")

    def get_session_history(self, session_id: str):
        if session_id not in self.chat_history:
            self.chat_history[session_id] = ChatMessageHistory()
        return self.chat_history[session_id]

    def reformat_json(self, json_string, path):
        data = json.loads(json_string)
        formatted_messages = []
        for message in data['messages']:
            if message['type'] == 'human':
                user_content = message['content']
                ai_response = next((msg['content'] for msg in data['messages'] if msg['type'] == 'ai'), None)
                if ai_response:
                    formatted_messages.append({
                        "user_query": user_content,
                        "ai_response": ai_response
                    })

        formatted_data = {"messages": formatted_messages}
        with open(path, 'w') as f:
            json.dump(formatted_data, f, indent=2)
        return formatted_data

    def save_history(self, path="./agent_stup.json"):
        history = self.chat_history["acc_setup"].json()
        self.reformat_json(history, path)
        print(f"History saved to {path}")

    def get_system_prompt(self):
        return (
            """
            You are my laptop assistant who will help me to operate the laptops through commands as well as
            responsible to provide me with updates
            """
        )

    def adjust_volume(self, command):
        system = platform.system()
        print(f"Adjusting volume on {system} with command: {command}")
        if system == "Windows":
            try:
                # Initialize COM library
                CoInitialize()
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current_volume = volume.GetMasterVolumeLevelScalar()
                if "increase" in command.lower() or "louder" in command.lower():
                    volume.SetMasterVolumeLevelScalar(min(current_volume + 0.1, 1.0), None)
                    return "Volume increased."
                elif "decrease" in command.lower() or "quieter" in command.lower():
                    volume.SetMasterVolumeLevelScalar(max(current_volume - 0.1, 0.0), None)
                    return "Volume decreased."
            except Exception as e:
                return f"Error adjusting volume on Windows: {e}"
            finally:
                # Uninitialize COM library
                CoUninitialize()
        elif system == "Linux":
            try:
                if "increase" in command.lower() or "louder" in command.lower():
                    os.system("amixer -D pulse sset Master 10%+")
                    return "Volume increased."
                elif "decrease" in command.lower() or "quieter" in command.lower():
                    os.system("amixer -D pulse sset Master 10%-")
                    return "Volume decreased."
            except Exception as e:
                return f"Error adjusting volume on Linux: {e}"
        return "Command not recognized for volume control."

    def create_file_on_current_directory(self, prompt):
        current_directory = os.getcwd()

        # Extract file name and extension using regex
        match = re.search(r'create\s+file\s+([^\s]+)', prompt, re.IGNORECASE)
        if not match:
            return "Please specify the file name in the format 'create file <filename.extension>'."

        file_name = match.group(1).strip()

        # Ensure file name is not empty and valid
        if not file_name:
            return "File name cannot be empty."

        # Check if file already exists
        file_path = os.path.join(current_directory, file_name)
        if os.path.exists(file_path):
            return f"File {file_name} already exists in the current directory."

        try:
            with open(file_path, 'w') as file:
                pass  # Create an empty file
            return f"File {file_name} created in the current directory."
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def delete_file_from_current_directory(self, prompt):
        current_directory = os.getcwd()

        # Extract file name and extension using regex
        match = re.search(r'delete\s+file\s+([^\s]+)', prompt, re.IGNORECASE)
        if not match:
            return "Please specify the file name in the format 'delete file <filename.extension>'."

        file_name = match.group(1).strip()

        # Ensure file name is not empty and valid
        if not file_name:
            return "File name cannot be empty."

        # Construct the file path
        file_path = os.path.join(current_directory, file_name)
        if not os.path.exists(file_path):
            return f"File {file_name} does not exist in the current directory."

        try:
            os.remove(file_path)
            return f"File {file_name} deleted from the current directory."
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    def agent_chat(self, usr_prompt):
        print(f"User prompt: {usr_prompt}")
        if "volume" in usr_prompt.lower() or "louder" in usr_prompt.lower() or "quieter" in usr_prompt.lower():
            return self.adjust_volume(usr_prompt)
        elif "create" in usr_prompt.lower() and "file" in usr_prompt.lower():
            return self.create_file_on_current_directory(usr_prompt)
        elif "delete" in usr_prompt.lower() and "file" in usr_prompt.lower():
            return self.delete_file_from_current_directory(usr_prompt)
        response = self.chat_model.invoke(
            {"input": usr_prompt},
                config={
                    "configurable": {"session_id": "acc_setup"}
                }
        )
        print(f"Model response: {response}")
        return response

app = Flask(__name__)
CORS(app)

chat_agent = QA_Agent()

@app.route('/query', methods=['POST'])
def route_query():
    data = request.get_json()
    query_text = data.get('query')

    if not query_text:
        return jsonify({"error": "No query text provided"}), 400

    try:
        response = chat_agent.agent_chat(query_text)
        return jsonify({"message": response}), 200
    except Exception as e:
        print(f"Error during query handling: {e}")
        return jsonify({"error": f"An error occurred while querying the model: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
