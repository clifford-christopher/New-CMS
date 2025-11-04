export interface SectionData {
  section_id: string;
  section_name: string;
  section_title: string;
  content: string;
}

export interface ValidationError {
  placeholder: string;
  line: number;
  column: number;
  message: string;
  position: { start: number; end: number };
}

export interface ValidationResult {
  errors: ValidationError[];
  validPlaceholders: string[];
  hasErrors: boolean;
}

export interface PlaceholderMatch {
  text: string;
  type: 'section' | 'field';
  name: string;
  start: number;
  end: number;
}

export interface AutocompleteSuggestion {
  label: string;
  kind: 'section' | 'field';
  detail: string;
  insertText: string;
}
