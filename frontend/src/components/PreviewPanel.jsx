import React, { useState } from 'react';
import { Maximize2, Code, Download, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import Editor from '@monaco-editor/react';

export default function PreviewPanel({ website }) {
  const [activeTab, setActiveTab] = useState('preview');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const downloadCode = () => {
    if (!website) return;

    const blob = new Blob([website.html_content || ''], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'website.html';
    a.click();
    URL.revokeObjectURL(url);
  };

  const openInNewTab = () => {
    if (!website?.html_content) return;
    
    const newWindow = window.open();
    newWindow.document.write(website.html_content);
    newWindow.document.close();
  };

  return (
    <div className="h-full flex flex-col bg-slate-900/30" data-testid="preview-panel">
      {/* Toolbar */}
      <div className="h-14 bg-slate-900/50 border-b border-slate-700 px-4 flex items-center justify-between">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex items-center justify-between">
            <TabsList className="bg-slate-800 border-slate-600">
              <TabsTrigger value="preview" className="data-[state=active]:bg-purple-600" data-testid="preview-tab">
                Preview
              </TabsTrigger>
              <TabsTrigger value="html" className="data-[state=active]:bg-purple-600" data-testid="html-tab">
                HTML
              </TabsTrigger>
              <TabsTrigger value="css" className="data-[state=active]:bg-purple-600" data-testid="css-tab">
                CSS
              </TabsTrigger>
              <TabsTrigger value="js" className="data-[state=active]:bg-purple-600" data-testid="js-tab">
                JavaScript
              </TabsTrigger>
            </TabsList>

            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={downloadCode}
                disabled={!website}
                className="text-slate-400 hover:text-slate-100"
                data-testid="download-button"
              >
                <Download className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={openInNewTab}
                disabled={!website}
                className="text-slate-400 hover:text-slate-100"
                data-testid="open-new-tab-button"
              >
                <ExternalLink className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Tabs>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {!website ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-slate-800 rounded-full mx-auto flex items-center justify-center">
                <Code className="w-10 h-10 text-slate-600" />
              </div>
              <p className="text-slate-400">
                Your generated website will appear here
              </p>
            </div>
          </div>
        ) : (
          <Tabs value={activeTab} className="h-full">
            <TabsContent value="preview" className="h-full m-0 p-0">
              <iframe
                srcDoc={website.html_content}
                className="w-full h-full bg-white"
                title="Website Preview"
                sandbox="allow-scripts allow-same-origin"
                data-testid="preview-iframe"
              />
            </TabsContent>

            <TabsContent value="html" className="h-full m-0">
              <Editor
                height="100%"
                defaultLanguage="html"
                value={website.html_content || ''}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
            </TabsContent>

            <TabsContent value="css" className="h-full m-0">
              <Editor
                height="100%"
                defaultLanguage="css"
                value={website.css_content || '/* No additional CSS */'}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
            </TabsContent>

            <TabsContent value="js" className="h-full m-0">
              <Editor
                height="100%"
                defaultLanguage="javascript"
                value={website.js_content || '// No JavaScript'}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
}