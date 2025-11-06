/**
 * Generation Context
 * Manages test generation state and results
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  GenerationResult,
  GenerationBatchStatus,
  PromptType,
  StructuredData
} from '@/types/generation';
import { generateBatch, buildGenerationRequests } from '@/services/generationService';

interface GenerationContextValue {
  // State
  results: GenerationResult[];
  isGenerating: boolean;
  status: GenerationBatchStatus | null;
  error: string | null;
  sessionId: string | null;

  // Actions
  triggerGeneration: (params: GenerationParams) => Promise<void>;
  clearResults: () => void;
  getResultsByType: (promptType: PromptType) => GenerationResult[];
  getResultByModelAndType: (modelId: string, promptType: PromptType) => GenerationResult | undefined;
}

export interface GenerationParams {
  triggerId: string;
  stockId: string;
  modelIds: string[];
  promptTypes: PromptType[];
  promptTemplates: Record<PromptType, string>; // In-memory prompt templates from Monaco editor
  structuredData: StructuredData;
  temperature: number;
  maxTokens: number;
}

const GenerationContext = createContext<GenerationContextValue | undefined>(undefined);

interface GenerationProviderProps {
  children: React.ReactNode;
}

export const GenerationProvider: React.FC<GenerationProviderProps> = ({ children }) => {
  const [results, setResults] = useState<GenerationResult[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<GenerationBatchStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  /**
   * Trigger batch generation
   */
  const triggerGeneration = useCallback(async (params: GenerationParams) => {
    const {
      triggerId,
      stockId,
      modelIds,
      promptTypes,
      promptTemplates,
      structuredData,
      temperature,
      maxTokens
    } = params;

    try {
      setIsGenerating(true);
      setError(null);
      setResults([]);

      // Generate unique session ID for this batch
      const newSessionId = `test-${Date.now()}`;
      setSessionId(newSessionId);

      // Build requests for all model × prompt type combinations
      const requests = buildGenerationRequests({
        triggerId,
        stockId,
        modelIds,
        promptTypes,
        promptTemplates,
        structuredData,
        temperature,
        maxTokens,
        sessionId: newSessionId
      });

      // Initialize status
      const totalGenerations = requests.length;
      setStatus({
        total: totalGenerations,
        completed: 0,
        pending: totalGenerations,
        generating: 0,
        errors: 0,
        total_cost: 0,
        total_latency: 0
      });

      // Execute batch generation with progress tracking
      const generationResults = await generateBatch(requests, (completed, total) => {
        setStatus((prev) => {
          if (!prev) return null;

          return {
            ...prev,
            completed,
            pending: total - completed,
            generating: total - completed > 0 ? 1 : 0
          };
        });
      });

      // Update results and final status
      setResults(generationResults);

      const completedResults = generationResults.filter(r => r.status === 'completed');
      const errorResults = generationResults.filter(r => r.status === 'error');

      const totalCost = completedResults.reduce((sum, r) => sum + (r.response.cost || 0), 0);
      const totalLatency = completedResults.reduce((sum, r) => sum + (r.response.latency || 0), 0);

      setStatus({
        total: totalGenerations,
        completed: completedResults.length,
        pending: 0,
        generating: 0,
        errors: errorResults.length,
        total_cost: totalCost,
        total_latency: totalLatency
      });

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate articles';
      setError(errorMessage);
      console.error('Generation failed:', err);
    } finally {
      setIsGenerating(false);
    }
  }, []);

  /**
   * Clear all results
   */
  const clearResults = useCallback(() => {
    setResults([]);
    setStatus(null);
    setError(null);
    setSessionId(null);
  }, []);

  /**
   * Get results filtered by prompt type
   */
  const getResultsByType = useCallback((promptType: PromptType): GenerationResult[] => {
    return results.filter(r => r.prompt_type === promptType);
  }, [results]);

  /**
   * Get specific result by model and prompt type
   */
  const getResultByModelAndType = useCallback((
    modelId: string,
    promptType: PromptType
  ): GenerationResult | undefined => {
    return results.find(
      r => r.model_id === modelId && r.prompt_type === promptType
    );
  }, [results]);

  const value: GenerationContextValue = {
    results,
    isGenerating,
    status,
    error,
    sessionId,
    triggerGeneration,
    clearResults,
    getResultsByType,
    getResultByModelAndType
  };

  return (
    <GenerationContext.Provider value={value}>
      {children}
    </GenerationContext.Provider>
  );
};

/**
 * Hook to use Generation Context
 */
export const useGeneration = (): GenerationContextValue => {
  const context = useContext(GenerationContext);
  if (!context) {
    throw new Error('useGeneration must be used within a GenerationProvider');
  }
  return context;
};
