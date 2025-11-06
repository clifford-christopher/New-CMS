/**
 * GenerationHistoryPanel Component
 * Story 4.6: Post-Generation Metadata Display
 *
 * Displays past test generations with:
 * - Filters (trigger, model, prompt type, date)
 * - Pagination
 * - "Load Configuration" to replay past tests
 * - "View Details" to expand results
 */

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Form, Row, Col, Badge, Alert, Spinner, Pagination } from 'react-bootstrap';
import { GenerationHistoryItem, GenerationHistoryFilters, PromptType } from '@/types/generation';
import { fetchGenerationHistory } from '@/services/generationService';

interface GenerationHistoryPanelProps {
  triggerId?: string;
  onLoadConfiguration?: (historyItem: GenerationHistoryItem) => void;
}

const GenerationHistoryPanel: React.FC<GenerationHistoryPanelProps> = ({
  triggerId,
  onLoadConfiguration
}) => {
  const [history, setHistory] = useState<GenerationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  // Filter state
  const [filters, setFilters] = useState<GenerationHistoryFilters>({
    trigger_name: triggerId || undefined,
    stock_id: undefined,
    prompt_type: undefined,
    provider: undefined,
    session_id: undefined,
    limit: 10,
    skip: 0
  });

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Expanded items (show full text)
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  /**
   * Load history on mount and filter changes
   */
  useEffect(() => {
    loadHistory();
  }, [filters]);

  /**
   * Load generation history from API
   */
  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetchGenerationHistory(filters);
      setHistory(response.items);
      setTotal(response.total);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load history';
      setError(errorMessage);
      console.error('Failed to load generation history:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle filter changes
   */
  const handleFilterChange = (key: keyof GenerationHistoryFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined, // Convert empty strings to undefined
      skip: 0 // Reset pagination when filters change
    }));
    setCurrentPage(1);
  };

  /**
   * Handle page change
   */
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    setFilters(prev => ({
      ...prev,
      skip: (page - 1) * pageSize
    }));
  };

  /**
   * Toggle expanded item
   */
  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  /**
   * Handle load configuration
   */
  const handleLoadConfiguration = (item: GenerationHistoryItem) => {
    if (onLoadConfiguration) {
      onLoadConfiguration(item);
    }
  };

  /**
   * Format cost
   */
  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(6)}`;
  };

  /**
   * Format latency
   */
  const formatLatency = (latency: number): string => {
    return `${latency.toFixed(2)}s`;
  };

  /**
   * Format timestamp
   */
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  /**
   * Truncate text
   */
  const truncateText = (text: string, maxLength: number = 100): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Calculate total pages
  const totalPages = Math.ceil(total / pageSize);

  return (
    <Card className="mt-4">
      <Card.Header>
        <div className="d-flex align-items-center justify-content-between">
          <h5 className="mb-0">
            <i className="bi bi-clock-history me-2"></i>
            Generation History
          </h5>
          <Badge bg="secondary">{total} total</Badge>
        </div>
      </Card.Header>

      <Card.Body>
        {/* Filters */}
        <div className="mb-3">
          <Row>
            <Col md={3}>
              <Form.Group>
                <Form.Label><small>Stock ID</small></Form.Label>
                <Form.Control
                  type="text"
                  size="sm"
                  placeholder="Filter by stock..."
                  value={filters.stock_id || ''}
                  onChange={(e) => handleFilterChange('stock_id', e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={2}>
              <Form.Group>
                <Form.Label><small>Prompt Type</small></Form.Label>
                <Form.Select
                  size="sm"
                  value={filters.prompt_type || ''}
                  onChange={(e) => handleFilterChange('prompt_type', e.target.value as PromptType)}
                >
                  <option value="">All</option>
                  <option value="paid">Paid</option>
                  <option value="unpaid">Unpaid</option>
                  <option value="crawler">Crawler</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={2}>
              <Form.Group>
                <Form.Label><small>Provider</small></Form.Label>
                <Form.Select
                  size="sm"
                  value={filters.provider || ''}
                  onChange={(e) => handleFilterChange('provider', e.target.value)}
                >
                  <option value="">All</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="gemini">Gemini</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label><small>Session ID</small></Form.Label>
                <Form.Control
                  type="text"
                  size="sm"
                  placeholder="Filter by session..."
                  value={filters.session_id || ''}
                  onChange={(e) => handleFilterChange('session_id', e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={2} className="d-flex align-items-end">
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={loadHistory}
                className="w-100"
              >
                <i className="bi bi-arrow-clockwise me-1"></i>
                Refresh
              </Button>
            </Col>
          </Row>
        </div>

        {/* Error Message */}
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
            <p className="mt-3 text-muted">Loading generation history...</p>
          </div>
        )}

        {/* No Results */}
        {!loading && history.length === 0 && (
          <Alert variant="info">
            <i className="bi bi-info-circle me-2"></i>
            No generation history found. Try adjusting your filters or generate some test articles first.
          </Alert>
        )}

        {/* History Table */}
        {!loading && history.length > 0 && (
          <>
            <div className="table-responsive">
              <Table hover size="sm">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Stock</th>
                    <th>Type</th>
                    <th>Model</th>
                    <th>Cost</th>
                    <th>Latency</th>
                    <th>Tokens</th>
                    <th>Preview</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <React.Fragment key={item.id}>
                      <tr>
                        <td>
                          <small className="text-muted">
                            {formatTimestamp(item.timestamp)}
                          </small>
                        </td>
                        <td>
                          <Badge bg="light" text="dark">{item.stock_id}</Badge>
                        </td>
                        <td>
                          <Badge bg="secondary">{item.prompt_type}</Badge>
                        </td>
                        <td>
                          <small>
                            {item.model_name}
                            <br />
                            <span className="text-muted">({item.provider})</span>
                          </small>
                        </td>
                        <td>
                          <small className="text-success">{formatCost(item.cost)}</small>
                        </td>
                        <td>
                          <small className="text-primary">{formatLatency(item.latency)}</small>
                        </td>
                        <td>
                          <small>
                            {item.input_tokens} / {item.output_tokens}
                          </small>
                        </td>
                        <td style={{ maxWidth: '300px' }}>
                          <small className="text-muted">
                            {expandedItems.has(item.id)
                              ? item.generated_text
                              : truncateText(item.generated_text, 80)}
                          </small>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => toggleExpanded(item.id)}
                              title={expandedItems.has(item.id) ? 'Collapse' : 'Expand'}
                            >
                              <i className={`bi bi-chevron-${expandedItems.has(item.id) ? 'up' : 'down'}`}></i>
                            </Button>
                            <Button
                              variant="outline-secondary"
                              size="sm"
                              onClick={() => handleLoadConfiguration(item)}
                              title="Load this configuration"
                            >
                              <i className="bi bi-arrow-repeat"></i>
                            </Button>
                          </div>
                        </td>
                      </tr>
                      {/* Expanded Row */}
                      {expandedItems.has(item.id) && (
                        <tr>
                          <td colSpan={9} style={{ background: '#f8f9fa' }}>
                            <div className="p-3">
                              <h6>Full Generated Text:</h6>
                              <p style={{ whiteSpace: 'pre-wrap' }}>{item.generated_text}</p>
                              <hr />
                              <Row>
                                <Col md={6}>
                                  <small>
                                    <strong>Temperature:</strong> {item.temperature}<br />
                                    <strong>Max Tokens:</strong> {item.max_tokens}<br />
                                    <strong>Finish Reason:</strong> {item.finish_reason}
                                  </small>
                                </Col>
                                <Col md={6}>
                                  <small>
                                    <strong>Trigger:</strong> {item.trigger_name}<br />
                                    {item.session_id && (
                                      <>
                                        <strong>Session ID:</strong> {item.session_id}
                                      </>
                                    )}
                                  </small>
                                </Col>
                              </Row>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </Table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="d-flex justify-content-center mt-3">
                <Pagination size="sm">
                  <Pagination.First
                    onClick={() => handlePageChange(1)}
                    disabled={currentPage === 1}
                  />
                  <Pagination.Prev
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  />

                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    const page = i + 1;
                    return (
                      <Pagination.Item
                        key={page}
                        active={page === currentPage}
                        onClick={() => handlePageChange(page)}
                      >
                        {page}
                      </Pagination.Item>
                    );
                  })}

                  {totalPages > 5 && (
                    <>
                      <Pagination.Ellipsis disabled />
                      <Pagination.Item onClick={() => handlePageChange(totalPages)}>
                        {totalPages}
                      </Pagination.Item>
                    </>
                  )}

                  <Pagination.Next
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  />
                  <Pagination.Last
                    onClick={() => handlePageChange(totalPages)}
                    disabled={currentPage === totalPages}
                  />
                </Pagination>
              </div>
            )}

            {/* Summary */}
            <div className="mt-3 text-center">
              <small className="text-muted">
                Showing {history.length} of {total} generations (Page {currentPage} of {totalPages})
              </small>
            </div>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default GenerationHistoryPanel;
