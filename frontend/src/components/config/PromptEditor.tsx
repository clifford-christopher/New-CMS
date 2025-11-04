'use client';

import { useEffect, useRef, useState } from 'react';
import { Card, Alert, Button, Spinner } from 'react-bootstrap';
import Editor from '@monaco-editor/react';
import { usePrompt } from '@/contexts/PromptContext';
import { useValidation } from '@/contexts/ValidationContext';
import { usePreview } from '@/contexts/PreviewContext';
import { useData } from '@/contexts/DataContext';
import PromptTabs from './PromptTabs';
import CharacterCounter from './CharacterCounter';
import PlaceholderDocumentation from './PlaceholderDocumentation';
import ValidationSummary from './ValidationSummary';
import PreviewModal from './PreviewModal';
import UndoRedoButtons from './UndoRedoButtons';
import { getAvailablePlaceholders } from '@/lib/placeholderUtils';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

interface PromptEditorProps {
  triggerId: string;
}

export default function PromptEditor({ triggerId }: PromptEditorProps) {
  const {
    prompts,
    activeTab,
    editorTheme,
    setPromptContent,
    isSaving,
    saveError,
    loadPrompts,
    savePrompts,
    undo,
    redo
  } = usePrompt();

  const [showSaveSuccess, setShowSaveSuccess] = useState(false);

  const { validation, validatePrompt, highlightedPosition } = useValidation();
  const { openModal: openPreviewModal } = usePreview();
  const { selectedSections } = useData();

  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationsRef = useRef<any[]>([]);

  // Setup keyboard shortcuts for undo/redo
  useKeyboardShortcuts({
    undo: () => undo(activeTab),
    redo: () => redo(activeTab)
  });

  // Load prompts on mount
  useEffect(() => {
    loadPrompts(triggerId);
  }, [triggerId]);

  // Configure Monaco Editor with custom language
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Define custom language for prompt placeholders
    monaco.languages.register({ id: 'prompt-template' });

    monaco.languages.setMonarchTokensProvider('prompt-template', {
      tokenizer: {
        root: [
          // Highlight {{section_name}} placeholders
          [/\{\{[a-zA-Z_][a-zA-Z0-9_\s]*\}\}/, 'custom-placeholder'],
          // Highlight {data.field} placeholders
          [/\{data\.[a-zA-Z_][a-zA-Z0-9_.]*\}/, 'custom-placeholder'],
          // Comments
          [/#.*$/, 'comment']
        ]
      }
    });

    // Define custom theme
    monaco.editor.defineTheme('prompt-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'custom-placeholder', foreground: '569cd6', fontStyle: 'bold' },
        { token: 'comment', foreground: '6a9955', fontStyle: 'italic' }
      ],
      colors: {}
    });

    monaco.editor.defineTheme('prompt-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'custom-placeholder', foreground: '0000ff', fontStyle: 'bold' },
        { token: 'comment', foreground: '008000', fontStyle: 'italic' }
      ],
      colors: {}
    });

    // Register autocomplete provider
    monaco.languages.registerCompletionItemProvider('prompt-template', {
      triggerCharacters: ['{'],
      provideCompletionItems: (model: any, position: any) => {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: position.lineNumber,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        });

        // Check if we're typing a placeholder
        if (textUntilPosition.endsWith('{{') || textUntilPosition.endsWith('{data.')) {
          const suggestions = getAvailablePlaceholders(selectedSections);

          return {
            suggestions: suggestions.map(s => ({
              label: s.label,
              kind: s.kind === 'section' ? monaco.languages.CompletionItemKind.Field : monaco.languages.CompletionItemKind.Property,
              detail: s.detail,
              insertText: s.insertText.replace(/^\{\{/, '').replace(/\}\}$/, '').replace(/^\{data\./, ''),
              range: {
                startLineNumber: position.lineNumber,
                startColumn: position.column,
                endLineNumber: position.lineNumber,
                endColumn: position.column
              }
            }))
          };
        }

        return { suggestions: [] };
      }
    });
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setPromptContent(activeTab, value);
      // Trigger validation (debounced)
      validatePrompt(activeTab, value, selectedSections);
    }
  };

  // Update decorations when validation results change
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;

    const currentValidation = validation[activeTab];
    const monaco = monacoRef.current;
    const editor = editorRef.current;

    // Create decorations for errors
    const newDecorations = currentValidation.errors.map(error => ({
      range: new monaco.Range(
        error.line,
        error.column,
        error.line,
        error.column + error.placeholder.length
      ),
      options: {
        inlineClassName: 'squiggly-error',
        hoverMessage: { value: `**Error:** ${error.message}` },
        className: 'error-highlight'
      }
    }));

    // Apply decorations
    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations);
  }, [validation, activeTab]);

  // Highlight placeholder when error is clicked in summary
  useEffect(() => {
    if (!editorRef.current || !highlightedPosition || highlightedPosition.type !== activeTab) return;

    const editor = editorRef.current;
    const model = editor.getModel();
    if (!model) return;

    const content = model.getValue();
    const index = content.indexOf(highlightedPosition.placeholder);
    if (index === -1) return;

    const position = model.getPositionAt(index);
    editor.setPosition(position);
    editor.revealPositionInCenter(position);
    editor.focus();
  }, [highlightedPosition, activeTab]);

  const currentPrompt = prompts[activeTab];

  // Handle save button click with success notification
  const handleSaveClick = async () => {
    try {
      await savePrompts(triggerId);
      setShowSaveSuccess(true);
      setTimeout(() => setShowSaveSuccess(false), 3000);
    } catch (error) {
      // Error is already handled by PromptContext
    }
  };

  const formatLastSaved = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 60) return 'just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)} min ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} hr ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      <Card className="mt-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <div>
            <h5 className="mb-0">Prompt Editor</h5>
            <small className="text-muted">
              Craft prompts with placeholders (e.g., {'{{section_1}}'}, {'{data.earnings.summary}'})
            </small>
          </div>
          <div className="d-flex gap-2 align-items-center">
            {isSaving && (
              <span className="text-muted">
                <i className="bi bi-cloud-upload me-1"></i>
                Saving...
              </span>
            )}
            {currentPrompt.lastSaved && !isSaving && (
              <small className="text-success">
                <i className="bi bi-check-circle me-1"></i>
                Saved {formatLastSaved(currentPrompt.lastSaved)}
              </small>
            )}
            <UndoRedoButtons />
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={openPreviewModal}
              className="me-2"
            >
              <i className="bi bi-eye me-1"></i>
              Preview
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleSaveClick}
              disabled={isSaving}
            >
              {isSaving ? (
                <>
                  <Spinner as="span" animation="border" size="sm" className="me-1" />
                  Saving...
                </>
              ) : (
                <>
                  <i className="bi bi-floppy me-1"></i>
                  Save
                </>
              )}
            </Button>
          </div>
        </Card.Header>

        <Card.Body className="p-0">
          {showSaveSuccess && (
            <Alert variant="success" className="m-3 mb-0" dismissible onClose={() => setShowSaveSuccess(false)}>
              <i className="bi bi-check-circle-fill me-2"></i>
              <strong>Success!</strong> Prompts saved successfully with version history.
            </Alert>
          )}

          {saveError && (
            <Alert variant="danger" className="m-3 mb-0" dismissible>
              <i className="bi bi-exclamation-triangle-fill me-2"></i>
              <strong>Error:</strong> {saveError}
            </Alert>
          )}

          <Alert variant="info" className="m-3 mb-0">
            <i className="bi bi-info-circle me-2"></i>
            <strong>Tip:</strong> Use placeholders to reference your data sections.
            For example, <code>{'{{section_1}}'}</code> for a section or <code>{'{data.field}'}</code> for a data field.
            Start typing <code>{'{{'}}</code> to see autocomplete suggestions.
          </Alert>

          <div className="mx-3 mb-3">
            <PlaceholderDocumentation />
          </div>

          {/* Tab Navigation */}
          <PromptTabs />

          {/* Monaco Editor */}
          <div style={{ height: '500px', position: 'relative' }}>
            <Editor
              height="100%"
              language="prompt-template"
              theme={editorTheme === 'vs-dark' ? 'prompt-dark' : 'prompt-light'}
              value={currentPrompt.content}
              onChange={handleEditorChange}
              onMount={handleEditorDidMount}
              options={{
                minimap: { enabled: true },
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                fontSize: 14,
                tabSize: 2,
                insertSpaces: true,
                automaticLayout: true,
                suggestOnTriggerCharacters: true,
                quickSuggestions: true,
                formatOnPaste: true,
                formatOnType: true
              }}
            />
          </div>

          {/* Character Counter */}
          <CharacterCounter
            characterCount={currentPrompt.characterCount}
            wordCount={currentPrompt.wordCount}
            promptType={activeTab}
          />
        </Card.Body>
      </Card>

      {/* Validation Summary */}
      <ValidationSummary />

      {/* Preview Modal */}
      <PreviewModal />
    </>
  );
}
