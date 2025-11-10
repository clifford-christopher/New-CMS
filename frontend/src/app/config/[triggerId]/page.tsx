/**
 * Configuration Page - NewsCMSUI Design
 *
 * Following Figma Design System v2.2
 * Features:
 * - Left sidebar navigation (5 steps)
 * - Trigger context bar with type selection
 * - Data section selection with multi-select dropdown
 * - Section management with drag-and-drop
 * - Sticky bottom actions bar
 */

'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { GenerationResult, VariantStrategy, getStrategyRequirements } from '@/types/generation';
import { Container, Row, Col, Card, Form, Button, Alert, Badge, Spinner, Dropdown } from 'react-bootstrap';
import SectionManagementPanel, { Section, DEFAULT_SECTIONS } from '@/components/SectionManagementPanel';
import OldDataDisplay from '@/components/OldDataDisplay';
import NewDataDisplay from '@/components/NewDataDisplay';
import DataPreviewPanel from '@/components/config/DataPreviewPanel';
import PromptEditor from '@/components/config/PromptEditor';
import { PromptProvider, usePrompt } from '@/contexts/PromptContext';
import { ValidationProvider } from '@/contexts/ValidationContext';
import { PreviewProvider } from '@/contexts/PreviewContext';
import { DataProvider } from '@/contexts/DataContext';
import { ModelProvider, useModel } from '@/contexts/ModelContext';
import { GenerationProvider, useGeneration } from '@/contexts/GenerationContext';
import { SectionData } from '@/types/validation';
import ModelSelection from '@/components/config/ModelSelection';
import TestGenerationPanel from '@/components/config/TestGenerationPanel';
import GenerationHistoryPanel from '@/components/config/GenerationHistoryPanel';
import ComparisonView from '@/components/config/ComparisonView';
import PublishConfirmationModal from '@/components/config/PublishConfirmationModal';
import ConfigVersionHistoryModal from '@/components/config/ConfigVersionHistoryModal';
import WorkflowGuideTour from '@/components/config/WorkflowGuideTour';

interface PageProps {
  params: { triggerId: string };
}

type DataMode = 'OLD' | 'NEW' | 'OLD_NEW';
type PromptType = 'paid' | 'unpaid' | 'webCrawler';

type NavigationStep = 'data' | 'sections' | 'prompts' | 'testing' | 'results';

/**
 * TriggerIdSetter - Sets triggerId in GenerationContext on mount
 * This triggers auto-load of last generated data
 */
const TriggerIdSetter: React.FC<{ triggerId: string }> = ({ triggerId }) => {
  const { setTriggerId } = useGeneration();

  useEffect(() => {
    setTriggerId(triggerId);
  }, [triggerId, setTriggerId]);

  return null;
};

/**
 * ResultsStepWrapper - Wraps ComparisonView with GenerationContext
 * Simply passes results from context (auto-loaded by GenerationProvider)
 */
const ResultsStepWrapper: React.FC<{ triggerName: string; onNavigateToTesting: () => void }> = ({
  triggerName,
  onNavigateToTesting
}) => {
  const { results, historyLoading } = useGeneration();

  return (
    <ComparisonView
      results={results}
      triggerName={triggerName}
      onNavigateToTesting={onNavigateToTesting}
      isLoading={historyLoading}
    />
  );
};

/**
 * DraftSaveButton - Button component with access to context providers
 * This component can safely call usePrompt() and useModel() hooks
 * because it's rendered inside the provider boundaries
 */
interface DraftSaveButtonProps {
  onSave: (contextData: {
    prompts: any;
    variantStrategy: string;
    selectedModels: string[]; // Multiple models for testing
    temperature: number;
    maxTokens: number;
  }) => Promise<void>;
  saveStatus: 'idle' | 'saving' | 'success' | 'error';
}

const DraftSaveButton: React.FC<DraftSaveButtonProps> = ({ onSave, saveStatus }) => {
  // Safe to call hooks here because this component is inside providers
  const { prompts, variantStrategy } = usePrompt();
  const { selectedModels, temperature, maxTokens } = useModel();

  const handleClick = () => {
    onSave({
      prompts,
      variantStrategy,
      selectedModels, // Multiple models array
      temperature,
      maxTokens
    });
  };

  return (
    <Button
      variant="outline-secondary"
      onClick={handleClick}
      disabled={saveStatus === 'saving'}
      style={{ width: '120px', height: '40px' }}
    >
      {saveStatus === 'saving' ? <Spinner as="span" animation="border" size="sm" /> : 'Save Draft'}
    </Button>
  );
};

/**
 * PublishButton Component - Auto-saves draft before opening publish modal
 * Must be inside PromptProvider and ModelProvider to access context data
 */
interface PublishButtonProps {
  onPublish: (contextData: {
    prompts: any;
    variantStrategy: string;
    selectedModels: string[];
    temperature: number;
    maxTokens: number;
  }) => Promise<void>;
  onOpenModal: () => void;
  disabled: boolean;
  saveStatus: 'idle' | 'saving' | 'success' | 'error';
  completedSteps: Record<NavigationStep, boolean>;
}

const PublishButton: React.FC<PublishButtonProps> = ({
  onPublish,
  onOpenModal,
  disabled,
  saveStatus,
  completedSteps
}) => {
  const { prompts, variantStrategy } = usePrompt();
  const { selectedModels, temperature, maxTokens } = useModel();
  const [isAutoSaving, setIsAutoSaving] = useState(false);

  const handleClick = async () => {
    // Validate all steps completed
    const allStepsCompleted = Object.values(completedSteps).every(v => v);
    if (!allStepsCompleted) {
      alert('Complete all required steps before publishing');
      return;
    }

    // Auto-save draft before publishing
    setIsAutoSaving(true);
    try {
      await onPublish({
        prompts,
        variantStrategy,
        selectedModels,
        temperature,
        maxTokens
      });

      // Open the publish modal after successful save
      onOpenModal();
    } catch (error) {
      console.error('Failed to auto-save before publish:', error);
      alert('Failed to save draft. Please try again.');
    } finally {
      setIsAutoSaving(false);
    }
  };

  const isDisabled = disabled || saveStatus === 'saving' || isAutoSaving;
  const showSpinner = saveStatus === 'saving' || isAutoSaving;

  return (
    <Button
      variant="primary"
      onClick={handleClick}
      disabled={isDisabled}
      style={{ width: '140px', height: '40px', fontWeight: 600 }}
      title={!Object.values(completedSteps).every(v => v) ? 'Complete all required steps before publishing' : ''}
    >
      {showSpinner ? <Spinner as="span" animation="border" size="sm" /> : 'Publish'}
    </Button>
  );
};

/**
 * TestingCompletionTracker - Tracks when testing step is complete
 * Must be inside GenerationProvider to access generation results
 */
interface TestingCompletionTrackerProps {
  onTestingComplete: () => void;
}

const TestingCompletionTracker: React.FC<TestingCompletionTrackerProps> = ({ onTestingComplete }) => {
  const { results } = useGeneration(); // Safe - inside GenerationProvider

  useEffect(() => {
    if (results && results.length > 0) {
      console.log('Generation results detected:', results.length, 'results - marking testing complete');
      onTestingComplete();
    }
  }, [results, onTestingComplete]);

  return null; // No UI - just tracks completion
};

export default function ConfigurationPage({ params }: PageProps) {
  const triggerId = params.triggerId;

  // Navigation state
  const [activeStep, setActiveStep] = useState<NavigationStep>('data');

  // Data mode state
  const [dataMode, setDataMode] = useState<DataMode>('NEW');

  // Post-generation section selection state (NEW mode only)
  const [selectedSectionIds, setSelectedSectionIds] = useState<string[]>([]);
  const [sectionOrder, setSectionOrder] = useState<string[]>([]); // Track reordered sections separately
  const [generatedDataCache, setGeneratedDataCache] = useState<Record<string, any[]>>({});

  // Prompt type selection
  const [promptTypes, setPromptTypes] = useState<Record<PromptType, boolean>>({
    paid: true, // Always checked, disabled
    unpaid: false,
    webCrawler: false
  });

  // Data panel visibility toggle for Prompt Engineering section
  const [showDataPanel, setShowDataPanel] = useState(true);

  // History panel visibility toggle for Testing step
  const [showHistoryPanel, setShowHistoryPanel] = useState(false);

  // Stock ID and data fetching
  const [stockId, setStockId] = useState('');
  const [dataStatus, setDataStatus] = useState<'notConfigured' | 'fetching' | 'ready' | 'error'>('notConfigured');

  // Fetched trigger data state
  const [triggerData, setTriggerData] = useState<any>(null); // Complete trigger object from news_triggers
  const [triggerFetched, setTriggerFetched] = useState(false); // Track if initial fetch is done

  // Data state for different modes
  const [oldData, setOldData] = useState<any>(null); // "data" node from trigger for OLD mode
  const [newSectionsData, setNewSectionsData] = useState<any[]>([]); // Generated sections for NEW mode

  // Save/publish state
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Publish modal state
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);

  // Version history modal state
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  // Workflow guide tour state
  const [showWorkflowGuide, setShowWorkflowGuide] = useState(false);

  // Completion tracking
  const [completedSteps, setCompletedSteps] = useState<Record<NavigationStep, boolean>>({
    data: false,
    sections: false,
    prompts: false,
    testing: false,
    results: false
  });

  // Transform section data based on mode for DataContext
  const selectedSections: SectionData[] = useMemo(() => {
    if (dataMode === 'OLD' && oldData) {
      // OLD mode: single section with all OLD data
      return [
        {
          section_id: 'old_data',
          section_name: 'OLD Data',
          section_title: 'OLD Data (Complete)',
          content: oldData
        }
      ];
    } else if (dataMode === 'NEW' && newSectionsData.length > 0) {
      // NEW mode: only selected sections in order
      return selectedSectionIds
        .map(id => newSectionsData.find(s => s.section_id === id))
        .filter((s): s is any => s !== undefined)
        .map(s => ({
          section_id: s.section_id,
          section_name: s.section_name,
          section_title: s.section_title,
          content: s.content
        }));
    } else if (dataMode === 'OLD_NEW' && oldData && newSectionsData.length > 0) {
      // OLD_NEW mode: OLD section first, then selected NEW sections
      const oldSection: SectionData = {
        section_id: 'old_data',
        section_name: 'OLD Data',
        section_title: 'OLD Data (Complete)',
        content: oldData
      };

      const newSections = selectedSectionIds
        .map(id => newSectionsData.find(s => s.section_id === id))
        .filter((s): s is any => s !== undefined)
        .map(s => ({
          section_id: s.section_id,
          section_name: s.section_name,
          section_title: s.section_title,
          content: s.content
        }));

      return [oldSection, ...newSections];
    }

    // Default: empty array if no data available yet
    return [];
  }, [dataMode, selectedSectionIds, newSectionsData, oldData]);

  // Load draft configuration on mount
  useEffect(() => {
    const loadDraft = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/triggers/${triggerId}/drafts/latest`);

        if (!response.ok) {
          console.warn('Failed to load draft configuration');
          return;
        }

        const result = await response.json();

        if (result.has_draft && result.draft) {
          const draft = result.draft;
          console.log('Loaded draft configuration:', draft);

          // Load data configuration if available
          if (draft.data_config) {
            const dataConfig = draft.data_config;

            // Set data mode (convert to uppercase to match frontend DataMode type)
            if (dataConfig.data_mode) {
              setDataMode(dataConfig.data_mode.toUpperCase() as DataMode);
            }

            // Set selected sections (support both new 'sections' and legacy 'selected_sections')
            const sections = dataConfig.sections || dataConfig.selected_sections;
            if (sections && Array.isArray(sections)) {
              setSelectedSectionIds(sections);
            }

            // Load section order to preserve arrangement
            if (dataConfig.section_order && Array.isArray(dataConfig.section_order)) {
              setSectionOrder(dataConfig.section_order);
            }
          }

          // Note: Prompts and model config are loaded separately through their respective contexts
          // PromptContext loads prompts via loadPrompts()
          // ModelContext loads model config via loadModelConfig()
        }
      } catch (error) {
        console.error('Error loading draft:', error);
        // Don't show error to user - it's okay if no draft exists yet
      }
    };

    loadDraft();
  }, [triggerId]);

  // Reset state when stock ID changes
  useEffect(() => {
    // Reset trigger fetch status
    setTriggerFetched(false);
    setTriggerData(null);
    setOldData(null);

    // Check if we have cached NEW data for this stock ID
    if (generatedDataCache[stockId]) {
      setNewSectionsData(generatedDataCache[stockId]);
      setSelectedSectionIds(generatedDataCache[stockId].map((s: any) => s.section_id));
    } else {
      // Clear NEW data when stock ID changes and not in cache
      setNewSectionsData([]);
      setSelectedSectionIds([]);
    }

    setDataStatus('notConfigured');
  }, [stockId]);

  // Callback for TestingCompletionTracker to mark testing step complete
  const handleTestingComplete = useCallback(() => {
    setCompletedSteps(prev => ({ ...prev, testing: true }));
  }, []);

  // Validate sections step completion
  useEffect(() => {
    if (dataMode === 'OLD' && oldData) {
      // OLD mode: sections step is complete when OLD data is available
      setCompletedSteps(prev => ({ ...prev, sections: true }));
    } else if ((dataMode === 'NEW' || dataMode === 'OLD_NEW') && selectedSectionIds.length > 0) {
      // NEW/OLD_NEW mode: sections step is complete when at least one section is selected
      setCompletedSteps(prev => ({ ...prev, sections: true }));
    } else {
      // Otherwise, mark as incomplete
      setCompletedSteps(prev => ({ ...prev, sections: false }));
    }
  }, [dataMode, oldData, selectedSectionIds]);

  // Step 3: Track prompts completion (callback from PromptEditorWrapper)
  const handlePromptsValidation = useCallback((isValid: boolean) => {
    setCompletedSteps(prev => {
      // Guard: Only update if value actually changed to prevent infinite loops
      if (prev.prompts === isValid) return prev;
      return { ...prev, prompts: isValid };
    });
  }, []);

  // Step 4: Track testing completion
  // NOTE: TestingCompletionTracker component (placed inside GenerationProvider) handles this
  // by monitoring the results array from GenerationContext. No duplicate fetch needed here.

  // Step 5: Track results completion (auto-complete when viewing results)
  useEffect(() => {
    if (activeStep === 'results') {
      // When user views results tab, mark step as complete
      setCompletedSteps(prev => ({ ...prev, results: true }));
    }
  }, [activeStep]);

  // Show workflow guide when step changes (unless user dismissed it)
  // DISABLED: User doesn't want auto-popup on every step
  // useEffect(() => {
  //   const guideDismissed = localStorage.getItem('workflow_guide_dismissed');
  //   if (!guideDismissed && activeStep) {
  //     // Show guide after a short delay to let the UI render
  //     const timer = setTimeout(() => {
  //       setShowWorkflowGuide(true);
  //     }, 500);
  //     return () => clearTimeout(timer);
  //   }
  // }, [activeStep]);

  // Handle data mode change
  const handleDataModeChange = (mode: DataMode) => {
    setDataMode(mode);
  };

  // Handle post-generation section selection
  const handleSectionSelection = (sectionIds: string[]) => {
    setSelectedSectionIds(sectionIds);
    setSectionOrder(sectionIds); // Initialize order same as selection when user manually selects
  };

  // Handle prompt type toggle
  const handlePromptTypeToggle = (type: PromptType) => {
    if (type === 'paid') return; // Can't toggle paid
    setPromptTypes(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  // Handle stock ID change (auto-fetch)
  const handleStockIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStockId(e.target.value);
  };

  const handleStockIdBlur = () => {
    // Auto-fetch removed - user must click button to generate
  };

  // Poll job status for async structured data generation
  const pollJobStatus = async (jobId: string): Promise<any[]> => {
    const maxAttempts = 60; // 5 minutes max (5s intervals)

    for (let i = 0; i < maxAttempts; i++) {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/data/structured/jobs/${jobId}`
      );

      if (!response.ok) {
        throw new Error('Failed to check job status');
      }

      const job = await response.json();

      if (job.status === 'completed') {
        return job.sections_data || [];
      } else if (job.status === 'failed') {
        throw new Error(job.error || 'Data generation failed');
      }

      // Still pending/running, wait 5 seconds
      await new Promise(resolve => setTimeout(resolve, 5000));
    }

    throw new Error('Data generation timeout (5 minutes exceeded)');
  };

  // Step 1: Fetch trigger data from news_triggers collection
  const fetchTriggerData = async () => {
    setDataStatus('fetching');
    setErrorMessage('');

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/stocks/${stockId}/trigger-data?trigger_name=${triggerId}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch trigger data: ${response.statusText}`);
      }

      const triggerDataResponse = await response.json();

      // Backend returns the "data" node directly
      setTriggerData(triggerDataResponse);
      setTriggerFetched(true);

      // Set OLD data (the response IS the data node content)
      if (triggerDataResponse) {
        setOldData(triggerDataResponse);
      }

      setDataStatus('ready');
    } catch (error) {
      console.error('Fetch trigger error:', error);
      setDataStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Failed to fetch trigger data');
    }
  };

  // Step 2: Generate NEW data (only called when NEW or OLD_NEW mode is active)
  const generateNewData = async () => {
    // Check if already in cache
    if (generatedDataCache[stockId]) {
      setNewSectionsData(generatedDataCache[stockId]);
      setSelectedSectionIds(generatedDataCache[stockId].map((s: any) => s.section_id));
      setDataStatus('ready');
      setCompletedSteps(prev => ({ ...prev, data: true }));
      return;
    }

    setDataStatus('fetching');
    setErrorMessage('');

    try {
      // Generate NEW structured data - ALWAYS generate ALL 14 sections
      const generateResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/data/structured/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stock_id: stockId,
            sections: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"] // ALL sections as strings
          })
        }
      );

      if (!generateResponse.ok) {
        throw new Error(`Failed to start data generation: ${generateResponse.statusText}`);
      }

      const { job_id } = await generateResponse.json();

      // Poll job status
      const sectionsData = await pollJobStatus(job_id);

      // Cache the generated data
      setGeneratedDataCache(prev => ({
        ...prev,
        [stockId]: sectionsData
      }));

      setNewSectionsData(sectionsData);
      setDataStatus('ready');

      // Auto-select all sections by default
      const sectionIds = sectionsData.map((s: any) => s.section_id);
      setSelectedSectionIds(sectionIds);
      setSectionOrder(sectionIds); // Initialize order same as selection

      setCompletedSteps(prev => ({ ...prev, data: true }));
    } catch (error) {
      console.error('Generate data error:', error);
      setDataStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Failed to generate data');
    }
  };

  // Handle data mode change - update completion status
  useEffect(() => {
    if (dataMode === 'OLD' && oldData) {
      setCompletedSteps(prev => ({ ...prev, data: true }));
    } else if (dataMode === 'NEW' && newSectionsData.length > 0) {
      setCompletedSteps(prev => ({ ...prev, data: true }));
    } else if (dataMode === 'OLD_NEW' && oldData && newSectionsData.length > 0) {
      setCompletedSteps(prev => ({ ...prev, data: true }));
    } else {
      setCompletedSteps(prev => ({ ...prev, data: false }));
    }
  }, [dataMode, oldData, newSectionsData]);

  // Save draft - accepts context data from inner components that have provider access
  const handleSaveDraft = async (contextData?: {
    prompts?: any;
    variantStrategy?: string;
    selectedModels?: string[]; // Array for testing multiple models
    temperature?: number;
    maxTokens?: number;
  }) => {
    setSaveStatus('saving');
    setErrorMessage('');

    try {
      // Build complete draft payload from passed context data
      const draftPayload = {
        prompts: {
          paid: { template: contextData?.prompts?.paid?.content || '' },
          unpaid: { template: contextData?.prompts?.unpaid?.content || '' },
          crawler: { template: contextData?.prompts?.crawler?.content || '' }
        },
        llm_config: {
          selected_models: contextData?.selectedModels || [], // Array for testing multiple models
          temperature: contextData?.temperature ?? 0.7,
          max_tokens: contextData?.maxTokens ?? 1000
        },
        data_config: {
          sections: dataMode === 'OLD_NEW'
            ? ['old_data', ...selectedSectionIds]  // Include OLD section for OLD_NEW mode
            : selectedSectionIds,
          section_order: sectionOrder.length > 0
            ? sectionOrder
            : (dataMode === 'OLD_NEW'
                ? ['old_data', ...selectedSectionIds]  // Default order includes OLD section
                : selectedSectionIds),
          data_mode: dataMode.toLowerCase()  // Convert to lowercase to match backend enum
        },
        variant_strategy: contextData?.variantStrategy || 'all_same',
        saved_by: "system" // TODO: Replace with actual user ID when auth is implemented
      };

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/triggers/${triggerId}/drafts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(draftPayload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to save draft');
      }

      const result = await response.json();
      console.log('Draft saved:', result);

      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Save draft error:', error);
      setSaveStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Failed to save draft');
    }
  };

  // Open publish modal
  const handlePublish = () => {
    const allStepsCompleted = Object.values(completedSteps).every(v => v);
    if (!allStepsCompleted) {
      alert('Complete all required steps before publishing');
      return;
    }

    // Show publish confirmation modal
    setShowPublishModal(true);
  };

  // Confirm and execute publish
  const handleConfirmPublish = async (publishData: any) => {
    setIsPublishing(true);
    setErrorMessage('');

    try {
      // Call the publish endpoint which copies draft to production
      // Send selected_model to override the models from draft
      const requestBody: any = {
        published_by: publishData.published_by || "system",
        notes: publishData.notes
      };

      // If user selected a specific model for production, send it
      if (publishData.selected_model) {
        requestBody.model_settings = {
          selected_models: [publishData.selected_model], // Single model array
          temperature: publishData.model_settings?.temperature || 0.7,
          max_tokens: publishData.model_settings?.max_tokens || 1000
        };
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/triggers/${triggerId}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to publish configuration');
      }

      const result = await response.json();
      console.log('Configuration published:', result);

      setIsPublishing(false);
      setShowPublishModal(false);
      setSaveStatus('success');
      alert(`Configuration published successfully! Version ${result.draft_version_published} is now live.`);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Publish error:', error);
      setIsPublishing(false);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to publish configuration');
    }
  };

  // Sidebar navigation items
  const navigationItems = [
    { id: 'data' as NavigationStep, icon: 'bi-database', label: 'Data Configuration' },
    { id: 'sections' as NavigationStep, icon: 'bi-list-ul', label: 'Section Management' },
    { id: 'prompts' as NavigationStep, icon: 'bi-code-slash', label: 'Prompt Engineering' },
    { id: 'testing' as NavigationStep, icon: 'bi-beaker', label: 'Model Testing' },
    { id: 'results' as NavigationStep, icon: 'bi-columns-gap', label: 'Results & Comparison' }
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f8f9fa' }}>
      {/* Breadcrumb */}
      <div style={{
        background: '#ffffff',
        borderBottom: '1px solid #dee2e6',
        padding: '8px 24px'
      }}>
        <div style={{ fontSize: '14px', color: '#6c757d' }}>
          <span style={{ color: '#0d6efd', cursor: 'pointer' }}>Dashboard</span>
          <span style={{ margin: '0 8px', color: '#adb5bd' }}>&gt;</span>
          <span style={{ color: '#0d6efd', cursor: 'pointer' }}>{triggerId}</span>
          <span style={{ margin: '0 8px', color: '#adb5bd' }}>&gt;</span>
          <span>{navigationItems.find(item => item.id === activeStep)?.label}</span>
        </div>
      </div>

      {/* Main Layout */}
      <div style={{ display: 'flex', flex: 1 }}>
        {/* Left Sidebar */}
        <div style={{
          width: '280px',
          background: '#ffffff',
          borderRight: '1px solid #dee2e6',
          padding: '24px 16px',
          height: 'calc(100vh - 42px)',
          position: 'sticky',
          top: 0
        }}>
          <div style={{
            fontSize: '14px',
            textTransform: 'uppercase',
            fontWeight: 600,
            color: '#6c757d',
            marginBottom: '24px'
          }}>
            Configuration Steps
          </div>

          {navigationItems.map(item => (
            <div
              key={item.id}
              onClick={() => setActiveStep(item.id)}
              style={{
                padding: '12px 16px',
                marginBottom: '16px',
                borderRadius: '4px',
                cursor: 'pointer',
                background: activeStep === item.id ? '#e7f1ff' : 'transparent',
                borderLeft: activeStep === item.id ? '3px solid #0d6efd' : '3px solid transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <i className={`bi ${item.icon}`} style={{
                  fontSize: '16px',
                  color: activeStep === item.id ? '#0d6efd' : '#6c757d'
                }}></i>
                <span style={{
                  fontSize: '14px',
                  fontWeight: activeStep === item.id ? 500 : 400,
                  color: activeStep === item.id ? '#0d6efd' : '#212529'
                }}>
                  {item.label}
                </span>
              </div>
              {completedSteps[item.id] && (
                <i className="bi bi-check-circle-fill" style={{
                  fontSize: '16px',
                  color: '#198754'
                }}></i>
              )}
            </div>
          ))}
        </div>

        {/* Main Content Area - Wrap with all context providers */}
        {/* Provider order: PromptProvider > GenerationProvider > ModelProvider */}
        {/* ModelProvider needs PromptContext for cost estimation (checkedTypes) */}
        <PromptProvider>
          <GenerationProvider>
            <ModelProvider triggerId={triggerId}>
              {/* Set triggerId to trigger auto-load */}
              <TriggerIdSetter triggerId={triggerId} />
              {/* Track testing completion based on generation results */}
              <TestingCompletionTracker onTestingComplete={handleTestingComplete} />

              <div style={{ flex: 1, padding: '32px', paddingBottom: '100px' }}>
            {/* Trigger Context Bar */}
          <div style={{
            background: '#ffffff',
            borderRadius: '8px',
            padding: '20px 24px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
            marginBottom: '24px'
          }}>
            {/* Top Row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              {/* Trigger Info */}
              <div>
                <div style={{ fontSize: '20px', fontWeight: 600, color: '#212529' }}>
                  {triggerId}
                </div>
                <div style={{ fontSize: '14px', color: '#6c757d', marginTop: '4px' }}>
                  Last published: 2 days ago (v1.2)
                </div>
              </div>

              {/* Stock ID Input */}
              <div>
                <label style={{ fontSize: '12px', color: '#6c757d', display: 'block', marginBottom: '4px' }}>
                  Test Stock ID
                </label>
                <Form.Control
                  type="text"
                  value={stockId}
                  onChange={handleStockIdChange}
                  onBlur={handleStockIdBlur}
                  placeholder="Enter stock ID (e.g., TCS)"
                  style={{ width: '200px', height: '40px' }}
                />
              </div>

              {/* Status Badge */}
              <div>
                {dataStatus === 'notConfigured' && (
                  <Badge bg="secondary" style={{ padding: '6px 12px', borderRadius: '12px' }}>
                    Configure Data
                  </Badge>
                )}
                {dataStatus === 'fetching' && (
                  <Badge bg="info" style={{ padding: '6px 12px', borderRadius: '12px' }}>
                    <Spinner as="span" animation="border" size="sm" className="me-2" />
                    Fetching Data...
                  </Badge>
                )}
                {dataStatus === 'ready' && (
                  <div>
                    <Badge bg="success" style={{ padding: '6px 12px', borderRadius: '12px' }}>
                      <i className="bi bi-check-circle-fill me-2"></i>
                      Data Ready
                    </Badge>
                    <span style={{ fontSize: '12px', color: '#6c757d', marginLeft: '8px' }}>
                      for {stockId}
                    </span>
                  </div>
                )}
                {dataStatus === 'error' && (
                  <Badge bg="danger" style={{ padding: '6px 12px', borderRadius: '12px' }}>
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    Configuration Error
                  </Badge>
                )}
              </div>
            </div>

            {/* Divider */}
            <hr style={{ margin: '16px 0 12px 0', border: 'none', borderTop: '1px solid #dee2e6' }} />

            {/* Prompt Type Selection */}
            <div>
              <div style={{ fontSize: '14px', fontWeight: 500, color: '#6c757d', marginBottom: '8px' }}>
                Prompt Types
              </div>
              <div style={{ display: 'flex', gap: '24px' }}>
                {/* Paid */}
                <Form.Check
                  type="checkbox"
                  id="type-paid"
                  checked={promptTypes.paid}
                  disabled
                  label={
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '16px' }}>💰</span>
                      <span style={{ fontSize: '14px', fontWeight: 600 }}>Paid</span>
                      <Badge bg="light" text="primary" style={{ fontSize: '12px', padding: '2px 6px' }}>
                        Default
                      </Badge>
                    </span>
                  }
                />
                {/* Unpaid */}
                <Form.Check
                  type="checkbox"
                  id="type-unpaid"
                  checked={promptTypes.unpaid}
                  onChange={() => handlePromptTypeToggle('unpaid')}
                  label={
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '16px' }}>🆓</span>
                      <span style={{ fontSize: '14px' }}>Unpaid</span>
                    </span>
                  }
                />
                {/* Web Crawler */}
                <Form.Check
                  type="checkbox"
                  id="type-webcrawler"
                  checked={promptTypes.webCrawler}
                  onChange={() => handlePromptTypeToggle('webCrawler')}
                  label={
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '16px' }}>🕷️</span>
                      <span style={{ fontSize: '14px' }}>Web Crawler</span>
                    </span>
                  }
                />
              </div>
              <div style={{ fontSize: '12px', fontStyle: 'italic', color: '#6c757d', marginTop: '8px' }}>
                Select the prompt types to configure and test. Paid is always included.
              </div>
            </div>
          </div>

          {/* Content Panels based on active step */}
          {activeStep === 'data' && (
            <>
              {/* Step 1: Fetch Trigger Data - ALWAYS FIRST */}
              {!triggerFetched && (
                <div style={{
                  background: '#ffffff',
                  borderRadius: '8px',
                  padding: '24px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  marginBottom: '24px'
                }}>
                  <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Step 1: Fetch Trigger Data
                  </h2>
                  <p style={{ fontSize: '14px', color: '#6c757d', marginBottom: '24px' }}>
                    First, fetch the existing trigger data from the <strong>news_triggers</strong> collection using Stock ID and Trigger Name.
                    This is required before you can select a data mode.
                  </p>

                  {!stockId && (
                    <Alert variant="warning" style={{
                      background: '#fff3cd',
                      borderLeft: '3px solid #ffc107',
                      marginBottom: '16px'
                    }}>
                      <i className="bi bi-exclamation-triangle me-2"></i>
                      Enter a Stock ID above to continue
                    </Alert>
                  )}

                  <Alert variant="info" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      <strong>What happens:</strong> The system will fetch the trigger document for <Badge bg="secondary">{triggerId}</Badge> and Stock ID <Badge bg="secondary">{stockId || '...'}</Badge>.
                      This contains the "data" node which can be used in OLD mode.
                    </small>
                  </Alert>

                  <Button
                    variant="primary"
                    size="lg"
                    onClick={fetchTriggerData}
                    disabled={!stockId || dataStatus === 'fetching'}
                    style={{
                      width: '220px',
                      height: '56px',
                      fontSize: '16px',
                      fontWeight: 600
                    }}
                  >
                    {dataStatus === 'fetching' ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" className="me-2" />
                        Fetching Trigger...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-database me-2"></i>
                        Fetch Trigger Data
                      </>
                    )}
                  </Button>

                  {!stockId && (
                    <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '12px', fontStyle: 'italic' }}>
                      Please enter a Stock ID in the trigger context bar above
                    </div>
                  )}
                </div>
              )}

              {/* Step 2: Data Mode Selection - AFTER TRIGGER FETCH */}
              {triggerFetched && (
                <div style={{
                  background: '#ffffff',
                  borderRadius: '8px',
                  padding: '24px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  marginBottom: '24px'
                }}>
                  <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Step 2: Select Data Mode
                  </h2>
                  <Alert variant="success" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-check-circle-fill me-2"></i>
                    <small>
                      Trigger data fetched successfully! Now choose how you want to view/use the data.
                    </small>
                  </Alert>
                  <Alert variant="info" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      <strong>OLD:</strong> Show only the "data" node from fetched trigger (read-only)<br />
                      <strong>NEW:</strong> Generate complete structured report (14 sections), select which to use<br />
                      <strong>OLD_NEW:</strong> Show both OLD data and NEW selected sections in separate panels
                    </small>
                  </Alert>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                    <Button
                      variant={dataMode === 'OLD' ? 'primary' : 'outline-primary'}
                      size="lg"
                      onClick={() => handleDataModeChange('OLD')}
                    >
                      <i className="bi bi-archive me-2"></i>
                      OLD
                      {dataMode === 'OLD' && <i className="bi bi-check-circle-fill ms-2"></i>}
                    </Button>

                    <Button
                      variant={dataMode === 'NEW' ? 'success' : 'outline-success'}
                      size="lg"
                      onClick={() => handleDataModeChange('NEW')}
                    >
                      <i className="bi bi-stars me-2"></i>
                      NEW
                      {dataMode === 'NEW' && <i className="bi bi-check-circle-fill ms-2"></i>}
                    </Button>

                    <Button
                      variant={dataMode === 'OLD_NEW' ? 'warning' : 'outline-warning'}
                      size="lg"
                      onClick={() => handleDataModeChange('OLD_NEW')}
                    >
                      <i className="bi bi-layers me-2"></i>
                      OLD_NEW
                      {dataMode === 'OLD_NEW' && <i className="bi bi-check-circle-fill ms-2"></i>}
                    </Button>
                  </div>
                </div>
              )}

              {/* Step 3: Generate/Display Data Based on Mode (Read-Only Preview) */}

              {/* OLD Mode - Display "data" node from trigger */}
              {triggerFetched && dataMode === 'OLD' && oldData && (
                <div style={{marginBottom: '24px'}}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Data Preview (Read-Only)
                  </h3>
                  <OldDataDisplay data={oldData} stockId={stockId} triggerId={triggerId} />
                  <Alert variant="info" style={{ marginTop: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      This is a preview of the OLD data. In OLD mode, this entire data structure will be treated as one section.
                      Click "Use This Data" to proceed to section management.
                    </small>
                  </Alert>

                  {/* Use This Data Button */}
                  <div style={{ marginTop: '24px', textAlign: 'center' }}>
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={() => {
                        setActiveStep('sections');
                        setCompletedSteps(prev => ({ ...prev, data: true, sections: false }));
                      }}
                      style={{
                        width: '300px',
                        height: '56px',
                        fontSize: '16px',
                        fontWeight: 600
                      }}
                    >
                      <i className="bi bi-check-circle me-2"></i>
                      Use This Data
                    </Button>
                  </div>
                </div>
              )}

              {/* NEW Mode - Generate Button (if not generated yet) */}
              {triggerFetched && dataMode === 'NEW' && newSectionsData.length === 0 && (
                <div style={{
                  background: '#ffffff',
                  borderRadius: '8px',
                  padding: '24px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  marginBottom: '24px'
                }}>
                  <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Step 3: Generate Structured Report
                  </h2>
                  <p style={{ fontSize: '14px', color: '#6c757d', marginBottom: '24px' }}>
                    Generate a complete structured report with ALL 14 sections. Once generated, you can select which sections to use.
                  </p>

                  <Alert variant="info" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      <strong>How it works:</strong> The system will generate ALL 14 sections using <code>generate_full_report.py</code>.
                      This takes approximately 8-15 seconds. Data is cached - regeneration only happens if you change the stock ID.
                    </small>
                  </Alert>

                  <Button
                    variant="success"
                    size="lg"
                    onClick={generateNewData}
                    disabled={dataStatus === 'fetching'}
                    style={{
                      width: '250px',
                      height: '56px',
                      fontSize: '16px',
                      fontWeight: 600
                    }}
                  >
                    {dataStatus === 'fetching' ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" className="me-2" />
                        Generating Report...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-file-earmark-plus me-2"></i>
                        Generate Complete Report
                      </>
                    )}
                  </Button>

                  {generatedDataCache[stockId] && (
                    <Alert variant="success" style={{ marginTop: '16px' }}>
                      <i className="bi bi-check-circle-fill me-2"></i>
                      <small>
                        <strong>Cached data available:</strong> A report for stock ID "{stockId}" was previously generated.
                        Click "Generate Complete Report" to use the cached data.
                      </small>
                    </Alert>
                  )}
                </div>
              )}

              {/* NEW Mode - Section Selection & Display */}
              {triggerFetched && dataMode === 'NEW' && newSectionsData.length > 0 && (
                <div style={{marginBottom: '24px'}}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Section Selection & Preview
                  </h3>
                  <Alert variant="info" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      <strong>All {newSectionsData.length} sections generated successfully!</strong>
                      {' '}Select which sections to use, then click "Use This Data" to proceed to section ordering.
                    </small>
                  </Alert>
                  <NewDataDisplay
                    sections={newSectionsData}
                    stockId={stockId}
                    selectedSectionIds={selectedSectionIds}
                    onSelectionChange={handleSectionSelection}
                    showSelection={true}  // Show checkboxes for selection
                  />

                  {/* Use This Data Button */}
                  {selectedSectionIds.length > 0 && (
                    <div style={{ marginTop: '24px', textAlign: 'center' }}>
                      <Button
                        variant="primary"
                        size="lg"
                        onClick={() => {
                          setActiveStep('sections');
                          setCompletedSteps(prev => ({ ...prev, data: true, sections: false }));
                        }}
                        style={{
                          width: '300px',
                          height: '56px',
                          fontSize: '16px',
                          fontWeight: 600
                        }}
                      >
                        <i className="bi bi-check-circle me-2"></i>
                        Use This Data ({selectedSectionIds.length} sections)
                      </Button>
                    </div>
                  )}
                </div>
              )}

              {/* OLD_NEW Mode - Generate Button (if not generated yet) */}
              {triggerFetched && dataMode === 'OLD_NEW' && newSectionsData.length === 0 && (
                <div style={{
                  background: '#ffffff',
                  borderRadius: '8px',
                  padding: '24px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                  marginBottom: '24px'
                }}>
                  <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Step 3: Generate NEW Data
                  </h2>
                  <p style={{ fontSize: '14px', color: '#6c757d', marginBottom: '24px' }}>
                    Generate NEW structured report to display alongside OLD data. Both will be shown in separate panels.
                  </p>

                  <Alert variant="info" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      Generates ALL 14 sections using <code>generate_full_report.py</code>. Takes 8-15 seconds.
                    </small>
                  </Alert>

                  <Button
                    variant="success"
                    size="lg"
                    onClick={generateNewData}
                    disabled={dataStatus === 'fetching'}
                    style={{
                      width: '250px',
                      height: '56px',
                      fontSize: '16px',
                      fontWeight: 600
                    }}
                  >
                    {dataStatus === 'fetching' ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" className="me-2" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-file-earmark-plus me-2"></i>
                        Generate NEW Report
                      </>
                    )}
                  </Button>

                  {generatedDataCache[stockId] && (
                    <Alert variant="success" style={{ marginTop: '16px' }}>
                      <i className="bi bi-check-circle-fill me-2"></i>
                      <small>Cached data available for this stock ID</small>
                    </Alert>
                  )}
                </div>
              )}

              {/* OLD_NEW Mode - Display BOTH with Section Selection */}
              {triggerFetched && dataMode === 'OLD_NEW' && newSectionsData.length > 0 && oldData && (
                <>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                    Data Preview - OLD + NEW
                  </h3>
                  <Alert variant="info" style={{ marginBottom: '16px' }}>
                    <i className="bi bi-info-circle me-2"></i>
                    <small>
                      Both OLD and NEW data are available. Select which NEW sections to use, then click "Use This Data".
                      In Section Management, you'll be able to arrange OLD data and selected NEW sections together.
                    </small>
                  </Alert>

                  <div style={{marginBottom: '24px'}}>
                    <h4 style={{ fontSize: '16px', fontWeight: 600, color: '#495057', marginBottom: '12px' }}>
                      OLD Data (Preview)
                    </h4>
                    <OldDataDisplay data={oldData} stockId={stockId} triggerId={triggerId} />
                  </div>

                  <div style={{marginBottom: '24px'}}>
                    <h4 style={{ fontSize: '16px', fontWeight: 600, color: '#495057', marginBottom: '12px' }}>
                      NEW Generated Data - Select Sections
                    </h4>
                    <NewDataDisplay
                      sections={newSectionsData}
                      stockId={stockId}
                      selectedSectionIds={selectedSectionIds}
                      onSelectionChange={handleSectionSelection}
                      showSelection={true}  // Show checkboxes for selection
                    />
                  </div>

                  {/* Use This Data Button */}
                  {selectedSectionIds.length > 0 && (
                    <div style={{ marginTop: '24px', textAlign: 'center' }}>
                      <Button
                        variant="primary"
                        size="lg"
                        onClick={() => {
                          setActiveStep('sections');
                          setCompletedSteps(prev => ({ ...prev, data: true, sections: false }));
                        }}
                        style={{
                          width: '350px',
                          height: '56px',
                          fontSize: '16px',
                          fontWeight: 600
                        }}
                      >
                        <i className="bi bi-check-circle me-2"></i>
                        Use This Data (OLD + {selectedSectionIds.length} NEW sections)
                      </Button>
                    </div>
                  )}
                </>
              )}
            </>
          )}

          {activeStep === 'sections' && (
            <>
              <div style={{
                background: '#ffffff',
                borderRadius: '8px',
                padding: '24px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                marginBottom: '24px'
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                  Section Management & Configuration
                </h2>

                {/* Show warning if no data fetched */}
                {!oldData && newSectionsData.length === 0 && (
                  <Alert variant="warning">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    No data fetched yet. Please go back to <strong>Data Configuration</strong> step and fetch data first.
                  </Alert>
                )}

                {/* OLD Mode - Show OLD data as a section */}
                {dataMode === 'OLD' && oldData && (
                  <>
                    <Alert variant="info" style={{ marginBottom: '16px' }}>
                      <i className="bi bi-info-circle me-2"></i>
                      <small>
                        <strong>OLD mode:</strong> The entire OLD data structure is treated as one section.
                        No reordering needed. You can proceed to configure prompts.
                      </small>
                    </Alert>

                    {/* Show OLD section in management panel */}
                    <div style={{ marginTop: '16px' }}>
                      <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                        Section Order
                      </h3>
                      <SectionManagementPanel
                        sections={[
                          {
                            id: 'old_data',
                            name: 'OLD Data (Complete)',
                            source: 'old' as const
                          }
                        ]}
                        onSectionsChange={() => {}}  // Read-only for OLD mode
                      />

                      {/* Use This Arrangement Button - OLD Mode */}
                      <div style={{ marginTop: '32px', display: 'flex', justifyContent: 'center' }}>
                        <Button
                          variant="primary"
                          size="lg"
                          onClick={async () => {
                            // Save configuration before navigating
                            await handleSaveDraft();
                            setCompletedSteps(prev => ({ ...prev, sections: true }));
                            setActiveStep('prompts');
                          }}
                          disabled={!oldData}
                          style={{
                            width: '320px',
                            height: '56px',
                            fontSize: '18px',
                            fontWeight: 600
                          }}
                        >
                          <i className="bi bi-check-circle me-2"></i>
                          Use This Arrangement
                        </Button>
                      </div>
                    </div>
                  </>
                )}

                {/* NEW Mode - Show selected NEW sections only */}
                {dataMode === 'NEW' && newSectionsData.length > 0 && selectedSectionIds.length > 0 && (() => {
                  // Build Section[] from selected IDs and generated data
                  // Use sectionOrder if available to preserve user's drag-and-drop arrangement
                  const orderToUse = sectionOrder.length > 0 ? sectionOrder : selectedSectionIds;
                  const selectedSections = orderToUse
                    .map(sectionId => {
                      const sectionData = newSectionsData.find(s => s.section_id === sectionId);
                      if (!sectionData) return null;
                      return {
                        id: sectionData.section_id,
                        name: sectionData.section_title || `Section ${sectionData.section_id}`,
                        source: 'new' as const
                      };
                    })
                    .filter((s): s is Section => s !== null);

                  return (
                    <>
                      <Alert variant="info" style={{ marginBottom: '16px' }}>
                        <i className="bi bi-arrows-move me-2"></i>
                        <small>
                          Drag and drop sections below to set their order in the final output.
                        </small>
                      </Alert>

                      <div>
                        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                          Section Order ({selectedSections.length} sections)
                        </h3>
                        <SectionManagementPanel
                          sections={selectedSections}
                          onSectionsChange={(reorderedSections) => {
                            // Update section order when user rearranges sections
                            const newOrder = reorderedSections.map(s => s.id);
                            setSectionOrder(newOrder);
                            // Keep selectedSectionIds as the original selection (not reordered)
                            // This allows us to track which sections are selected vs their order
                          }}
                        />

                        {/* Use This Arrangement Button - NEW Mode */}
                        <div style={{ marginTop: '32px', display: 'flex', justifyContent: 'center' }}>
                          <Button
                            variant="primary"
                            size="lg"
                            onClick={async () => {
                              // Save section order before navigating
                              await handleSaveDraft();
                              setCompletedSteps(prev => ({ ...prev, sections: true }));
                              setActiveStep('prompts');
                            }}
                            disabled={selectedSectionIds.length === 0}
                            style={{
                              width: '320px',
                              height: '56px',
                              fontSize: '18px',
                              fontWeight: 600
                            }}
                          >
                            <i className="bi bi-check-circle me-2"></i>
                            Use This Arrangement
                          </Button>
                        </div>
                      </div>
                    </>
                  );
                })()}

                {/* OLD_NEW Mode - Show OLD section + selected NEW sections */}
                {dataMode === 'OLD_NEW' && oldData && newSectionsData.length > 0 && selectedSectionIds.length > 0 && (() => {
                  // Build combined Section[] with OLD data + NEW sections
                  const oldSection: Section = {
                    id: 'old_data',
                    name: 'OLD Data (Complete)',
                    source: 'old' as const
                  };

                  // Use sectionOrder if available to preserve user's drag-and-drop arrangement
                  // sectionOrder includes both 'old_data' and NEW section IDs in the desired order
                  let allSections: Section[];

                  if (sectionOrder.length > 0) {
                    // Build sections from sectionOrder (preserves user's arrangement)
                    allSections = sectionOrder
                      .map(sectionId => {
                        if (sectionId === 'old_data') {
                          return oldSection;
                        }
                        const sectionData = newSectionsData.find(s => s.section_id === sectionId);
                        if (!sectionData) return null;
                        return {
                          id: sectionData.section_id,
                          name: sectionData.section_title || `Section ${sectionData.section_id}`,
                          source: 'new' as const
                        };
                      })
                      .filter((s): s is Section => s !== null);
                  } else {
                    // Default order: OLD section first, then NEW sections
                    const newSections = selectedSectionIds
                      .map(sectionId => {
                        const sectionData = newSectionsData.find(s => s.section_id === sectionId);
                        if (!sectionData) return null;
                        return {
                          id: sectionData.section_id,
                          name: sectionData.section_title || `Section ${sectionData.section_id}`,
                          source: 'new' as const
                        };
                      })
                      .filter((s): s is Section => s !== null);
                    allSections = [oldSection, ...newSections];
                  }

                  return (
                    <>
                      <Alert variant="info" style={{ marginBottom: '16px' }}>
                        <i className="bi bi-arrows-move me-2"></i>
                        <small>
                          <strong>OLD_NEW mode:</strong> Arrange the order of OLD data section and NEW sections below.
                          Drag and drop to change their relative positions.
                        </small>
                      </Alert>

                      <div>
                        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                          Section Order (1 OLD + {selectedSectionIds.length} NEW sections)
                        </h3>
                        <SectionManagementPanel
                          sections={allSections}
                          onSectionsChange={(reorderedSections) => {
                            // Save complete order including OLD section position
                            const completeOrder = reorderedSections.map(s => s.id);
                            setSectionOrder(completeOrder);
                            // This preserves the position of 'old_data' section in the arrangement
                          }}
                        />

                        {/* Use This Arrangement Button - OLD_NEW Mode */}
                        <div style={{ marginTop: '32px', display: 'flex', justifyContent: 'center' }}>
                          <Button
                            variant="primary"
                            size="lg"
                            onClick={async () => {
                              // Save section order before navigating
                              await handleSaveDraft();
                              setCompletedSteps(prev => ({ ...prev, sections: true }));
                              setActiveStep('prompts');
                            }}
                            disabled={!oldData || selectedSectionIds.length === 0}
                            style={{
                              width: '320px',
                              height: '56px',
                              fontSize: '18px',
                              fontWeight: 600
                            }}
                          >
                            <i className="bi bi-check-circle me-2"></i>
                            Use This Arrangement
                          </Button>
                        </div>
                      </div>
                    </>
                  );
                })()}

                {/* Warning if no selections made in NEW/OLD_NEW modes */}
                {(dataMode === 'NEW' || dataMode === 'OLD_NEW') && selectedSectionIds.length === 0 && (
                  <Alert variant="warning">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    <small>
                      No sections selected yet. Please go back to <strong>Data Configuration</strong> and select sections to use.
                    </small>
                  </Alert>
                )}
              </div>
            </>
          )}

          {activeStep === 'prompts' && (
            <div style={{
              background: '#ffffff',
              borderRadius: '8px',
              padding: '24px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.08)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', margin: 0 }}>
                  Prompt Engineering
                </h2>
                <Button
                  variant="outline-secondary"
                  size="sm"
                  onClick={() => setShowDataPanel(!showDataPanel)}
                >
                  <i className={`bi bi-${showDataPanel ? 'eye-slash' : 'eye'} me-1`}></i>
                  {showDataPanel ? 'Hide' : 'Show'} Data Preview
                </Button>
              </div>

              <Alert variant="info" style={{ marginBottom: '24px' }}>
                <i className="bi bi-info-circle me-2"></i>
                <strong>Prompt Type Selection:</strong> Configure which prompt types you want to use.
                The Paid prompt is required and always active. Unpaid and Crawler prompts are optional.
              </Alert>

              {/* Prompt Type Checkboxes */}
              <div style={{ marginBottom: '24px' }}>
                <h5 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px' }}>
                  Select Prompt Types
                </h5>
                <Form.Check
                  type="checkbox"
                  id="prompt-paid"
                  label="💰 Paid (Required)"
                  checked={true}
                  disabled
                  style={{ marginBottom: '8px' }}
                />
                <Form.Check
                  type="checkbox"
                  id="prompt-unpaid"
                  label="🆓 Unpaid"
                  checked={promptTypes.unpaid}
                  onChange={(e) => setPromptTypes({ ...promptTypes, unpaid: e.target.checked })}
                  style={{ marginBottom: '8px' }}
                />
                <Form.Check
                  type="checkbox"
                  id="prompt-crawler"
                  label="🕷️ Crawler"
                  checked={promptTypes.webCrawler}
                  onChange={(e) => setPromptTypes({ ...promptTypes, webCrawler: e.target.checked })}
                />
              </div>

              {/* Variant Strategy Selector */}
              <VariantStrategySelector />

              {/* Two-column layout: Data Display + Prompt Editor */}
              <Row>
                {showDataPanel && (
                  <Col lg={5} style={{ marginBottom: '24px' }}>
                    <DataPreviewPanel
                      dataMode={dataMode}
                      oldData={oldData}
                      stockId={stockId}
                      triggerId={triggerId}
                      newSectionsData={newSectionsData}
                      selectedSectionIds={selectedSectionIds}
                      selectedSections={selectedSections}
                    />
                  </Col>
                )}

                <Col lg={showDataPanel ? 7 : 12}>
                  {/* Prompt Editor with Monaco */}
                  <PromptEditorWrapper
                    triggerId={triggerId}
                    checkedTypes={promptTypes}
                    selectedSectionIds={selectedSectionIds}
                    newSectionsData={newSectionsData}
                    oldData={oldData}
                    dataMode={dataMode}
                    stockId={stockId}
                    selectedSections={selectedSections}
                    onValidationChange={handlePromptsValidation}
                  />
                </Col>
              </Row>
            </div>
          )}

          {activeStep === 'testing' && (
            <DataProvider
              selectedSections={selectedSections}
              dataMode={dataMode}
              stockId={stockId}
              triggerId={triggerId}
            >
              <TestingStepWrapper promptTypes={promptTypes}>
                {/* Toggle History Button */}
                <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant={showHistoryPanel ? 'primary' : 'outline-secondary'}
                    size="sm"
                    onClick={() => setShowHistoryPanel(!showHistoryPanel)}
                  >
                    <i className={`bi bi-clock-history me-1`}></i>
                    {showHistoryPanel ? 'Hide History' : 'View History'}
                  </Button>
                </div>

                <ModelSelection />
                <TestGenerationPanel />

                {/* History Panel */}
                {showHistoryPanel && (
                  <GenerationHistoryPanel
                    triggerId={triggerId}
                    onLoadConfiguration={(item) => {
                      // TODO: Implement loading configuration from history item
                      // This would populate the model selection, temperature, max_tokens
                      // from the history item
                      console.log('Load configuration from history:', item);
                      alert('Load configuration feature coming soon! Check console for history item.');
                    }}
                  />
                )}
              </TestingStepWrapper>
            </DataProvider>
          )}

          {activeStep === 'results' && (
            <ResultsStepWrapper
              triggerName={triggerId}
              onNavigateToTesting={() => setActiveStep('testing')}
            />
          )}

          {/* Publish Modal - inside providers */}
          <PublishModalWrapperInner
            show={showPublishModal}
            onHide={() => setShowPublishModal(false)}
            triggerName={triggerId}
            dataMode={dataMode}
            selectedSectionIds={selectedSectionIds}
            sectionOrder={sectionOrder}
            newSectionsData={newSectionsData}
            onConfirm={handleConfirmPublish}
            isPublishing={isPublishing}
          />

          {/* Sticky Bottom Actions Bar - inside providers so DraftSaveButton can access context */}
          <div style={{
            position: 'fixed',
            bottom: 0,
            left: '280px',
            right: 0,
            height: '72px',
            background: '#ffffff',
            borderTop: '1px solid #dee2e6',
            padding: '16px 32px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            boxShadow: '0 -2px 8px rgba(0,0,0,0.05)',
            zIndex: 1000
          }}>
            <div style={{ display: 'flex', gap: '16px' }}>
              <DraftSaveButton onSave={handleSaveDraft} saveStatus={saveStatus} />
              <Button
                variant="outline-secondary"
                onClick={() => setShowHistoryModal(true)}
                style={{ width: '120px', height: '40px' }}
              >
                View History
              </Button>
            </div>

            <PublishButton
              onPublish={handleSaveDraft}
              onOpenModal={() => setShowPublishModal(true)}
              disabled={!Object.values(completedSteps).every(v => v)}
              saveStatus={saveStatus}
              completedSteps={completedSteps}
            />
          </div>
          </div>
            </ModelProvider>
          </GenerationProvider>
        </PromptProvider>
      </div>

      {/* Success/Error Alerts */}
      {saveStatus === 'success' && (
        <Alert
          variant="success"
          dismissible
          onClose={() => setSaveStatus('idle')}
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 2000,
            minWidth: '300px'
          }}
        >
          <i className="bi bi-check-circle-fill me-2"></i>
          Configuration saved successfully!
        </Alert>
      )}

      {saveStatus === 'error' && (
        <Alert
          variant="danger"
          dismissible
          onClose={() => setSaveStatus('idle')}
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 2000,
            minWidth: '300px'
          }}
        >
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {errorMessage || 'An error occurred'}
        </Alert>
      )}

      {/* Version History Modal */}
      <ConfigVersionHistoryModal
        show={showHistoryModal}
        onHide={() => setShowHistoryModal(false)}
        triggerName={triggerId}
        onRollbackSuccess={() => {
          setShowHistoryModal(false);
          // Optionally reload the page or refresh data after rollback
          window.location.reload();
        }}
      />

      {/* Workflow Guide Tour */}
      <WorkflowGuideTour
        currentStep={activeStep}
        show={showWorkflowGuide}
        onClose={() => setShowWorkflowGuide(false)}
        onNext={() => {
          // Optionally navigate to next step
          const stepOrder: NavigationStep[] = ['data', 'sections', 'prompts', 'testing', 'results'];
          const currentIndex = stepOrder.indexOf(activeStep);
          if (currentIndex < stepOrder.length - 1) {
            setActiveStep(stepOrder[currentIndex + 1]);
          }
        }}
      />

    </div>
  );
}

// Wrapper component to handle PromptProvider context
interface PromptEditorWrapperProps {
  triggerId: string;
  checkedTypes: Record<PromptType, boolean>;
  selectedSectionIds: string[];
  newSectionsData: any[];
  oldData: any;
  dataMode: DataMode;
  stockId: string;
  selectedSections: SectionData[];
  onValidationChange?: (isValid: boolean) => void;
}

function PromptEditorWrapper({
  triggerId,
  checkedTypes,
  selectedSections,
  dataMode,
  stockId,
  onValidationChange
}: PromptEditorWrapperProps) {
  return (
    <DataProvider
      selectedSections={selectedSections}
      dataMode={dataMode}
      stockId={stockId}
      triggerId={triggerId}
    >
      <ValidationProvider>
        <PreviewProvider>
          <PromptEditorContent
            triggerId={triggerId}
            checkedTypes={checkedTypes}
            onValidationChange={onValidationChange}
          />
        </PreviewProvider>
      </ValidationProvider>
    </DataProvider>
  );
}

// Inner component that uses the prompt context
function PromptEditorContent({ triggerId, checkedTypes, onValidationChange }: PromptEditorWrapperProps) {
  const { setCheckedTypes, prompts, variantStrategy, strategyValidation } = usePrompt();

  // Sync checked types with PromptContext
  useEffect(() => {
    const types = new Set<'paid' | 'unpaid' | 'crawler'>();
    types.add('paid'); // Always include paid
    if (checkedTypes.unpaid) types.add('unpaid');
    if (checkedTypes.webCrawler) types.add('crawler');
    setCheckedTypes(types);
  }, [checkedTypes, setCheckedTypes]);

  // Track prompts validation and notify parent
  useEffect(() => {
    if (!onValidationChange) return;

    // Check if all required prompts are filled based on variant strategy
    const requiredPrompts = getStrategyRequirements(variantStrategy).required;
    const allPromptsFilled = requiredPrompts.every(promptType => {
      const promptTemplate = prompts[promptType];
      return promptTemplate && promptTemplate.content && promptTemplate.content.trim().length > 0;
    });

    // Also check strategy validation
    const isValid = allPromptsFilled && strategyValidation.isValid;
    onValidationChange(isValid);
  }, [prompts, variantStrategy, strategyValidation]); // Removed onValidationChange to prevent infinite loop

  return <PromptEditor triggerId={triggerId} />;
}

// Wrapper component for Testing step to sync prompt types
interface TestingStepWrapperProps {
  promptTypes: Record<PromptType, boolean>;
  children: React.ReactNode;
}

function TestingStepWrapper({ promptTypes, children }: TestingStepWrapperProps) {
  const { setCheckedTypes } = usePrompt();

  // Sync checked types with PromptContext
  useEffect(() => {
    const types = new Set<'paid' | 'unpaid' | 'crawler'>();
    types.add('paid'); // Always include paid
    if (promptTypes.unpaid) types.add('unpaid');
    if (promptTypes.webCrawler) types.add('crawler');
    setCheckedTypes(types);
  }, [promptTypes, setCheckedTypes]);

  return <>{children}</>;
}

// Variant Strategy Selector Component
function VariantStrategySelector() {
  const { variantStrategy, setVariantStrategy, strategyValidation } = usePrompt();

  const strategies: VariantStrategy[] = [
    'all_same',
    'all_unique',
    'paid_unique',
    'unpaid_unique',
    'crawler_unique'
  ];

  return (
    <div style={{ marginBottom: '24px' }}>
      <h5 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px' }}>
        Content Variation Strategy
      </h5>
      <Alert variant="secondary" style={{ marginBottom: '16px', fontSize: '14px' }}>
        <i className="bi bi-info-circle me-2"></i>
        <strong>Optimize API calls:</strong> Control how prompts are used across paid/unpaid/crawler news types.
      </Alert>

      <Form.Group>
        {strategies.map((strategy) => {
          const info = getStrategyRequirements(strategy);
          return (
            <div
              key={strategy}
              style={{
                marginBottom: '12px',
                padding: '12px',
                border: '1px solid #dee2e6',
                borderRadius: '6px',
                backgroundColor: variantStrategy === strategy ? '#f8f9fa' : 'white',
                cursor: 'pointer'
              }}
              onClick={() => setVariantStrategy(strategy)}
            >
              <Form.Check
                type="radio"
                id={`strategy-${strategy}`}
                name="variant-strategy"
                checked={variantStrategy === strategy}
                onChange={() => setVariantStrategy(strategy)}
                label={
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                      {strategy.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      <Badge bg="info" className="ms-2" style={{ fontSize: '11px' }}>
                        {info.apiCalls} API call{info.apiCalls !== 1 ? 's' : ''}
                      </Badge>
                    </div>
                    <div style={{ fontSize: '13px', color: '#6c757d' }}>
                      {info.description}
                    </div>
                  </div>
                }
              />
            </div>
          );
        })}
      </Form.Group>

      {/* Validation Warning */}
      {!strategyValidation.isValid && (
        <Alert variant="warning" style={{ marginTop: '12px' }}>
          <i className="bi bi-exclamation-triangle me-2"></i>
          <strong>Missing required prompts:</strong> {strategyValidation.errorMessage}
        </Alert>
      )}
    </div>
  );
}

// Publish Modal Wrapper Inner - Has access to PromptProvider and GenerationProvider
interface PublishModalWrapperInnerProps {
  show: boolean;
  onHide: () => void;
  triggerName: string;
  dataMode: DataMode;
  selectedSectionIds: string[];
  sectionOrder: string[];  // Added to fix scope error
  newSectionsData: any[];
  onConfirm: (publishData: any) => void;
  isPublishing: boolean;
}

function PublishModalWrapperInner({
  show,
  onHide,
  triggerName,
  dataMode,
  selectedSectionIds,
  sectionOrder,
  newSectionsData,
  onConfirm,
  isPublishing
}: PublishModalWrapperInnerProps) {
  const { prompts, variantStrategy } = usePrompt();
  const { results } = useGeneration();

  // Extract models and settings from test results instead of separate API call
  // This is more reliable and shows exactly what was tested
  const availableModels = useMemo(() => {
    const modelSet = new Set<string>();
    results.forEach(result => {
      if (result.model_id) {
        modelSet.add(result.model_id);
      }
    });
    return Array.from(modelSet);
  }, [results]);

  // Get temperature and max_tokens from first result metadata
  const modelSettings = useMemo(() => {
    const firstResult = results[0];
    return {
      selected_models: availableModels,
      temperature: firstResult?.metadata?.temperature || 0.7,
      max_tokens: firstResult?.metadata?.max_tokens || 1000
    };
  }, [availableModels, results]);

  // Build configuration object
  const configuration = {
    apis: [], // TODO: Track APIs if needed
    section_order: (sectionOrder.length > 0 ? sectionOrder : selectedSectionIds).map(id => {
      // Use sectionOrder if available (user's arrangement), otherwise fall back to selectedSectionIds
      const section = newSectionsData.find(s => s.section_id === id);
      return section ? section.section_name : id;
    }),
    prompts: {
      paid: prompts.paid.content,
      unpaid: prompts.unpaid.content,
      crawler: prompts.crawler.content
    },
    model_settings: modelSettings,
    data_mode: dataMode,
    variant_strategy: variantStrategy
  };

  // Build test results from generation results
  const testResults: Record<string, any> = {};

  // Group results by prompt type
  const resultsByType = results.reduce((acc, result) => {
    const type = result.prompt_type || 'paid';
    if (!acc[type]) acc[type] = [];
    acc[type].push(result);
    return acc;
  }, {} as Record<string, GenerationResult[]>);

  Object.entries(resultsByType).forEach(([promptType, typeResults]) => {
    testResults[promptType] = {
      models_tested: [...new Set(typeResults.map(r => r.model))],
      total_tests: typeResults.length,
      avg_cost: typeResults.reduce((sum, r) => sum + (r.cost || 0), 0) / typeResults.length,
      avg_latency: typeResults.reduce((sum, r) => sum + (r.time_taken || 0), 0) / typeResults.length,
      total_cost: typeResults.reduce((sum, r) => sum + (r.cost || 0), 0),
      sample_output: typeResults[0]?.generated_text || ''
    };
  });

  return (
    <PublishConfirmationModal
      show={show}
      onHide={onHide}
      triggerName={triggerName}
      configuration={configuration}
      testResults={testResults}
      onConfirm={onConfirm}
      isPublishing={isPublishing}
    />
  );
}
