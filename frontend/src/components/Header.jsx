import React from 'react';
import { Code2, Sparkles } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

export default function Header({ selectedModel, onModelChange }) {
  const models = [
    { id: 'claude-sonnet-4', name: 'Claude Sonnet 4' },
    { id: 'gpt-5', name: 'GPT-5' },
    { id: 'gpt-5-mini', name: 'GPT-5 Mini' },
    { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro' }
  ];

  return (
    <header className="h-16 bg-slate-900/50 backdrop-blur-xl border-b border-slate-700 px-6 flex items-center justify-between" data-testid="header">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
          <Code2 className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Code Weaver
          </h1>
          <p className="text-xs text-slate-400">AI-Powered Website Generator</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-sm text-slate-300">AI Model:</span>
        </div>
        <Select value={selectedModel} onValueChange={onModelChange}>
          <SelectTrigger className="w-48 bg-slate-800 border-slate-600 text-slate-100" data-testid="model-selector">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-slate-800 border-slate-600">
            {models.map(model => (
              <SelectItem 
                key={model.id} 
                value={model.id}
                className="text-slate-100 focus:bg-slate-700 focus:text-slate-100"
                data-testid={`model-option-${model.id}`}
              >
                {model.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </header>
  );
}