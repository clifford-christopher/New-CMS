/**
 * VersionDiffModal Component
 * Story 5.4: Version History & Rollback
 *
 * Display detailed diff between two configuration versions
 */

import React, { useState, useEffect } from 'react';
import { Modal, Button, Alert, Spinner, Badge, Card, Table } from 'react-bootstrap';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface VersionDiffModalProps {
  show: boolean;
  onHide: () => void;
  triggerName: string;
  versionA: number;
  versionB: number;
}

interface DiffResult {
  version_a: number;
  version_b: number;
  differences: {
    apis?: {
      version_a: string[];
      version_b: string[];
      added: string[];
      removed: string[];
    };
    section_order?: {
      version_a: string[];
      version_b: string[];
    };
    prompts?: Record<string, {
      version_a: string;
      version_b: string;
      changed: boolean;
    }>;
    model_settings?: {
      version_a: any;
      version_b: any;
    };
    test_results_summary?: {
      version_a: any;
      version_b: any;
    };
  };
}

const VersionDiffModal: React.FC<VersionDiffModalProps> = ({
  show,
  onHide,
  triggerName,
  versionA,
  versionB
}) => {
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (show) {
      fetchDiff();
    }
  }, [show, triggerName, versionA, versionB]);

  const fetchDiff = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/triggers/${triggerName}/versions/${versionA}/compare`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            compare_with_version: versionB
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to compare versions');
      }

      const data = await response.json();
      setDiff(data.diff);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const hasDifferences = diff && Object.keys(diff.differences).length > 0;

  return (
    <Modal show={show} onHide={onHide} size="xl" fullscreen="lg-down">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="bi bi-code-square me-2"></i>
          Compare Versions: v{versionA} vs v{versionB}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {/* Error Alert */}
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </Alert>
        )}

        {/* Loading Spinner */}
        {isLoading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
            <p className="mt-2">Comparing versions...</p>
          </div>
        ) : !diff ? (
          <Alert variant="warning">No diff data available</Alert>
        ) : !hasDifferences ? (
          <Alert variant="success">
            <i className="bi bi-check-circle me-2"></i>
            <strong>No differences found!</strong> Versions {versionA} and {versionB} are identical.
          </Alert>
        ) : (
          <div>
            {/* APIs Diff */}
            {diff.differences.apis && (
              <Card className="mb-3">
                <Card.Header className="bg-warning bg-opacity-10">
                  <strong>APIs Configuration</strong>
                </Card.Header>
                <Card.Body>
                  {diff.differences.apis.added.length > 0 && (
                    <div className="mb-2">
                      <Badge bg="success">Added</Badge>
                      <div className="mt-1">
                        {diff.differences.apis.added.map((api, idx) => (
                          <Badge key={idx} bg="success" className="me-1">
                            + {api}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {diff.differences.apis.removed.length > 0 && (
                    <div>
                      <Badge bg="danger">Removed</Badge>
                      <div className="mt-1">
                        {diff.differences.apis.removed.map((api, idx) => (
                          <Badge key={idx} bg="danger" className="me-1">
                            - {api}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </Card.Body>
              </Card>
            )}

            {/* Section Order Diff */}
            {diff.differences.section_order && (
              <Card className="mb-3">
                <Card.Header className="bg-warning bg-opacity-10">
                  <strong>Section Order</strong>
                </Card.Header>
                <Card.Body>
                  <div className="row">
                    <div className="col-md-6">
                      <strong>v{versionA}:</strong>
                      <ol>
                        {diff.differences.section_order.version_a.map((section, idx) => (
                          <li key={idx}>{section}</li>
                        ))}
                      </ol>
                    </div>
                    <div className="col-md-6">
                      <strong>v{versionB}:</strong>
                      <ol>
                        {diff.differences.section_order.version_b.map((section, idx) => (
                          <li key={idx}>{section}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            )}

            {/* Prompts Diff */}
            {diff.differences.prompts && (
              <Card className="mb-3">
                <Card.Header className="bg-warning bg-opacity-10">
                  <strong>Prompts</strong>
                </Card.Header>
                <Card.Body>
                  {Object.entries(diff.differences.prompts).map(([promptType, promptDiff]) => (
                    <div key={promptType} className="mb-3 pb-3 border-bottom last:border-0">
                      <h6 className="text-capitalize">{promptType} Prompt</h6>
                      <div className="row">
                        <div className="col-md-6">
                          <Badge bg="primary">v{versionA}</Badge>
                          <div
                            className="mt-2 p-2 border rounded"
                            style={{ backgroundColor: '#f8f9fa', maxHeight: '200px', overflowY: 'auto' }}
                          >
                            <small style={{ whiteSpace: 'pre-wrap' }}>{promptDiff.version_a}</small>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <Badge bg="primary">v{versionB}</Badge>
                          <div
                            className="mt-2 p-2 border rounded"
                            style={{ backgroundColor: '#f8f9fa', maxHeight: '200px', overflowY: 'auto' }}
                          >
                            <small style={{ whiteSpace: 'pre-wrap' }}>{promptDiff.version_b}</small>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </Card.Body>
              </Card>
            )}

            {/* Model Settings Diff */}
            {diff.differences.model_settings && (
              <Card className="mb-3">
                <Card.Header className="bg-warning bg-opacity-10">
                  <strong>Model Settings</strong>
                </Card.Header>
                <Card.Body>
                  <Table size="sm" bordered>
                    <thead>
                      <tr>
                        <th>Setting</th>
                        <th>v{versionA}</th>
                        <th>v{versionB}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Selected Models</strong></td>
                        <td>
                          {diff.differences.model_settings.version_a.selected_models?.join(', ') || 'N/A'}
                        </td>
                        <td>
                          {diff.differences.model_settings.version_b.selected_models?.join(', ') || 'N/A'}
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Temperature</strong></td>
                        <td>{diff.differences.model_settings.version_a.temperature || 'N/A'}</td>
                        <td>{diff.differences.model_settings.version_b.temperature || 'N/A'}</td>
                      </tr>
                      <tr>
                        <td><strong>Max Tokens</strong></td>
                        <td>{diff.differences.model_settings.version_a.max_tokens || 'N/A'}</td>
                        <td>{diff.differences.model_settings.version_b.max_tokens || 'N/A'}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            )}

            {/* Test Results Diff */}
            {diff.differences.test_results_summary && (
              <Card className="mb-3">
                <Card.Header className="bg-warning bg-opacity-10">
                  <strong>Test Results Summary</strong>
                </Card.Header>
                <Card.Body>
                  <Alert variant="info" className="mb-0">
                    <small>
                      <i className="bi bi-info-circle me-2"></i>
                      Test results differ between versions. Review the test metadata for each version in the version history table.
                    </small>
                  </Alert>
                </Card.Body>
              </Card>
            )}
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default VersionDiffModal;
