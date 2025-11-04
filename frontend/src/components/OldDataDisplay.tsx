/**
 * OldDataDisplay Component
 *
 * Displays existing trigger data from news_triggers collection (OLD mode)
 * Uses react-json-view for collapsible JSON visualization
 */

'use client';

import dynamic from 'next/dynamic';
import { Card, Badge } from 'react-bootstrap';

// Dynamic import for react-json-view to avoid SSR issues
const ReactJson = dynamic(() => import('react-json-view'), { ssr: false });

interface OldDataDisplayProps {
  data: any;
  stockId: string;
  triggerId: string;
}

export default function OldDataDisplay({ data, stockId, triggerId }: OldDataDisplayProps) {
  return (
    <Card style={{
      background: '#ffffff',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
      marginBottom: '24px'
    }}>
      <Card.Header style={{ background: '#e7f1ff', borderBottom: '1px solid #dee2e6' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <i className="bi bi-database-fill" style={{ fontSize: '20px', color: '#0d6efd' }}></i>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#212529', margin: 0 }}>
              Existing Trigger Data (OLD Mode)
            </h3>
            <div style={{ fontSize: '13px', color: '#6c757d', marginTop: '4px' }}>
              <span>Stock ID: <Badge bg="secondary">{stockId}</Badge></span>
              <span style={{ margin: '0 8px' }}>|</span>
              <span>Trigger: <Badge bg="primary">{triggerId}</Badge></span>
            </div>
          </div>
        </div>
      </Card.Header>

      <Card.Body style={{ padding: '24px' }}>
        {data ? (
          typeof data === 'string' ? (
            // Plain text display for string data
            <pre style={{
              background: '#f8f9fa',
              padding: '16px',
              borderRadius: '4px',
              fontSize: '13px',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              fontFamily: 'monospace',
              maxHeight: '600px',
              overflow: 'auto',
              margin: 0,
              border: '1px solid #dee2e6'
            }}>
              {data}
            </pre>
          ) : (
            // JSON viewer for object/array data
            <ReactJson
              src={data}
              collapsed={2}
              theme="rjv-default"
              displayDataTypes={false}
              enableClipboard={true}
              displayObjectSize={true}
              indentWidth={4}
              style={{
                background: '#f8f9fa',
                padding: '16px',
                borderRadius: '4px',
                fontSize: '13px'
              }}
            />
          )
        ) : (
          <div style={{ textAlign: 'center', padding: '32px', color: '#6c757d' }}>
            <i className="bi bi-inbox" style={{ fontSize: '48px', display: 'block', marginBottom: '16px' }}></i>
            <p>No data available</p>
          </div>
        )}
      </Card.Body>

      <Card.Footer style={{ background: '#f8f9fa', fontSize: '12px', color: '#6c757d' }}>
        <i className="bi bi-info-circle me-2"></i>
        This data is fetched from the <strong>news_triggers</strong> collection (existing trigger data)
      </Card.Footer>
    </Card>
  );
}
