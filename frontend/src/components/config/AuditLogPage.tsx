/**
 * AuditLogPage Component
 * Story 5.3: Audit Log for Publishing History
 *
 * Display audit trail of all publishing events for a trigger
 */

import React, { useState, useEffect } from 'react';
import { Container, Card, Table, Badge, Alert, Spinner, Form, Row, Col, Button } from 'react-bootstrap';
import { useParams } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AuditLog {
  trigger_id: string;
  action: string;
  performed_by: string;
  timestamp: string;
  version?: number;
  previous_version?: number;
  notes?: string;
  metadata: Record<string, any>;
  success: boolean;
  error_message?: string;
}

interface AuditStats {
  total_publishes: number;
  total_rollbacks: number;
  total_actions: number;
  last_publish?: string;
  unique_publishers: number;
  success_rate: number;
}

const AuditLogPage: React.FC = () => {
  const params = useParams();
  const triggerName = params?.trigger as string;

  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [actionFilter, setActionFilter] = useState<string>('');
  const [performedByFilter, setPerformedByFilter] = useState<string>('');

  useEffect(() => {
    if (triggerName) {
      fetchAuditData();
    }
  }, [triggerName, actionFilter, performedByFilter]);

  const fetchAuditData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch logs
      const logsParams = new URLSearchParams();
      if (actionFilter) logsParams.append('action', actionFilter);
      if (performedByFilter) logsParams.append('performed_by', performedByFilter);
      logsParams.append('limit', '100');

      const logsResponse = await fetch(
        `${API_BASE_URL}/api/triggers/${triggerName}/audit-logs?${logsParams.toString()}`
      );

      if (!logsResponse.ok) {
        throw new Error('Failed to fetch audit logs');
      }

      const logsData = await logsResponse.json();
      setLogs(logsData.logs || []);

      // Fetch stats
      const statsResponse = await fetch(`${API_BASE_URL}/api/triggers/${triggerName}/audit-stats`);

      if (!statsResponse.ok) {
        throw new Error('Failed to fetch audit stats');
      }

      const statsData = await statsResponse.json();
      setStats(statsData.stats || null);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetFilters = () => {
    setActionFilter('');
    setPerformedByFilter('');
  };

  const getActionBadgeVariant = (action: string): string => {
    switch (action) {
      case 'publish':
        return 'success';
      case 'rollback':
        return 'warning';
      case 'deactivate':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString();
  };

  const formatSuccessRate = (rate: number): string => {
    return `${rate.toFixed(1)}%`;
  };

  if (isLoading && logs.length === 0) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading audit logs...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>
            <i className="bi bi-clock-history me-2"></i>
            Audit Log
          </h2>
          <p className="text-muted mb-0">Publishing history for trigger: <strong>{triggerName}</strong></p>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="mb-0">{stats.total_publishes}</h3>
                <small className="text-muted">Total Publishes</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="mb-0">{stats.total_rollbacks}</h3>
                <small className="text-muted">Total Rollbacks</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="mb-0">{stats.unique_publishers}</h3>
                <small className="text-muted">Unique Publishers</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h3 className="mb-0">{formatSuccessRate(stats.success_rate)}</h3>
                <small className="text-muted">Success Rate</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={4}>
              <Form.Group>
                <Form.Label><strong>Filter by Action</strong></Form.Label>
                <Form.Select
                  value={actionFilter}
                  onChange={(e) => setActionFilter(e.target.value)}
                >
                  <option value="">All Actions</option>
                  <option value="publish">Publish</option>
                  <option value="rollback">Rollback</option>
                  <option value="deactivate">Deactivate</option>
                  <option value="update">Update</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label><strong>Filter by User</strong></Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Enter user ID..."
                  value={performedByFilter}
                  onChange={(e) => setPerformedByFilter(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={4} className="d-flex align-items-end">
              <Button variant="secondary" onClick={handleResetFilters}>
                <i className="bi bi-x-circle me-1"></i>
                Reset Filters
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Audit Log Table */}
      <Card>
        <Card.Header>
          <strong>Audit Trail ({logs.length} entries)</strong>
        </Card.Header>
        <Card.Body>
          {logs.length === 0 ? (
            <Alert variant="info" className="mb-0">
              <i className="bi bi-info-circle me-2"></i>
              No audit logs found for this trigger.
            </Alert>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Action</th>
                    <th>Version</th>
                    <th>Performed By</th>
                    <th>Notes</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, idx) => (
                    <tr key={idx}>
                      <td style={{ whiteSpace: 'nowrap' }}>
                        <small>{formatTimestamp(log.timestamp)}</small>
                      </td>
                      <td>
                        <Badge bg={getActionBadgeVariant(log.action)}>
                          {log.action}
                        </Badge>
                      </td>
                      <td>
                        {log.version && (
                          <div>
                            <Badge bg="info">v{log.version}</Badge>
                            {log.previous_version && (
                              <small className="text-muted d-block mt-1">
                                (from v{log.previous_version})
                              </small>
                            )}
                          </div>
                        )}
                      </td>
                      <td>
                        <code>{log.performed_by}</code>
                      </td>
                      <td>
                        {log.notes ? (
                          <small>{log.notes}</small>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        {log.success ? (
                          <Badge bg="success">
                            <i className="bi bi-check-circle me-1"></i>
                            Success
                          </Badge>
                        ) : (
                          <div>
                            <Badge bg="danger">
                              <i className="bi bi-x-circle me-1"></i>
                              Failed
                            </Badge>
                            {log.error_message && (
                              <small className="text-danger d-block mt-1">
                                {log.error_message}
                              </small>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default AuditLogPage;
