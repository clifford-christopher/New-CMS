/**
 * Loading Spinner Component
 *
 * Reusable loading indicator with configurable size and message.
 * Uses Bootstrap Spinner component.
 *
 * Size options: sm (1rem), md (2rem), lg (3rem)
 *
 * Usage:
 * <LoadingSpinner size="sm" />
 * <LoadingSpinner size="md" message="Fetching data..." />
 * <LoadingSpinner size="lg" message="Generating news..." className="min-vh-50" />
 */

import { Spinner } from 'react-bootstrap';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export default function LoadingSpinner({
  size = 'md',
  message,
  className = ''
}: LoadingSpinnerProps) {
  const sizeMap = {
    sm: { width: '1rem', height: '1rem' },
    md: { width: '2rem', height: '2rem' },
    lg: { width: '3rem', height: '3rem' },
  };

  return (
    <div className={`d-flex flex-column align-items-center justify-content-center ${className}`}>
      <Spinner
        animation="border"
        role="status"
        style={sizeMap[size]}
      >
        <span className="visually-hidden">Loading...</span>
      </Spinner>
      {message && (
        <p className="mt-3 text-muted">{message}</p>
      )}
    </div>
  );
}
