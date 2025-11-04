import type { WorkflowStep } from './ConfigurationWorkspace';

type TabletWorkflowTabsProps = {
  currentStep: WorkflowStep;
  onStepChange: (step: WorkflowStep) => void;
};

const tabs = [
  { id: 'data' as WorkflowStep, label: '1. Data' },
  { id: 'sections' as WorkflowStep, label: '2. Sections' },
  { id: 'prompt' as WorkflowStep, label: '3. Prompt' },
  { id: 'models' as WorkflowStep, label: '4. Models' },
  { id: 'results' as WorkflowStep, label: '5. Results' }
];

export function TabletWorkflowTabs({ currentStep, onStepChange }: TabletWorkflowTabsProps) {
  return (
    <div className="bg-white border-b border-[#dee2e6] overflow-x-auto lg:hidden">
      <div className="flex min-w-max">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onStepChange(tab.id)}
            className={`flex-shrink-0 px-6 py-4 text-sm transition-colors ${
              currentStep === tab.id
                ? 'bg-[#0d6efd] text-white border-b-2 border-[#0d6efd]'
                : 'text-[#6c757d] hover:text-[#212529] hover:bg-[#f8f9fa]'
            }`}
            style={{ minWidth: '180px' }}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
