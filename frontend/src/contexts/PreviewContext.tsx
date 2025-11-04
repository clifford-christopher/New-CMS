'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { usePrompt } from './PromptContext';
import { useData } from './DataContext';
import { substitutePlaceholders, estimateTokenCount } from '@/lib/dataSubstitution';
import { PreviewContent, PreviewMetadata, PromptType, VersionHistoryItem, VersionResponse, VersionData } from '@/types/preview';

interface PreviewContextType {
  isModalOpen: boolean;
  openModal: () => void;
  closeModal: () => void;
  previewContent: Record<PromptType, PreviewContent>;
  previewMetadata: PreviewMetadata | null;
  activePreviewTab: PromptType;
  setActivePreviewTab: (type: PromptType) => void;
  isGenerating: boolean;
  error: string | null;
  selectedVersion: number | 'current';
  versionHistory: VersionHistoryItem[];
  isLoadingVersions: boolean;
  loadVersionHistory: (triggerId: string) => Promise<void>;
  loadVersionPreview: (triggerId: string, version: number) => Promise<void>;
  setSelectedVersion: (version: number | 'current') => void;
}

const PreviewContext = createContext<PreviewContextType | undefined>(undefined);

export function PreviewProvider({ children }: { children: ReactNode }) {
  const { prompts, activeTab, checkedTypes } = usePrompt();
  const { selectedSections, stockId, triggerId } = useData();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activePreviewTab, setActivePreviewTab] = useState<PromptType>('paid');
  const [previewContent, setPreviewContent] = useState<Record<PromptType, PreviewContent>>({
    paid: {
      prompt: '',
      substitutedPrompt: '',
      validPlaceholders: [],
      missingPlaceholders: [],
      estimatedTokens: 0,
      characterCount: 0
    },
    unpaid: {
      prompt: '',
      substitutedPrompt: '',
      validPlaceholders: [],
      missingPlaceholders: [],
      estimatedTokens: 0,
      characterCount: 0
    },
    crawler: {
      prompt: '',
      substitutedPrompt: '',
      validPlaceholders: [],
      missingPlaceholders: [],
      estimatedTokens: 0,
      characterCount: 0
    }
  });
  const [previewMetadata, setPreviewMetadata] = useState<PreviewMetadata | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number | 'current'>('current');
  const [versionHistory, setVersionHistory] = useState<VersionHistoryItem[]>([]);
  const [isLoadingVersions, setIsLoadingVersions] = useState(false);

  // Load version history from backend
  const loadVersionHistory = useCallback(async (trigId: string) => {
    setIsLoadingVersions(true);
    setError(null);
    try {
      const response = await fetch(`/api/triggers/${trigId}/config/prompts/versions`);
      if (!response.ok) {
        throw new Error(`Failed to load version history: ${response.statusText}`);
      }
      const data: VersionResponse = await response.json();
      setVersionHistory(data.versions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load version history');
      console.error('Error loading version history:', err);
    } finally {
      setIsLoadingVersions(false);
    }
  }, []);

  // Load specific version for preview
  const loadVersionPreview = useCallback(async (trigId: string, version: number) => {
    setIsGenerating(true);
    setError(null);
    try {
      const response = await fetch(`/api/triggers/${trigId}/config/prompts/version/${version}`);
      if (!response.ok) {
        throw new Error(`Failed to load version ${version}: ${response.statusText}`);
      }
      const versionData: VersionData = await response.json();

      // Create fresh preview object without relying on existing state
      const updatedPreview: Record<PromptType, PreviewContent> = {
        paid: {
          prompt: '',
          substitutedPrompt: '',
          validPlaceholders: [],
          missingPlaceholders: [],
          estimatedTokens: 0,
          characterCount: 0
        },
        unpaid: {
          prompt: '',
          substitutedPrompt: '',
          validPlaceholders: [],
          missingPlaceholders: [],
          estimatedTokens: 0,
          characterCount: 0
        },
        crawler: {
          prompt: '',
          substitutedPrompt: '',
          validPlaceholders: [],
          missingPlaceholders: [],
          estimatedTokens: 0,
          characterCount: 0
        }
      };

      // Generate preview for each prompt type in the version
      (['paid', 'unpaid', 'crawler'] as PromptType[]).forEach(type => {
        if (versionData.prompts[type]) {
          const promptText = versionData.prompts[type].template;
          const result = substitutePlaceholders(promptText, selectedSections);

          const characterCount = result.substitutedPrompt.length;
          const estimatedTokens = estimateTokenCount(result.substitutedPrompt);

          updatedPreview[type] = {
            prompt: promptText,
            substitutedPrompt: result.substitutedPrompt,
            validPlaceholders: result.validPlaceholders,
            missingPlaceholders: result.missingPlaceholders,
            estimatedTokens,
            characterCount
          };
        }
      });

      setPreviewContent(updatedPreview);
      setPreviewMetadata({
        stockId: stockId || null,
        triggerName: trigId,
        promptType: activeTab,
        timestamp: new Date(),
        version: versionData.version,
        savedBy: versionData.saved_by,
        savedAt: versionData.saved_at
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load version preview');
      console.error('Error loading version preview:', err);
    } finally {
      setIsGenerating(false);
    }
  }, [selectedSections, stockId, activeTab]);

  // Generate preview content when modal opens or dependencies change
  useEffect(() => {
    if (!isModalOpen) return;

    // Only generate current draft preview when selectedVersion is 'current'
    if (selectedVersion !== 'current') return;

    setIsGenerating(true);
    setError(null);

    try {
      // Create fresh preview object
      const updatedPreview: Record<PromptType, PreviewContent> = {
        paid: {
          prompt: '',
          substitutedPrompt: '',
          validPlaceholders: [],
          missingPlaceholders: [],
          estimatedTokens: 0,
          characterCount: 0
        },
        unpaid: {
          prompt: '',
          substitutedPrompt: '',
          validPlaceholders: [],
          missingPlaceholders: [],
          estimatedTokens: 0,
          characterCount: 0
        },
        crawler: {
          prompt: '',
          substitutedPrompt: '',
          validPlaceholders: [],
          missingPlaceholders: [],
          estimatedTokens: 0,
          characterCount: 0
        }
      };

      // Generate preview for all checked types
      (['paid', 'unpaid', 'crawler'] as PromptType[]).forEach(type => {
        if (!checkedTypes.has(type)) return;

        const promptText = prompts[type].content;
        const result = substitutePlaceholders(promptText, selectedSections);

        const characterCount = result.substitutedPrompt.length;
        const estimatedTokens = estimateTokenCount(result.substitutedPrompt);

        updatedPreview[type] = {
          prompt: promptText,
          substitutedPrompt: result.substitutedPrompt,
          validPlaceholders: result.validPlaceholders,
          missingPlaceholders: result.missingPlaceholders,
          estimatedTokens,
          characterCount
        };
      });

      setPreviewContent(updatedPreview);
      setPreviewMetadata({
        stockId: stockId || null,
        triggerName: triggerId,
        promptType: activeTab,
        timestamp: new Date(),
        version: 'current'
      });

      // Set initial preview tab to active tab
      setActivePreviewTab(activeTab);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate preview');
    } finally {
      setIsGenerating(false);
    }
  }, [isModalOpen, prompts, checkedTypes, activeTab, selectedSections, stockId, triggerId, selectedVersion]);

  // Load version history when modal opens
  useEffect(() => {
    if (isModalOpen && triggerId) {
      loadVersionHistory(triggerId);
    }
  }, [isModalOpen, triggerId, loadVersionHistory]);

  // Load specific version preview when selectedVersion changes
  useEffect(() => {
    if (isModalOpen && typeof selectedVersion === 'number' && triggerId) {
      loadVersionPreview(triggerId, selectedVersion);
    }
  }, [isModalOpen, selectedVersion, triggerId, loadVersionPreview]);

  const openModal = useCallback(() => {
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    // Reset to current version when closing to avoid flickering on next open
    setSelectedVersion('current');
  }, []);

  const value: PreviewContextType = {
    isModalOpen,
    openModal,
    closeModal,
    previewContent,
    previewMetadata,
    activePreviewTab,
    setActivePreviewTab,
    isGenerating,
    error,
    selectedVersion,
    versionHistory,
    isLoadingVersions,
    loadVersionHistory,
    loadVersionPreview,
    setSelectedVersion
  };

  return <PreviewContext.Provider value={value}>{children}</PreviewContext.Provider>;
}

export function usePreview() {
  const context = useContext(PreviewContext);
  if (context === undefined) {
    throw new Error('usePreview must be used within a PreviewProvider');
  }
  return context;
}
