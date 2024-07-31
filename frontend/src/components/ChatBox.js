import React, { useState } from 'react';
import axios from 'axios';

const ChatBox = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);

    const sendMessage = async () => {
        if (input.trim() === '') return;

        try {
            const response = await axios.post('http://localhost:8080/query', {
                query: input
            });

            const message = response.data.message;

            setMessages([...messages, { from: 'user', text: input }, { from: 'assistant', text: message }]);
            setInput('');
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages([...messages, { from: 'user', text: input }, { from: 'assistant', text: 'Error: Unable to get response from server.' }]);
        }
    };

    return (
        <div>
            <div className="chat-box">
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.from}`}>
                        {message.text}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default ChatBox;
