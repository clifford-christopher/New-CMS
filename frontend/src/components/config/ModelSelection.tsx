/**
 * ModelSelection Component
 * Story 4.2: Model Selection Interface
 *
 * Main component for LLM model selection:
 * - Displays available models grouped by provider
 * - Temperature slider (0.0 - 1.0)
 * - Max tokens input (50 - 4000)
 * - Real-time cost estimation
 * - Save configuration button
 * - "Used for All Types" badge
 */

import React, { useState } from 'react';
import { Card, Row, Col, Form, Button, Alert, Spinner, Accordion } from 'react-bootstrap';
import { useModel } from '@/contexts/ModelContext';
import ModelCard from './ModelCard';
import CostEstimator from './CostEstimator';

const ModelSelection: React.FC = () => {
  const {
    availableModels,
    modelsLoading,
    modelsError,
    selectedModels,
    temperature,
    maxTokens,
    costEstimate,
    isSaving,
    saveError,
    setTemperature,
    setMaxTokens,
    toggleModel,
    saveModelConfig,
    isModelSelected
  } = useModel();

  const [showSuccessMessage, setShowSuccessMessage] = useState(false);

  // Group models by provider
  const modelsByProvider = {
    openai: availableModels.filter((m) => m.provider === 'openai'),
    anthropic: availableModels.filter((m) => m.provider === 'anthropic'),
    gemini: availableModels.filter((m) => m.provider === 'gemini')
  };

  const providerNames = {
    openai: 'OpenAI',
    anthropic: 'Anthropic',
    gemini: 'Google Gemini'
  };

  const handleSave = async () => {
    try {
      await saveModelConfig();
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 3000);
    } catch (error) {
      // Error handled by context
    }
  };

  const handleTemperatureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    if (!isNaN(value)) {
      setTemperature(value);
    }
  };

  const handleMaxTokensChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value)) {
      setMaxTokens(value);
    }
  };

  if (modelsLoading) {
    return (
      <Card>
        <Card.Body className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3 text-muted">Loading available models...</p>
        </Card.Body>
      </Card>
    );
  }

  if (modelsError) {
    return (
      <Alert variant="danger">
        <i className="bi bi-exclamation-triangle me-2"></i>
        {modelsError}
      </Alert>
    );
  }

  return (
    <div className="model-selection">
      {/* Header */}
      <Card className="mb-3">
        <Card.Header>
          <div className="d-flex align-items-center justify-content-between">
            <h5 className="mb-0">
              <i className="bi bi-cpu me-2"></i>
              LLM Model Selection
            </h5>
            <span className="badge bg-info">
              <i className="bi bi-info-circle me-1"></i>
              Used for All Types
            </span>
          </div>
        </Card.Header>
        <Card.Body>
          <Alert variant="info" className="mb-0">
            <small>
              <i className="bi bi-lightbulb me-2"></i>
              <strong>Tip:</strong> Model selection applies to all prompt types (paid, unpaid, crawler).
              Select multiple models to compare results side-by-side.
            </small>
          </Alert>
        </Card.Body>
      </Card>

      {/* Success Message */}
      {showSuccessMessage && (
        <Alert variant="success" dismissible onClose={() => setShowSuccessMessage(false)}>
          <i className="bi bi-check-circle me-2"></i>
          Model configuration saved successfully!
        </Alert>
      )}

      {/* Error Message */}
      {saveError && (
        <Alert variant="danger" dismissible>
          <i className="bi bi-exclamation-triangle me-2"></i>
          {saveError}
        </Alert>
      )}

      <Row>
        {/* Left Column: Model Selection */}
        <Col lg={8}>
          <Card className="mb-3">
            <Card.Header>
              <h6 className="mb-0">Select Models ({selectedModels.length} selected)</h6>
            </Card.Header>
            <Card.Body>
              {selectedModels.length === 0 && (
                <Alert variant="warning">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  Please select at least one model to enable generation.
                </Alert>
              )}

              <Accordion defaultActiveKey={['0', '1', '2']} alwaysOpen>
                {Object.entries(modelsByProvider).map(([provider, models], index) => (
                  <Accordion.Item eventKey={index.toString()} key={provider}>
                    <Accordion.Header>
                      <strong>{providerNames[provider as keyof typeof providerNames]}</strong>
                      <span className="ms-2 text-muted">
                        ({models.filter((m) => isModelSelected(m.model_id)).length}/{models.length} selected)
                      </span>
                    </Accordion.Header>
                    <Accordion.Body>
                      <div className="d-flex flex-column gap-2">
                        {models.map((model) => (
                          <ModelCard
                            key={model.model_id}
                            model={model}
                            isSelected={isModelSelected(model.model_id)}
                            onToggle={toggleModel}
                          />
                        ))}
                      </div>
                    </Accordion.Body>
                  </Accordion.Item>
                ))}
              </Accordion>
            </Card.Body>
          </Card>

          {/* Generation Parameters */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">
                <i className="bi bi-sliders me-2"></i>
                Generation Parameters
              </h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      Temperature: <strong>{temperature.toFixed(2)}</strong>
                      <i
                        className="bi bi-question-circle ms-2 text-muted"
                        title="Controls randomness: 0.0 = deterministic, 1.0 = very creative"
                      />
                    </Form.Label>
                    <Form.Range
                      min="0"
                      max="1"
                      step="0.05"
                      value={temperature}
                      onChange={handleTemperatureChange}
                    />
                    <Form.Text className="text-muted">
                      0.0 = deterministic, 1.0 = very creative
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      Max Tokens
                      <i
                        className="bi bi-question-circle ms-2 text-muted"
                        title="Maximum number of tokens to generate (roughly 0.75 words per token)"
                      />
                    </Form.Label>
                    <Form.Control
                      type="number"
                      min="50"
                      max="4000"
                      step="50"
                      value={maxTokens}
                      onChange={handleMaxTokensChange}
                    />
                    <Form.Text className="text-muted">
                      Range: 50-4000 (≈ {Math.floor(maxTokens * 0.75)} words)
                    </Form.Text>
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* Right Column: Cost Estimation */}
        <Col lg={4}>
          <div className="sticky-top" style={{ top: '20px' }}>
            <CostEstimator costEstimate={costEstimate} />

            {/* Save Button */}
            <div className="d-grid gap-2 mt-3">
              <Button
                variant="primary"
                size="lg"
                onClick={handleSave}
                disabled={isSaving || selectedModels.length === 0}
              >
                {isSaving ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <i className="bi bi-save me-2"></i>
                    Save Model Configuration
                  </>
                )}
              </Button>
            </div>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default ModelSelection;
