import { render, screen } from '@testing-library/react';
import LoadingSpinner from '@/components/common/LoadingSpinner';

describe('LoadingSpinner Component', () => {
  test('renders spinner with default size', () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('renders with custom message', () => {
    render(<LoadingSpinner message="Loading data..." />);
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  test('renders small spinner', () => {
    const { container } = render(<LoadingSpinner size="sm" />);
    const spinner = container.querySelector('.spinner-border');
    expect(spinner).toHaveStyle({ width: '1rem', height: '1rem' });
  });

  test('renders large spinner', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const spinner = container.querySelector('.spinner-border');
    expect(spinner).toHaveStyle({ width: '3rem', height: '3rem' });
  });

  test('applies custom className', () => {
    const { container } = render(<LoadingSpinner className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
