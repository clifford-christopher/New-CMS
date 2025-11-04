import { Undo, Redo, Eye, Clock } from 'lucide-react';
import { Button } from './ui/button';
import { useEffect, useRef, useState } from 'react';
import type { PromptType } from './TypeSelectionCheckbox';

type PromptEditorProps = {
  value: string;
  onChange: (value: string) => void;
  selectedTypes?: PromptType[];
};

type PromptStates = {
  paid: string;
  unpaid: string;
  crawler: string;
};

export function PromptEditor({ value, onChange, selectedTypes = ['paid'] }: PromptEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [activeTab, setActiveTab] = useState<PromptType>('paid');
  const [promptStates, setPromptStates] = useState<PromptStates>({
    paid: value,
    unpaid: `# Unpaid Version Prompt

Generate a free-tier news article for {{stock_symbol}}:

## Earnings Information
{{earnings}}

## Basic Summary
- Provide essential information only
- Keep under 150 words
- No premium insights`,
    crawler: `# Web Crawler Version Prompt

Generate a web-crawled article for {{stock_symbol}}:

## Crawled Data
{{web_data}}

## Instructions:
- Use publicly available data
- Include source citations
- Aggregate multiple sources`
  });

  // Initialize with current value
  useEffect(() => {
    setPromptStates(prev => ({
      ...prev,
      paid: value
    }));
  }, [value]);

  // Switch to first available tab if current tab is not selected
  useEffect(() => {
    if (!selectedTypes.includes(activeTab)) {
      setActiveTab(selectedTypes[0]);
    }
  }, [selectedTypes, activeTab]);

  const currentPrompt = promptStates[activeTab];

  const handlePromptChange = (newValue: string) => {
    setPromptStates(prev => ({
      ...prev,
      [activeTab]: newValue
    }));
    
    if (activeTab === 'paid') {
      onChange(newValue);
    }
  };

  const getTabIcon = (type: PromptType) => {
    switch (type) {
      case 'paid': return '💰';
      case 'unpaid': return '🆓';
      case 'crawler': return '🕷️';
    }
  };

  const getTabLabel = (type: PromptType) => {
    switch (type) {
      case 'paid': return 'Paid';
      case 'unpaid': return 'Unpaid';
      case 'crawler': return 'Web Crawler';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Toolbar with Tabs */}
      <div className="bg-[#f8f9fa] border-b border-[#dee2e6]">
        {/* Top Row - Title & Actions */}
        <div className="px-4 py-3 flex items-center justify-between border-b border-[#dee2e6]">
          <div className="flex items-center gap-3">
            <h3>Prompt Template</h3>
            <span className="text-xs italic text-[#6c757d]">
              <Clock className="w-3 h-3 inline mr-1" />
              Saved 2 minutes ago
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm">
              <Undo className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm">
              <Redo className="w-4 h-4" />
            </Button>
            <div className="w-px h-6 bg-[#dee2e6] mx-1" />
            <Button variant="outline" size="sm">
              Preview
            </Button>
            <Button variant="outline" size="sm">
              History
            </Button>
          </div>
        </div>

        {/* Bottom Row - Tabs */}
        <div className="px-4 flex items-center gap-2">
          {selectedTypes.map(type => (
            <button
              key={type}
              onClick={() => setActiveTab(type)}
              className={`px-5 py-2.5 flex items-center gap-2 transition-all border-b-3 ${
                activeTab === type
                  ? 'bg-white text-[#0d6efd] border-b-[3px] border-[#0d6efd]'
                  : 'text-[#6c757d] hover:bg-[#e9ecef] border-b-[3px] border-transparent'
              }`}
            >
              <span className="text-base">{getTabIcon(type)}</span>
              <span className={activeTab === type ? '' : ''}>{getTabLabel(type)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Editor Area */}
      <div className="relative">
        <div className="flex">
          {/* Line Numbers */}
          <div className="bg-[#f8f9fa] p-4 pr-2 text-right select-none">
            {currentPrompt.split('\n').map((_, idx) => (
              <div key={idx} className="text-xs text-[#6c757d] leading-6">
                {idx + 1}
              </div>
            ))}
          </div>

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={currentPrompt}
            onChange={(e) => handlePromptChange(e.target.value)}
            className="flex-1 p-4 font-mono text-sm leading-6 resize-none border-0 focus:outline-none focus:ring-2 focus:ring-[#0d6efd] min-h-[600px]"
            style={{ fontFamily: 'SF Mono, Consolas, Monaco, monospace' }}
          />
        </div>
      </div>

      {/* Validation Panel */}
      <div className="border-t border-[#dee2e6] p-4 bg-[#f8f9fa]">
        <div className="flex items-center gap-2 text-sm text-[#198754]">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>All placeholders valid</span>
        </div>

        <div className="mt-4 flex items-center gap-4">
          <Button className="bg-[#0d6efd] hover:bg-[#0b5ed7]">
            <Eye className="w-4 h-4 mr-2" />
            Preview Final Prompt
          </Button>
          <span className="text-xs text-[#6c757d]">Test with: TCS</span>
        </div>
      </div>
    </div>
  );
}
