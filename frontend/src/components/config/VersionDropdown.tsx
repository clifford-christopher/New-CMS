/**
 * VersionDropdown Component
 * Reusable version selector with preview for generation history
 */

import React, { useState } from 'react';
import { Card, Row, Col, Form, Badge, Button, Spinner } from 'react-bootstrap';
import { GenerationVersion, PromptType } from '@/types/generation';

export interface VersionOption {
  key: string;
  label: string;
  modelId: string;
  promptType: PromptType;
  versionIndex: number;
  version: number;
  timestamp: string;
}

interface VersionDropdownProps {
  versionOptions: VersionOption[];
  resultVersions: Map<string, GenerationVersion[]>;
  isLoading?: boolean;
  onVersionSelect?: (option: VersionOption | null) => void;
}

const VersionDropdown: React.FC<VersionDropdownProps> = ({
  versionOptions,
  resultVersions,
  isLoading = false,
  onVersionSelect
}) => {
  const [selectedVersion, setSelectedVersion] = useState<string>('');
  const [showVersionPreview, setShowVersionPreview] = useState(false);

  // Get currently selected version details
  const getSelectedVersionDetails = (): GenerationVersion | null => {
    if (!selectedVersion) return null;
    const option = versionOptions.find(opt => opt.key === selectedVersion);
    if (!option) return null;

    const key = `${option.modelId}-${option.promptType}`;
    const versions = resultVersions.get(key);
    if (!versions) return null;

    return versions[option.versionIndex];
  };

  const selectedVersionDetails = getSelectedVersionDetails();

  const handleVersionChange = (value: string) => {
    setSelectedVersion(value);
    setShowVersionPreview(!!value);

    if (onVersionSelect) {
      if (value) {
        const option = versionOptions.find(opt => opt.key === value);
        onVersionSelect(option || null);
      } else {
        onVersionSelect(null);
      }
    }
  };

  const handleClearSelection = () => {
    setSelectedVersion('');
    setShowVersionPreview(false);
    if (onVersionSelect) {
      onVersionSelect(null);
    }
  };

  if (versionOptions.length === 0 && !isLoading) {
    return null;
  }

  return (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">
          <i className="bi bi-clock-history me-2"></i>
          Previous Generations
        </h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={8}>
            <Form.Group>
              <Form.Label>
                <strong>Select a previous generation to view:</strong>
                <Badge bg="secondary" className="ms-2">
                  {versionOptions.length} version{versionOptions.length !== 1 ? 's' : ''}
                </Badge>
              </Form.Label>
              <Form.Select
                value={selectedVersion}
                onChange={(e) => handleVersionChange(e.target.value)}
                disabled={isLoading}
              >
                <option value="">-- Select a version --</option>
                {versionOptions.map((option) => (
                  <option key={option.key} value={option.key}>
                    {option.label}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={4} className="d-flex align-items-end">
            {selectedVersion && (
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={handleClearSelection}
              >
                <i className="bi bi-x-circle me-1"></i>
                Clear Selection
              </Button>
            )}
          </Col>
        </Row>

        {/* Version Preview */}
        {showVersionPreview && selectedVersionDetails && (
          <Card className="mt-3 border-info">
            <Card.Header className="bg-info bg-opacity-10">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <Badge bg="info" className="me-2">v{selectedVersionDetails.version}</Badge>
                  <strong>{selectedVersionDetails.result.response.model_name}</strong>
                  <Badge bg="secondary" className="ms-2 text-capitalize">
                    {selectedVersionDetails.result.prompt_type}
                  </Badge>
                </div>
                <small className="text-muted">
                  {new Date(selectedVersionDetails.timestamp).toLocaleString()}
                </small>
              </div>
            </Card.Header>
            <Card.Body>
              {/* Generated Text Preview */}
              <div
                style={{
                  maxHeight: '150px',
                  overflowY: 'auto',
                  backgroundColor: '#f8f9fa',
                  padding: '12px',
                  borderRadius: '4px',
                  marginBottom: '12px',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {selectedVersionDetails.result.response.generated_text.substring(0, 300)}
                {selectedVersionDetails.result.response.generated_text.length > 300 && '...'}
              </div>

              {/* Metrics */}
              <Row>
                <Col md={3}>
                  <small className="text-muted">Cost:</small>
                  <div><strong>${selectedVersionDetails.result.response.cost.toFixed(6)}</strong></div>
                </Col>
                <Col md={3}>
                  <small className="text-muted">Latency:</small>
                  <div><strong>{selectedVersionDetails.result.response.latency.toFixed(2)}s</strong></div>
                </Col>
                <Col md={3}>
                  <small className="text-muted">Tokens:</small>
                  <div><strong>{selectedVersionDetails.result.response.total_tokens.toLocaleString()}</strong></div>
                </Col>
                <Col md={3}>
                  <small className="text-muted">Provider:</small>
                  <div className="text-capitalize"><strong>{selectedVersionDetails.result.response.provider}</strong></div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        )}

        {isLoading && (
          <div className="text-center mt-3">
            <Spinner animation="border" size="sm" className="me-2" />
            <small className="text-muted">Loading previous generations...</small>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default VersionDropdown;
