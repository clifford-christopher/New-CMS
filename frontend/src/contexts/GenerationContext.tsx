/**
 * Generation Context
 * Manages test generation state and results
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  GenerationResult,
  GenerationBatchStatus,
  GenerationHistoryItem,
  GenerationHistoryFilters,
  GenerationVersion,
  PromptType,
  StructuredData
} from '@/types/generation';
import { generateBatch, buildGenerationRequests, fetchGenerationHistory as fetchHistoryAPI } from '@/services/generationService';

interface GenerationContextValue {
  // State
  results: GenerationResult[];
  isGenerating: boolean;
  status: GenerationBatchStatus | null;
  error: string | null;
  sessionId: string | null;

  // History state
  history: GenerationHistoryItem[];
  historyLoading: boolean;
  historyError: string | null;

  // Version tracking state (Story 4.5)
  resultVersions: Map<string, GenerationVersion[]>;
  selectedVersions: Map<string, number>;

  // Actions
  triggerGeneration: (params: GenerationParams) => Promise<void>;
  clearResults: () => void;
  getResultsByType: (promptType: PromptType) => GenerationResult[];
  getResultByModelAndType: (modelId: string, promptType: PromptType) => GenerationResult | undefined;

  // History actions
  fetchHistory: (filters?: GenerationHistoryFilters) => Promise<void>;

  // Version tracking actions (Story 4.5)
  regenerateResult: (modelId: string, promptType: PromptType, customPrompt?: string) => Promise<void>;
  getVersions: (modelId: string, promptType: PromptType) => GenerationVersion[];
  selectVersion: (modelId: string, promptType: PromptType, versionIndex: number) => void;
  getSelectedVersion: (modelId: string, promptType: PromptType) => GenerationVersion | undefined;
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

  // History state
  const [history, setHistory] = useState<GenerationHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // Version tracking state (Story 4.5)
  const [resultVersions, setResultVersions] = useState<Map<string, GenerationVersion[]>>(new Map());
  const [selectedVersions, setSelectedVersions] = useState<Map<string, number>>(new Map());

  // Store last generation params for regeneration
  const [lastGenerationParams, setLastGenerationParams] = useState<GenerationParams | null>(null);

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

      // Store params for regeneration
      setLastGenerationParams(params);

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

      // Initialize version tracking for each result (v1)
      const newVersions = new Map<string, GenerationVersion[]>();
      const newSelectedVersions = new Map<string, number>();

      generationResults.forEach((result) => {
        const key = `${result.model_id}-${result.prompt_type}`;
        const promptUsed = promptTemplates[result.prompt_type];

        const version: GenerationVersion = {
          version: 1,
          result,
          timestamp: new Date().toISOString(),
          prompt_used: promptUsed,
          is_selected: true
        };

        newVersions.set(key, [version]);
        newSelectedVersions.set(key, 0); // Index 0 = version 1
      });

      setResultVersions(newVersions);
      setSelectedVersions(newSelectedVersions);

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
    setResultVersions(new Map());
    setSelectedVersions(new Map());
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

  /**
   * Regenerate a specific result (Story 4.5)
   */
  const regenerateResult = useCallback(async (
    modelId: string,
    promptType: PromptType,
    customPrompt?: string
  ) => {
    if (!lastGenerationParams) {
      console.error('No generation params available for regeneration');
      return;
    }

    const key = `${modelId}-${promptType}`;

    try {
      setIsGenerating(true);
      setError(null);

      // Use custom prompt if provided, otherwise use original
      const promptToUse = customPrompt || lastGenerationParams.promptTemplates[promptType];

      // Build single generation request
      const request = buildGenerationRequests({
        ...lastGenerationParams,
        modelIds: [modelId],
        promptTypes: [promptType],
        promptTemplates: {
          ...lastGenerationParams.promptTemplates,
          [promptType]: promptToUse
        },
        sessionId: sessionId || `test-${Date.now()}`
      })[0];

      // Generate
      const [result] = await generateBatch([request]);

      // Get existing versions
      const existingVersions = resultVersions.get(key) || [];
      const nextVersion = existingVersions.length + 1;

      // Create new version
      const newVersion: GenerationVersion = {
        version: nextVersion,
        result,
        timestamp: new Date().toISOString(),
        prompt_used: promptToUse,
        is_selected: false // User needs to explicitly select it
      };

      // Update versions
      const updatedVersions = [...existingVersions, newVersion];
      setResultVersions(prev => new Map(prev).set(key, updatedVersions));

      // Update results to show latest version
      setResults(prev => prev.map(r =>
        r.model_id === modelId && r.prompt_type === promptType ? result : r
      ));

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Regeneration failed';
      setError(errorMessage);
      console.error('Regeneration error:', err);
    } finally {
      setIsGenerating(false);
    }
  }, [lastGenerationParams, resultVersions, sessionId]);

  /**
   * Get all versions for a model/type combination
   */
  const getVersions = useCallback((
    modelId: string,
    promptType: PromptType
  ): GenerationVersion[] => {
    const key = `${modelId}-${promptType}`;
    return resultVersions.get(key) || [];
  }, [resultVersions]);

  /**
   * Select a specific version
   */
  const selectVersion = useCallback((
    modelId: string,
    promptType: PromptType,
    versionIndex: number
  ) => {
    const key = `${modelId}-${promptType}`;
    const versions = resultVersions.get(key);

    if (!versions || versionIndex < 0 || versionIndex >= versions.length) {
      console.error('Invalid version index');
      return;
    }

    // Update selected versions map
    setSelectedVersions(prev => new Map(prev).set(key, versionIndex));

    // Update is_selected flags
    const updatedVersions = versions.map((v, idx) => ({
      ...v,
      is_selected: idx === versionIndex
    }));
    setResultVersions(prev => new Map(prev).set(key, updatedVersions));

    // Update results to show selected version
    const selectedVersion = versions[versionIndex];
    setResults(prev => prev.map(r =>
      r.model_id === modelId && r.prompt_type === promptType ? selectedVersion.result : r
    ));
  }, [resultVersions]);

  /**
   * Get the currently selected version
   */
  const getSelectedVersion = useCallback((
    modelId: string,
    promptType: PromptType
  ): GenerationVersion | undefined => {
    const key = `${modelId}-${promptType}`;
    const versions = resultVersions.get(key);
    const selectedIndex = selectedVersions.get(key);

    if (!versions || selectedIndex === undefined) {
      return undefined;
    }

    return versions[selectedIndex];
  }, [resultVersions, selectedVersions]);

  /**
   * Fetch generation history
   */
  const fetchHistory = useCallback(async (filters?: GenerationHistoryFilters) => {
    try {
      setHistoryLoading(true);
      setHistoryError(null);

      const response = await fetchHistoryAPI(filters);
      setHistory(response.items);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load history';
      setHistoryError(errorMessage);
      console.error('Failed to fetch generation history:', err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const value: GenerationContextValue = {
    results,
    isGenerating,
    status,
    error,
    sessionId,
    history,
    historyLoading,
    historyError,
    resultVersions,
    selectedVersions,
    triggerGeneration,
    clearResults,
    getResultsByType,
    getResultByModelAndType,
    fetchHistory,
    regenerateResult,
    getVersions,
    selectVersion,
    getSelectedVersion
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
