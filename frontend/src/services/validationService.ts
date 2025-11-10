/**
 * Validation Service
 * Story 5.1: Pre-Publish Validation
 *
 * Service for validating trigger configurations before publishing
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface ValidationRequest {
  apis: string[];
  section_order: string[];
  prompts: Record<string, string>;
  model_settings: {
    selected_models: string[];
    temperature: number;
    max_tokens: number;
  };
  enabled_prompt_types: string[];
  session_id?: string;
}

export interface ValidationIssue {
  severity: 'error' | 'warning';
  category: string;
  message: string;
  prompt_type?: string;
}

export interface TestMetadata {
  models_tested: string[];
  total_tests: number;
  avg_cost: number;
  avg_latency: number;
  total_cost: number;
  sample_output?: string;
}

export interface PromptTypeValidation {
  prompt_type: string;
  is_valid: boolean;
  issues: ValidationIssue[];
  test_metadata?: TestMetadata;
}

export interface ValidationResult {
  is_valid: boolean;
  prompt_types: Record<string, PromptTypeValidation>;
  shared_config_issues: ValidationIssue[];
  summary: {
    total_errors: number;
    total_warnings: number;
    prompt_types_validated: number;
  };
}

export interface ValidationResponse {
  success: boolean;
  is_valid: boolean;
  prompt_types: Record<string, PromptTypeValidation>;
  shared_config_issues: ValidationIssue[];
  summary: {
    total_errors: number;
    total_warnings: number;
    prompt_types_validated: number;
  };
}

/**
 * Validate trigger configuration before publishing
 */
export async function validateConfiguration(
  triggerName: string,
  validationData: ValidationRequest
): Promise<ValidationResult> {
  const response = await fetch(`${API_BASE_URL}/api/triggers/${triggerName}/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(validationData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Validation failed');
  }

  const data: ValidationResponse = await response.json();

  return {
    is_valid: data.is_valid,
    prompt_types: data.prompt_types,
    shared_config_issues: data.shared_config_issues,
    summary: data.summary,
  };
}
