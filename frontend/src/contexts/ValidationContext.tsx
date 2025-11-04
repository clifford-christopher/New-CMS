'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { useDebouncedCallback } from 'use-debounce';
import { validatePlaceholders } from '@/lib/placeholderUtils';
import { ValidationError, ValidationResult, SectionData } from '@/types/validation';

type PromptType = 'paid' | 'unpaid' | 'crawler';

interface ValidationContextType {
  validation: Record<PromptType, ValidationResult>;
  validatePrompt: (type: PromptType, content: string, sections: SectionData[]) => void;
  getErrorsForLine: (type: PromptType, lineNumber: number) => ValidationError[];
  highlightedPosition: { type: PromptType; placeholder: string } | null;
  setHighlightedPosition: (pos: { type: PromptType; placeholder: string } | null) => void;
  isValidating: boolean;
}

const ValidationContext = createContext<ValidationContextType | undefined>(undefined);

export function ValidationProvider({ children }: { children: ReactNode }) {
  const [validation, setValidation] = useState<Record<PromptType, ValidationResult>>({
    paid: { errors: [], validPlaceholders: [], hasErrors: false },
    unpaid: { errors: [], validPlaceholders: [], hasErrors: false },
    crawler: { errors: [], validPlaceholders: [], hasErrors: false }
  });
  const [isValidating, setIsValidating] = useState(false);
  const [highlightedPosition, setHighlightedPosition] = useState<{ type: PromptType; placeholder: string } | null>(null);

  const validatePromptInternal = useCallback((type: PromptType, content: string, sections: SectionData[]) => {
    setIsValidating(true);
    try {
      if (!sections || sections.length === 0) {
        setValidation(prev => ({
          ...prev,
          [type]: {
            errors: [],
            validPlaceholders: [],
            hasErrors: false
          }
        }));
        return;
      }

      const result = validatePlaceholders(content, sections);
      setValidation(prev => ({
        ...prev,
        [type]: result
      }));
    } finally {
      setIsValidating(false);
    }
  }, []);

  // Debounced validation function (500ms delay)
  const validatePrompt = useDebouncedCallback(
    (type: PromptType, content: string, sections: SectionData[]) => {
      validatePromptInternal(type, content, sections);
    },
    500
  );

  const getErrorsForLine = useCallback((type: PromptType, lineNumber: number) => {
    return validation[type].errors.filter(err => err.line === lineNumber);
  }, [validation]);

  const value: ValidationContextType = {
    validation,
    validatePrompt,
    getErrorsForLine,
    highlightedPosition,
    setHighlightedPosition,
    isValidating
  };

  return <ValidationContext.Provider value={value}>{children}</ValidationContext.Provider>;
}

export function useValidation() {
  const context = useContext(ValidationContext);
  if (context === undefined) {
    throw new Error('useValidation must be used within a ValidationProvider');
  }
  return context;
}
