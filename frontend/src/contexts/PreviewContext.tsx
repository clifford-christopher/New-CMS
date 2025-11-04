'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { usePrompt } from './PromptContext';
import { useData } from './DataContext';
import { substitutePlaceholders, estimateTokenCount } from '@/lib/dataSubstitution';
import { PreviewContent, PreviewMetadata, PromptType } from '@/types/preview';

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

  // Generate preview content when modal opens or dependencies change
  useEffect(() => {
    if (!isModalOpen) return;

    setIsGenerating(true);
    setError(null);

    try {
      const updatedPreview: Record<PromptType, PreviewContent> = { ...previewContent };

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
        timestamp: new Date()
      });

      // Set initial preview tab to active tab
      setActivePreviewTab(activeTab);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate preview');
    } finally {
      setIsGenerating(false);
    }
  }, [isModalOpen, prompts, checkedTypes, activeTab, selectedSections, stockId, triggerId]);

  const openModal = useCallback(() => {
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
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
    error
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
