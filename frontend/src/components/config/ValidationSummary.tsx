'use client';

import { Card, Alert, Badge, ListGroup } from 'react-bootstrap';
import { useValidation } from '@/contexts/ValidationContext';
import { usePrompt } from '@/contexts/PromptContext';

export default function ValidationSummary() {
  const { validation, setHighlightedPosition } = useValidation();
  const { activeTab } = usePrompt();

  const currentValidation = validation[activeTab];

  if (!currentValidation.hasErrors) {
    return (
      <Card className="mt-4">
        <Card.Header>
          <h5 className="mb-0">
            <i className="bi bi-shield-check me-2"></i>
            Placeholder Validation
          </h5>
        </Card.Header>
        <Card.Body>
          <Alert variant="success" className="mb-0">
            <i className="bi bi-check-circle me-2"></i>
            <strong>All placeholders are valid!</strong> No errors detected in your prompt template.
          </Alert>
          {currentValidation.validPlaceholders.length > 0 && (
            <div className="mt-3">
              <small className="text-muted">
                Found {currentValidation.validPlaceholders.length} valid placeholder{currentValidation.validPlaceholders.length !== 1 ? 's' : ''}:
              </small>
              <div className="d-flex flex-wrap gap-1 mt-2">
                {currentValidation.validPlaceholders.map((placeholder, idx) => (
                  <Badge key={idx} bg="success" className="font-monospace">
                    {placeholder}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="mt-4 border-danger">
      <Card.Header className="bg-danger bg-opacity-10">
        <h5 className="mb-0 text-danger">
          <i className="bi bi-exclamation-triangle me-2"></i>
          Placeholder Errors
          <Badge bg="danger" className="ms-2">{currentValidation.errors.length}</Badge>
        </h5>
      </Card.Header>
      <Card.Body>
        <Alert variant="warning" className="mb-3">
          <i className="bi bi-info-circle me-2"></i>
          The following placeholders are invalid. Click an error to highlight it in the editor.
        </Alert>
        <ListGroup variant="flush">
          {currentValidation.errors.map((error, idx) => (
            <ListGroup.Item
              key={idx}
              className="d-flex justify-content-between align-items-start"
              onClick={() => setHighlightedPosition({ type: activeTab, placeholder: error.placeholder })}
              style={{ cursor: 'pointer' }}
              action
            >
              <div className="flex-grow-1">
                <div className="d-flex align-items-center mb-1">
                  <code className="text-danger fw-bold me-2">{error.placeholder}</code>
                  <small className="text-muted">
                    Line {error.line}, Column {error.column}
                  </small>
                </div>
                <div className="text-muted small">{error.message}</div>
              </div>
              <Badge bg="danger" className="ms-2">
                <i className="bi bi-x-circle me-1"></i>
                Error
              </Badge>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Card.Body>
    </Card>
  );
}
