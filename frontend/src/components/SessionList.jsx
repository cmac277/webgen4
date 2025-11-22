import React, { useState } from 'react';
import { MessageSquare, Edit2, Check, X, Plus } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';

export default function SessionList({ sessions, currentSessionId, onSelectSession, onCreateSession, onRenameSession }) {
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');

  const startEdit = (session) => {
    setEditingId(session.session_id);
    setEditName(session.project_name);
  };

  const saveEdit = (sessionId) => {
    if (editName.trim()) {
      onRenameSession(sessionId, editName.trim());
    }
    setEditingId(null);
    setEditName('');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };

  return (
    <div className="w-64 bg-slate-900/50 border-r border-slate-700 flex flex-col" data-testid="session-list">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <Button
          onClick={onCreateSession}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          data-testid="new-session-button"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Sessions List */}
      <ScrollArea className="flex-1 p-2">
        <div className="space-y-2">
          {sessions.map(session => (
            <div
              key={session.session_id}
              className={`group rounded-lg p-3 transition-all ${
                currentSessionId === session.session_id
                  ? 'bg-purple-600/20 border border-purple-600/50'
                  : 'bg-slate-800/50 hover:bg-slate-800 border border-transparent'
              }`}
            >
              {editingId === session.session_id ? (
                <div className="flex items-center space-x-2">
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') saveEdit(session.session_id);
                      if (e.key === 'Escape') cancelEdit();
                    }}
                    className="h-8 bg-slate-900 border-slate-600 text-slate-100"
                    autoFocus
                    data-testid="rename-input"
                  />
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => saveEdit(session.session_id)}
                    className="h-8 w-8 text-green-400 hover:text-green-300"
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={cancelEdit}
                    className="h-8 w-8 text-red-400 hover:text-red-300"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ) : (
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => onSelectSession(session.session_id)}
                >
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <MessageSquare className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    <span className="text-sm text-slate-100 truncate">
                      {session.project_name}
                    </span>
                  </div>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      startEdit(session);
                    }}
                    className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-slate-100"
                    data-testid={`edit-session-${session.session_id}`}
                  >
                    <Edit2 className="w-3 h-3" />
                  </Button>
                </div>
              )}
              <p className="text-xs text-slate-500 mt-1">
                {new Date(session.last_updated).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}