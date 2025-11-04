import { useState } from 'react';
import { Navbar } from './Navbar';
import { Breadcrumb } from './Breadcrumb';
import { ContextBar } from './ContextBar';
import { WorkflowSidebar } from './WorkflowSidebar';
import { TabletWorkflowTabs } from './TabletWorkflowTabs';
import { DataConfigurationPanel } from './DataConfigurationPanel';
import { SectionManagementPanel } from './SectionManagementPanel';
import { PromptEditor } from './PromptEditor';
import { ModelSelection } from './ModelSelection';
import { ResultsComparisonPanel } from './ResultsComparisonPanel';
import { BottomActionsBar } from './BottomActionsBar';
import { PublishModal } from './PublishModal';
import { HistoryDrawer } from './HistoryDrawer';
import type { TriggerConfig } from '../App';
import type { PromptType } from './TypeSelectionCheckbox';

type ConfigurationWorkspaceProps = {
  trigger: TriggerConfig;
  onBack: () => void;
};

export type WorkflowStep = 'data' | 'sections' | 'prompt' | 'models' | 'results';

export function ConfigurationWorkspace({ trigger, onBack }: ConfigurationWorkspaceProps) {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('data');
  const [stockId, setStockId] = useState('TCS');
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [showHistoryDrawer, setShowHistoryDrawer] = useState(false);
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [dataConfigured, setDataConfigured] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<PromptType[]>(['paid']);
  const [promptText, setPromptText] = useState(`# News Article Prompt

Generate a news article based on the following earnings data:

Company: {{company_name}}
Quarter: {{quarter}}
Revenue: {{revenue}}
Earnings per Share: {{eps}}

{{earnings_summary}}

Article should be 300-400 words, professional tone.`);

  const handleDataConfigured = (sections: string[]) => {
    setSelectedSections(sections);
    setDataConfigured(true);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar 
        activeView="configuration" 
        showConfigurationLink={true}
        onNavigate={onBack}
      />
      <Breadcrumb triggerName={trigger.name} onBack={onBack} />
      <ContextBar 
        triggerName={trigger.name}
        lastPublished={trigger.lastUpdated}
        dataStatus={dataConfigured ? 'ready' : 'not-configured'}
        stockId={stockId}
        onStockIdChange={setStockId}
        selectedTypes={selectedTypes}
        onTypesChange={setSelectedTypes}
      />
      
      <div className="flex flex-1 overflow-hidden">
        <WorkflowSidebar 
          currentStep={currentStep}
          onStepChange={setCurrentStep}
          completedSteps={dataConfigured ? ['data'] : []}
        />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <TabletWorkflowTabs 
            currentStep={currentStep}
            onStepChange={setCurrentStep}
          />
          
          <main className="flex-1 bg-[#f8f9fa] p-6 overflow-y-auto">
          <div className="max-w-[1592px] mx-auto space-y-6">
            {currentStep === 'data' && (
              <DataConfigurationPanel onDataConfigured={handleDataConfigured} />
            )}

            {currentStep === 'sections' && (
              <SectionManagementPanel selectedSectionIds={selectedSections} />
            )}
            
            {currentStep === 'prompt' && (
              <PromptEditor 
                value={promptText}
                onChange={setPromptText}
                selectedTypes={selectedTypes}
              />
            )}
            
            {currentStep === 'models' && (
              <ModelSelection selectedTypes={selectedTypes} />
            )}

            {currentStep === 'results' && (
              <ResultsComparisonPanel selectedTypes={selectedTypes} />
            )}
          </div>
          </main>
        </div>
      </div>

      <BottomActionsBar 
        onPublish={() => setShowPublishModal(true)}
        onViewHistory={() => setShowHistoryDrawer(true)}
      />

      {showPublishModal && (
        <PublishModal 
          triggerName={trigger.name}
          onClose={() => setShowPublishModal(false)}
        />
      )}

      {showHistoryDrawer && (
        <HistoryDrawer onClose={() => setShowHistoryDrawer(false)} />
      )}
    </div>
  );
}
