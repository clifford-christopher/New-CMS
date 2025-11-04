/**
 * Dashboard Page - Trigger Management
 *
 * Displays a dropdown selector to choose a trigger for configuration.
 * Based on Figma DashboardV2 design with Quick Stats and Recent Activity.
 *
 * Story 1.4: Trigger Management Dashboard
 */

'use client';

import { useState, useEffect } from 'react';
import { Container, Row, Col, Form, Card, Badge, Button, Alert } from 'react-bootstrap';
import { useRouter } from 'next/navigation';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface Trigger {
  trigger_name: string;
  isActive: boolean;
  status: 'configured' | 'unconfigured';
  has_llm_config: boolean;
  has_data_config: boolean;
  has_prompts: boolean;
  version: number;
  updated_at: string | null;
  published_at: string | null;
  published_by: string | null;
  error?: string;
}

export default function DashboardPage() {
  const [triggers, setTriggers] = useState<Trigger[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTriggerName, setSelectedTriggerName] = useState<string>('');
  const router = useRouter();

  useEffect(() => {
    fetchTriggers();
  }, []);

  const fetchTriggers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/triggers/');

      if (!response.ok) {
        throw new Error(`Failed to fetch triggers: ${response.statusText}`);
      }

      const data = await response.json();
      setTriggers(data);
    } catch (err) {
      console.error('Error fetching triggers:', err);
      setError(err instanceof Error ? err.message : 'Failed to load triggers');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigure = () => {
    if (selectedTriggerName) {
      router.push(`/config/${selectedTriggerName}`);
    }
  };

  const getStatusBadge = (trigger: Trigger) => {
    if (trigger.isActive) {
      return <Badge bg="success">Configured</Badge>;
    }
    if (trigger.has_llm_config || trigger.has_data_config || trigger.has_prompts) {
      return <Badge bg="warning" text="dark">In Progress</Badge>;
    }
    return <Badge bg="secondary">Unconfigured</Badge>;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Invalid date';
    }
  };

  const configuredCount = triggers.filter(t => t.isActive).length;
  const inProgressCount = triggers.filter(t => !t.isActive && (t.has_llm_config || t.has_data_config || t.has_prompts)).length;
  const lastUpdated = triggers.length > 0 && triggers[0].updated_at
    ? formatDate(triggers[0].updated_at)
    : 'Never';

  // Loading state
  if (loading) {
    return (
      <Container className="py-5">
        <LoadingSpinner size="lg" message="Loading triggers..." />
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          <Alert.Heading>Error Loading Triggers</Alert.Heading>
          <p>{error}</p>
          <Button variant="primary" onClick={fetchTriggers}>
            Retry
          </Button>
        </Alert>
      </Container>
    );
  }

  // Empty state
  if (triggers.length === 0) {
    return (
      <Container className="py-5">
        <Alert variant="info">
          <Alert.Heading>No Triggers Found</Alert.Heading>
          <p>No triggers are currently available in the trigger_prompts collection.</p>
          <p className="mb-0">The database should have been seeded during Story 1.2 setup.</p>
        </Alert>
      </Container>
    );
  }

  // Main content
  return (
    <div className="min-h-screen bg-light">
      {/* Page Header */}
      <div className="px-4 px-md-5 py-5">
        <h1 className="mb-2">News Trigger Dashboard</h1>
        <p className="text-muted">Configure and manage AI-powered news generation triggers</p>
      </div>

      {/* Trigger Selector Section */}
      <div className="d-flex justify-content-center px-4 mb-5">
        <Card className="shadow-sm" style={{ maxWidth: '600px', width: '100%' }}>
          <Card.Body className="p-4">
            <h3 className="mb-4">Select Trigger to Configure</h3>

            <Form.Select
              size="lg"
              className="mb-4"
              value={selectedTriggerName}
              onChange={(e) => setSelectedTriggerName(e.target.value)}
            >
              <option value="">Choose a trigger...</option>
              {triggers.map((trigger) => (
                <option key={trigger.trigger_name} value={trigger.trigger_name}>
                  {trigger.trigger_name}
                </option>
              ))}
            </Form.Select>

            {selectedTriggerName && (
              <div className="mb-4 p-3 bg-light rounded">
                <div className="d-flex justify-content-between align-items-center">
                  <strong>{selectedTriggerName}</strong>
                  {getStatusBadge(triggers.find(t => t.trigger_name === selectedTriggerName)!)}
                </div>
              </div>
            )}

            <Button
              variant="primary"
              size="lg"
              className="w-100"
              disabled={!selectedTriggerName}
              onClick={handleConfigure}
            >
              Configure Selected Trigger
            </Button>
          </Card.Body>
        </Card>
      </div>

      {/* Quick Stats Section */}
      <div className="d-flex justify-content-center px-4 mb-5">
        <div className="w-100" style={{ maxWidth: '1200px' }}>
          <Row className="g-4">
            {/* Total Triggers Card */}
            <Col xs={12} md={4}>
              <Card className="shadow-sm">
                <Card.Body className="p-4">
                  <div className="d-flex align-items-center justify-content-center bg-primary bg-opacity-10 rounded-circle mb-3" style={{ width: '48px', height: '48px' }}>
                    <i className="bi bi-lightning-charge-fill text-primary fs-4"></i>
                  </div>
                  <div className="text-muted small mb-1">Total Triggers</div>
                  <div className="fs-1 fw-bold">{triggers.length}</div>
                </Card.Body>
              </Card>
            </Col>

            {/* Configured Card */}
            <Col xs={12} md={4}>
              <Card className="shadow-sm">
                <Card.Body className="p-4">
                  <div className="d-flex align-items-center justify-content-center bg-success bg-opacity-10 rounded-circle mb-3" style={{ width: '48px', height: '48px' }}>
                    <i className="bi bi-check-circle-fill text-success fs-4"></i>
                  </div>
                  <div className="text-muted small mb-1">Configured</div>
                  <div className="fs-1 fw-bold">{configuredCount}</div>
                </Card.Body>
              </Card>
            </Col>

            {/* Recent Activity Card */}
            <Col xs={12} md={4}>
              <Card className="shadow-sm">
                <Card.Body className="p-4">
                  <div className="d-flex align-items-center justify-content-center bg-warning bg-opacity-10 rounded-circle mb-3" style={{ width: '48px', height: '48px' }}>
                    <i className="bi bi-clock-fill text-warning fs-4"></i>
                  </div>
                  <div className="text-muted small mb-1">Last Updated</div>
                  <div className="fs-5 fw-bold">{lastUpdated}</div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </div>
      </div>

      {/* Recent Configuration Changes Section */}
      <div className="d-flex justify-content-center px-4 pb-5">
        <div className="w-100" style={{ maxWidth: '1200px' }}>
          <h4 className="mb-4">All Triggers</h4>

          <Card className="shadow-sm">
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead className="bg-light border-bottom">
                  <tr>
                    <th className="px-4 py-3 text-muted small">Trigger Name</th>
                    <th className="px-4 py-3 text-muted small">Status</th>
                    <th className="px-4 py-3 text-muted small">Version</th>
                    <th className="px-4 py-3 text-muted small">Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {triggers.map((trigger) => (
                    <tr key={trigger.trigger_name} className="border-bottom">
                      <td className="px-4 py-3">{trigger.trigger_name}</td>
                      <td className="px-4 py-3">{getStatusBadge(trigger)}</td>
                      <td className="px-4 py-3 text-muted small">v{trigger.version}</td>
                      <td className="px-4 py-3 text-muted small">{formatDate(trigger.updated_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
