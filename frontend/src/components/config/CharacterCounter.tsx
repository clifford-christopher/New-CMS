'use client';

import { Badge } from 'react-bootstrap';

interface CharacterCounterProps {
  characterCount: number;
  wordCount: number;
  promptType: 'paid' | 'unpaid' | 'crawler';
}

export default function CharacterCounter({
  characterCount,
  wordCount,
  promptType
}: CharacterCounterProps) {
  // Estimate token count (rough approximation: 1 token ≈ 4 characters)
  const estimatedTokens = Math.ceil(characterCount / 4);

  return (
    <div className="d-flex justify-content-between align-items-center px-3 py-2 bg-light border-top">
      <div className="d-flex gap-3">
        <small className="text-muted">
          <i className="bi bi-fonts me-1"></i>
          <strong>{characterCount.toLocaleString()}</strong> characters
        </small>
        <small className="text-muted">
          <i className="bi bi-chat-text me-1"></i>
          <strong>{wordCount.toLocaleString()}</strong> words
        </small>
        <small className="text-muted">
          <i className="bi bi-lightning me-1"></i>
          ~<strong>{estimatedTokens.toLocaleString()}</strong> tokens (est.)
        </small>
      </div>
      <Badge bg="secondary" className="text-capitalize">
        {promptType} Prompt
      </Badge>
    </div>
  );
}
