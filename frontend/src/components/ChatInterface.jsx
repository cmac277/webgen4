import React, { useState, useRef, useEffect } from 'react';
import { Send, Wand2, Upload, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import axios from 'axios';
import { toast } from 'sonner';
import ReactMarkdown from 'react-markdown';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ChatInterface({ messages, onSendMessage, onGenerateWebsite, isLoading, sessionId }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleGenerate = () => {
    if (input.trim() && !isLoading) {
      onGenerateWebsite(input);
      setInput('');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !sessionId) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      toast.info('Uploading file...');
      const response = await axios.post(`${API}/upload/asset`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('File uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('File upload failed');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900/30" data-testid="chat-interface">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full mx-auto flex items-center justify-center">
                <Wand2 className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-100">Start Creating</h2>
              <p className="text-slate-400 max-w-md mx-auto">
                Describe your dream website and watch it come to life with AI-powered code generation.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            data-testid={`message-${msg.role}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  : 'bg-slate-800 text-slate-100'
              }`}
            >
              {msg.role === 'assistant' ? (
                <ReactMarkdown className="prose prose-invert prose-sm max-w-none">
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <p className="text-sm">{msg.content}</p>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start" data-testid="loading-indicator">
            <div className="bg-slate-800 rounded-2xl px-4 py-3 flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
              <span className="text-sm text-slate-300">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-700 p-4 bg-slate-900/50">
        <div className="flex items-end space-x-2">
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileUpload}
            accept="image/*,.pdf,.doc,.docx"
          />
          
          <Button
            variant="ghost"
            size="icon"
            className="mb-1 text-slate-400 hover:text-slate-100"
            onClick={() => fileInputRef.current?.click()}
            data-testid="upload-button"
          >
            <Upload className="w-5 h-5" />
          </Button>

          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your website idea..."
            className="flex-1 bg-slate-800 border-slate-600 text-slate-100 placeholder:text-slate-500 resize-none"
            rows={3}
            data-testid="chat-input"
          />

          <div className="flex flex-col space-y-2">
            <Button
              onClick={handleGenerate}
              disabled={!input.trim() || isLoading}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              data-testid="generate-button"
            >
              <Wand2 className="w-4 h-4 mr-2" />
              Generate
            </Button>
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              variant="outline"
              className="border-slate-600 text-slate-100 hover:bg-slate-800"
              data-testid="send-button"
            >
              <Send className="w-4 h-4 mr-2" />
              Chat
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}