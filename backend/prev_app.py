'''import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.llms import Ollama

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
            You are my assistant who will help me by organizing my thoughts.
            Your job is to ask questions that solve my goals or help me
            understand my issues better and help me gain new insights.
            Ask thought provoking questions which will challenge my
            abilities or give me a deeper perspective to myself. Always
            ask a single question at a time.
            """
        )
    
    def agent_chat(self, usr_prompt):
        response = self.chat_model.invoke(
            {"input": usr_prompt},
                config={
                    "configurable": {"session_id": "acc_setup"}
                }
        )
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
        return jsonify({"error": f"An error occurred while querying the model: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
'''