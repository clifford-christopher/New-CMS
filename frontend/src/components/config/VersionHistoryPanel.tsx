'use client';

import { Card, ListGroup, Badge, Button, Collapse } from 'react-bootstrap';
import { useState } from 'react';
import { usePrompt } from '@/contexts/PromptContext';

export default function VersionHistoryPanel() {
  const { activeTab, history, saveAsVersion, loadVersion } = usePrompt();
  const [open, setOpen] = useState(true);

  const typeHistory = history[activeTab];
  const currentVersion = typeHistory.versions[typeHistory.currentIndex];

  const handleSaveAsCheckpoint = () => {
    saveAsVersion(activeTab, true);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatDate = (date: Date) => {
    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();

    if (isToday) {
      return `Today ${formatTime(date)}`;
    }

    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Capitalize first letter of prompt type
  const capitalizeType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  return (
    <Card className="mt-4">
      <Card.Header
        className="cursor-pointer d-flex justify-content-between align-items-center"
        onClick={() => setOpen(!open)}
        style={{ cursor: 'pointer' }}
      >
        <div>
          <h5 className="mb-0">
            <i className="bi bi-clock-history me-2"></i>
            Version History - {capitalizeType(activeTab)}
          </h5>
          <small className="text-muted">
            {typeHistory.versions.length} version{typeHistory.versions.length !== 1 ? 's' : ''}
            {currentVersion && ` | Current: v${typeHistory.currentIndex + 1}`}
            {typeHistory.pendingChanges && <Badge bg="warning" className="ms-2">Unsaved Changes</Badge>}
          </small>
        </div>
        <i className={`bi bi-chevron-${open ? 'up' : 'down'}`}></i>
      </Card.Header>

      <Collapse in={open}>
        <Card.Body>
          {typeHistory.versions.length === 0 ? (
            <div className="text-center py-4">
              <i className="bi bi-clock-history text-muted" style={{ fontSize: '3rem' }}></i>
              <p className="text-muted mb-0 mt-2">No version history yet.</p>
              <small className="text-muted">Start editing to create versions automatically.</small>
            </div>
          ) : (
            <ListGroup variant="flush" className="mb-3">
              {typeHistory.versions.map((version, idx) => {
                const isCurrent = idx === typeHistory.currentIndex;
                return (
                  <ListGroup.Item
                    key={version.id}
                    className={`d-flex justify-content-between align-items-start ${isCurrent ? 'bg-light border-primary' : ''}`}
                    style={{ borderLeftWidth: isCurrent ? '3px' : '1px' }}
                  >
                    <div className="flex-grow-1">
                      <div className="d-flex align-items-center mb-1">
                        <span className="fw-bold me-2">v{idx + 1}</span>
                        {isCurrent && <Badge bg="primary">Current</Badge>}
                        {version.isManualCheckpoint && (
                          <Badge bg="success" className="ms-2">
                            <i className="bi bi-bookmark-fill me-1"></i>
                            Checkpoint
                          </Badge>
                        )}
                      </div>
                      <small className="text-muted d-block">
                        <i className="bi bi-clock me-1"></i>
                        {formatDate(version.timestamp)}
                      </small>
                      <small className="text-muted d-block">
                        <i className="bi bi-text-paragraph me-1"></i>
                        {version.characterCount.toLocaleString()} chars | {version.wordCount} words
                      </small>
                    </div>
                    <Button
                      variant={isCurrent ? "outline-secondary" : "outline-primary"}
                      size="sm"
                      disabled={isCurrent}
                      onClick={() => loadVersion(activeTab, idx)}
                      title={isCurrent ? "Already viewing this version" : "Load this version"}
                    >
                      {isCurrent ? 'Viewing' : 'Load'}
                    </Button>
                  </ListGroup.Item>
                );
              })}
            </ListGroup>
          )}

          <div className="d-grid gap-2">
            <Button
              variant="success"
              size="sm"
              onClick={handleSaveAsCheckpoint}
            >
              <i className="bi bi-bookmark-plus me-2"></i>
              Save as New Version (Checkpoint)
            </Button>
            <small className="text-muted text-center">
              <i className="bi bi-info-circle me-1"></i>
              Versions auto-save every 30 seconds. Maximum 10 versions kept.
            </small>
          </div>
        </Card.Body>
      </Collapse>
    </Card>
  );
}
