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
}

export interface SubstitutionResult {
  substitutedPrompt: string;
  validPlaceholders: string[];
  missingPlaceholders: string[];
}

export { SectionData };
