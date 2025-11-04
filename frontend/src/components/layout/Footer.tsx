/**
 * Footer Component
 *
 * Application footer displaying:
 * - Application name
 * - Version number
 * Positioned at bottom of page using flexbox layout
 */

import { Container } from 'react-bootstrap';

export default function Footer() {
  return (
    <footer className="bg-light border-top mt-auto py-3">
      <Container fluid>
        <div className="d-flex justify-content-between align-items-center">
          <span className="text-muted small">
            AI-Powered News CMS for Equity Market Research
          </span>
          <span className="text-muted small">
            Version 1.0.0
          </span>
        </div>
      </Container>
    </footer>
  );
}
