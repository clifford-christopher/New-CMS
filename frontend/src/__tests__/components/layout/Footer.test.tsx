import { render, screen } from '@testing-library/react';
import Footer from '@/components/layout/Footer';

describe('Footer Component', () => {
  test('renders application name', () => {
    render(<Footer />);
    expect(screen.getByText(/AI-Powered News CMS/i)).toBeInTheDocument();
  });

  test('displays version number', () => {
    render(<Footer />);
    expect(screen.getByText(/Version/i)).toBeInTheDocument();
    expect(screen.getByText(/1.0.0/i)).toBeInTheDocument();
  });
});
