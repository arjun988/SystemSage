import React, { useState } from "react";
import axios from "axios";

const ChatBox = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { from: "assistant", text: "Hello! How can I help you today?" },
    { from: "user", text: "I need information about your services." },
    { from: "assistant", text: "Sure! What would you like to know?" },
    { from: "user", text: "Can you tell me about your pricing?" },
  ]);

  const sendMessage = async () => {
    if (input.trim() === "") return;

    try {
      const response = await axios.post("http://localhost:8080/query", {
        query: input,
      });

      const message = response.data.message;

      setMessages([
        ...messages,
        { from: "user", text: input },
        { from: "assistant", text: message },
      ]);
      setInput("");
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages([
        ...messages,
        { from: "user", text: input },
        {
          from: "assistant",
          text: "Error: Unable to get response from server.",
        },
      ]);
    }
  };

  return (
    <div className="flex flex-col gap-4 relative">
      <div className="space-y-2">
        {messages.map((message, index) => (
          <div
            className={`w-full flex ${
              message.from === "assistant" ? "justify-start" : "justify-end"
            }`}
          >
            <div
              className={`p-2 w-fit rounded-xl ${
                message.from === "assistant"
                  ? "bg-zinc-200"
                  : "bg-blue-400 text-white"
              }`}
              key={index}
            >
              {message.text}
            </div>
          </div>
        ))}
        <div />
      </div>
      <div className="flex gap-4 w-full sticky bottom-4">
        <input
          style={{
            boxShadow:
              "rgba(0, 0, 0, 0.16) 0px 3px 6px, rgba(0, 0, 0, 0.23) 0px 3px 6px",
          }}
          className="w-full p-2 rounded-xl"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          style={{
            boxShadow:
              "rgba(0, 0, 0, 0.16) 0px 3px 6px, rgba(0, 0, 0, 0.23) 0px 3px 6px",
          }}
          className="px-6 py-2 rounded-xl bg-green-600 hover:bg-green-500  text-white "
          onClick={sendMessage}
        >
          SEND
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
