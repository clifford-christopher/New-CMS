import { SectionData } from './validation';

export type PromptType = 'paid' | 'unpaid' | 'crawler';

export interface PreviewContent {
  prompt: string;
  substitutedPrompt: string;
  validPlaceholders: string[];
  missingPlaceholders: string[];
  estimatedTokens: number;
  characterCount: number;
}

export interface PreviewMetadata {
  stockId: string | null;
  triggerName: string;
  promptType: PromptType;
  timestamp: Date;
  version?: number | 'current';
  savedBy?: string;
  savedAt?: string;
}

export interface SubstitutionResult {
  substitutedPrompt: string;
  validPlaceholders: string[];
  missingPlaceholders: string[];
}

export interface VersionHistoryItem {
  version: number;
  saved_at: string;
  saved_by: string;
  is_draft: boolean;
  prompt_types: string[];
}

export interface VersionResponse {
  versions: VersionHistoryItem[];
  total: number;
  trigger_name: string;
}

export interface VersionData {
  trigger_name: string;
  version: number;
  saved_at: string;
  saved_by: string;
  prompts: {
    [key: string]: {
      template: string;
      character_count: number;
      word_count: number;
      last_saved: string;
      version: number;
      is_draft: boolean;
    };
  };
  is_draft: boolean;
}

export { SectionData };
