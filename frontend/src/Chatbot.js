import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Chatbot.css';
import ReactMarkdown from 'react-markdown';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);

  // Ref để scroll đến cuối
  const messagesEndRef = useRef(null);

  // Hàm scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Gọi scroll mỗi khi messages thay đổi
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newUserMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/message-generator', {
        question: input,
        session_id: sessionId
      });

      const answer = response.data.answer;
      const newSessionId = response.data.session_id;

      if (!sessionId) setSessionId(newSessionId);

      const newBotMessage = { role: 'bot', content: answer };
      setMessages(prev => [...prev, newBotMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { role: 'bot', content: '⚠️ Lỗi khi gửi yêu cầu. Vui lòng thử lại.' };
      setMessages(prev => [...prev, errorMessage]);
    }

    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">Chatbot - Đại Học Công Nghiệp Hà Nội (HaUI)</div>
      <div className="chat-window">
        {messages.map((msg, index) => {
          const cleanContent = msg.content.replace(/\n{3,}/g, '\n\n');

          return (
            <div key={index} className={`chat-message ${msg.role === 'user' ? 'user' : 'bot'}`}>
              {msg.role === 'bot' && (
                <img src="/logo_haui.png" alt="bot-avatar" className="avatar" />
              )}
              <div className="message-content">
                <ReactMarkdown>
                  {cleanContent}
                </ReactMarkdown>
              </div>
            </div>
          );
        })}

        {/* Auto scroll target */}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          placeholder="Nhập tin nhắn..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button onClick={handleSend}>Gửi</button>
      </div>
    </div>
  );
};

export default Chatbot;
