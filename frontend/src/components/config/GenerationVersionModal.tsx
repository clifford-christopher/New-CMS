/**
 * GenerationVersionModal Component
 * Story 4.5: Iterative Refinement Workflow
 *
 * Side-by-side comparison of different generation versions
 */

import React, { useState } from 'react';
import { Modal, Button, Badge, Alert, Form, Table } from 'react-bootstrap';
import { GenerationVersion, PromptType } from '@/types/generation';
import { useGeneration } from '@/contexts/GenerationContext';

interface GenerationVersionModalProps {
  modelId: string;
  promptType: PromptType;
  show: boolean;
  onHide: () => void;
}

const GenerationVersionModal: React.FC<GenerationVersionModalProps> = ({
  modelId,
  promptType,
  show,
  onHide
}) => {
  const { getVersions, selectVersion, getSelectedVersion } = useGeneration();

  const versions = getVersions(modelId, promptType);
  const selectedVersion = getSelectedVersion(modelId, promptType);

  // State for comparison
  const [leftVersionIndex, setLeftVersionIndex] = useState<number>(0);
  const [rightVersionIndex, setRightVersionIndex] = useState<number>(
    versions.length > 1 ? versions.length - 1 : 0
  );

  if (versions.length === 0) {
    return null;
  }

  const leftVersion = versions[leftVersionIndex];
  const rightVersion = versions[rightVersionIndex];

  /**
   * Handle version selection
   */
  const handleSelectVersion = (versionIndex: number) => {
    selectVersion(modelId, promptType, versionIndex);
    onHide();
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
   * Calculate cost difference
   */
  const costDiff = rightVersion.result.response.cost - leftVersion.result.response.cost;
  const costDiffPercent = leftVersion.result.response.cost > 0
    ? ((costDiff / leftVersion.result.response.cost) * 100).toFixed(1)
    : '0.0';

  /**
   * Calculate latency difference
   */
  const latencyDiff = rightVersion.result.response.latency - leftVersion.result.response.latency;
  const latencyDiffPercent = leftVersion.result.response.latency > 0
    ? ((latencyDiff / leftVersion.result.response.latency) * 100).toFixed(1)
    : '0.0';

  /**
   * Calculate token difference
   */
  const tokenDiff = rightVersion.result.response.total_tokens - leftVersion.result.response.total_tokens;

  return (
    <Modal show={show} onHide={onHide} size="xl" fullscreen="lg-down">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="bi bi-code-square me-2"></i>
          Compare Versions - {modelId}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {/* Version Selectors */}
        <div className="row mb-4">
          <div className="col-md-6">
            <Form.Group>
              <Form.Label>
                <strong>Left Version</strong>
              </Form.Label>
              <Form.Select
                value={leftVersionIndex}
                onChange={(e) => setLeftVersionIndex(Number(e.target.value))}
              >
                {versions.map((v, idx) => (
                  <option key={idx} value={idx}>
                    v{v.version} {v.is_selected ? '(Selected)' : ''} - {new Date(v.timestamp).toLocaleString()}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </div>
          <div className="col-md-6">
            <Form.Group>
              <Form.Label>
                <strong>Right Version</strong>
              </Form.Label>
              <Form.Select
                value={rightVersionIndex}
                onChange={(e) => setRightVersionIndex(Number(e.target.value))}
              >
                {versions.map((v, idx) => (
                  <option key={idx} value={idx}>
                    v{v.version} {v.is_selected ? '(Selected)' : ''} - {new Date(v.timestamp).toLocaleString()}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </div>
        </div>

        {/* Metrics Comparison */}
        <Alert variant="info" className="mb-4">
          <h6 className="mb-3">
            <i className="bi bi-graph-up me-2"></i>
            Metrics Comparison
          </h6>
          <Table size="sm" bordered className="mb-0 bg-white">
            <thead>
              <tr>
                <th>Metric</th>
                <th className="text-center">v{leftVersion.version}</th>
                <th className="text-center">v{rightVersion.version}</th>
                <th className="text-center">Difference</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><i className="bi bi-coin me-1"></i>Cost</td>
                <td className="text-center">{formatCost(leftVersion.result.response.cost)}</td>
                <td className="text-center">{formatCost(rightVersion.result.response.cost)}</td>
                <td className={`text-center ${costDiff > 0 ? 'text-danger' : costDiff < 0 ? 'text-success' : ''}`}>
                  {costDiff > 0 ? '+' : ''}{formatCost(costDiff)} ({costDiff > 0 ? '+' : ''}{costDiffPercent}%)
                </td>
              </tr>
              <tr>
                <td><i className="bi bi-clock me-1"></i>Latency</td>
                <td className="text-center">{formatLatency(leftVersion.result.response.latency)}</td>
                <td className="text-center">{formatLatency(rightVersion.result.response.latency)}</td>
                <td className={`text-center ${latencyDiff > 0 ? 'text-danger' : latencyDiff < 0 ? 'text-success' : ''}`}>
                  {latencyDiff > 0 ? '+' : ''}{formatLatency(latencyDiff)} ({latencyDiff > 0 ? '+' : ''}{latencyDiffPercent}%)
                </td>
              </tr>
              <tr>
                <td><i className="bi bi-cpu me-1"></i>Total Tokens</td>
                <td className="text-center">{leftVersion.result.response.total_tokens.toLocaleString()}</td>
                <td className="text-center">{rightVersion.result.response.total_tokens.toLocaleString()}</td>
                <td className={`text-center ${tokenDiff > 0 ? 'text-warning' : tokenDiff < 0 ? 'text-success' : ''}`}>
                  {tokenDiff > 0 ? '+' : ''}{tokenDiff.toLocaleString()}
                </td>
              </tr>
              <tr>
                <td><i className="bi bi-thermometer me-1"></i>Temperature</td>
                <td className="text-center">{leftVersion.result.response.temperature.toFixed(2)}</td>
                <td className="text-center">{rightVersion.result.response.temperature.toFixed(2)}</td>
                <td className="text-center">
                  {(rightVersion.result.response.temperature - leftVersion.result.response.temperature).toFixed(2)}
                </td>
              </tr>
            </tbody>
          </Table>
        </Alert>

        {/* Side-by-side Generated Text Comparison */}
        <h6 className="mb-3">
          <i className="bi bi-file-text me-2"></i>
          Generated Content
        </h6>
        <div className="row">
          {/* Left Version Text */}
          <div className="col-md-6">
            <div className="border rounded p-3" style={{ height: '400px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
              <div className="d-flex justify-content-between align-items-center mb-2">
                <Badge bg="primary">v{leftVersion.version}</Badge>
                {leftVersion.is_selected && (
                  <Badge bg="success">
                    <i className="bi bi-check-circle me-1"></i>
                    Selected
                  </Badge>
                )}
              </div>
              <small className="text-muted d-block mb-3">
                {new Date(leftVersion.timestamp).toLocaleString()}
              </small>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '14px' }}>
                {leftVersion.result.response.generated_text}
              </p>
            </div>
            {!leftVersion.is_selected && (
              <Button
                variant="outline-success"
                size="sm"
                className="mt-2 w-100"
                onClick={() => handleSelectVersion(leftVersionIndex)}
              >
                <i className="bi bi-check-circle me-1"></i>
                Select This Version
              </Button>
            )}
          </div>

          {/* Right Version Text */}
          <div className="col-md-6">
            <div className="border rounded p-3" style={{ height: '400px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
              <div className="d-flex justify-content-between align-items-center mb-2">
                <Badge bg="primary">v{rightVersion.version}</Badge>
                {rightVersion.is_selected && (
                  <Badge bg="success">
                    <i className="bi bi-check-circle me-1"></i>
                    Selected
                  </Badge>
                )}
              </div>
              <small className="text-muted d-block mb-3">
                {new Date(rightVersion.timestamp).toLocaleString()}
              </small>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '14px' }}>
                {rightVersion.result.response.generated_text}
              </p>
            </div>
            {!rightVersion.is_selected && (
              <Button
                variant="outline-success"
                size="sm"
                className="mt-2 w-100"
                onClick={() => handleSelectVersion(rightVersionIndex)}
              >
                <i className="bi bi-check-circle me-1"></i>
                Select This Version
              </Button>
            )}
          </div>
        </div>

        {/* Prompt Comparison */}
        <h6 className="mt-4 mb-3">
          <i className="bi bi-chat-square-quote me-2"></i>
          Prompt Used
        </h6>
        <div className="row">
          {/* Left Version Prompt */}
          <div className="col-md-6">
            <div className="border rounded p-3" style={{ height: '200px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
              <Badge bg="secondary" className="mb-2">v{leftVersion.version} Prompt</Badge>
              <pre style={{ fontSize: '12px', whiteSpace: 'pre-wrap', marginBottom: 0 }}>
                {leftVersion.prompt_used}
              </pre>
            </div>
          </div>

          {/* Right Version Prompt */}
          <div className="col-md-6">
            <div className="border rounded p-3" style={{ height: '200px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}>
              <Badge bg="secondary" className="mb-2">v{rightVersion.version} Prompt</Badge>
              <pre style={{ fontSize: '12px', whiteSpace: 'pre-wrap', marginBottom: 0 }}>
                {rightVersion.prompt_used}
              </pre>
            </div>
          </div>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default GenerationVersionModal;
