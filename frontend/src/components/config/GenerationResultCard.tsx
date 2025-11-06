/**
 * GenerationResultCard Component
 * Displays a single generation result with metadata
 */

import React, { useState } from 'react';
import { Card, Badge, Button, Alert, Spinner } from 'react-bootstrap';
import { GenerationResult } from '@/types/generation';

interface GenerationResultCardProps {
  result: GenerationResult;
}

const GenerationResultCard: React.FC<GenerationResultCardProps> = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const { response, status, error } = result;

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
    </Card>
  );
};

export default GenerationResultCard;
