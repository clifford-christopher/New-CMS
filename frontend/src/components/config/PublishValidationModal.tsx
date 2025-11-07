/**
 * PublishValidationModal Component
 * Story 5.1: Pre-Publish Validation
 *
 * Displays validation results before allowing configuration publish
 */

import React from 'react';
import { Modal, Button, Alert, Badge, Card, ListGroup } from 'react-bootstrap';

interface ValidationIssue {
  severity: 'error' | 'warning';
  category: string;
  message: string;
  prompt_type?: string;
}

interface TestMetadata {
  models_tested: string[];
  total_tests: number;
  avg_cost: number;
  avg_latency: number;
  total_cost: number;
  sample_output?: string;
}

interface PromptTypeValidation {
  prompt_type: string;
  is_valid: boolean;
  issues: ValidationIssue[];
  test_metadata?: TestMetadata;
}

interface ValidationResult {
  is_valid: boolean;
  prompt_types: Record<string, PromptTypeValidation>;
  shared_config_issues: ValidationIssue[];
  summary: {
    total_errors: number;
    total_warnings: number;
    prompt_types_validated: number;
  };
}

interface PublishValidationModalProps {
  show: boolean;
  onHide: () => void;
  validationResult: ValidationResult | null;
  isValidating: boolean;
  onProceedToPublish: () => void;
  onRunTests: () => void;
}

const PublishValidationModal: React.FC<PublishValidationModalProps> = ({
  show,
  onHide,
  validationResult,
  isValidating,
  onProceedToPublish,
  onRunTests
}) => {
  const promptTypeLabels: Record<string, string> = {
    paid: 'Paid',
    unpaid: 'Unpaid',
    crawler: 'Web Crawler'
  };

  const getPromptTypeIcon = (promptType: string): string => {
    const icons: Record<string, string> = {
      paid: '💰',
      unpaid: '🆓',
      crawler: '🕷️'
    };
    return icons[promptType] || '📄';
  };

  const renderIssue = (issue: ValidationIssue, index: number) => {
    const isError = issue.severity === 'error';
    const icon = isError ? '❌' : '⚠️';
    const variant = isError ? 'danger' : 'warning';

    return (
      <Alert key={index} variant={variant} className="py-2 px-3 mb-2">
        <small>
          <strong>{icon} {isError ? 'Error' : 'Warning'}:</strong> {issue.message}
        </small>
      </Alert>
    );
  };

  const renderPromptTypeValidation = (promptType: string, validation: PromptTypeValidation) => {
    const hasErrors = validation.issues.some(i => i.severity === 'error');
    const hasWarnings = validation.issues.some(i => i.severity === 'warning');
    const isValid = validation.is_valid;

    return (
      <Card key={promptType} className="mb-3">
        <Card.Header className={isValid ? 'bg-success bg-opacity-10' : 'bg-danger bg-opacity-10'}>
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <span className="me-2">{getPromptTypeIcon(promptType)}</span>
              <strong>{promptTypeLabels[promptType]} Prompt Type</strong>
              {isValid && (
                <Badge bg="success" className="ms-2">
                  <i className="bi bi-check-circle me-1"></i>
                  Valid
                </Badge>
              )}
              {hasErrors && (
                <Badge bg="danger" className="ms-2">
                  {validation.issues.filter(i => i.severity === 'error').length} Error(s)
                </Badge>
              )}
              {hasWarnings && (
                <Badge bg="warning" className="ms-2">
                  {validation.issues.filter(i => i.severity === 'warning').length} Warning(s)
                </Badge>
              )}
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          {/* Validation Issues */}
          {validation.issues.length > 0 ? (
            <div className="mb-3">
              {validation.issues.map((issue, idx) => renderIssue(issue, idx))}
            </div>
          ) : (
            <Alert variant="success" className="mb-3">
              <i className="bi bi-check-circle me-2"></i>
              <strong>All validations passed</strong>
            </Alert>
          )}

          {/* Test Metadata */}
          {validation.test_metadata && (
            <Card className="bg-light">
              <Card.Body>
                <h6 className="mb-3">
                  <i className="bi bi-graph-up me-2"></i>
                  Test Results Summary
                </h6>
                <ListGroup variant="flush">
                  <ListGroup.Item className="bg-transparent px-0 py-2">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">
                        <i className="bi bi-cpu me-1"></i>
                        Models Tested:
                      </span>
                      <span>
                        {validation.test_metadata.models_tested.map((model, idx) => (
                          <Badge key={idx} bg="secondary" className="ms-1">
                            {model}
                          </Badge>
                        ))}
                      </span>
                    </div>
                  </ListGroup.Item>
                  <ListGroup.Item className="bg-transparent px-0 py-2">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">
                        <i className="bi bi-file-earmark-text me-1"></i>
                        Total Tests:
                      </span>
                      <strong>{validation.test_metadata.total_tests}</strong>
                    </div>
                  </ListGroup.Item>
                  <ListGroup.Item className="bg-transparent px-0 py-2">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">
                        <i className="bi bi-coin me-1"></i>
                        Average Cost:
                      </span>
                      <strong>${validation.test_metadata.avg_cost.toFixed(4)}</strong>
                    </div>
                  </ListGroup.Item>
                  <ListGroup.Item className="bg-transparent px-0 py-2">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">
                        <i className="bi bi-clock me-1"></i>
                        Average Latency:
                      </span>
                      <strong>{validation.test_metadata.avg_latency.toFixed(2)}s</strong>
                    </div>
                  </ListGroup.Item>
                  <ListGroup.Item className="bg-transparent px-0 py-2">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">
                        <i className="bi bi-calculator me-1"></i>
                        Total Cost:
                      </span>
                      <strong className={validation.test_metadata.total_cost > 1.0 ? 'text-warning' : ''}>
                        ${validation.test_metadata.total_cost.toFixed(4)}
                      </strong>
                    </div>
                  </ListGroup.Item>
                </ListGroup>
              </Card.Body>
            </Card>
          )}
        </Card.Body>
      </Card>
    );
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="bi bi-shield-check me-2"></i>
          Pre-Publish Validation
        </Modal.Title>
      </Modal.Header>
      <Modal.Body style={{ maxHeight: '70vh', overflowY: 'auto' }}>
        {isValidating ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary mb-3" role="status">
              <span className="visually-hidden">Validating...</span>
            </div>
            <p className="text-muted">Validating configuration...</p>
          </div>
        ) : validationResult ? (
          <>
            {/* Summary Alert */}
            {validationResult.is_valid ? (
              <Alert variant="success" className="mb-4">
                <div className="d-flex align-items-center">
                  <i className="bi bi-check-circle-fill me-3" style={{ fontSize: '2rem' }}></i>
                  <div>
                    <h5 className="mb-1">Configuration is Valid</h5>
                    <p className="mb-0">
                      All {validationResult.summary.prompt_types_validated} prompt type(s) passed validation.
                      {validationResult.summary.total_warnings > 0 && (
                        <span className="text-warning ms-2">
                          ({validationResult.summary.total_warnings} warning(s) detected)
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              </Alert>
            ) : (
              <Alert variant="danger" className="mb-4">
                <div className="d-flex align-items-center">
                  <i className="bi bi-x-circle-fill me-3" style={{ fontSize: '2rem' }}></i>
                  <div>
                    <h5 className="mb-1">Validation Failed</h5>
                    <p className="mb-0">
                      Found {validationResult.summary.total_errors} error(s)
                      {validationResult.summary.total_warnings > 0 && (
                        <> and {validationResult.summary.total_warnings} warning(s)</>
                      )}. Please fix the issues before publishing.
                    </p>
                  </div>
                </div>
              </Alert>
            )}

            {/* Shared Configuration Issues */}
            {validationResult.shared_config_issues.length > 0 && (
              <Card className="mb-3">
                <Card.Header className="bg-warning bg-opacity-10">
                  <strong>
                    <i className="bi bi-gear me-2"></i>
                    Shared Configuration Issues
                  </strong>
                </Card.Header>
                <Card.Body>
                  {validationResult.shared_config_issues.map((issue, idx) => renderIssue(issue, idx))}
                </Card.Body>
              </Card>
            )}

            {/* Prompt Type Validations */}
            {Object.entries(validationResult.prompt_types).map(([promptType, validation]) =>
              renderPromptTypeValidation(promptType, validation)
            )}
          </>
        ) : (
          <Alert variant="info">
            <i className="bi bi-info-circle me-2"></i>
            Click "Validate" to check if your configuration is ready for publishing.
          </Alert>
        )}
      </Modal.Body>
      <Modal.Footer>
        <div className="d-flex justify-content-between w-100">
          <div>
            {validationResult && !validationResult.is_valid && (
              <Button
                variant="outline-primary"
                size="sm"
                onClick={onRunTests}
              >
                <i className="bi bi-play-circle me-1"></i>
                Run Tests
              </Button>
            )}
          </div>
          <div className="d-flex gap-2">
            <Button variant="secondary" onClick={onHide}>
              Cancel
            </Button>
            <Button
              variant="success"
              onClick={onProceedToPublish}
              disabled={!validationResult || !validationResult.is_valid || isValidating}
            >
              <i className="bi bi-arrow-right-circle me-1"></i>
              Proceed to Publish
            </Button>
          </div>
        </div>
      </Modal.Footer>
    </Modal>
  );
};

export default PublishValidationModal;
