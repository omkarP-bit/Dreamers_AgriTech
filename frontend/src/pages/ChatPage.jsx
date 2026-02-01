import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { chatAPI } from '../api';
import { Send, LogOut, MessageCircle } from 'lucide-react';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [season, setSeason] = useState(null);
  const [error, setError] = useState('');
  const { user, logout } = useAuth();
  const messagesEndRef = useRef(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await chatAPI.getChatHistory();
      const conversations = response.data.conversations || [];
      
      // Convert conversations to messages format
      const messagesList = [];
      conversations.forEach(conv => {
        if (conv.message) {
          messagesList.push({
            id: conv.id,
            text: conv.message,
            sender: 'user',
            timestamp: new Date(conv.created_at)
          });
        }
        if (conv.response) {
          messagesList.push({
            id: conv.id + '_response',
            text: conv.response,
            sender: 'bot',
            timestamp: new Date(conv.created_at)
          });
        }
      });
      
      setMessages(messagesList);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError('');

    // Add user message to UI immediately
    const userMsg = {
      id: Date.now(),
      text: userMessage,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      setLoading(true);

      // 🔥 FIX: If no season exists, create one NOW (don't wait for response)
      let seasonId = season?.id;
      if (!seasonId) {
        // Generate a new season ID for this conversation
        seasonId = 'season_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        setSeason({ id: seasonId });
        console.log(`📦 Created new season: ${seasonId}`);
      }

      console.log(`📤 Sending message with season_id: ${seasonId}`);

      // Send message to backend
      const response = await chatAPI.sendMessage({
        message: userMessage,
        season_id: seasonId
      });

      // Add bot response
      const botMsg = {
        id: response.data.message_id,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMsg]);

      // Update season ID if it came from backend
      if (response.data.season_id && response.data.season_id !== seasonId) {
        setSeason({ id: response.data.season_id });
      }

    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMessage = err.response?.data?.detail || 
                          (typeof err.response?.data === 'string' ? err.response?.data : null) ||
                          err.message || 
                          'Failed to send message. Please try again.';
      setError(String(errorMessage));
      
      // Remove the failed user message from display
      setMessages(prev => prev.filter(msg => msg.id !== userMsg.id));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="h-screen bg-gradient-to-br from-green-50 to-blue-50 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
            <MessageCircle className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">FasalMitra</h1>
            <p className="text-xs text-gray-600">Chat with your AI farming assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {user && (
            <div className="text-right">
              <p className="text-sm font-medium text-gray-800">{user.name}</p>
              <p className="text-xs text-gray-600">{user.email}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 px-4 py-2 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut size={18} />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <MessageCircle className="text-green-600 mb-4" size={48} />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to FasalMitra!</h2>
            <p className="text-gray-600 max-w-md">
              I'm your AI-powered farming assistant. Ask me anything about your crops, 
              farming techniques, weather, market prices, and more. Let's get started!
            </p>
          </div>
        ) : (
          <>
            {messages.map(message => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-green-600 text-white rounded-br-none'
                      : 'bg-gray-200 text-gray-800 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <span className={`text-xs mt-1 block ${
                    message.sender === 'user' ? 'text-green-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex justify-between items-center">
            <span>{String(error)}</span>
            <button 
              onClick={() => setError('')}
              className="text-red-700 hover:text-red-900 font-bold ml-4"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask me anything about farming..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2 font-semibold"
          >
            <Send size={18} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">
          No prerequisites needed - just start chatting with your AI assistant!
        </p>
      </div>
    </div>
  );
};

export default ChatPage;
