import { render, screen } from '@testing-library/react';
import Navbar from '@/components/layout/Navbar';

describe('Navbar Component', () => {
  test('renders navigation links', () => {
    render(<Navbar />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  test('displays application name', () => {
    render(<Navbar />);
    expect(screen.getByText('News CMS')).toBeInTheDocument();
  });

  test('displays user avatar with initials', () => {
    render(<Navbar />);
    expect(screen.getByText('AU')).toBeInTheDocument();
    expect(screen.getByText('Admin User')).toBeInTheDocument();
  });

  test('Dashboard link has active state styling', () => {
    render(<Navbar />);
    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink).toHaveStyle({ color: '#ffffff' });
  });

  test('Configuration Workspace link is hidden when no trigger selected', () => {
    render(<Navbar />);
    expect(screen.queryByText('Configuration Workspace')).not.toBeInTheDocument();
  });

  test('renders navbar brand link', () => {
    render(<Navbar />);
    const brandLink = screen.getByText('News CMS').closest('a');
    expect(brandLink).toHaveAttribute('href', '/');
  });

  test('renders navbar toggle button for mobile', () => {
    render(<Navbar />);
    const toggleButton = screen.getByRole('button', { name: /toggle navigation/i });
    expect(toggleButton).toBeInTheDocument();
  });
});
