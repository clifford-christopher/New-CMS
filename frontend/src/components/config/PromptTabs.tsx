'use client';

import { Nav, Badge } from 'react-bootstrap';
import { usePrompt } from '@/contexts/PromptContext';
import { useValidation } from '@/contexts/ValidationContext';

type PromptType = 'paid' | 'unpaid' | 'crawler';

const TAB_CONFIG: Record<PromptType, { icon: string; label: string; color: string }> = {
  paid: { icon: '💰', label: 'Paid', color: '#0d6efd' },
  unpaid: { icon: '🆓', label: 'Unpaid', color: '#198754' },
  crawler: { icon: '🕷️', label: 'Crawler', color: '#fd7e14' }
};

export default function PromptTabs() {
  const { activeTab, checkedTypes, setActiveTab } = usePrompt();
  const { validation } = useValidation();

  // Filter tabs to show only checked types
  const visibleTabs = (['paid', 'unpaid', 'crawler'] as PromptType[]).filter(type =>
    checkedTypes.has(type)
  );

  return (
    <Nav variant="tabs" className="px-3 pt-2" style={{ borderBottom: '1px solid #dee2e6' }}>
      {visibleTabs.map(type => {
        const config = TAB_CONFIG[type];
        const isActive = activeTab === type;
        const hasErrors = validation[type]?.hasErrors || false;
        const errorCount = validation[type]?.errors.length || 0;

        return (
          <Nav.Item key={type}>
            <Nav.Link
              active={isActive}
              onClick={() => setActiveTab(type)}
              style={{
                cursor: 'pointer',
                borderBottom: isActive ? `3px solid ${config.color}` : 'none',
                color: isActive ? config.color : '#6c757d',
                fontWeight: isActive ? 'bold' : 'normal'
              }}
            >
              <span className="me-2">{config.icon}</span>
              {config.label}
              {hasErrors && (
                <Badge
                  bg="danger"
                  className="ms-2"
                  title={`${errorCount} validation error${errorCount !== 1 ? 's' : ''}`}
                >
                  <i className="bi bi-exclamation-triangle me-1"></i>
                  {errorCount}
                </Badge>
              )}
            </Nav.Link>
          </Nav.Item>
        );
      })}
    </Nav>
  );
}
