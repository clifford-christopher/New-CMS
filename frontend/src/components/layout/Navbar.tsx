/**
 * Navbar Component
 *
 * Bootstrap 5 implementation matching Figma design.
 * Design: Dark navbar (#212529) with centered navigation links and user avatar.
 * Features:
 * - "News CMS" branding (left)
 * - Dashboard link (always enabled, with active state border-bottom)
 * - Configuration Workspace link (conditionally shown)
 * - User avatar with initials (right)
 * - Responsive hamburger menu on mobile
 */

'use client';

import { Navbar as BSNavbar, Nav, Container } from 'react-bootstrap';
import Link from 'next/link';
import { useState } from 'react';

export default function Navbar() {
  const [selectedTrigger] = useState<string | null>(null);
  const [activeView] = useState<'dashboard' | 'configuration'>('dashboard');

  return (
    <BSNavbar
      expand="lg"
      className="shadow-sm"
      style={{
        backgroundColor: '#212529',
        height: '64px',
        minHeight: '64px'
      }}
    >
      <Container fluid className="px-4 px-md-5">
        {/* Brand/Logo */}
        <BSNavbar.Brand
          as={Link}
          href="/"
          className="text-white fs-4 fw-normal"
          style={{ width: '200px' }}
        >
          News CMS
        </BSNavbar.Brand>

        {/* Mobile hamburger toggle */}
        <BSNavbar.Toggle
          aria-controls="navbar-nav"
          className="border-0"
        >
          <span className="navbar-toggler-icon"></span>
        </BSNavbar.Toggle>

        <BSNavbar.Collapse id="navbar-nav">
          {/* Center navigation links */}
          <Nav className="mx-auto">
            <Nav.Link
              as={Link}
              href="/"
              className="px-3 py-3 position-relative"
              style={{
                color: activeView === 'dashboard' ? '#ffffff' : '#adb5bd',
                borderBottom: activeView === 'dashboard' ? '2px solid #0d6efd' : 'none',
                transition: 'color 0.2s ease'
              }}
            >
              Dashboard
            </Nav.Link>

            {selectedTrigger && (
              <Nav.Link
                as={Link}
                href="/config"
                className="px-3 py-3 position-relative"
                style={{
                  color: activeView === 'configuration' ? '#ffffff' : '#adb5bd',
                  borderBottom: activeView === 'configuration' ? '2px solid #0d6efd' : 'none',
                  transition: 'color 0.2s ease'
                }}
              >
                Configuration Workspace
              </Nav.Link>
            )}
          </Nav>

          {/* User info (right side) */}
          <div className="d-flex align-items-center gap-2">
            <div
              className="rounded-circle d-flex align-items-center justify-content-center"
              style={{
                width: '32px',
                height: '32px',
                backgroundColor: '#6c757d'
              }}
            >
              <span className="text-white small">AU</span>
            </div>
            <span className="text-secondary small d-none d-lg-inline">Admin User</span>
          </div>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
}
