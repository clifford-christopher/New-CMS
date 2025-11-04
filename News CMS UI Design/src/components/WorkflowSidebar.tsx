import { Check, ChevronDown, ChevronUp } from 'lucide-react';
import type { WorkflowStep } from './ConfigurationWorkspace';

type WorkflowSidebarProps = {
  currentStep: WorkflowStep;
  onStepChange: (step: WorkflowStep) => void;
  completedSteps?: WorkflowStep[];
};

type Step = {
  id: WorkflowStep;
  number: number;
  label: string;
};

const steps: Step[] = [
  { id: 'data', number: 1, label: 'Data Configuration' },
  { id: 'sections', number: 2, label: 'Section Management' },
  { id: 'prompt', number: 3, label: 'Prompt Engineering' },
  { id: 'models', number: 4, label: 'Model Testing' },
  { id: 'results', number: 5, label: 'Results & Comparison' }
];

export function WorkflowSidebar({ currentStep, onStepChange, completedSteps = [] }: WorkflowSidebarProps) {
  return (
    <div className="w-[280px] bg-white border-r border-[#dee2e6] p-4 overflow-y-auto hidden lg:block">
      <div className="space-y-4">
        {steps.map((step) => {
          const isActive = currentStep === step.id;
          const isCompleted = completedSteps.includes(step.id);
          
          return (
            <button
              key={step.id}
              onClick={() => onStepChange(step.id)}
              className={`w-full rounded p-3 flex items-center gap-3 transition-all ${
                isActive 
                  ? 'bg-[#e7f1ff] border-l-4 border-[#0d6efd]' 
                  : 'hover:bg-[#f8f9fa]'
              }`}
            >
              <div 
                className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-sm ${
                  isActive 
                    ? 'bg-[#0d6efd] text-white' 
                    : 'bg-[#e9ecef] text-[#212529]'
                }`}
              >
                {step.number}
              </div>
              
              <span className={isActive ? 'font-bold' : ''}>
                {step.label}
              </span>

              <div className="ml-auto flex items-center gap-2">
                {isCompleted && (
                  <Check className="w-5 h-5 text-[#198754]" />
                )}
                {isActive ? (
                  <ChevronUp className="w-5 h-5 text-[#0d6efd]" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-[#6c757d]" />
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
