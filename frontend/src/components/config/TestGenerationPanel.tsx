/**
 * TestGenerationPanel Component
 * Main panel for triggering test generation
 */

import React, { useState, useEffect } from 'react';
import { Card, Button, Alert, ProgressBar, Row, Col } from 'react-bootstrap';
import { useGeneration } from '@/contexts/GenerationContext';
import { useModel } from '@/contexts/ModelContext';
import { usePrompt } from '@/contexts/PromptContext';
import { useData } from '@/contexts/DataContext';
import { PromptType, StructuredData } from '@/types/generation';
import GenerationResultsView from './GenerationResultsView';
import VersionDropdown, { VersionOption } from './VersionDropdown';

const TestGenerationPanel: React.FC = () => {
  const {
    triggerGeneration,
    isGenerating,
    status,
    error,
    clearResults,
    results,
    fetchHistory,
    historyLoading,
    resultVersions,
    selectedVersions,
    selectVersion
  } = useGeneration();
  const { selectedModels, temperature, maxTokens } = useModel();
  const { checkedTypes, prompts, variantStrategy, strategyValidation } = usePrompt(); // Also extract prompts and strategy from context
  const { selectedSections, dataMode, stockId, triggerId } = useData();

  // Convert Set to Array for prompt types
  const promptTypesArray = Array.from(checkedTypes) as PromptType[];

  // Build version dropdown options
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

  // Calculate total generations
  const totalGenerations = selectedModels.length * promptTypesArray.length;

  // Check if prompt has placeholders
  const hasPlaceholders = (content: string): boolean => {
    const sectionPattern = /\{\{[a-zA-Z_][a-zA-Z0-9_\s]*\}\}/;
    const dataPattern = /\{data\.[a-zA-Z_][a-zA-Z0-9_.]*\}/;
    return sectionPattern.test(content) || dataPattern.test(content);
  };

  // Check if any enabled prompt has no placeholders
  const promptsWithoutPlaceholders = promptTypesArray.filter(
    type => prompts[type].content.trim().length > 0 && !hasPlaceholders(prompts[type].content)
  );

  // Check if ready to generate
  const canGenerate =
    selectedModels.length > 0 &&
    promptTypesArray.length > 0 &&
    selectedSections.length > 0 &&
    stockId &&
    !isGenerating &&
    // Verify all checked prompt types have non-empty content
    promptTypesArray.every(type => prompts[type].content.trim().length > 0) &&
    // Verify variant strategy requirements are met
    strategyValidation.isValid;

  // Build structured data from DataContext
  const buildStructuredData = (): StructuredData => {
    const sections: Record<string, any> = {};

    selectedSections.forEach((section) => {
      // Store by both section_id and section_name for flexibility
      sections[section.section_id] = section.content;
      sections[section.section_name] = section.content;
    });

    return {
      stock_id: stockId,
      data_mode: dataMode,
      sections
    };
  };

  const handleGenerate = async () => {
    if (!canGenerate) return;

    try {
      const structuredData = buildStructuredData();

      // Extract current prompt templates from PromptContext (in-memory drafts from Monaco editor)
      const promptTemplates = {
        paid: prompts.paid.content,
        unpaid: prompts.unpaid.content,
        crawler: prompts.crawler.content
      };

      await triggerGeneration({
        triggerId,
        stockId,
        modelIds: selectedModels,
        promptTypes: promptTypesArray,
        promptTemplates, // Pass in-memory prompt templates
        structuredData,
        temperature,
        maxTokens,
        variantStrategy // Pass variant strategy to generation service
      });
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };

  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(6)}`;
  };

  return (
    <div className="test-generation-panel">
      {/* Version History Dropdown */}
      <VersionDropdown
        versionOptions={versionOptions}
        resultVersions={resultVersions}
        isLoading={historyLoading}
      />

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">
            <i className="bi bi-play-circle me-2"></i>
            Test Generation
          </h5>
        </Card.Header>
        <Card.Body>
          {/* Info Alert */}
          <Alert variant="info" className="mb-3">
            <i className="bi bi-lightbulb me-2"></i>
            <strong>Test your configuration:</strong> Generate sample articles using your selected models
            and prompts before saving the trigger configuration. This allows you to preview and compare
            outputs from different models.
          </Alert>

          {/* Generation Summary */}
          <Row className="mb-3">
            <Col md={6}>
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">
                  <i className="bi bi-cpu me-1"></i>
                  Models Selected:
                </span>
                <strong>{selectedModels.length}</strong>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">
                  <i className="bi bi-file-text me-1"></i>
                  Prompt Types:
                </span>
                <strong>{promptTypesArray.length}</strong>
              </div>
            </Col>
            <Col md={6}>
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">
                  <i className="bi bi-shuffle me-1"></i>
                  Total Generations:
                </span>
                <strong>
                  {selectedModels.length} × {promptTypesArray.length} = {totalGenerations}
                </strong>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">
                  <i className="bi bi-database me-1"></i>
                  Data Sections:
                </span>
                <strong>{selectedSections.length}</strong>
              </div>
            </Col>
          </Row>

          {/* Warnings */}
          {selectedModels.length === 0 && (
            <Alert variant="warning">
              <i className="bi bi-exclamation-triangle me-2"></i>
              Please select at least one model from the Model Selection section above.
            </Alert>
          )}

          {promptTypesArray.length === 0 && (
            <Alert variant="warning">
              <i className="bi bi-exclamation-triangle me-2"></i>
              No prompt types are enabled. Enable at least one prompt type in the Prompts step.
            </Alert>
          )}

          {selectedSections.length === 0 && (
            <Alert variant="warning">
              <i className="bi bi-exclamation-triangle me-2"></i>
              No data sections selected. Please select data sections in a previous step.
            </Alert>
          )}

          {promptTypesArray.length > 0 && !promptTypesArray.every(type => prompts[type].content.trim().length > 0) && (
            <Alert variant="warning">
              <i className="bi bi-exclamation-triangle me-2"></i>
              One or more prompt types have empty content. Please configure prompts in the Prompt Engineering step before generating.
            </Alert>
          )}

          {!strategyValidation.isValid && (
            <Alert variant="danger">
              <i className="bi bi-exclamation-circle me-2"></i>
              <strong>Variant Strategy Requirement Not Met:</strong> {strategyValidation.errorMessage}
            </Alert>
          )}

          {promptsWithoutPlaceholders.length > 0 && (
            <Alert variant="warning">
              <i className="bi bi-exclamation-triangle me-2"></i>
              <strong>Warning: Missing Placeholders!</strong> The following prompt type(s) contain no placeholders:{' '}
              <strong>{promptsWithoutPlaceholders.join(', ')}</strong>.
              Without placeholders like <code>{'{{old_data}}'}</code>, the LLM will not receive your configured data
              and may generate unrelated content. Go back to the Prompt Engineering step to add placeholders.
            </Alert>
          )}

          {/* Error Message */}
          {error && (
            <Alert variant="danger" dismissible>
              <i className="bi bi-exclamation-triangle me-2"></i>
              {error}
            </Alert>
          )}

          {/* Progress Bar */}
          {isGenerating && status && (
            <div className="mb-3">
              <div className="d-flex justify-content-between mb-2">
                <span>
                  Generating articles... ({status.completed} / {status.total})
                </span>
                <span className="text-primary">{formatCost(status.total_cost)}</span>
              </div>
              <ProgressBar
                now={(status.completed / status.total) * 100}
                label={`${Math.round((status.completed / status.total) * 100)}%`}
                animated
                variant="primary"
              />
            </div>
          )}

          {/* Action Buttons */}
          <div className="d-flex gap-2">
            <Button
              variant="primary"
              size="lg"
              onClick={handleGenerate}
              disabled={!canGenerate}
              className="flex-grow-1"
            >
              {isGenerating ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Generating...
                </>
              ) : (
                <>
                  <i className="bi bi-play-fill me-2"></i>
                  Generate Test Articles
                </>
              )}
            </Button>

            {status && status.completed > 0 && !isGenerating && (
              <Button
                variant="outline-secondary"
                size="lg"
                onClick={clearResults}
              >
                <i className="bi bi-arrow-counterclockwise me-2"></i>
                Clear Results
              </Button>
            )}
          </div>

          {/* Cost Estimate */}
          {!isGenerating && totalGenerations > 0 && (
            <Alert variant="secondary" className="mb-0 mt-3">
              <small>
                <i className="bi bi-info-circle me-2"></i>
                <strong>Estimated cost range:</strong> Varies by model. Typically $0.001 - $0.02 per generation.
                Total for {totalGenerations} generation{totalGenerations !== 1 ? 's' : ''}: approximately ${(totalGenerations * 0.005).toFixed(3)} - ${(totalGenerations * 0.02).toFixed(3)}
              </small>
            </Alert>
          )}

          {/* Final Status */}
          {!isGenerating && status && status.completed > 0 && (
            <Alert variant="success" className="mb-0 mt-3">
              <div className="d-flex justify-content-between align-items-center">
                <span>
                  <i className="bi bi-check-circle me-2"></i>
                  <strong>Generation complete!</strong> {status.completed} article{status.completed !== 1 ? 's' : ''} generated
                  {status.errors > 0 && ` (${status.errors} error${status.errors !== 1 ? 's' : ''})`}
                </span>
                <span>
                  <i className="bi bi-coin me-1"></i>
                  Total Cost: {formatCost(status.total_cost)}
                </span>
              </div>
            </Alert>
          )}
        </Card.Body>
      </Card>

      {/* Results View */}
      <GenerationResultsView />
    </div>
  );
};

export default TestGenerationPanel;
