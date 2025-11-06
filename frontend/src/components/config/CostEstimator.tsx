/**
 * CostEstimator Component
 * Story 4.2: Model Selection Interface
 *
 * Displays real-time cost estimation:
 * - Cost per model
 * - Total generations (models × checked prompt types)
 * - Total estimated cost
 * - Cost breakdown per model
 */

import React from 'react';
import { Card, Table, Alert } from 'react-bootstrap';
import { TotalCostEstimate } from '@/types/model';

interface CostEstimatorProps {
  costEstimate: TotalCostEstimate | null;
}

const CostEstimator: React.FC<CostEstimatorProps> = ({ costEstimate }) => {
  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(6)}`;
  };

  if (!costEstimate) {
    return (
      <Alert variant="info">
        <i className="bi bi-info-circle me-2"></i>
        Select models and check prompt types to see cost estimation
      </Alert>
    );
  }

  return (
    <Card className="border-info">
      <Card.Header className="bg-info bg-opacity-10">
        <div className="d-flex align-items-center justify-content-between">
          <h6 className="mb-0">
            <i className="bi bi-calculator me-2"></i>
            Cost Estimation
          </h6>
          <span className="badge bg-info">
            {costEstimate.total_generations} Generation{costEstimate.total_generations !== 1 ? 's' : ''}
          </span>
        </div>
      </Card.Header>
      <Card.Body>
        {/* Summary */}
        <div className="mb-3">
          <div className="d-flex justify-content-between mb-2">
            <span className="text-muted">Models Selected:</span>
            <strong>{costEstimate.total_models}</strong>
          </div>
          <div className="d-flex justify-content-between mb-2">
            <span className="text-muted">Prompt Types Checked:</span>
            <strong>{costEstimate.total_prompt_types}</strong>
          </div>
          <div className="d-flex justify-content-between mb-2">
            <span className="text-muted">Total Generations:</span>
            <strong>
              {costEstimate.total_models} × {costEstimate.total_prompt_types} = {costEstimate.total_generations}
            </strong>
          </div>
          <hr />
          <div className="d-flex justify-content-between">
            <span className="text-muted">Cost per Prompt Type:</span>
            <strong>{formatCost(costEstimate.cost_per_prompt_type)}</strong>
          </div>
          <div className="d-flex justify-content-between mt-2">
            <span><strong>Total Estimated Cost:</strong></span>
            <span className="h5 mb-0 text-primary">
              {formatCost(costEstimate.total_estimated_cost)}
            </span>
          </div>
        </div>

        {/* Model Breakdown */}
        {costEstimate.models.length > 0 && (
          <>
            <h6 className="mb-2">Cost Breakdown by Model</h6>
            <Table size="sm" bordered hover>
              <thead>
                <tr>
                  <th>Model</th>
                  <th className="text-end">Per Generation</th>
                  <th className="text-end">Total</th>
                </tr>
              </thead>
              <tbody>
                {costEstimate.models.map((model) => {
                  const totalForModel = model.cost_per_generation * costEstimate.total_prompt_types;
                  return (
                    <tr key={model.model_id}>
                      <td>
                        <div>{model.display_name}</div>
                        <small className="text-muted text-capitalize">{model.provider}</small>
                      </td>
                      <td className="text-end font-monospace">
                        {formatCost(model.cost_per_generation)}
                      </td>
                      <td className="text-end font-monospace">
                        <strong>{formatCost(totalForModel)}</strong>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
          </>
        )}

        {/* Disclaimer */}
        <Alert variant="warning" className="mb-0 mt-3">
          <small>
            <i className="bi bi-exclamation-triangle me-2"></i>
            <strong>Note:</strong> Costs are estimates based on ~800 input tokens and {costEstimate.models[0]?.output_tokens_estimated || 500} output tokens per generation. Actual costs may vary.
          </small>
        </Alert>
      </Card.Body>
    </Card>
  );
};

export default CostEstimator;
