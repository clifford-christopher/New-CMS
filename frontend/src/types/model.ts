/**
 * TypeScript type definitions for LLM models and configurations
 * Story 4.2: Model Selection Interface
 */

/**
 * LLM Model information
 */
export interface LLMModel {
  model_id: string;
  display_name: string;
  provider: 'openai' | 'anthropic' | 'gemini';
  description: string;
  pricing: {
    input: number;    // Cost per 1M tokens
    output: number;   // Cost per 1M tokens
    [key: string]: number; // Additional pricing fields (cache_writes, cache_hits, etc.)
  };
}

/**
 * Model configuration for a trigger
 */
export interface ModelConfig {
  selected_models: string[];  // Array of model IDs
  temperature: number;        // 0.0 - 1.0
  max_tokens: number;         // 50 - 4000
  updated_at: string | null;
}

/**
 * Model configuration response from API
 */
export interface ModelConfigResponse {
  trigger_name: string;
  model_config: ModelConfig;
  is_configured: boolean;
  models_count?: number;
  message?: string;
}

/**
 * Cost estimation for a single model
 */
export interface ModelCostEstimate {
  model_id: string;
  display_name: string;
  provider: string;
  cost_per_generation: number;  // Estimated cost in USD
  input_tokens_estimated: number;
  output_tokens_estimated: number;
}

/**
 * Total cost estimation for all selected models
 */
export interface TotalCostEstimate {
  total_models: number;
  total_prompt_types: number;
  total_generations: number;  // models × prompt_types
  cost_per_prompt_type: number;
  total_estimated_cost: number;
  models: ModelCostEstimate[];
}
