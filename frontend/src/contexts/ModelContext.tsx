/**
 * Model Context for LLM Model Selection
 * Story 4.2: Model Selection Interface
 *
 * Manages:
 * - Available LLM models
 * - Selected models for the current trigger
 * - Temperature and max_tokens configuration
 * - Cost estimation based on selected models and checked prompt types
 * - Loading and persisting model configuration
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  LLMModel,
  ModelConfig,
  ModelConfigResponse,
  TotalCostEstimate,
  ModelCostEstimate
} from '@/types/model';
import { usePrompt } from './PromptContext';

interface ModelContextValue {
  // Available models from API
  availableModels: LLMModel[];
  modelsLoading: boolean;
  modelsError: string | null;

  // Current configuration (multiple models for testing)
  selectedModels: string[];
  temperature: number;
  maxTokens: number;

  // Configuration state
  isConfigured: boolean;
  isSaving: boolean;
  saveError: string | null;

  // Cost estimation
  costEstimate: TotalCostEstimate | null;

  // Actions
  setSelectedModels: (modelIds: string[]) => void;
  setTemperature: (temp: number) => void;
  setMaxTokens: (tokens: number) => void;
  toggleModel: (modelId: string) => void;
  saveModelConfig: () => Promise<void>;
  loadModelConfig: () => Promise<void>;

  // Helpers
  getModelById: (modelId: string) => LLMModel | undefined;
  isModelSelected: (modelId: string) => boolean;
}

const ModelContext = createContext<ModelContextValue | undefined>(undefined);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

/**
 * Default cost estimation parameters
 * Based on typical news article length
 */
const DEFAULT_INPUT_TOKENS = 800;   // ~600 words prompt
const DEFAULT_OUTPUT_TOKENS = 500;  // ~375 words article

interface ModelProviderProps {
  children: React.ReactNode;
  triggerId: string;
}

export const ModelProvider: React.FC<ModelProviderProps> = ({ children, triggerId }) => {
  const { checkedTypes } = usePrompt();

  // Available models
  const [availableModels, setAvailableModels] = useState<LLMModel[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState<string | null>(null);

  // Current configuration (multiple models for testing)
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(500);
  const [isConfigured, setIsConfigured] = useState(false);

  // Saving state
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Cost estimate
  const [costEstimate, setCostEstimate] = useState<TotalCostEstimate | null>(null);

  /**
   * Load available models from API
   */
  const loadAvailableModels = useCallback(async () => {
    try {
      setModelsLoading(true);
      setModelsError(null);

      const response = await axios.get<{ models: LLMModel[]; total: number }>(
        `${API_BASE_URL}/api/news/models`
      );

      setAvailableModels(response.data.models);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load models';
      setModelsError(errorMsg);
      console.error('Failed to load available models:', error);
    } finally {
      setModelsLoading(false);
    }
  }, []);

  /**
   * Load model configuration for current trigger
   */
  const loadModelConfig = useCallback(async () => {
    if (!triggerId) return;

    try {
      const response = await axios.get<ModelConfigResponse>(
        `${API_BASE_URL}/api/triggers/${triggerId}/config/models`
      );

      const config = response.data.llm_config;
      // Handle both formats: selected_models array (preferred) or model string (legacy)
      if (config.selected_models && Array.isArray(config.selected_models)) {
        setSelectedModels(config.selected_models);
      } else if (config.model) {
        // Legacy single model format - convert to array
        setSelectedModels([config.model]);
      }
      setTemperature(config.temperature);
      setMaxTokens(config.max_tokens);
      setIsConfigured(response.data.is_configured);

    } catch (error: any) {
      console.error('Failed to load model config:', error);
      // Don't show error for 404 (trigger not found) - it's expected for new triggers
      if (error.response?.status !== 404) {
        setModelsError(error.response?.data?.detail || 'Failed to load configuration');
      }
    }
  }, [triggerId]);

  /**
   * Save model configuration to backend
   */
  const saveModelConfig = useCallback(async () => {
    if (!triggerId) {
      setSaveError('No trigger selected');
      return;
    }

    if (selectedModels.length === 0) {
      setSaveError('At least one model must be selected');
      return;
    }

    try {
      setIsSaving(true);
      setSaveError(null);

      await axios.post(
        `${API_BASE_URL}/api/triggers/${triggerId}/config/models`,
        {
          selected_models: selectedModels, // Send array for testing
          temperature,
          max_tokens: maxTokens
        }
      );

      setIsConfigured(true);

    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to save configuration';
      setSaveError(errorMsg);
      console.error('Failed to save model config:', error);
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [triggerId, selectedModels, temperature, maxTokens]);

  /**
   * Toggle model selection (for multi-select during testing)
   */
  const toggleModel = useCallback((modelId: string) => {
    setSelectedModels(prev => {
      if (prev.includes(modelId)) {
        return prev.filter(id => id !== modelId);
      } else {
        return [...prev, modelId];
      }
    });
  }, []);

  /**
   * Get model by ID
   */
  const getModelById = useCallback((modelId: string): LLMModel | undefined => {
    return availableModels.find(m => m.model_id === modelId);
  }, [availableModels]);

  /**
   * Check if model is selected
   */
  const isModelSelected = useCallback((modelId: string): boolean => {
    return selectedModels.includes(modelId);
  }, [selectedModels]);

  /**
   * Calculate cost estimation
   * Formula: (selected models) × (checked prompt types) × (cost per generation)
   */
  const calculateCostEstimate = useCallback(() => {
    if (selectedModels.length === 0) {
      setCostEstimate(null);
      return;
    }

    const checkedPromptTypes = checkedTypes.size;
    if (checkedPromptTypes === 0) {
      setCostEstimate(null);
      return;
    }

    const modelEstimates: ModelCostEstimate[] = [];
    let totalCost = 0;

    for (const modelId of selectedModels) {
      const model = getModelById(modelId);
      if (!model) continue;

      // Calculate cost per generation
      // Cost = (input_tokens / 1M) × input_price + (output_tokens / 1M) × output_price
      const inputTokens = DEFAULT_INPUT_TOKENS;
      const outputTokens = Math.min(maxTokens, DEFAULT_OUTPUT_TOKENS);

      const inputCost = (inputTokens / 1_000_000) * model.pricing.input;
      const outputCost = (outputTokens / 1_000_000) * model.pricing.output;
      const costPerGeneration = inputCost + outputCost;

      modelEstimates.push({
        model_id: modelId,
        display_name: model.display_name,
        provider: model.provider,
        cost_per_generation: costPerGeneration,
        input_tokens_estimated: inputTokens,
        output_tokens_estimated: outputTokens
      });

      totalCost += costPerGeneration * checkedPromptTypes;
    }

    setCostEstimate({
      total_models: selectedModels.length,
      total_prompt_types: checkedPromptTypes,
      total_generations: selectedModels.length * checkedPromptTypes,
      cost_per_prompt_type: totalCost / checkedPromptTypes,
      total_estimated_cost: totalCost,
      models: modelEstimates
    });
  }, [selectedModels, checkedTypes, maxTokens, getModelById]);

  /**
   * Load available models on mount
   */
  useEffect(() => {
    loadAvailableModels();
  }, [loadAvailableModels]);

  /**
   * Load model configuration when trigger changes
   */
  useEffect(() => {
    if (triggerId) {
      loadModelConfig();
    }
  }, [triggerId, loadModelConfig]);

  /**
   * Recalculate cost estimate when dependencies change
   */
  useEffect(() => {
    calculateCostEstimate();
  }, [calculateCostEstimate]);

  const value: ModelContextValue = {
    availableModels,
    modelsLoading,
    modelsError,
    selectedModels,
    temperature,
    maxTokens,
    isConfigured,
    isSaving,
    saveError,
    costEstimate,
    setSelectedModels,
    setTemperature,
    setMaxTokens,
    toggleModel,
    saveModelConfig,
    loadModelConfig,
    getModelById,
    isModelSelected
  };

  return <ModelContext.Provider value={value}>{children}</ModelContext.Provider>;
};

/**
 * Hook to use Model Context
 */
export const useModel = (): ModelContextValue => {
  const context = useContext(ModelContext);
  if (!context) {
    throw new Error('useModel must be used within a ModelProvider');
  }
  return context;
};
