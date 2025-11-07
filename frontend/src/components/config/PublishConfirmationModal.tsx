/**
 * PublishConfirmationModal Component
 * Story 5.2: Configuration Publishing with Confirmation
 *
 * Final confirmation modal before publishing configuration to production
 */

import React, { useState } from 'react';
import { Modal, Button, Alert, Card, Badge, Table, Form } from 'react-bootstrap';
import { TestMetadata } from '@/services/validationService';

interface PublishConfirmationModalProps {
  show: boolean;
  onHide: () => void;
  triggerName: string;
  configuration: {
    apis: string[];
    section_order: string[];
    prompts: Record<string, string>;
    model_settings: {
      selected_models: string[];
      temperature: number;
      max_tokens: number;
    };
  };
  testResults: Record<string, TestMetadata>; // Test results by prompt type
  onConfirm: (publishData: PublishData) => void;
  isPublishing: boolean;
}

export interface PublishData {
  apis: string[];
  section_order: string[];
  prompts: Record<string, string>;
  model_settings: {
    selected_models: string[];
    temperature: number;
    max_tokens: number;
  };
  test_results_summary: Record<string, {
    models_tested: string[];
    avg_cost: number;
    avg_latency: number;
    total_tests: number;
    sample_output_preview?: string;
  }>;
  published_by: string;
  notes?: string;
}

const PublishConfirmationModal: React.FC<PublishConfirmationModalProps> = ({
  show,
  onHide,
  triggerName,
  configuration,
  testResults,
  onConfirm,
  isPublishing
}) => {
  const [publishNotes, setPublishNotes] = useState('');
  const [understood, setUnderstood] = useState(false);

  const handlePublish = () => {
    // Prepare test results summary
    const test_results_summary: Record<string, {
      models_tested: string[];
      avg_cost: number;
      avg_latency: number;
      total_tests: number;
      sample_output_preview?: string;
    }> = {};

    Object.entries(testResults).forEach(([promptType, metadata]) => {
      test_results_summary[promptType] = {
        models_tested: metadata.models_tested,
        avg_cost: metadata.avg_cost,
        avg_latency: metadata.avg_latency,
        total_tests: metadata.total_tests,
        sample_output_preview: metadata.sample_output?.substring(0, 200)
      };
    });

    // Prepare publish data
    const publishData: PublishData = {
      apis: configuration.apis,
      section_order: configuration.section_order,
      prompts: configuration.prompts,
      model_settings: configuration.model_settings,
      test_results_summary,
      published_by: 'user123', // TODO: Get from auth context
      notes: publishNotes.trim() || undefined
    };

    onConfirm(publishData);
  };

  const promptTypeLabels: Record<string, string> = {
    paid: 'Paid',
    unpaid: 'Unpaid',
    crawler: 'Crawler'
  };

  // Calculate total cost across all prompt types
  const totalCost = Object.values(testResults).reduce((sum, metadata) =>
    sum + (metadata.total_cost || metadata.avg_cost * metadata.total_tests), 0
  );

  return (
    <Modal show={show} onHide={onHide} size="lg" backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="bi bi-upload me-2"></i>
          Confirm Publishing to Production
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {/* Warning Banner */}
        <Alert variant="warning" className="mb-4">
          <div className="d-flex">
            <i className="bi bi-exclamation-triangle-fill me-2" style={{ fontSize: '24px' }}></i>
            <div>
              <h6 className="mb-2">You are about to publish configuration to production</h6>
              <ul className="mb-0">
                <li>This will affect live article generation for trigger: <strong>{triggerName}</strong></li>
                <li>A new version will be created and marked as active</li>
                <li>Previous configurations will be deactivated but retained in history</li>
              </ul>
            </div>
          </div>
        </Alert>

        {/* Configuration Summary */}
        <Card className="mb-3">
          <Card.Header className="bg-light">
            <strong>Configuration Summary</strong>
          </Card.Header>
          <Card.Body>
            <div className="row g-3">
              <div className="col-md-6">
                <div className="mb-2">
                  <small className="text-muted">APIs Configured:</small>
                  <div>
                    {configuration.apis.map((api, idx) => (
                      <Badge key={idx} bg="info" className="me-1">{api}</Badge>
                    ))}
                  </div>
                </div>
                <div className="mb-2">
                  <small className="text-muted">Section Order:</small>
                  <div>
                    {configuration.section_order.map((section, idx) => (
                      <Badge key={idx} bg="secondary" className="me-1">{section}</Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="mb-2">
                  <small className="text-muted">Models Selected:</small>
                  <div>
                    {configuration.model_settings.selected_models.map((model, idx) => (
                      <Badge key={idx} bg="success" className="me-1">{model}</Badge>
                    ))}
                  </div>
                </div>
                <div className="mb-2">
                  <small className="text-muted">Temperature:</small>
                  <strong className="ms-2">{configuration.model_settings.temperature}</strong>
                </div>
                <div>
                  <small className="text-muted">Max Tokens:</small>
                  <strong className="ms-2">{configuration.model_settings.max_tokens}</strong>
                </div>
              </div>
            </div>
          </Card.Body>
        </Card>

        {/* Test Results Summary */}
        <Card className="mb-3">
          <Card.Header className="bg-light d-flex justify-content-between align-items-center">
            <strong>Test Results Summary</strong>
            <Badge bg="primary">Total Cost: ${totalCost.toFixed(4)}</Badge>
          </Card.Header>
          <Card.Body>
            {Object.entries(testResults).map(([promptType, metadata]) => (
              <div key={promptType} className="mb-3 pb-3 border-bottom last:border-0">
                <h6 className="mb-2">
                  {promptTypeLabels[promptType] || promptType} Prompt Type
                </h6>
                <Table size="sm" bordered className="mb-0">
                  <tbody>
                    <tr>
                      <td className="bg-light" style={{ width: '40%' }}>
                        <i className="bi bi-cpu me-1"></i>
                        <strong>Models Tested</strong>
                      </td>
                      <td>
                        {metadata.models_tested.map((model, idx) => (
                          <Badge key={idx} bg="secondary" className="me-1">{model}</Badge>
                        ))}
                      </td>
                    </tr>
                    <tr>
                      <td className="bg-light">
                        <i className="bi bi-check-circle me-1"></i>
                        <strong>Total Tests</strong>
                      </td>
                      <td>{metadata.total_tests}</td>
                    </tr>
                    <tr>
                      <td className="bg-light">
                        <i className="bi bi-coin me-1"></i>
                        <strong>Average Cost</strong>
                      </td>
                      <td>
                        ${metadata.avg_cost.toFixed(4)}
                        {metadata.avg_cost > 0.50 && (
                          <Badge bg="warning" className="ms-2">High Cost</Badge>
                        )}
                      </td>
                    </tr>
                    <tr>
                      <td className="bg-light">
                        <i className="bi bi-clock me-1"></i>
                        <strong>Average Latency</strong>
                      </td>
                      <td>
                        {metadata.avg_latency.toFixed(2)}s
                        {metadata.avg_latency > 30 && (
                          <Badge bg="warning" className="ms-2">Slow</Badge>
                        )}
                      </td>
                    </tr>
                    {metadata.sample_output && (
                      <tr>
                        <td className="bg-light">
                          <i className="bi bi-file-text me-1"></i>
                          <strong>Sample Output</strong>
                        </td>
                        <td>
                          <small className="text-muted" style={{ fontStyle: 'italic' }}>
                            {metadata.sample_output.substring(0, 100)}...
                          </small>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </Table>
              </div>
            ))}
          </Card.Body>
        </Card>

        {/* Publishing Notes */}
        <Form.Group className="mb-3">
          <Form.Label>
            <strong>Publishing Notes</strong> (Optional)
          </Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            placeholder="Add notes about this publish (e.g., 'Updated prompts for better accuracy', 'Changed model to reduce cost')..."
            value={publishNotes}
            onChange={(e) => setPublishNotes(e.target.value)}
            disabled={isPublishing}
          />
          <Form.Text className="text-muted">
            These notes will be saved in the audit log for future reference
          </Form.Text>
        </Form.Group>

        {/* Confirmation Checkbox */}
        <Form.Check
          type="checkbox"
          id="publish-confirmation"
          label={<strong>I understand this will publish configuration to production</strong>}
          checked={understood}
          onChange={(e) => setUnderstood(e.target.checked)}
          disabled={isPublishing}
          className="mb-3"
        />

        {/* Publishing Info */}
        <Alert variant="info" className="mb-0">
          <small>
            <i className="bi bi-info-circle me-2"></i>
            <strong>What happens next:</strong>
            <ul className="mb-0 mt-2">
              <li>A new version will be created with auto-incremented version number</li>
              <li>This version will be marked as active and used for production generation</li>
              <li>You can rollback to previous versions from the version history page</li>
            </ul>
          </small>
        </Alert>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={isPublishing}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handlePublish}
          disabled={!understood || isPublishing}
        >
          {isPublishing ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Publishing...
            </>
          ) : (
            <>
              <i className="bi bi-upload me-2"></i>
              Publish to Production
            </>
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default PublishConfirmationModal;
