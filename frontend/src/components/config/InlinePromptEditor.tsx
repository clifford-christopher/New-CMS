/**
 * InlinePromptEditor Component
 * Story 4.5: Iterative Refinement Workflow
 *
 * Compact Monaco editor for inline prompt editing and regeneration
 */

import React, { useState, useEffect } from 'react';
import { Button, Alert } from 'react-bootstrap';
import dynamic from 'next/dynamic';
import { PromptType } from '@/types/generation';

// Dynamically import Monaco Editor (client-side only)
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

interface InlinePromptEditorProps {
  initialPrompt: string;
  promptType: PromptType;
  onRegenerate: (editedPrompt: string) => void;
  onCancel: () => void;
  isGenerating?: boolean;
}

const InlinePromptEditor: React.FC<InlinePromptEditorProps> = ({
  initialPrompt,
  promptType,
  onRegenerate,
  onCancel,
  isGenerating = false
}) => {
  const [editedPrompt, setEditedPrompt] = useState(initialPrompt);
  const [hasPlaceholders, setHasPlaceholders] = useState(true);

  /**
   * Check if prompt has placeholders
   */
  useEffect(() => {
    const sectionPattern = /\{\{[a-zA-Z_][a-zA-Z0-9_\s]*\}\}/;
    const dataPattern = /\{data\.[a-zA-Z_][a-zA-Z0-9_.]*\}/;
    const hasSectionPlaceholder = sectionPattern.test(editedPrompt);
    const hasDataPlaceholder = dataPattern.test(editedPrompt);
    setHasPlaceholders(hasSectionPlaceholder || hasDataPlaceholder);
  }, [editedPrompt]);

  /**
   * Handle editor change
   */
  const handleEditorChange = (value: string | undefined) => {
    setEditedPrompt(value || '');
  };

  /**
   * Handle regenerate
   */
  const handleRegenerate = () => {
    if (editedPrompt.trim().length === 0) {
      alert('Prompt cannot be empty');
      return;
    }
    onRegenerate(editedPrompt);
  };

  /**
   * Handle revert
   */
  const handleRevert = () => {
    setEditedPrompt(initialPrompt);
  };

  const isModified = editedPrompt !== initialPrompt;

  return (
    <div style={{
      background: '#f8f9fa',
      border: '1px solid #dee2e6',
      borderRadius: '4px',
      padding: '12px'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong style={{ fontSize: '14px' }}>
            <i className="bi bi-pencil me-2"></i>
            Edit Prompt for {promptType}
          </strong>
          {isModified && (
            <span style={{ marginLeft: '8px', fontSize: '12px', color: '#ffc107' }}>
              <i className="bi bi-exclamation-circle me-1"></i>
              Modified
            </span>
          )}
        </div>
        <Button
          variant="link"
          size="sm"
          onClick={onCancel}
          style={{ padding: '0', color: '#6c757d' }}
        >
          <i className="bi bi-x-lg"></i>
        </Button>
      </div>

      {/* Warning if no placeholders */}
      {!hasPlaceholders && editedPrompt.trim().length > 0 && (
        <Alert variant="warning" style={{ marginBottom: '8px', padding: '8px', fontSize: '12px' }}>
          <i className="bi bi-exclamation-triangle me-2"></i>
          <strong>Warning:</strong> No placeholders detected! Without placeholders like{' '}
          <code>{'{{section_id}}'}</code> or <code>{'{data.field}'}</code>, the LLM won't receive your configured data.
        </Alert>
      )}

      {/* Monaco Editor */}
      <div style={{
        border: '1px solid #ced4da',
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <MonacoEditor
          height="200px"
          defaultLanguage="markdown"
          value={editedPrompt}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            lineNumbers: 'off',
            folding: false,
            wordWrap: 'on',
            scrollBeyondLastLine: false,
            fontSize: 13,
            padding: { top: 8, bottom: 8 }
          }}
          theme="vs-light"
        />
      </div>

      {/* Actions */}
      <div style={{ marginTop: '12px', display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={handleRevert}
          disabled={!isModified || isGenerating}
        >
          <i className="bi bi-arrow-counterclockwise me-1"></i>
          Revert to Original
        </Button>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={onCancel}
          disabled={isGenerating}
        >
          Cancel
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={handleRegenerate}
          disabled={isGenerating || editedPrompt.trim().length === 0}
        >
          {isGenerating ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Regenerating...
            </>
          ) : (
            <>
              <i className="bi bi-arrow-repeat me-1"></i>
              Apply & Regenerate
            </>
          )}
        </Button>
      </div>

      {/* Help Text */}
      <div style={{ marginTop: '8px', fontSize: '11px', color: '#6c757d', fontStyle: 'italic' }}>
        <i className="bi bi-info-circle me-1"></i>
        Edit the prompt above and click "Apply & Regenerate" to create a new version with your changes.
        This won't save to the database - only affects the current test generation.
      </div>
    </div>
  );
};

export default InlinePromptEditor;
