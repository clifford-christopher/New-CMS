/**
 * GenerationResultsView Component
 * Displays generation results organized by prompt type
 */

import React, { useState } from 'react';
import { Card, Tabs, Tab, Alert, Badge } from 'react-bootstrap';
import { useGeneration } from '@/contexts/GenerationContext';
import { PromptType } from '@/types/generation';
import GenerationResultCard from './GenerationResultCard';

const GenerationResultsView: React.FC = () => {
  const { results, status } = useGeneration();
  const [activeTab, setActiveTab] = useState<PromptType>('paid');

  // Group results by prompt type
  const resultsByType: Record<PromptType, typeof results> = {
    paid: results.filter(r => r.prompt_type === 'paid'),
    unpaid: results.filter(r => r.prompt_type === 'unpaid'),
    crawler: results.filter(r => r.prompt_type === 'crawler')
  };

  // Prompt type labels
  const promptTypeLabels: Record<PromptType, string> = {
    paid: 'Paid',
    unpaid: 'Unpaid',
    crawler: 'Web Crawler'
  };

  // Filter tabs that have results
  const availableTabs = React.useMemo(() => {
    return (Object.keys(resultsByType) as PromptType[]).filter(
      type => resultsByType[type].length > 0
    );
  }, [resultsByType]);

  // Set default active tab to first available (only when truly needed)
  React.useEffect(() => {
    if (availableTabs.length > 0 && activeTab && !availableTabs.includes(activeTab)) {
      setActiveTab(availableTabs[0]);
    } else if (availableTabs.length > 0 && !activeTab) {
      setActiveTab(availableTabs[0]);
    }
  }, [availableTabs]); // Remove activeTab from dependencies to prevent flicker

  // Early return AFTER all hooks
  if (results.length === 0) {
    return null;
  }

  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(6)}`;
  };

  return (
    <Card className="mt-4">
      <Card.Header>
        <div className="d-flex align-items-center justify-content-between">
          <h5 className="mb-0">
            <i className="bi bi-file-earmark-text me-2"></i>
            Generation Results
          </h5>
          {status && (
            <div className="d-flex gap-3">
              <span className="text-muted">
                <i className="bi bi-check-circle me-1"></i>
                {status.completed} / {status.total}
              </span>
              {status.errors > 0 && (
                <span className="text-danger">
                  <i className="bi bi-exclamation-triangle me-1"></i>
                  {status.errors} error{status.errors !== 1 ? 's' : ''}
                </span>
              )}
              <span className="text-primary">
                <i className="bi bi-coin me-1"></i>
                {formatCost(status.total_cost)}
              </span>
            </div>
          )}
        </div>
      </Card.Header>
      <Card.Body>
        {availableTabs.length === 0 ? (
          <Alert variant="info">
            <i className="bi bi-info-circle me-2"></i>
            No results to display yet.
          </Alert>
        ) : (
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k as PromptType)}
            className="mb-3"
          >
            {availableTabs.map((promptType) => {
              const typeResults = resultsByType[promptType];
              const completedCount = typeResults.filter(r => r.status === 'completed').length;
              const errorCount = typeResults.filter(r => r.status === 'error').length;

              return (
                <Tab
                  key={promptType}
                  eventKey={promptType}
                  title={
                    <span>
                      {promptTypeLabels[promptType]}
                      <Badge bg="secondary" className="ms-2">
                        {typeResults.length}
                      </Badge>
                      {errorCount > 0 && (
                        <Badge bg="danger" className="ms-1">
                          {errorCount} error{errorCount !== 1 ? 's' : ''}
                        </Badge>
                      )}
                    </span>
                  }
                >
                  <div className="mt-3">
                    {/* Summary for this type */}
                    <Alert variant="info" className="mb-3">
                      <div className="d-flex justify-content-between align-items-center">
                        <span>
                          <i className="bi bi-info-circle me-2"></i>
                          Showing {typeResults.length} generation{typeResults.length !== 1 ? 's' : ''} for {promptTypeLabels[promptType]} prompt type
                        </span>
                        {completedCount > 0 && (
                          <span>
                            <i className="bi bi-check-circle me-1 text-success"></i>
                            {completedCount} completed
                          </span>
                        )}
                      </div>
                    </Alert>

                    {/* Results */}
                    {typeResults.length === 0 ? (
                      <Alert variant="warning">
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        No results for this prompt type.
                      </Alert>
                    ) : (
                      <div>
                        {typeResults.map((result, index) => (
                          <GenerationResultCard
                            key={`${result.model_id}-${result.prompt_type}-${index}`}
                            result={result}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                </Tab>
              );
            })}
          </Tabs>
        )}
      </Card.Body>
    </Card>
  );
};

export default GenerationResultsView;
