/**
 * GenerationResultCard Component
 * Story 4.4 & 4.5: Displays a single generation result with metadata and version tracking
 */

import React, { useState } from 'react';
import { Card, Badge, Button, Alert, Spinner } from 'react-bootstrap';
import { GenerationResult } from '@/types/generation';
import { useGeneration } from '@/contexts/GenerationContext';
import InlinePromptEditor from './InlinePromptEditor';
import GenerationVersionModal from './GenerationVersionModal';

interface GenerationResultCardProps {
  result: GenerationResult;
}

const GenerationResultCard: React.FC<GenerationResultCardProps> = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);

  const { response, status, error } = result;

  // Get version tracking context (Story 4.5)
  const {
    isGenerating,
    regenerateResult,
    getVersions,
    getSelectedVersion,
    selectVersion
  } = useGeneration();

  // Get version information
  const versions = getVersions(result.model_id, result.prompt_type);
  const selectedVersion = getSelectedVersion(result.model_id, result.prompt_type);
  const currentVersionNumber = selectedVersion?.version || 1;
  const totalVersions = versions.length;
  const hasMultipleVersions = totalVersions > 1;

  // Provider badge colors
  const providerColors: Record<string, string> = {
    openai: 'success',
    anthropic: 'warning',
    gemini: 'info'
  };

  // Status badge colors
  const statusColors: Record<string, string> = {
    pending: 'secondary',
    generating: 'primary',
    completed: 'success',
    error: 'danger'
  };

  const handleCopy = async () => {
    if (response.generated_text) {
      try {
        await navigator.clipboard.writeText(response.generated_text);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    }
  };

  /**
   * Handle regeneration with same prompt (Story 4.5)
   */
  const handleRegenerateSame = async () => {
    await regenerateResult(result.model_id, result.prompt_type);
  };

  /**
   * Handle regeneration with edited prompt (Story 4.5)
   */
  const handleRegenerateEdited = async (editedPrompt: string) => {
    await regenerateResult(result.model_id, result.prompt_type, editedPrompt);
    setShowPromptEditor(false);
  };

  /**
   * Handle open version comparison modal (Story 4.5)
   */
  const handleCompareVersions = () => {
    setShowVersionModal(true);
  };

  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(6)}`;
  };

  const formatLatency = (latency: number): string => {
    return `${latency.toFixed(2)}s`;
  };

  // Rendering states
  if (status === 'pending' || status === 'generating') {
    return (
      <Card className="mb-3 border-primary">
        <Card.Body>
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <Badge bg={providerColors[response.provider] || 'secondary'} className="me-2">
                {response.provider || 'Unknown'}
              </Badge>
              <strong>{response.model_name || result.model_id}</strong>
            </div>
            <Spinner animation="border" size="sm" variant="primary" />
          </div>
          <p className="text-muted mb-0 mt-2">
            <small>{status === 'generating' ? 'Generating...' : 'Pending...'}</small>
          </p>
        </Card.Body>
      </Card>
    );
  }

  if (status === 'error') {
    return (
      <Card className="mb-3 border-danger">
        <Card.Body>
          <div className="d-flex align-items-center justify-content-between mb-2">
            <div>
              <Badge bg="secondary" className="me-2">
                {result.model_id}
              </Badge>
            </div>
            <Badge bg="danger">Error</Badge>
          </div>
          <Alert variant="danger" className="mb-0">
            <small>
              <i className="bi bi-exclamation-triangle me-2"></i>
              {error || 'Generation failed'}
            </small>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // Completed status
  const characterCount = response.generated_text?.length || 0;
  const wordCount = response.generated_text ? response.generated_text.split(/\s+/).filter(Boolean).length : 0;
  const previewLength = 200;
  const needsTruncation = characterCount > previewLength;
  const displayText = isExpanded || !needsTruncation
    ? response.generated_text
    : response.generated_text?.substring(0, previewLength) + '...';

  return (
    <Card className="mb-3 border-success">
      <Card.Header className="bg-success bg-opacity-10">
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <Badge
              bg={providerColors[response.provider] || 'secondary'}
              className="me-2 text-capitalize"
            >
              {response.provider}
            </Badge>
            <strong>{response.model_name}</strong>
            {/* Version Badge (Story 4.5) */}
            {totalVersions > 0 && (
              <Badge bg="info" className="ms-2">
                v{currentVersionNumber} of {totalVersions}
              </Badge>
            )}
            {selectedVersion?.is_selected && (
              <i className="bi bi-check-circle-fill text-success ms-2" title="Selected version"></i>
            )}
          </div>
          <div className="d-flex gap-2">
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleCopy}
              disabled={!response.generated_text}
            >
              <i className={`bi ${copySuccess ? 'bi-check' : 'bi-clipboard'} me-1`}></i>
              {copySuccess ? 'Copied!' : 'Copy'}
            </Button>
          </div>
        </div>
      </Card.Header>
      <Card.Body>
        {/* Generated Text */}
        <div className="mb-3">
          <p className="mb-2" style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {displayText}
          </p>
          {needsTruncation && (
            <Button
              variant="link"
              size="sm"
              className="p-0"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Show Less' : 'Show More'}
            </Button>
          )}
        </div>

        {/* Regeneration Actions (Story 4.5) */}
        <div className="mb-3 pb-3 border-bottom">
          <div className="d-flex gap-2 flex-wrap">
            <Button
              variant="outline-primary"
              size="sm"
              onClick={handleRegenerateSame}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  Regenerating...
                </>
              ) : (
                <>
                  <i className="bi bi-arrow-repeat me-1"></i>
                  Regenerate with Same Prompt
                </>
              )}
            </Button>
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={() => setShowPromptEditor(!showPromptEditor)}
              disabled={isGenerating}
            >
              <i className="bi bi-pencil me-1"></i>
              {showPromptEditor ? 'Cancel Edit' : 'Edit & Regenerate'}
            </Button>
            {hasMultipleVersions && (
              <Button
                variant="outline-info"
                size="sm"
                onClick={handleCompareVersions}
                disabled={isGenerating}
              >
                <i className="bi bi-code-square me-1"></i>
                Compare Versions ({totalVersions})
              </Button>
            )}
          </div>
        </div>

        {/* Inline Prompt Editor (Story 4.5) */}
        {showPromptEditor && selectedVersion && (
          <div className="mb-3">
            <InlinePromptEditor
              initialPrompt={selectedVersion.prompt_used}
              promptType={result.prompt_type}
              onRegenerate={handleRegenerateEdited}
              onCancel={() => setShowPromptEditor(false)}
              isGenerating={isGenerating}
            />
          </div>
        )}

        {/* Metadata */}
        <div className="border-top pt-3">
          <div className="row g-3">
            <div className="col-md-6">
              <div className="d-flex justify-content-between">
                <span className="text-muted">
                  <i className="bi bi-file-text me-1"></i>
                  Characters:
                </span>
                <strong>{characterCount.toLocaleString()}</strong>
              </div>
              <div className="d-flex justify-content-between">
                <span className="text-muted">
                  <i className="bi bi-chat-square-text me-1"></i>
                  Words:
                </span>
                <strong>{wordCount.toLocaleString()}</strong>
              </div>
            </div>
            <div className="col-md-6">
              <div className="d-flex justify-content-between">
                <span className="text-muted">
                  <i className="bi bi-coin me-1"></i>
                  Cost:
                </span>
                <strong>{formatCost(response.cost)}</strong>
              </div>
              <div className="d-flex justify-content-between">
                <span className="text-muted">
                  <i className="bi bi-clock me-1"></i>
                  Latency:
                </span>
                <strong>{formatLatency(response.latency)}</strong>
              </div>
            </div>
            <div className="col-12">
              <div className="d-flex justify-content-between">
                <span className="text-muted">
                  <i className="bi bi-cpu me-1"></i>
                  Tokens:
                </span>
                <strong>
                  {response.input_tokens.toLocaleString()} in / {response.output_tokens.toLocaleString()} out
                  <span className="text-muted ms-2">({response.total_tokens.toLocaleString()} total)</span>
                </strong>
              </div>
              <div className="d-flex justify-content-between mt-1">
                <span className="text-muted">
                  <i className="bi bi-thermometer me-1"></i>
                  Temperature:
                </span>
                <strong>{response.temperature.toFixed(2)}</strong>
              </div>
              <div className="d-flex justify-content-between mt-1">
                <span className="text-muted">
                  <i className="bi bi-check-circle me-1"></i>
                  Finish Reason:
                </span>
                <Badge bg="secondary">{response.finish_reason}</Badge>
              </div>
            </div>
          </div>
        </div>
      </Card.Body>

      {/* Version Comparison Modal (Story 4.5) */}
      <GenerationVersionModal
        modelId={result.model_id}
        promptType={result.prompt_type}
        show={showVersionModal}
        onHide={() => setShowVersionModal(false)}
      />
    </Card>
  );
};

export default GenerationResultCard;
