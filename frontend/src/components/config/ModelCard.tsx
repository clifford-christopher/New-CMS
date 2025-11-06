/**
 * ModelCard Component
 * Story 4.2: Model Selection Interface
 *
 * Displays a single LLM model with:
 * - Model name and provider
 * - Description
 * - Pricing information
 * - Selection checkbox
 */

import React from 'react';
import { Card, Form } from 'react-bootstrap';
import { LLMModel } from '@/types/model';

interface ModelCardProps {
  model: LLMModel;
  isSelected: boolean;
  onToggle: (modelId: string) => void;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, isSelected, onToggle }) => {
  // Format pricing for display
  const formatPrice = (price: number): string => {
    return `$${price.toFixed(2)}`;
  };

  // Provider badge colors
  const getProviderBadgeClass = (provider: string): string => {
    switch (provider) {
      case 'openai':
        return 'bg-success';
      case 'anthropic':
        return 'bg-primary';
      case 'gemini':
        return 'bg-info';
      default:
        return 'bg-secondary';
    }
  };

  return (
    <Card
      className={`model-card ${isSelected ? 'border-primary' : ''}`}
      style={{
        cursor: 'pointer',
        transition: 'all 0.2s',
        opacity: isSelected ? 1 : 0.85
      }}
      onClick={() => onToggle(model.model_id)}
    >
      <Card.Body>
        <div className="d-flex align-items-start justify-content-between">
          <div className="flex-grow-1">
            <div className="d-flex align-items-center gap-2 mb-1">
              <Form.Check
                type="checkbox"
                checked={isSelected}
                onChange={() => {}} // Handled by card click
                onClick={(e) => e.stopPropagation()}
              />
              <h6 className="mb-0">{model.display_name}</h6>
              <span className={`badge ${getProviderBadgeClass(model.provider)} text-capitalize`}>
                {model.provider}
              </span>
            </div>
            <p className="text-muted small mb-2">{model.description}</p>
            <div className="d-flex gap-3 small">
              <span>
                <strong>Input:</strong> {formatPrice(model.pricing.input)}/1M
              </span>
              <span>
                <strong>Output:</strong> {formatPrice(model.pricing.output)}/1M
              </span>
            </div>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ModelCard;
