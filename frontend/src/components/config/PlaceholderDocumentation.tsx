'use client';

import { Card, Button, ListGroup, Badge, Accordion, Alert } from 'react-bootstrap';
import { useData } from '@/contexts/DataContext';
import { useState } from 'react';

export default function PlaceholderDocumentation() {
  const [showHelp, setShowHelp] = useState(false);
  const { selectedSections } = useData();

  return (
    <>
      <Button
        variant="outline-info"
        size="sm"
        className="mt-2"
        onClick={() => setShowHelp(!showHelp)}
      >
        <i className="bi bi-question-circle me-1"></i>
        {showHelp ? 'Hide' : 'Show'} Available Placeholders
      </Button>

      {showHelp && (
        <Card className="mt-3 bg-light">
          <Card.Header>
            <h6 className="mb-0">
              <i className="bi bi-book me-2"></i>
              Placeholder Reference Guide
            </h6>
          </Card.Header>
          <Card.Body className="small">
            <Alert variant="info" className="mb-3">
              <strong>How to use placeholders:</strong>
              <ul className="mb-0 mt-2">
                <li>Use <code>{`{{section_ID}}`}</code> to reference a section by its ID</li>
                <li>Use <code>{`{{section_name}}`}</code> to reference a section by name</li>
                <li>Use <code>{`{data.field}`}</code> to reference nested data fields</li>
              </ul>
              {selectedSections.length === 0 && (
                <div className="mt-2 text-warning">
                  <i className="bi bi-exclamation-triangle me-1"></i>
                  <strong>No sections selected yet.</strong> Please complete Data Configuration and Section Management steps first.
                </div>
              )}
            </Alert>

            {selectedSections.length > 0 && (
              <>
                <div className="mb-3">
                  <strong className="d-block mb-2">Syntax Examples:</strong>
                  <ListGroup variant="flush">
                    <ListGroup.Item className="bg-transparent border-0 py-1">
                      <code className="text-primary">{`{{section_${selectedSections[0].section_id}}}`}</code>
                      <span className="text-muted ms-2">→ References section by ID</span>
                    </ListGroup.Item>
                    <ListGroup.Item className="bg-transparent border-0 py-1">
                      <code className="text-primary">{`{{${selectedSections[0].section_id}}}`}</code>
                      <span className="text-muted ms-2">→ Short form by ID</span>
                    </ListGroup.Item>
                    <ListGroup.Item className="bg-transparent border-0 py-1">
                      <code className="text-primary">{`{{${selectedSections[0].section_name}}}`}</code>
                      <span className="text-muted ms-2">→ Reference by section name</span>
                    </ListGroup.Item>
                    <ListGroup.Item className="bg-transparent border-0 py-1">
                      <code className="text-success">{`{data.field_name}`}</code>
                      <span className="text-muted ms-2">→ Reference a data field</span>
                    </ListGroup.Item>
                  </ListGroup>
                </div>

                <div>
                  <strong className="d-block mb-2">
                    Available Sections ({selectedSections.length} selected):
                  </strong>
                  <Accordion>
                    {selectedSections.map((section, index) => (
                      <Accordion.Item eventKey={section.section_id} key={section.section_id}>
                        <Accordion.Header>
                          <Badge bg="primary" className="me-2">#{index + 1}</Badge>
                          <strong>Section {section.section_id}:</strong>
                          <span className="ms-2">{section.section_title || section.section_name}</span>
                        </Accordion.Header>
                        <Accordion.Body className="p-2 bg-white">
                          <div className="mb-2">
                            <small className="text-muted d-block mb-1">Valid placeholder formats:</small>
                            <div className="d-flex flex-wrap gap-2">
                              <Badge bg="secondary" className="font-monospace">{`{{section_${section.section_id}}}`}</Badge>
                              <Badge bg="secondary" className="font-monospace">{`{{${section.section_id}}}`}</Badge>
                              <Badge bg="secondary" className="font-monospace">{`{{${section.section_name}}}`}</Badge>
                            </div>
                          </div>
                          <small className="text-muted">
                            All three formats reference the same section and are equally valid.
                          </small>
                        </Accordion.Body>
                      </Accordion.Item>
                    ))}
                  </Accordion>
                </div>
              </>
            )}

            <Alert variant="secondary" className="mt-3 mb-0">
              <small>
                <i className="bi bi-lightbulb me-1"></i>
                <strong>Tip:</strong> Start typing <code>{`{{`}</code> in the editor to see autocomplete suggestions!
              </small>
            </Alert>
          </Card.Body>
        </Card>
      )}
    </>
  );
}
