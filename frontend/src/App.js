import React from "react";
import ChatBox from "./components/ChatBox";

function App() {
  return (
    <div className="flex justify-center w-full">
      <div className="flex flex-col gap-4 p-4 container">
        <div className="text-4xl text-center">Ollama AI Chat</div>
        <ChatBox />
      </div>
    </div>
  );
}

export default App;
