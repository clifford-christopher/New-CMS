'use client';

import { Button, ButtonGroup } from 'react-bootstrap';
import { usePrompt } from '@/contexts/PromptContext';

export default function UndoRedoButtons() {
  const { activeTab, canUndo, canRedo, undo, redo } = usePrompt();

  return (
    <ButtonGroup size="sm" className="me-2">
      <Button
        variant="outline-secondary"
        onClick={() => undo(activeTab)}
        disabled={!canUndo(activeTab)}
        title="Undo (Ctrl+Z)"
      >
        <i className="bi bi-arrow-counterclockwise me-1"></i>
        Undo
      </Button>
      <Button
        variant="outline-secondary"
        onClick={() => redo(activeTab)}
        disabled={!canRedo(activeTab)}
        title="Redo (Ctrl+Y)"
      >
        <i className="bi bi-arrow-clockwise me-1"></i>
        Redo
      </Button>
    </ButtonGroup>
  );
}
