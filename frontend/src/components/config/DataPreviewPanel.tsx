'use client';

import { Alert } from 'react-bootstrap';
import OldDataDisplay from '@/components/OldDataDisplay';
import NewDataDisplay from '@/components/NewDataDisplay';

interface DataPreviewPanelProps {
  dataMode: 'OLD' | 'NEW' | 'OLD_NEW';
  oldData: any;
  stockId: string;
  triggerId: string;
  newSectionsData: any[];
  selectedSectionIds: string[];
  selectedSections: any[];
}

export default function DataPreviewPanel({
  dataMode,
  oldData,
  stockId,
  triggerId,
  newSectionsData,
  selectedSectionIds,
  selectedSections
}: DataPreviewPanelProps) {
  return (
    <div style={{
      position: 'sticky',
      top: '20px',
      maxHeight: 'calc(100vh - 200px)',
      overflowY: 'auto'
    }}>
      <h5 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#212529' }}>
        <i className="bi bi-database me-2"></i>
        Available Data for Prompts
      </h5>

      {dataMode === 'OLD' && oldData && (
        <OldDataDisplay
          data={oldData}
          stockId={stockId}
          triggerId={triggerId}
        />
      )}

      {(dataMode === 'NEW' || dataMode === 'OLD_NEW') && selectedSections.length > 0 && (
        <>
          {dataMode === 'OLD_NEW' && oldData && (
            <OldDataDisplay
              data={oldData}
              stockId={stockId}
              triggerId={triggerId}
            />
          )}
          <NewDataDisplay
            sections={newSectionsData.filter(s => selectedSectionIds.includes(s.section_id))}
            showSelection={false}
          />
        </>
      )}

      {selectedSections.length === 0 && (
        <Alert variant="warning">
          <i className="bi bi-exclamation-triangle me-2"></i>
          <strong>No data available.</strong> Please complete the Data Configuration and Section Management steps first.
        </Alert>
      )}
    </div>
  );
}
