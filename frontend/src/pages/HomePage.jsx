import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from '../components/ChatInterface';
import PreviewPanel from '../components/PreviewPanel';
import Header from '../components/Header';
import { Toaster, toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function HomePage() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [generatedWebsite, setGeneratedWebsite] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('claude-sonnet-4');

  useEffect(() => {
    // Create session on mount
    createSession();
  }, []);

  const createSession = async () => {
    try {
      const response = await axios.post(`${API}/session/create`, {
        project_name: 'New Website Project'
      });
      setSessionId(response.data.session_id);
      toast.success('Session created successfully!');
    } catch (error) {
      console.error('Failed to create session:', error);
      toast.error('Failed to create session');
    }
  };

  const sendMessage = async (message) => {
    if (!sessionId) {
      toast.error('No active session');
      return;
    }

    setIsLoading(true);
    
    // Add user message immediately
    const userMsg = { role: 'user', content: message, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const response = await axios.post(`${API}/chat/message`, {
        session_id: sessionId,
        message: message,
        model: selectedModel
      });

      // Add assistant message
      const assistantMsg = {
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMsg]);

      // If website data is included
      if (response.data.website_data) {
        setGeneratedWebsite(response.data.website_data);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const generateWebsite = async (prompt) => {
    if (!sessionId) {
      toast.error('No active session');
      return;
    }

    setIsLoading(true);
    toast.info('Generating your website...');

    try {
      const response = await axios.post(`${API}/generate/website`, {
        session_id: sessionId,
        prompt: prompt,
        model: selectedModel,
        framework: 'html'
      });

      setGeneratedWebsite(response.data);
      toast.success('Website generated successfully!');
    } catch (error) {
      console.error('Failed to generate website:', error);
      toast.error('Failed to generate website');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" data-testid="homepage">
      <Toaster position="top-right" richColors />
      
      <Header 
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
      />

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Chat Panel */}
        <div className="w-1/2 border-r border-slate-700">
          <ChatInterface
            messages={messages}
            onSendMessage={sendMessage}
            onGenerateWebsite={generateWebsite}
            isLoading={isLoading}
            sessionId={sessionId}
          />
        </div>

        {/* Preview Panel */}
        <div className="w-1/2">
          <PreviewPanel website={generatedWebsite} />
        </div>
      </div>
    </div>
  );
}