/**
 * Generation Service
 * API service for news article generation
 */

import axios, { AxiosError } from 'axios';
import {
  GenerationRequest,
  GenerationResponse,
  GenerationResult,
  GenerationHistoryItem,
  GenerationHistoryFilters,
  PromptType,
  VariantStrategy
} from '@/types/generation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

/**
 * Generate a single news article
 */
export async function generateArticle(
  request: GenerationRequest
): Promise<GenerationResponse> {
  try {
    const response = await axios.post<GenerationResponse>(
      `${API_BASE_URL}/api/news/generate`,
      request
    );

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail: string }>;
    throw new Error(
      axiosError.response?.data?.detail ||
      axiosError.message ||
      'Failed to generate article'
    );
  }
}

/**
 * Generate multiple articles in parallel
 * Returns results as they complete (including failures)
 */
export async function generateBatch(
  requests: GenerationRequest[],
  onProgress?: (completed: number, total: number) => void
): Promise<GenerationResult[]> {
  const total = requests.length;
  let completed = 0;

  // Create promises for all generations
  const generationPromises = requests.map(async (request): Promise<GenerationResult> => {
    const result: GenerationResult = {
      prompt_type: request.prompt_type,
      model_id: request.model_id,
      response: {} as GenerationResponse,
      status: 'generating',
      requested_at: new Date().toISOString()
    };

    try {
      const response = await generateArticle(request);
      result.response = response;
      result.status = 'completed';
      result.completed_at = new Date().toISOString();
    } catch (error) {
      result.status = 'error';
      result.error = error instanceof Error ? error.message : 'Unknown error';
      result.completed_at = new Date().toISOString();
    } finally {
      completed++;
      if (onProgress) {
        onProgress(completed, total);
      }
    }

    return result;
  });

  // Wait for all generations to complete (or fail)
  const results = await Promise.allSettled(generationPromises);

  // Extract values from settled promises
  return results.map((result) => {
    if (result.status === 'fulfilled') {
      return result.value;
    } else {
      // This should rarely happen since we handle errors inside the promise
      return {
        prompt_type: 'paid' as PromptType,
        model_id: 'unknown',
        response: {} as GenerationResponse,
        status: 'error' as const,
        error: result.reason?.message || 'Promise rejected',
        requested_at: new Date().toISOString(),
        completed_at: new Date().toISOString()
      };
    }
  });
}

/**
 * Fetch generation history
 */
export async function fetchGenerationHistory(
  filters?: GenerationHistoryFilters
): Promise<{ items: GenerationHistoryItem[]; total: number }> {
  try {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response = await axios.get<{ items: GenerationHistoryItem[]; total: number }>(
      `${API_BASE_URL}/api/news/history?${params.toString()}`
    );

    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail: string }>;
    throw new Error(
      axiosError.response?.data?.detail ||
      axiosError.message ||
      'Failed to fetch generation history'
    );
  }
}

/**
 * Helper to build generation requests from current config
 */
export function buildGenerationRequests(params: {
  triggerId: string;
  stockId: string;
  modelIds: string[];
  promptTypes: PromptType[];
  promptTemplates: Record<PromptType, string>;
  structuredData: GenerationRequest['structured_data'];
  temperature: number;
  maxTokens: number;
  sessionId?: string;
  variantStrategy?: VariantStrategy;
}): GenerationRequest[] {
  const {
    triggerId,
    stockId,
    modelIds,
    promptTypes,
    promptTemplates,
    structuredData,
    temperature,
    maxTokens,
    sessionId,
    variantStrategy
  } = params;

  const requests: GenerationRequest[] = [];

  // Create a request for each model × prompt type combination
  for (const modelId of modelIds) {
    for (const promptType of promptTypes) {
      requests.push({
        trigger_name: triggerId,
        stock_id: stockId,
        prompt_type: promptType,
        prompt_template: promptTemplates[promptType], // Include in-memory prompt template
        model_id: modelId,
        structured_data: structuredData,
        temperature,
        max_tokens: maxTokens,
        session_id: sessionId || `test-${Date.now()}`
      });
    }
  }

  return requests;
}
