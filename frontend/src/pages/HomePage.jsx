import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from '../components/ChatInterface';
import PreviewPanel from '../components/PreviewPanel';
import SessionList from '../components/SessionList';
import Header from '../components/Header';
import { Toaster, toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function HomePage() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [generatedWebsite, setGeneratedWebsite] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('claude-sonnet-4');
  const [generationSteps, setGenerationSteps] = useState([]);

  useEffect(() => {
    // Create initial session on mount
    createSession();
  }, []);

  useEffect(() => {
    // Load sessions list
    loadSessions();
  }, [sessionId]);

  useEffect(() => {
    // Load messages when session changes
    if (sessionId) {
      loadMessages(sessionId);
      loadLatestWebsite(sessionId);
    }
  }, [sessionId]);

  const loadSessions = async () => {
    try {
      // Get all sessions from localStorage for now (can be backend later)
      const storedSessions = JSON.parse(localStorage.getItem('sessions') || '[]');
      setSessions(storedSessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createSession = async (projectName = 'New Website Project') => {
    try {
      const response = await axios.post(`${API}/session/create`, {
        project_name: projectName
      });
      
      const newSession = response.data;
      setSessionId(newSession.session_id);
      
      // Save to localStorage
      const storedSessions = JSON.parse(localStorage.getItem('sessions') || '[]');
      storedSessions.unshift(newSession);
      localStorage.setItem('sessions', JSON.stringify(storedSessions));
      setSessions(storedSessions);
      
      // Clear current state
      setMessages([]);
      setGeneratedWebsite(null);
      
      toast.success('New project created!');
    } catch (error) {
      console.error('Failed to create session:', error);
      toast.error('Failed to create session');
    }
  };

  const renameSession = async (sessionId, newName) => {
    try {
      // Update in backend (could add endpoint later)
      // For now, update in localStorage
      const storedSessions = JSON.parse(localStorage.getItem('sessions') || '[]');
      const updatedSessions = storedSessions.map(s => 
        s.session_id === sessionId ? { ...s, project_name: newName } : s
      );
      localStorage.setItem('sessions', JSON.stringify(updatedSessions));
      setSessions(updatedSessions);
      toast.success('Project renamed!');
    } catch (error) {
      console.error('Failed to rename session:', error);
      toast.error('Failed to rename project');
    }
  };

  const selectSession = async (sessionId) => {
    setSessionId(sessionId);
    setMessages([]);
    setGeneratedWebsite(null);
  };

  const loadMessages = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/session/${sessionId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const loadLatestWebsite = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/website/${sessionId}/latest`);
      setGeneratedWebsite(response.data);
    } catch (error) {
      // No website yet, that's ok
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
    
    // Initialize generation steps
    setGenerationSteps([
      { title: 'Planning', description: 'Analyzing requirements and creating structure...', status: 'active' },
      { title: 'Design', description: 'Generating visual design and color scheme...', status: 'pending' },
      { title: 'Code Generation', description: 'Writing HTML, CSS, and JavaScript...', status: 'pending' },
      { title: 'Optimization', description: 'Polishing and optimizing code...', status: 'pending' }
    ]);

    try {
      // Step 1: Planning
      await new Promise(resolve => setTimeout(resolve, 1000));
      setGenerationSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'complete' } :
        idx === 1 ? { ...step, status: 'active' } : step
      ));

      // Step 2: Design
      await new Promise(resolve => setTimeout(resolve, 1000));
      setGenerationSteps(prev => prev.map((step, idx) => 
        idx === 1 ? { ...step, status: 'complete' } :
        idx === 2 ? { ...step, status: 'active' } : step
      ));

      // Step 3: Code Generation (actual API call)
      const response = await axios.post(`${API}/generate/website`, {
        session_id: sessionId,
        prompt: prompt,
        model: selectedModel,
        framework: 'html'
      });

      setGenerationSteps(prev => prev.map((step, idx) => 
        idx === 2 ? { ...step, status: 'complete' } :
        idx === 3 ? { ...step, status: 'active' } : step
      ));

      // Step 4: Optimization
      await new Promise(resolve => setTimeout(resolve, 500));
      setGenerationSteps(prev => prev.map(step => ({ ...step, status: 'complete' })));

      setGeneratedWebsite(response.data);
      toast.success('Website generated successfully!');
    } catch (error) {
      console.error('Failed to generate website:', error);
      toast.error('Failed to generate website');
      setGenerationSteps([]);
    } finally {
      setIsLoading(false);
      setTimeout(() => setGenerationSteps([]), 2000);
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
        {/* Session List Sidebar */}
        <SessionList
          sessions={sessions}
          currentSessionId={sessionId}
          onSelectSession={selectSession}
          onCreateSession={() => createSession()}
          onRenameSession={renameSession}
        />

        {/* Chat Panel */}
        <div className="flex-1 border-r border-slate-700">
          <ChatInterface
            messages={messages}
            onSendMessage={sendMessage}
            onGenerateWebsite={generateWebsite}
            isLoading={isLoading}
            sessionId={sessionId}
            generationSteps={generationSteps}
          />
        </div>

        {/* Preview Panel */}
        <div className="flex-1">
          <PreviewPanel website={generatedWebsite} />
        </div>
      </div>
    </div>
  );
}