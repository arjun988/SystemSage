import json
import os
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.llms import Ollama

from volume import adjust_volume
from file import create_file_in_parent_directory, delete_file_from_parent_directory
from package_checker import check_package_installed, check_version

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

    def agent_chat(self, usr_prompt):
        print(f"User prompt: {usr_prompt}")
        if "volume" in usr_prompt.lower() or "louder" in usr_prompt.lower() or "quieter" in usr_prompt.lower():
            return adjust_volume(usr_prompt)
        elif "create" in usr_prompt.lower() and "file" in usr_prompt.lower():
            return create_file_in_parent_directory(usr_prompt)
        elif "delete" in usr_prompt.lower() and "file" in usr_prompt.lower():
            return delete_file_from_parent_directory(usr_prompt)
        elif "check package" in usr_prompt.lower():
            match = re.search(r'check package\s+([^\s]+)', usr_prompt, re.IGNORECASE)
            if match:
                package_name = match.group(1).strip()
                return check_package_installed(package_name)
            else:
                return "Please specify the package name in the format 'check package <package_name>'."
        elif "check version" in usr_prompt.lower():
            match = re.search(r'check version\s+([^\s]+)', usr_prompt, re.IGNORECASE)
            if match:
                software_name = match.group(1).strip()
                return check_version(software_name)
            else:
                return "Please specify the software name in the format 'check version <software_name>'."
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
