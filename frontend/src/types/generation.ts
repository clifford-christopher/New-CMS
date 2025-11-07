/**
 * Generation Types
 * Type definitions for news article generation and testing
 */

export type PromptType = 'paid' | 'unpaid' | 'crawler';
export type DataMode = 'OLD' | 'NEW' | 'OLD_NEW';

/**
 * Variant Strategy - Controls how prompts are used across news types
 * - all_same: Use one prompt for all types (1 API call)
 * - all_unique: Generate unique content for each type (3 API calls)
 * - paid_unique: Unique paid content, shared unpaid/crawler (2 API calls)
 * - unpaid_unique: Unique unpaid content, shared paid/crawler (2 API calls)
 * - crawler_unique: Unique crawler content, shared paid/unpaid (2 API calls)
 */
export type VariantStrategy = 'all_same' | 'all_unique' | 'paid_unique' | 'unpaid_unique' | 'crawler_unique';

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

/**
 * Version tracking for iterative refinement (Story 4.5)
 */
export interface GenerationVersion {
  version: number;
  result: GenerationResult;
  timestamp: string;
  prompt_used: string;
  is_selected: boolean;
}

/**
 * Extended GenerationResult with version metadata
 */
export interface VersionedGenerationResult extends GenerationResult {
  version?: number;
  total_versions?: number;
  is_selected_version?: boolean;
}

/**
 * Variant strategy validation result
 */
export interface StrategyValidationResult {
  isValid: boolean;
  missingPrompts: PromptType[];
  errorMessage?: string;
}

/**
 * Get required prompts for a variant strategy
 */
export function getStrategyRequirements(strategy: VariantStrategy): {
  required: PromptType[];
  description: string;
  apiCalls: number;
} {
  switch (strategy) {
    case 'all_same':
      return {
        required: ['paid'],
        description: 'Use one prompt for all types (most cost-effective)',
        apiCalls: 1
      };
    case 'all_unique':
      return {
        required: ['paid', 'unpaid', 'crawler'],
        description: 'Generate unique content for each type',
        apiCalls: 3
      };
    case 'paid_unique':
      return {
        required: ['paid'],
        description: 'Unique paid content, shared unpaid/crawler',
        apiCalls: 2
      };
    case 'unpaid_unique':
      return {
        required: ['unpaid'],
        description: 'Unique unpaid content, shared paid/crawler',
        apiCalls: 2
      };
    case 'crawler_unique':
      return {
        required: ['crawler'],
        description: 'Unique crawler content, shared paid/unpaid',
        apiCalls: 2
      };
  }
}

/**
 * Validate prompts against variant strategy requirements
 */
export function validateStrategy(
  strategy: VariantStrategy,
  prompts: Record<PromptType, { content: string; enabled: boolean }>
): StrategyValidationResult {
  const requirements = getStrategyRequirements(strategy);
  const missingPrompts: PromptType[] = [];

  // Check required prompts
  for (const promptType of requirements.required) {
    if (!prompts[promptType].content.trim()) {
      missingPrompts.push(promptType);
    }
  }

  // Special handling for strategies that need at least one additional prompt
  if (strategy === 'paid_unique') {
    const hasUnpaid = prompts.unpaid.content.trim().length > 0;
    const hasCrawler = prompts.crawler.content.trim().length > 0;
    if (!hasUnpaid && !hasCrawler) {
      if (!missingPrompts.includes('unpaid')) missingPrompts.push('unpaid');
      if (!missingPrompts.includes('crawler')) missingPrompts.push('crawler');
    }
  } else if (strategy === 'unpaid_unique') {
    const hasPaid = prompts.paid.content.trim().length > 0;
    const hasCrawler = prompts.crawler.content.trim().length > 0;
    if (!hasPaid && !hasCrawler) {
      if (!missingPrompts.includes('paid')) missingPrompts.push('paid');
      if (!missingPrompts.includes('crawler')) missingPrompts.push('crawler');
    }
  } else if (strategy === 'crawler_unique') {
    const hasPaid = prompts.paid.content.trim().length > 0;
    const hasUnpaid = prompts.unpaid.content.trim().length > 0;
    if (!hasPaid && !hasUnpaid) {
      if (!missingPrompts.includes('paid')) missingPrompts.push('paid');
      if (!missingPrompts.includes('unpaid')) missingPrompts.push('unpaid');
    }
  }

  const isValid = missingPrompts.length === 0;
  let errorMessage: string | undefined;

  if (!isValid) {
    if (strategy === 'all_unique') {
      errorMessage = `All prompts (${missingPrompts.join(', ')}) must be filled for "All Unique" strategy.`;
    } else if (strategy === 'paid_unique' || strategy === 'unpaid_unique' || strategy === 'crawler_unique') {
      const primary = requirements.required[0];
      errorMessage = `"${strategy.replace('_', ' ')}" strategy requires "${primary}" prompt and at least one other prompt to be filled.`;
    } else {
      errorMessage = `Please fill in the ${missingPrompts.join(', ')} prompt(s) for this strategy.`;
    }
  }

  return {
    isValid,
    missingPrompts,
    errorMessage
  };
}

/**
 * Get which prompt tabs should be visible based on variant strategy
 */
export function getVisibleTabs(strategy: VariantStrategy): PromptType[] {
  switch (strategy) {
    case 'all_same':
      return ['paid']; // Only paid tab visible
    case 'all_unique':
    case 'paid_unique':
    case 'unpaid_unique':
    case 'crawler_unique':
      return ['paid', 'unpaid', 'crawler']; // All tabs visible
  }
}

/**
 * Map prompts to news types based on variant strategy
 * Returns which prompt content to use for each news type
 */
export function getPromptMapping(
  strategy: VariantStrategy,
  prompts: Record<PromptType, string>
): Record<PromptType, string> {
  const mapping: Record<PromptType, string> = {
    paid: '',
    unpaid: '',
    crawler: ''
  };

  switch (strategy) {
    case 'all_same':
      // Use paid prompt for all types
      mapping.paid = prompts.paid;
      mapping.unpaid = prompts.paid;
      mapping.crawler = prompts.paid;
      break;

    case 'all_unique':
      // Each type uses its own prompt
      mapping.paid = prompts.paid;
      mapping.unpaid = prompts.unpaid;
      mapping.crawler = prompts.crawler;
      break;

    case 'paid_unique':
      // Paid is unique, unpaid/crawler share
      mapping.paid = prompts.paid;
      const sharedForPaidUnique = prompts.unpaid || prompts.crawler;
      mapping.unpaid = sharedForPaidUnique;
      mapping.crawler = sharedForPaidUnique;
      break;

    case 'unpaid_unique':
      // Unpaid is unique, paid/crawler share
      mapping.unpaid = prompts.unpaid;
      const sharedForUnpaidUnique = prompts.paid || prompts.crawler;
      mapping.paid = sharedForUnpaidUnique;
      mapping.crawler = sharedForUnpaidUnique;
      break;

    case 'crawler_unique':
      // Crawler is unique, paid/unpaid share
      mapping.crawler = prompts.crawler;
      const sharedForCrawlerUnique = prompts.paid || prompts.unpaid;
      mapping.paid = sharedForCrawlerUnique;
      mapping.unpaid = sharedForCrawlerUnique;
      break;
  }

  return mapping;
}

/**
 * Get unique prompts that need to be generated (to avoid duplicate API calls)
 * Returns array of [promptType, promptContent] pairs
 */
export function getUniquePromptsForGeneration(
  strategy: VariantStrategy,
  prompts: Record<PromptType, string>
): Array<{ promptType: PromptType; promptContent: string }> {
  const mapping = getPromptMapping(strategy, prompts);
  const uniquePrompts = new Map<string, PromptType>();

  // Find unique prompt contents
  (['paid', 'unpaid', 'crawler'] as PromptType[]).forEach(type => {
    const content = mapping[type];
    if (content && !uniquePrompts.has(content)) {
      uniquePrompts.set(content, type);
    }
  });

  // Return array of unique prompts
  return Array.from(uniquePrompts.entries()).map(([promptContent, promptType]) => ({
    promptType,
    promptContent
  }));
}
