/**
 * WorkflowGuideTour Component
 *
 * Provides step-by-step guidance for the 5-step configuration workflow.
 * Shows contextual tooltips/popups guiding users through:
 * 1. Data Configuration
 * 2. Section Management
 * 3. Prompt Configuration
 * 4. Model Testing
 * 5. Results & Comparison
 */

import React, { useState, useEffect } from 'react';
import { Modal, Button, Alert } from 'react-bootstrap';

export type WorkflowStep = 'data' | 'sections' | 'prompts' | 'testing' | 'results';

interface WorkflowGuideTourProps {
  currentStep: WorkflowStep;
  onClose: () => void;
  onNext?: () => void;
  show: boolean;
}

interface StepGuide {
  title: string;
  content: string;
  icon: string;
  tips: string[];
  nextAction?: string;
}

const STEP_GUIDES: Record<WorkflowStep, StepGuide> = {
  data: {
    title: 'Step 1: Configure Data',
    icon: 'bi-database',
    content: 'Choose how to fetch data for your news generation.',
    tips: [
      'Select "OLD" to use existing trigger data from the database',
      'Select "NEW" to generate fresh structured data for a stock',
      'Select "OLD + NEW" to combine both data sources',
      'Enter a stock ID and click "Fetch Data" or "Generate Data"',
      'Once data is loaded, this step will be marked complete ✓'
    ],
    nextAction: 'After data is loaded, click "Section Management" to continue'
  },
  sections: {
    title: 'Step 2: Section Management',
    icon: 'bi-list-ol',
    content: 'Organize and order the data sections for your news output.',
    tips: [
      'Select which sections to include in the generated news',
      'Drag and drop to reorder sections',
      'The section order determines how data appears in prompts',
      'Preview your section arrangement before moving to prompts',
      'This step completes when at least one section is selected ✓'
    ],
    nextAction: 'Click "Prompts" to configure your prompt templates'
  },
  prompts: {
    title: 'Step 3: Prompt Configuration',
    icon: 'bi-code-slash',
    content: 'Create and customize prompt templates for news generation.',
    tips: [
      'Choose a Variant Strategy (all_same, all_unique, etc.)',
      'Edit prompts for Paid, Unpaid, and Crawler content types',
      'Use placeholders like {{section_1}} to reference sections',
      'Use {{data.field}} to reference specific data fields',
      'Save your prompts - this step completes when all required prompts are filled ✓'
    ],
    nextAction: 'Click "Model Testing" to test your prompts with LLMs'
  },
  testing: {
    title: 'Step 4: Model Testing',
    icon: 'bi-cpu',
    content: 'Test your prompts with multiple LLM providers.',
    tips: [
      'Select one or more LLM models (OpenAI, Anthropic, Google)',
      'Configure temperature and max_tokens parameters',
      'Click "Generate News" to test your prompts',
      'View generation results and costs',
      'This step completes when you have at least one successful generation ✓'
    ],
    nextAction: 'Click "Results & Comparison" to review outputs'
  },
  results: {
    title: 'Step 5: Results & Comparison',
    icon: 'bi-bar-chart',
    content: 'Review and compare outputs from different models.',
    tips: [
      'Compare outputs side-by-side across models',
      'Review cost estimates and quality',
      'Select your preferred model/output',
      'This step auto-completes when you view results ✓',
      'Click "Publish" when ready to deploy your configuration'
    ],
    nextAction: 'Ready to publish? Click "Publish" in the bottom bar'
  }
};

const WorkflowGuideTour: React.FC<WorkflowGuideTourProps> = ({
  currentStep,
  onClose,
  onNext,
  show
}) => {
  const guide = STEP_GUIDES[currentStep];
  const [dontShowAgain, setDontShowAgain] = useState(false);

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem('workflow_guide_dismissed', 'true');
    }
    onClose();
  };

  const handleNext = () => {
    handleClose();
    if (onNext) {
      onNext();
    }
  };

  if (!show) return null;

  return (
    <Modal show={show} onHide={handleClose} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className={`${guide.icon} me-2`}></i>
          {guide.title}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant="info" className="mb-3">
          <strong>{guide.content}</strong>
        </Alert>

        <div className="mb-3">
          <h6 className="mb-2">
            <i className="bi bi-lightbulb me-2"></i>
            <strong>Tips:</strong>
          </h6>
          <ul className="mb-0">
            {guide.tips.map((tip, idx) => (
              <li key={idx} style={{ marginBottom: '8px' }}>
                {tip}
              </li>
            ))}
          </ul>
        </div>

        {guide.nextAction && (
          <Alert variant="success" className="mb-0">
            <i className="bi bi-arrow-right-circle me-2"></i>
            <strong>Next:</strong> {guide.nextAction}
          </Alert>
        )}

        <div className="form-check mt-3">
          <input
            className="form-check-input"
            type="checkbox"
            id="dontShowAgain"
            checked={dontShowAgain}
            onChange={(e) => setDontShowAgain(e.target.checked)}
          />
          <label className="form-check-label" htmlFor="dontShowAgain">
            Don't show workflow guide again
          </label>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
        {onNext && (
          <Button variant="primary" onClick={handleNext}>
            Got it, Continue <i className="bi bi-arrow-right ms-2"></i>
          </Button>
        )}
      </Modal.Footer>
    </Modal>
  );
};

export default WorkflowGuideTour;
