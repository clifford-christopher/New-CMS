/**
 * Generation Types
 * Type definitions for news article generation and testing
 */

export type PromptType = 'paid' | 'unpaid' | 'crawler';
export type DataMode = 'OLD' | 'NEW' | 'OLD_NEW';

/**
 * Structured data format for generation API
 * Contains stock data and sections for prompt substitution
 */
export interface StructuredData {
  stock_id: string;
  data_mode: DataMode;
  sections: Record<string, any>;
  data?: Record<string, any>;
}

/**
 * Request payload for POST /api/news/generate
 */
export interface GenerationRequest {
  trigger_name: string;
  stock_id: string;
  prompt_type: PromptType;
  model_id: string;
  structured_data: StructuredData;
  temperature?: number;
  max_tokens?: number;
  session_id?: string;
  prompt_template?: string; // Optional in-memory prompt template (bypasses DB lookup)
}

/**
 * Response from POST /api/news/generate
 * Matches backend GenerationResponse model
 */
export interface GenerationResponse {
  generated_text: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
  latency: number;
  model_name: string;
  provider: string;
  timestamp: string;
  temperature: number;
  max_tokens: number;
  finish_reason: string;
}

/**
 * Extended result with request context
 * Used in frontend for display and tracking
 */
export interface GenerationResult {
  // Request context
  prompt_type: PromptType;
  model_id: string;

  // Response data
  response: GenerationResponse;

  // Status tracking
  status: 'pending' | 'generating' | 'completed' | 'error';
  error?: string;

  // Metadata
  requested_at: string;
  completed_at?: string;
}

/**
 * Batch generation status
 */
export interface GenerationBatchStatus {
  total: number;
  completed: number;
  pending: number;
  generating: number;
  errors: number;
  total_cost: number;
  total_latency: number;
}

/**
 * Generation history item from GET /api/news/history
 */
export interface GenerationHistoryItem {
  id: string;
  trigger_name: string;
  stock_id: string;
  prompt_type: PromptType;
  model_name: string;
  provider: string;
  generated_text: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
  latency: number;
  temperature: number;
  max_tokens: number;
  finish_reason: string;
  timestamp: string;
  session_id?: string;
}

/**
 * Filters for generation history
 */
export interface GenerationHistoryFilters {
  trigger_name?: string;
  stock_id?: string;
  prompt_type?: PromptType;
  provider?: string;
  session_id?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  skip?: number;
}
