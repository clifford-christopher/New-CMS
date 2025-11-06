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

import React, { useState, useEffect, useMemo } from 'react';
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
import { ModelProvider } from '@/contexts/ModelContext';
import { GenerationProvider } from '@/contexts/GenerationContext';
import { SectionData } from '@/types/validation';
import ModelSelection from '@/components/config/ModelSelection';
import TestGenerationPanel from '@/components/config/TestGenerationPanel';

interface PageProps {
  params: { triggerId: string };
}

type DataMode = 'OLD' | 'NEW' | 'OLD_NEW';
type PromptType = 'paid' | 'unpaid' | 'webCrawler';

type NavigationStep = 'data' | 'sections' | 'prompts' | 'testing' | 'results';

export default function ConfigurationPage({ params }: PageProps) {
  const triggerId = params.triggerId;

  // Navigation state
  const [activeStep, setActiveStep] = useState<NavigationStep>('data');

  // Data mode state
  const [dataMode, setDataMode] = useState<DataMode>('NEW');

  // Post-generation section selection state (NEW mode only)
  const [selectedSectionIds, setSelectedSectionIds] = useState<string[]>([]);
  const [generatedDataCache, setGeneratedDataCache] = useState<Record<string, any[]>>({});

  // Prompt type selection
  const [promptTypes, setPromptTypes] = useState<Record<PromptType, boolean>>({
    paid: true, // Always checked, disabled
    unpaid: false,
    webCrawler: false
  });

  // Data panel visibility toggle for Prompt Engineering section
  const [showDataPanel, setShowDataPanel] = useState(true);

  // Stock ID and data fetching
  const [stockId, setStockId] = useState('TCS');
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
        const response = await fetch(`http://localhost:8001/api/triggers/${triggerId}/drafts/latest`);

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

            // Set data mode
            if (dataConfig.data_mode) {
              setDataMode(dataConfig.data_mode as DataMode);
            }

            // Set selected sections
            if (dataConfig.selected_sections && Array.isArray(dataConfig.selected_sections)) {
              setSelectedSectionIds(dataConfig.selected_sections);
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

  // Handle data mode change
  const handleDataModeChange = (mode: DataMode) => {
    setDataMode(mode);
  };

  // Handle post-generation section selection
  const handleSectionSelection = (sectionIds: string[]) => {
    setSelectedSectionIds(sectionIds);
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
        `http://localhost:8000/api/data/structured/jobs/${jobId}`
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
        `http://localhost:8000/api/stocks/${stockId}/trigger-data?trigger_name=${triggerId}`,
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
        'http://localhost:8000/api/data/structured/generate',
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
      setSelectedSectionIds(sectionsData.map((s: any) => s.section_id));

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

  // Save draft
  const handleSaveDraft = async () => {
    setSaveStatus('saving');
    setErrorMessage('');

    try {
      // Build draft payload from current page state
      // Note: This saves the structure to drafts. Prompts and model config
      // are saved separately through their respective contexts.
      const draftPayload = {
        prompts: {}, // Prompts are managed by PromptContext, saved separately
        model_config: {}, // Model config managed by ModelContext, saved separately
        data_config: {
          data_mode: dataMode,
          selected_sections: selectedSectionIds,
          section_order: selectedSectionIds
        },
        saved_by: "system" // TODO: Replace with actual user ID when auth is implemented
      };

      const response = await fetch(`http://localhost:8001/api/triggers/${triggerId}/drafts`, {
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

  // Publish configuration
  const handlePublish = async () => {
    const allStepsCompleted = Object.values(completedSteps).every(v => v);
    if (!allStepsCompleted) {
      alert('Complete all required steps before publishing');
      return;
    }

    setSaveStatus('saving');
    setErrorMessage('');

    try {
      // Call the new publish endpoint which copies draft to production
      const response = await fetch(`http://localhost:8001/api/triggers/${triggerId}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          published_by: "system" // TODO: Replace with actual user ID when auth is implemented
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to publish configuration');
      }

      const result = await response.json();
      console.log('Configuration published:', result);

      setSaveStatus('success');
      alert(`Configuration published successfully! Version ${result.draft_version_published} is now live.`);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Publish error:', error);
      setSaveStatus('error');
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

        {/* Main Content Area */}
        <PromptProvider>
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
                    </div>
                  </>
                )}

                {/* NEW Mode - Show selected NEW sections only */}
                {dataMode === 'NEW' && newSectionsData.length > 0 && selectedSectionIds.length > 0 && (() => {
                  // Build Section[] from selected IDs and generated data
                  const selectedSections = selectedSectionIds
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
                            // Update selectedSectionIds to match the new order
                            setSelectedSectionIds(reorderedSections.map(s => s.id));
                          }}
                        />
                      </div>
                    </>
                  );
                })()}

                {/* OLD_NEW Mode - Show OLD section + selected NEW sections */}
                {dataMode === 'OLD_NEW' && oldData && newSectionsData.length > 0 && selectedSectionIds.length > 0 && (() => {
                  // Build combined Section[] with OLD data as first section + NEW sections
                  const oldSection: Section = {
                    id: 'old_data',
                    name: 'OLD Data (Complete)',
                    source: 'old' as const
                  };

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

                  // Combine: OLD section first, then NEW sections
                  const allSections = [oldSection, ...newSections];

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
                          Section Order (1 OLD + {newSections.length} NEW sections)
                        </h3>
                        <SectionManagementPanel
                          sections={allSections}
                          onSectionsChange={(reorderedSections) => {
                            // Extract only NEW section IDs (filter out OLD section)
                            const newSectionIds = reorderedSections
                              .filter(s => s.source === 'new')
                              .map(s => s.id);
                            setSelectedSectionIds(newSectionIds);
                          }}
                        />
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
                <ModelProvider triggerId={triggerId}>
                  <GenerationProvider>
                    <ModelSelection />
                    <TestGenerationPanel />
                  </GenerationProvider>
                </ModelProvider>
              </TestingStepWrapper>
            </DataProvider>
          )}

          {activeStep === 'results' && (
            <div style={{
              background: '#ffffff',
              borderRadius: '8px',
              padding: '24px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.08)'
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#212529', marginBottom: '16px' }}>
                {navigationItems.find(item => item.id === activeStep)?.label}
              </h2>
              <p style={{ fontSize: '16px', color: '#6c757d', fontStyle: 'italic' }}>
                [Content panels will be placed here]
              </p>
            </div>
          )}
          </div>
        </PromptProvider>
      </div>

      {/* Sticky Bottom Actions Bar */}
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
          <Button
            variant="outline-secondary"
            onClick={handleSaveDraft}
            disabled={saveStatus === 'saving'}
            style={{ width: '120px', height: '40px' }}
          >
            {saveStatus === 'saving' ? <Spinner as="span" animation="border" size="sm" /> : 'Save Draft'}
          </Button>
          <Button
            variant="outline-secondary"
            style={{ width: '120px', height: '40px' }}
          >
            View History
          </Button>
        </div>

        <Button
          variant="primary"
          onClick={handlePublish}
          disabled={!Object.values(completedSteps).every(v => v) || saveStatus === 'saving'}
          style={{ width: '140px', height: '40px', fontWeight: 600 }}
          title={!Object.values(completedSteps).every(v => v) ? 'Complete all required steps before publishing' : ''}
        >
          {saveStatus === 'saving' ? <Spinner as="span" animation="border" size="sm" /> : 'Publish'}
        </Button>
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
}

function PromptEditorWrapper({
  triggerId,
  checkedTypes,
  selectedSections,
  dataMode,
  stockId
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
          <PromptEditorContent triggerId={triggerId} checkedTypes={checkedTypes} />
        </PreviewProvider>
      </ValidationProvider>
    </DataProvider>
  );
}

// Inner component that uses the prompt context
function PromptEditorContent({ triggerId, checkedTypes }: PromptEditorWrapperProps) {
  const { setCheckedTypes } = usePrompt();

  // Sync checked types with PromptContext
  useEffect(() => {
    const types = new Set<'paid' | 'unpaid' | 'crawler'>();
    types.add('paid'); // Always include paid
    if (checkedTypes.unpaid) types.add('unpaid');
    if (checkedTypes.webCrawler) types.add('crawler');
    setCheckedTypes(types);
  }, [checkedTypes, setCheckedTypes]);

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
