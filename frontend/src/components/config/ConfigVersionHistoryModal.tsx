/**
 * ConfigVersionHistoryModal Component
 * Story 5.4: Version History & Rollback
 *
 * Display version history for published configurations with rollback capability
 */

import React, { useState, useEffect } from 'react';
import { Modal, Button, Table, Badge, Alert, Spinner, Form } from 'react-bootstrap';
import VersionDiffModal from './VersionDiffModal';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface PublishedVersion {
  trigger_id: string;
  version: number;
  is_active: boolean;
  published_at: string;
  published_by: string;
  apis: string[];
  prompts: Record<string, string>;
  model_settings: {
    selected_models: string[];
    temperature: number;
    max_tokens: number;
  };
  test_results_summary: Record<string, any>;
  notes?: string;
}

interface ConfigVersionHistoryModalProps {
  show: boolean;
  onHide: () => void;
  triggerName: string;
  onRollbackSuccess?: () => void;
}

const ConfigVersionHistoryModal: React.FC<ConfigVersionHistoryModalProps> = ({
  show,
  onHide,
  triggerName,
  onRollbackSuccess
}) => {
  const [versions, setVersions] = useState<PublishedVersion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersions, setSelectedVersions] = useState<[number | null, number | null]>([null, null]);
  const [showDiffModal, setShowDiffModal] = useState(false);
  const [rollbackingVersion, setRollbackingVersion] = useState<number | null>(null);

  useEffect(() => {
    if (show) {
      fetchVersions();
    }
  }, [show, triggerName]);

  const fetchVersions = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/triggers/${triggerName}/versions?limit=50`);

      if (!response.ok) {
        throw new Error('Failed to fetch versions');
      }

      const data = await response.json();
      setVersions(data.versions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVersionSelect = (version: number, position: 0 | 1) => {
    const newSelection: [number | null, number | null] = [...selectedVersions];
    newSelection[position] = version;
    setSelectedVersions(newSelection);
  };

  const handleCompareVersions = () => {
    if (selectedVersions[0] && selectedVersions[1]) {
      setShowDiffModal(true);
    }
  };

  const handleRollback = async (version: number) => {
    if (!confirm(`Are you sure you want to rollback to version ${version}? This will create a new version.`)) {
      return;
    }

    setRollbackingVersion(version);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/triggers/${triggerName}/versions/${version}/rollback`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            performed_by: 'user123' // TODO: Get from auth context
          })
        }
      );

      if (!response.ok) {
        throw new Error('Rollback failed');
      }

      const data = await response.json();
      alert(`Successfully rolled back to version ${version}! New version ${data.version} created.`);

      // Refresh versions
      await fetchVersions();

      if (onRollbackSuccess) {
        onRollbackSuccess();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rollback failed');
    } finally {
      setRollbackingVersion(null);
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString();
  };

  const canCompare = selectedVersions[0] !== null && selectedVersions[1] !== null;

  return (
    <>
      <Modal show={show} onHide={onHide} size="xl" fullscreen="lg-down">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-clock-history me-2"></i>
            Version History - {triggerName}
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
              <p className="mt-2">Loading version history...</p>
            </div>
          ) : versions.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              No published versions found for this trigger.
            </Alert>
          ) : (
            <>
              {/* Comparison Controls */}
              <div className="mb-3 d-flex align-items-center gap-2">
                <Form.Label className="mb-0"><strong>Compare Versions:</strong></Form.Label>
                <Form.Select
                  style={{ width: '120px' }}
                  value={selectedVersions[0] || ''}
                  onChange={(e) => handleVersionSelect(Number(e.target.value), 0)}
                >
                  <option value="">Select v1</option>
                  {versions.map((v) => (
                    <option key={v.version} value={v.version}>
                      v{v.version}
                    </option>
                  ))}
                </Form.Select>
                <span>vs</span>
                <Form.Select
                  style={{ width: '120px' }}
                  value={selectedVersions[1] || ''}
                  onChange={(e) => handleVersionSelect(Number(e.target.value), 1)}
                >
                  <option value="">Select v2</option>
                  {versions.map((v) => (
                    <option key={v.version} value={v.version}>
                      v{v.version}
                    </option>
                  ))}
                </Form.Select>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleCompareVersions}
                  disabled={!canCompare}
                >
                  <i className="bi bi-code-square me-1"></i>
                  Compare
                </Button>
              </div>

              {/* Versions Table */}
              <div style={{ overflowX: 'auto' }}>
                <Table striped bordered hover>
                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Status</th>
                      <th>Published</th>
                      <th>Publisher</th>
                      <th>Models</th>
                      <th>Notes</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.map((version) => (
                      <tr key={version.version} className={version.is_active ? 'table-success' : ''}>
                        <td>
                          <Badge bg="info">v{version.version}</Badge>
                        </td>
                        <td>
                          {version.is_active ? (
                            <Badge bg="success">
                              <i className="bi bi-check-circle me-1"></i>
                              Active
                            </Badge>
                          ) : (
                            <Badge bg="secondary">Inactive</Badge>
                          )}
                        </td>
                        <td>
                          <small>{formatTimestamp(version.published_at)}</small>
                        </td>
                        <td>
                          <code>{version.published_by}</code>
                        </td>
                        <td>
                          <small>
                            {version.model_settings.selected_models.join(', ')}
                          </small>
                        </td>
                        <td>
                          {version.notes ? (
                            <small>{version.notes}</small>
                          ) : (
                            <span className="text-muted">-</span>
                          )}
                        </td>
                        <td>
                          {!version.is_active && (
                            <Button
                              variant="warning"
                              size="sm"
                              onClick={() => handleRollback(version.version)}
                              disabled={rollbackingVersion === version.version}
                            >
                              {rollbackingVersion === version.version ? (
                                <>
                                  <span className="spinner-border spinner-border-sm me-1"></span>
                                  Rolling back...
                                </>
                              ) : (
                                <>
                                  <i className="bi bi-arrow-counterclockwise me-1"></i>
                                  Rollback
                                </>
                              )}
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Version Diff Modal */}
      {showDiffModal && selectedVersions[0] && selectedVersions[1] && (
        <VersionDiffModal
          show={showDiffModal}
          onHide={() => setShowDiffModal(false)}
          triggerName={triggerName}
          versionA={selectedVersions[0]}
          versionB={selectedVersions[1]}
        />
      )}
    </>
  );
};

export default ConfigVersionHistoryModal;
