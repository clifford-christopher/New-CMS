'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';

type PromptType = 'paid' | 'unpaid' | 'crawler';

interface VersionEntry {
  id: string;
  timestamp: Date;
  template: string;
  characterCount: number;
  wordCount: number;
  isManualCheckpoint: boolean;
}

interface PromptHistory {
  versions: VersionEntry[];
  currentIndex: number;
  pendingChanges: boolean;
}

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
  canUndo: (type: PromptType) => boolean;
  canRedo: (type: PromptType) => boolean;
  undo: (type: PromptType) => void;
  redo: (type: PromptType) => void;
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

const HISTORY_KEY_PREFIX = 'promptHistory_';
const MAX_VERSIONS = 10;

const calculateStats = (content: string) => {
  const characterCount = content.length;
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  return { characterCount, wordCount };
};

const createVersionEntry = (template: string, isCheckpoint: boolean = false): VersionEntry => {
  const stats = calculateStats(template);
  return {
    id: `v_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date(),
    template,
    characterCount: stats.characterCount,
    wordCount: stats.wordCount,
    isManualCheckpoint: isCheckpoint
  };
};

const loadHistoryFromStorage = (type: PromptType): PromptHistory => {
  try {
    const stored = sessionStorage.getItem(`${HISTORY_KEY_PREFIX}${type}`);
    if (stored) {
      const parsed = JSON.parse(stored);
      return {
        versions: parsed.versions.map((v: any) => ({
          ...v,
          timestamp: new Date(v.timestamp)
        })),
        currentIndex: parsed.currentIndex,
        pendingChanges: false
      };
    }
  } catch (err) {
    console.warn(`Failed to load history for ${type}:`, err);
  }

  return {
    versions: [],
    currentIndex: -1,
    pendingChanges: false
  };
};

const saveHistoryToStorage = (type: PromptType, history: PromptHistory) => {
  try {
    sessionStorage.setItem(
      `${HISTORY_KEY_PREFIX}${type}`,
      JSON.stringify({
        versions: history.versions,
        currentIndex: history.currentIndex
      })
    );
  } catch (err) {
    console.warn(`Failed to save history for ${type}:`, err);
  }
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

  // Initialize history from sessionStorage
  const [history, setHistory] = useState<Record<PromptType, PromptHistory>>({
    paid: loadHistoryFromStorage('paid'),
    unpaid: loadHistoryFromStorage('unpaid'),
    crawler: loadHistoryFromStorage('crawler')
  });


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

  // Version history functions
  const canUndo = useCallback((type: PromptType) => history[type].currentIndex > 0, [history]);

  const canRedo = useCallback(
    (type: PromptType) => history[type].currentIndex < history[type].versions.length - 1,
    [history]
  );

  const undo = useCallback((type: PromptType) => {
    if (!canUndo(type)) return;

    setHistory(prev => {
      const newHistory = { ...prev };
      const typeHistory = { ...newHistory[type] };
      typeHistory.currentIndex--;

      const version = typeHistory.versions[typeHistory.currentIndex];
      if (version) {
        setPrompts(p => ({
          ...p,
          [type]: {
            ...p[type],
            content: version.template,
            ...calculateStats(version.template)
          }
        }));
      }

      typeHistory.pendingChanges = false;
      newHistory[type] = typeHistory;
      saveHistoryToStorage(type, typeHistory);
      return newHistory;
    });
  }, [canUndo]);

  const redo = useCallback((type: PromptType) => {
    if (!canRedo(type)) return;

    setHistory(prev => {
      const newHistory = { ...prev };
      const typeHistory = { ...newHistory[type] };
      typeHistory.currentIndex++;

      const version = typeHistory.versions[typeHistory.currentIndex];
      if (version) {
        setPrompts(p => ({
          ...p,
          [type]: {
            ...p[type],
            content: version.template,
            ...calculateStats(version.template)
          }
        }));
      }

      typeHistory.pendingChanges = false;
      newHistory[type] = typeHistory;
      saveHistoryToStorage(type, typeHistory);
      return newHistory;
    });
  }, [canRedo]);

  const saveAsVersion = useCallback((type: PromptType, isCheckpoint: boolean = false) => {
    const currentContent = prompts[type].content;
    const newVersion = createVersionEntry(currentContent, isCheckpoint);

    setHistory(prev => {
      const newHistory = { ...prev };
      const typeHistory = { ...newHistory[type] };

      // If not at the end, discard future history
      if (typeHistory.currentIndex < typeHistory.versions.length - 1) {
        typeHistory.versions = typeHistory.versions.slice(0, typeHistory.currentIndex + 1);
      }

      // Add new version
      typeHistory.versions.push(newVersion);
      typeHistory.currentIndex = typeHistory.versions.length - 1;

      // Keep only last 10 versions (FIFO)
      if (typeHistory.versions.length > MAX_VERSIONS) {
        typeHistory.versions = typeHistory.versions.slice(-MAX_VERSIONS);
        typeHistory.currentIndex = typeHistory.versions.length - 1;
      }

      typeHistory.pendingChanges = false;

      newHistory[type] = typeHistory;
      saveHistoryToStorage(type, typeHistory);
      return newHistory;
    });
  }, [prompts]);

  const loadVersion = useCallback((type: PromptType, versionIndex: number) => {
    const version = history[type].versions[versionIndex];
    if (!version) return;

    setPrompts(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        content: version.template,
        ...calculateStats(version.template)
      }
    }));

    setHistory(prev => {
      const newHistory = { ...prev };
      const typeHistory = { ...newHistory[type] };
      typeHistory.currentIndex = versionIndex;
      typeHistory.pendingChanges = false;
      newHistory[type] = typeHistory;
      saveHistoryToStorage(type, typeHistory);
      return newHistory;
    });
  }, [history]);

  const setPromptContent = (type: PromptType, content: string) => {
    const stats = calculateStats(content);
    const currentContent = prompts[type].content;

    setPrompts(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        content,
        ...stats
      }
    }));

    // Only create a new version if content actually changed and we're at the current version
    if (content !== currentContent) {
      setHistory(prev => {
        const newHistory = { ...prev };
        const typeHistory = { ...newHistory[type] };

        // If not at the end, discard future history
        if (typeHistory.currentIndex < typeHistory.versions.length - 1) {
          typeHistory.versions = typeHistory.versions.slice(0, typeHistory.currentIndex + 1);
        }

        // Create and add new version
        const newVersion = createVersionEntry(content, false);
        typeHistory.versions.push(newVersion);
        typeHistory.currentIndex = typeHistory.versions.length - 1;

        // Keep only last 10 versions (FIFO)
        if (typeHistory.versions.length > MAX_VERSIONS) {
          typeHistory.versions = typeHistory.versions.slice(-MAX_VERSIONS);
          typeHistory.currentIndex = typeHistory.versions.length - 1;
        }

        typeHistory.pendingChanges = false;

        newHistory[type] = typeHistory;
        saveHistoryToStorage(type, typeHistory);
        return newHistory;
      });
    }
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
    canUndo,
    canRedo,
    undo,
    redo,
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
