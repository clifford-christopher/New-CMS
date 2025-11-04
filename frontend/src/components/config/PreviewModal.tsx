'use client';

import { Modal, Button, Tab, Tabs, Alert, Badge, Form } from 'react-bootstrap';
import { usePreview } from '@/contexts/PreviewContext';
import { usePrompt } from '@/contexts/PromptContext';
import { useState } from 'react';
import { PromptType } from '@/types/preview';

const TAB_CONFIG: Record<PromptType, { icon: string; label: string; color: string }> = {
  paid: { icon: '💰', label: 'Paid', color: '#0d6efd' },
  unpaid: { icon: '🆓', label: 'Unpaid', color: '#198754' },
  crawler: { icon: '🕷️', label: 'Crawler', color: '#fd7e14' }
};

export default function PreviewModal() {
  const {
    isModalOpen,
    closeModal,
    previewContent,
    previewMetadata,
    activePreviewTab,
    setActivePreviewTab,
    isGenerating,
    error,
    selectedVersion,
    versionHistory,
    isLoadingVersions,
    setSelectedVersion
  } = usePreview();

  const { checkedTypes } = usePrompt();
  const [copiedTab, setCopiedTab] = useState<PromptType | null>(null);

  const handleCopyToClipboard = async () => {
    const content = previewContent[activePreviewTab].substitutedPrompt;
    try {
      await navigator.clipboard.writeText(content);
      setCopiedTab(activePreviewTab);
      setTimeout(() => setCopiedTab(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleVersionChange = (value: string) => {
    if (value === 'current') {
      setSelectedVersion('current');
    } else {
      setSelectedVersion(parseInt(value, 10));
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const visibleTabs = (['paid', 'unpaid', 'crawler'] as PromptType[]).filter(type =>
    checkedTypes.has(type)
  );

  return (
    <Modal show={isModalOpen} onHide={closeModal} size="xl" scrollable>
      <Modal.Header closeButton>
        <div className="w-100">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <Modal.Title>
                <i className="bi bi-eye me-2"></i>
                Preview Final Prompt
              </Modal.Title>
              {previewMetadata && (
                <small className="text-muted d-block mt-1">
                  <i className="bi bi-tag me-1"></i>
                  {previewMetadata.triggerName} |
                  <i className="bi bi-graph-up ms-2 me-1"></i>
                  Stock: {previewMetadata.stockId} |
                  <i className="bi bi-clock ms-2 me-1"></i>
                  {previewMetadata.timestamp.toLocaleTimeString()}
                </small>
              )}
            </div>

            <div className="d-flex align-items-center gap-2 ms-3">
              <Form.Label className="mb-0 text-muted small">Version:</Form.Label>
              <Form.Select
                size="sm"
                style={{ width: '250px' }}
                value={selectedVersion}
                onChange={(e) => handleVersionChange(e.target.value)}
                disabled={isLoadingVersions || isGenerating}
              >
                <option value="current">Current (Unsaved)</option>
                {versionHistory.map((v) => (
                  <option key={v.version} value={v.version}>
                    v{v.version} - {formatDate(v.saved_at)} by {v.saved_by}
                  </option>
                ))}
              </Form.Select>
              <Badge
                bg={selectedVersion === 'current' ? 'warning' : 'info'}
                className="ms-1"
              >
                {selectedVersion === 'current' ? 'Unsaved' : `v${selectedVersion}`}
              </Badge>
            </div>
          </div>
        </div>
      </Modal.Header>

      <Modal.Body style={{ minHeight: '400px' }}>
        {error && (
          <Alert variant="danger">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </Alert>
        )}

        {isGenerating && (
          <Alert variant="info">
            <i className="bi bi-hourglass-split me-2"></i>
            Generating preview...
          </Alert>
        )}

        {!isGenerating && !error && (
          <>
            {/* Tab Navigation */}
            <Tabs
              activeKey={activePreviewTab}
              onSelect={(tab) => setActivePreviewTab(tab as PromptType)}
              className="mb-3"
            >
              {visibleTabs.map(type => {
                const config = TAB_CONFIG[type];
                const content = previewContent[type];
                const hasMissing = content.missingPlaceholders.length > 0;

                return (
                  <Tab
                    key={type}
                    eventKey={type}
                    title={
                      <span>
                        <span className="me-2">{config.icon}</span>
                        {config.label}
                        {hasMissing && (
                          <Badge bg="warning" text="dark" className="ms-2">
                            <i className="bi bi-exclamation-triangle me-1"></i>
                            {content.missingPlaceholders.length}
                          </Badge>
                        )}
                      </span>
                    }
                  >
                    {/* Preview Content */}
                    <div className="bg-light p-3 rounded mb-3 border" style={{ minHeight: '300px', maxHeight: '500px', overflow: 'auto' }}>
                      <Form.Control
                        as="textarea"
                        value={content.substitutedPrompt}
                        readOnly
                        rows={15}
                        style={{
                          fontFamily: 'monospace',
                          fontSize: '0.9rem',
                          backgroundColor: 'white',
                          border: 'none',
                          resize: 'none'
                        }}
                      />
                    </div>

                    {/* Metadata Stats */}
                    <div className="bg-light p-3 rounded border">
                      <div className="row">
                        <div className="col-md-3">
                          <small className="text-muted">
                            <i className="bi bi-lightning me-1"></i>
                            <strong>{content.estimatedTokens.toLocaleString()}</strong> tokens (est.)
                          </small>
                        </div>
                        <div className="col-md-3">
                          <small className="text-muted">
                            <i className="bi bi-fonts me-1"></i>
                            <strong>{content.characterCount.toLocaleString()}</strong> characters
                          </small>
                        </div>
                        <div className="col-md-3">
                          <small className="text-muted">
                            <i className="bi bi-check-circle me-1 text-success"></i>
                            <strong>{content.validPlaceholders.length}</strong> valid
                          </small>
                        </div>
                        <div className="col-md-3 text-end">
                          <Badge bg="secondary">
                            {config.icon} {config.label}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {/* Warnings for Missing Placeholders */}
                    {content.missingPlaceholders.length > 0 && (
                      <Alert variant="warning" className="mt-3">
                        <div className="d-flex align-items-start">
                          <i className="bi bi-exclamation-triangle me-2 mt-1"></i>
                          <div>
                            <strong>Missing Data ({content.missingPlaceholders.length}):</strong>
                            <ul className="mb-0 mt-2">
                              {content.missingPlaceholders.map((placeholder, idx) => (
                                <li key={idx}>
                                  <code>{placeholder}</code> - Not found in available data
                                </li>
                              ))}
                            </ul>
                            <small className="text-muted mt-2 d-block">
                              These placeholders will appear as [MISSING: ...] in the preview.
                            </small>
                          </div>
                        </div>
                      </Alert>
                    )}

                    {/* Success message if all valid */}
                    {content.missingPlaceholders.length === 0 && content.validPlaceholders.length > 0 && (
                      <Alert variant="success" className="mt-3">
                        <i className="bi bi-check-circle me-2"></i>
                        <strong>All placeholders resolved successfully!</strong>
                        <div className="mt-2">
                          <small className="text-muted">
                            {content.validPlaceholders.length} placeholder{content.validPlaceholders.length !== 1 ? 's' : ''} found and substituted with actual data.
                          </small>
                        </div>
                      </Alert>
                    )}
                  </Tab>
                );
              })}
            </Tabs>
          </>
        )}
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={closeModal}>
          <i className="bi bi-x-lg me-2"></i>
          Close
        </Button>
        <Button
          variant="primary"
          onClick={handleCopyToClipboard}
          disabled={isGenerating}
        >
          <i className={`bi ${copiedTab === activePreviewTab ? 'bi-check-lg' : 'bi-clipboard'} me-2`}></i>
          {copiedTab === activePreviewTab ? 'Copied!' : 'Copy to Clipboard'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
