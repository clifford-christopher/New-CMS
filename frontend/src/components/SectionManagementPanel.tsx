/**
 * Section Management Panel Component
 *
 * Provides drag-and-drop functionality for reordering sections,
 * visibility toggles, and live preview of section order.
 * Uses React DnD for drag-and-drop functionality.
 */

'use client';

import { useState, useCallback } from 'react';
import { Card, Form, Button, Badge, Alert } from 'react-bootstrap';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

// Section definition
export interface Section {
  id: string;
  name: string;
  source?: 'old' | 'new'; // Track data source for visual indicators
}

// Default sections (1-14) - for reference only
// In practice, parent component will pass only selected sections
export const DEFAULT_SECTIONS: Section[] = [
  { id: '1', name: 'Company Information' },
  { id: '2', name: 'Quarterly Income Statement' },
  { id: '3', name: 'Annual Income Statement' },
  { id: '4', name: 'Balance Sheet' },
  { id: '5', name: 'Cash Flow Statement' },
  { id: '6', name: 'Financial Ratios' },
  { id: '7', name: 'Valuation Metrics' },
  { id: '8', name: 'Shareholding Pattern' },
  { id: '9', name: 'Stock Performance' },
  { id: '10', name: 'Technical Analysis' },
  { id: '11', name: 'Quality Assessment' },
  { id: '12', name: 'Financial Trend Analysis' },
  { id: '13', name: 'Proprietary Score' },
  { id: '14', name: 'Peer Comparison' }
];

// Props for the main component
interface SectionManagementPanelProps {
  sections: Section[];
  onSectionsChange: (sections: Section[]) => void;
  disabled?: boolean;
}

// Drag item type
const ItemType = 'SECTION';

interface DragItem {
  index: number;
  id: string;
}

// Draggable section item component
interface SectionItemProps {
  section: Section;
  index: number;
  moveSection: (dragIndex: number, hoverIndex: number) => void;
  disabled?: boolean;
}

function SectionItem({ section, index, moveSection, disabled }: SectionItemProps) {
  const [{ isDragging }, drag] = useDrag({
    type: ItemType,
    item: { index, id: section.id },
    canDrag: !disabled,
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    })
  });

  const [{ isOver }, drop] = useDrop({
    accept: ItemType,
    hover: (item: DragItem) => {
      if (item.index !== index) {
        moveSection(item.index, index);
        item.index = index;
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver()
    })
  });

  return (
    <div
      ref={(node) => drag(drop(node))}
      className={`p-3 mb-2 border rounded bg-white ${isDragging ? 'opacity-50' : ''} ${isOver ? 'border-primary' : ''} ${disabled ? 'cursor-not-allowed' : 'cursor-move'}`}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: disabled ? 'not-allowed' : 'move'
      }}
    >
      <div className="d-flex align-items-center">
        {/* Drag Handle */}
        <div className="me-3 text-muted" style={{ fontSize: '1.2rem' }}>
          <i className="bi bi-grip-vertical"></i>
        </div>

        {/* Section Number */}
        <Badge bg="secondary" className="me-2" style={{ minWidth: '35px' }}>
          {section.id}
        </Badge>

        {/* Section Name */}
        <div className="flex-grow-1">
          <span>{section.name}</span>
        </div>

        {/* Source Badge (OLD/NEW) */}
        {section.source && (
          <Badge
            bg={section.source === 'old' ? 'info' : 'success'}
            className="ms-2"
          >
            {section.source.toUpperCase()}
          </Badge>
        )}
      </div>
    </div>
  );
}

// Main Section Management Panel Component
export default function SectionManagementPanel({
  sections,
  onSectionsChange,
  disabled = false
}: SectionManagementPanelProps) {
  const [previewMode, setPreviewMode] = useState(false);

  // Move section handler
  const moveSection = useCallback(
    (dragIndex: number, hoverIndex: number) => {
      const newSections = [...sections];
      const [removed] = newSections.splice(dragIndex, 1);
      newSections.splice(hoverIndex, 0, removed);
      onSectionsChange(newSections);
    },
    [sections, onSectionsChange]
  );

  // Visibility toggle removed - sections passed to this component are already selected/visible

  // Reset to default order (resets to sections passed by parent)
  const handleReset = () => {
    // Note: This will reset the order but parent decides which sections to show
    const resetSections = sections.map((s, idx) => ({
      ...DEFAULT_SECTIONS.find(ds => ds.id === s.id),
      id: s.id,
      name: s.name,
      source: s.source
    }) as Section);
    onSectionsChange(resetSections);
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <Card>
        <Card.Header className="bg-primary text-white">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <i className="bi bi-list-ol me-2"></i>
              <strong>Section Management</strong>
            </div>
            <Badge bg="light" text="dark">
              {sections.length} section{sections.length !== 1 ? 's' : ''}
            </Badge>
          </div>
        </Card.Header>

        <Card.Body>
          {/* Instructions */}
          <Alert variant="info" className="mb-3">
            <i className="bi bi-info-circle me-2"></i>
            <small>
              <strong>Drag</strong> sections to reorder them. Only selected sections from Data Configuration appear here.
            </small>
          </Alert>

          {/* Bulk Actions */}
          <div className="d-flex gap-2 mb-3 flex-wrap">
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleReset}
              disabled={disabled}
            >
              <i className="bi bi-arrow-counterclockwise me-1"></i>
              Reset Order
            </Button>
            <Button
              variant={previewMode ? 'primary' : 'outline-primary'}
              size="sm"
              onClick={() => setPreviewMode(!previewMode)}
              disabled={disabled}
              className="ms-auto"
            >
              <i className={`bi bi-${previewMode ? 'pencil' : 'eye'} me-1`}></i>
              {previewMode ? 'Edit Mode' : 'Preview'}
            </Button>
          </div>

          {/* Section List or Preview */}
          {previewMode ? (
            // Preview Mode - Show all sections in order (all are selected)
            <div className="border rounded p-3 bg-light">
              <h6 className="mb-3">
                <i className="bi bi-file-earmark-text me-2"></i>
                Final Output Preview
              </h6>
              {sections.length === 0 ? (
                <Alert variant="warning" className="mb-0">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  No sections selected. Please select sections in Data Configuration step.
                </Alert>
              ) : (
                <ol className="mb-0 ps-3">
                  {sections.map((section, idx) => (
                    <li key={section.id} className="mb-2">
                      <Badge bg="secondary" className="me-2">
                        Section {section.id}
                      </Badge>
                      {section.name}
                      {section.source && (
                        <Badge
                          bg={section.source === 'old' ? 'info' : 'success'}
                          className="ms-2"
                        >
                          {section.source.toUpperCase()}
                        </Badge>
                      )}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          ) : (
            // Edit Mode - Draggable section list
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              {sections.map((section, index) => (
                <SectionItem
                  key={section.id}
                  section={section}
                  index={index}
                  moveSection={moveSection}
                  disabled={disabled}
                />
              ))}
            </div>
          )}

          {/* Footer Info */}
          <div className="mt-3 pt-3 border-top">
            <small className="text-muted">
              <i className="bi bi-lightbulb me-1"></i>
              All sections shown here will appear in the generated content. Reorder by dragging.
            </small>
          </div>
        </Card.Body>
      </Card>
    </DndProvider>
  );
}
