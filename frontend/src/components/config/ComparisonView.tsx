/**
 * ComparisonView Component
 * Side-by-side comparison of model outputs for test results
 *
 * Features:
 * - Groups results by prompt type (Paid, Unpaid, Crawler)
 * - Displays results in side-by-side columns for each model
 * - Highlights best performers (lowest cost, fastest latency)
 * - Auto-populates with last generated test data
 */

import React, { useState, useMemo } from 'react';
import { Card, Nav, Row, Col, Badge, Button, Alert, Spinner } from 'react-bootstrap';
import { GenerationResult, PromptType } from '../../types/generation';
import { useGeneration } from '../../contexts/GenerationContext';
import VersionDropdown, { VersionOption } from './VersionDropdown';

interface ComparisonViewProps {
  results: GenerationResult[];
  triggerName: string;
  onNavigateToTesting: () => void;
  isLoading?: boolean;
}

interface GroupedResults {
  paid: GenerationResult[];
  unpaid: GenerationResult[];
  crawler: GenerationResult[];
}

const ComparisonView: React.FC<ComparisonViewProps> = ({
  results,
  triggerName,
  onNavigateToTesting,
  isLoading = false
}) => {
  const [activeTab, setActiveTab] = useState<PromptType>('paid');

  // Access version tracking from GenerationContext
  const { resultVersions, historyLoading } = useGeneration();

  // Build version dropdown options (same logic as TestGenerationPanel)
  const versionOptions: VersionOption[] = [];

  resultVersions.forEach((versions, key) => {
    versions.forEach((version, index) => {
      const [modelId, promptType] = key.split('-');
      versionOptions.push({
        key: `${key}-v${version.version}`,
        label: `v${version.version} - ${version.result.response.model_name} (${promptType}) - ${new Date(version.timestamp).toLocaleString()}`,
        modelId,
        promptType: promptType as PromptType,
        versionIndex: index,
        version: version.version,
        timestamp: version.timestamp
      });
    });
  });

  // Sort by timestamp (newest first)
  versionOptions.sort((a, b) =>
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  // Group results by prompt type
  const groupedResults = useMemo((): GroupedResults => {
    const groups: GroupedResults = {
      paid: [],
      unpaid: [],
      crawler: []
    };

    results.forEach(result => {
      if (result.status === 'completed' && result.response) {
        groups[result.prompt_type].push(result);
      }
    });

    return groups;
  }, [results]);

  // Get results for active tab
  const activeResults = groupedResults[activeTab];

  // Calculate best performers for active tab
  const bestPerformers = useMemo(() => {
    if (activeResults.length === 0) return { lowestCost: null, fastestLatency: null };

    const lowestCost = activeResults.reduce((min, result) =>
      result.response.cost < min.response.cost ? result : min
    );

    const fastestLatency = activeResults.reduce((min, result) =>
      result.response.latency < min.response.latency ? result : min
    );

    return {
      lowestCost: lowestCost.model_id,
      fastestLatency: fastestLatency.model_id
    };
  }, [activeResults]);

  // Format cost
  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(4)}`;
  };

  // Format latency
  const formatLatency = (latency: number): string => {
    return `${latency.toFixed(2)}s`;
  };

  // Copy to clipboard
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    // TODO: Add toast notification
  };

  // Get tab counts
  const getTabCount = (promptType: PromptType): number => {
    return groupedResults[promptType].length;
  };

  // Get tab variant
  const getTabVariant = (promptType: PromptType): string => {
    switch (promptType) {
      case 'paid': return 'primary';
      case 'unpaid': return 'success';
      case 'crawler': return 'warning';
      default: return 'secondary';
    }
  };

  // Empty state
  if (!isLoading && results.length === 0) {
    return (
      <Card className="mt-3">
        <Card.Body className="text-center py-5">
          <i className="bi bi-columns-gap" style={{ fontSize: '48px', color: '#6c757d' }}></i>
          <h4 className="mt-3">No Test Results Available</h4>
          <p className="text-muted">
            Please generate test articles in the "Model Testing" step first.
          </p>
          <Button variant="primary" onClick={onNavigateToTesting}>
            <i className="bi bi-arrow-left me-2"></i>
            Go to Testing
          </Button>
        </Card.Body>
      </Card>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <Card className="mt-3">
        <Card.Body className="text-center py-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading test results...</p>
        </Card.Body>
      </Card>
    );
  }

  return (
    <div className="mt-3">
      {/* Version History Dropdown */}
      <VersionDropdown
        versionOptions={versionOptions}
        resultVersions={resultVersions}
        isLoading={historyLoading}
      />

      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4>
            <i className="bi bi-columns-gap me-2"></i>
            Results & Comparison
          </h4>
          <p className="text-muted mb-0">
            Compare test results across different models
          </p>
        </div>
        <div>
          <small className="text-muted">
            <i className="bi bi-clock me-1"></i>
            {results.length} result{results.length !== 1 ? 's' : ''} available
          </small>
        </div>
      </div>

      {/* Prompt Type Tabs */}
      <Card className="mb-3">
        <Card.Header>
          <Nav variant="tabs" className="card-header-tabs">
            <Nav.Item>
              <Nav.Link
                active={activeTab === 'paid'}
                onClick={() => setActiveTab('paid')}
                style={{ cursor: 'pointer' }}
              >
                <i className="bi bi-cash-coin me-2"></i>
                Paid News
                {getTabCount('paid') > 0 && (
                  <Badge bg={getTabVariant('paid')} className="ms-2">
                    {getTabCount('paid')}
                  </Badge>
                )}
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link
                active={activeTab === 'unpaid'}
                onClick={() => setActiveTab('unpaid')}
                style={{ cursor: 'pointer' }}
              >
                <i className="bi bi-newspaper me-2"></i>
                Unpaid News
                {getTabCount('unpaid') > 0 && (
                  <Badge bg={getTabVariant('unpaid')} className="ms-2">
                    {getTabCount('unpaid')}
                  </Badge>
                )}
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link
                active={activeTab === 'crawler'}
                onClick={() => setActiveTab('crawler')}
                style={{ cursor: 'pointer' }}
              >
                <i className="bi bi-globe me-2"></i>
                Web Crawler
                {getTabCount('crawler') > 0 && (
                  <Badge bg={getTabVariant('crawler')} className="ms-2">
                    {getTabCount('crawler')}
                  </Badge>
                )}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>

        <Card.Body>
          {/* No results for selected tab */}
          {activeResults.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              No test results available for {activeTab} news. Generate tests in the Model Testing step.
            </Alert>
          ) : (
            <>
              {/* Comparison Grid */}
              <Row>
                {activeResults.map((result, index) => (
                  <Col key={index} md={12 / Math.min(activeResults.length, 3)} className="mb-3">
                    <Card className="h-100" style={{ borderColor: bestPerformers.lowestCost === result.model_id || bestPerformers.fastestLatency === result.model_id ? '#198754' : '#dee2e6' }}>
                      {/* Model Header */}
                      <Card.Header className="d-flex justify-content-between align-items-center">
                        <strong>{result.response.model_name}</strong>
                        <small className="text-muted">{result.response.provider}</small>
                      </Card.Header>

                      <Card.Body>
                        {/* Generated Text Preview */}
                        <div
                          style={{
                            maxHeight: '200px',
                            overflowY: 'auto',
                            backgroundColor: '#f8f9fa',
                            padding: '12px',
                            borderRadius: '4px',
                            marginBottom: '12px',
                            fontSize: '14px',
                            lineHeight: '1.5'
                          }}
                        >
                          {result.response.generated_text.substring(0, 500)}
                          {result.response.generated_text.length > 500 && '...'}
                        </div>

                        {/* Metrics */}
                        <div className="d-flex flex-column gap-2">
                          {/* Cost */}
                          <div className="d-flex justify-content-between align-items-center">
                            <span>
                              <i className="bi bi-cash me-2" style={{ color: '#6c757d' }}></i>
                              Cost
                            </span>
                            <strong>
                              {formatCost(result.response.cost)}
                              {bestPerformers.lowestCost === result.model_id && (
                                <i className="bi bi-star-fill ms-2" style={{ color: '#ffc107' }} title="Lowest Cost"></i>
                              )}
                            </strong>
                          </div>

                          {/* Latency */}
                          <div className="d-flex justify-content-between align-items-center">
                            <span>
                              <i className="bi bi-clock me-2" style={{ color: '#6c757d' }}></i>
                              Latency
                            </span>
                            <strong>
                              {formatLatency(result.response.latency)}
                              {bestPerformers.fastestLatency === result.model_id && (
                                <i className="bi bi-lightning-fill ms-2" style={{ color: '#0dcaf0' }} title="Fastest"></i>
                              )}
                            </strong>
                          </div>

                          {/* Tokens */}
                          <div className="d-flex justify-content-between align-items-center">
                            <span>
                              <i className="bi bi-hash me-2" style={{ color: '#6c757d' }}></i>
                              Tokens
                            </span>
                            <strong>{result.response.total_tokens.toLocaleString()}</strong>
                          </div>

                          {/* Timestamp */}
                          <div className="d-flex justify-content-between align-items-center">
                            <span>
                              <i className="bi bi-calendar me-2" style={{ color: '#6c757d' }}></i>
                              Generated
                            </span>
                            <small className="text-muted">
                              {new Date(result.response.timestamp).toLocaleTimeString()}
                            </small>
                          </div>
                        </div>
                      </Card.Body>

                      {/* Actions */}
                      <Card.Footer>
                        <div className="d-grid gap-2">
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            onClick={() => handleCopy(result.response.generated_text)}
                          >
                            <i className="bi bi-clipboard me-2"></i>
                            Copy Text
                          </Button>
                        </div>
                      </Card.Footer>
                    </Card>
                  </Col>
                ))}
              </Row>

              {/* Summary Stats */}
              <Card className="mt-3" style={{ backgroundColor: '#f8f9fa' }}>
                <Card.Body>
                  <Row>
                    <Col md={4} className="text-center">
                      <div>
                        <strong>Total Cost</strong>
                        <div className="h5 mb-0 mt-1">
                          {formatCost(activeResults.reduce((sum, r) => sum + r.response.cost, 0))}
                        </div>
                      </div>
                    </Col>
                    <Col md={4} className="text-center border-start border-end">
                      <div>
                        <strong>Avg Latency</strong>
                        <div className="h5 mb-0 mt-1">
                          {formatLatency(activeResults.reduce((sum, r) => sum + r.response.latency, 0) / activeResults.length)}
                        </div>
                      </div>
                    </Col>
                    <Col md={4} className="text-center">
                      <div>
                        <strong>Total Tokens</strong>
                        <div className="h5 mb-0 mt-1">
                          {activeResults.reduce((sum, r) => sum + r.response.total_tokens, 0).toLocaleString()}
                        </div>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ComparisonView;
