'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

type PromptType = 'paid' | 'unpaid' | 'crawler';

interface PromptTemplate {
  content: string;
  lastSaved: Date | null;
  characterCount: number;
  wordCount: number;
}

interface PromptContextType {
  prompts: Record<PromptType, PromptTemplate>;
  activeTab: PromptType;
  checkedTypes: Set<PromptType>;
  editorTheme: 'vs-light' | 'vs-dark';
  setPromptContent: (type: PromptType, content: string) => void;
  setActiveTab: (type: PromptType) => void;
  setCheckedTypes: (types: Set<PromptType>) => void;
  setEditorTheme: (theme: 'vs-light' | 'vs-dark') => void;
  savePrompts: (triggerId: string) => Promise<void>;
  loadPrompts: (triggerId: string) => Promise<void>;
  isSaving: boolean;
  saveError: string | null;
}

const PromptContext = createContext<PromptContextType | undefined>(undefined);

const calculateStats = (content: string) => {
  const characterCount = content.length;
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  return { characterCount, wordCount };
};

export function PromptProvider({ children }: { children: ReactNode }) {
  const [prompts, setPrompts] = useState<Record<PromptType, PromptTemplate>>({
    paid: { content: '', lastSaved: null, characterCount: 0, wordCount: 0 },
    unpaid: { content: '', lastSaved: null, characterCount: 0, wordCount: 0 },
    crawler: { content: '', lastSaved: null, characterCount: 0, wordCount: 0 }
  });

  const [activeTab, setActiveTab] = useState<PromptType>('paid');
  const [checkedTypes, setCheckedTypes] = useState<Set<PromptType>>(new Set(['paid']));
  const [editorTheme, setEditorThemeState] = useState<'vs-light' | 'vs-dark'>('vs-dark');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [triggerId, setTriggerId] = useState<string | null>(null);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('editor-theme') as 'vs-light' | 'vs-dark' | null;
    if (savedTheme) {
      setEditorThemeState(savedTheme);
    } else {
      // Auto-detect system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setEditorThemeState(prefersDark ? 'vs-dark' : 'vs-light');
    }
  }, []);

  const setEditorTheme = (theme: 'vs-light' | 'vs-dark') => {
    setEditorThemeState(theme);
    localStorage.setItem('editor-theme', theme);
  };

  const setPromptContent = (type: PromptType, content: string) => {
    const stats = calculateStats(content);
    setPrompts(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        content,
        ...stats
      }
    }));
  };

  const savePrompts = async (tid: string) => {
    try {
      setIsSaving(true);
      setSaveError(null);

      const response = await fetch(`/api/triggers/${tid}/config/prompts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompts: {
            paid: { template: prompts.paid.content },
            unpaid: { template: prompts.unpaid.content },
            crawler: { template: prompts.crawler.content }
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save prompts');
      }

      // Update lastSaved timestamps
      const now = new Date();
      setPrompts(prev => ({
        paid: { ...prev.paid, lastSaved: now },
        unpaid: { ...prev.unpaid, lastSaved: now },
        crawler: { ...prev.crawler, lastSaved: now }
      }));

    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save prompts');
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  // Manual save - no auto-save functionality

  const loadPrompts = async (tid: string) => {
    try {
      setTriggerId(tid);
      const response = await fetch(`/api/triggers/${tid}/config`);

      if (!response.ok) {
        throw new Error('Failed to load configuration');
      }

      const config = await response.json();

      if (config.prompts) {
        // Helper function to extract template from either new or legacy format
        const extractTemplate = (promptData: any): string => {
          if (!promptData) return '';
          // New format: { template: "...", last_saved: "...", version_history: [] }
          if (promptData.template) return promptData.template;
          // Legacy format: { article: "...", system: null }
          if (promptData.article) return promptData.article;
          return '';
        };

        const extractLastSaved = (promptData: any): Date | null => {
          if (!promptData || !promptData.last_saved) return null;
          return new Date(promptData.last_saved);
        };

        setPrompts({
          paid: {
            content: extractTemplate(config.prompts.paid),
            lastSaved: extractLastSaved(config.prompts.paid),
            ...calculateStats(extractTemplate(config.prompts.paid))
          },
          unpaid: {
            content: extractTemplate(config.prompts.unpaid),
            lastSaved: extractLastSaved(config.prompts.unpaid),
            ...calculateStats(extractTemplate(config.prompts.unpaid))
          },
          crawler: {
            content: extractTemplate(config.prompts.crawler),
            lastSaved: extractLastSaved(config.prompts.crawler),
            ...calculateStats(extractTemplate(config.prompts.crawler))
          }
        });
      }
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to load prompts');
    }
  };

  const value: PromptContextType = {
    prompts,
    activeTab,
    checkedTypes,
    editorTheme,
    setPromptContent,
    setActiveTab,
    setCheckedTypes,
    setEditorTheme,
    savePrompts,
    loadPrompts,
    isSaving,
    saveError
  };

  return <PromptContext.Provider value={value}>{children}</PromptContext.Provider>;
}

export function usePrompt() {
  const context = useContext(PromptContext);
  if (context === undefined) {
    throw new Error('usePrompt must be used within a PromptProvider');
  }
  return context;
}
