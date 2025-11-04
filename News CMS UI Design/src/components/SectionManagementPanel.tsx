import { GripVertical, Eye } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

type SectionManagementPanelProps = {
  selectedSectionIds?: string[];
};

// Map section IDs to names
const sectionNameMap: Record<string, string> = {
  '1': 'Company Information',
  '2': 'Quarterly Income Statement',
  '3': 'Annual Income Statement',
  '4': 'Balance Sheet',
  '5': 'Cash Flow Statement',
  '6': 'Key Financial Ratios & Metrics',
  '7': 'Valuation Metrics',
  '8': 'Shareholding Pattern',
  '9': 'Stock Price & Returns Analysis',
  '10': 'Technical Analysis',
  '11': 'Quality Assessment',
  '12': 'Financial Trend Analysis',
  '13': 'Proprietary Score & Advisory',
  '14': 'Peer Comparison'
};

export function SectionManagementPanel({ selectedSectionIds = ['1', '2', '3', '5', '7'] }: SectionManagementPanelProps) {
  // Build sections array from selected IDs
  const sections = selectedSectionIds.map((id, index) => ({
    id,
    name: sectionNameMap[id] || `Section ${id}`,
    placeholder: `{{section_${id}}}`,
    order: index + 1
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="mb-2">Section Management</h3>
        <p className="text-sm text-[#6c757d]">
          Reorder the sections below to control how data appears in your prompt. Only the {sections.length} sections you selected are shown.
        </p>
      </div>

      {/* Section List */}
      <div className="space-y-2 mb-6">
        {sections.map((section) => (
          <div
            key={section.id}
            className="bg-[#f8f9fa] border border-[#dee2e6] rounded-md p-4 flex items-center gap-4 cursor-grab hover:shadow-sm transition-shadow"
          >
            {/* Drag Handle */}
            <GripVertical className="w-5 h-5 text-[#6c757d]" />

            {/* Order Number Input */}
            <Input
              type="number"
              value={section.order}
              className="w-[60px] h-10 text-center"
              readOnly
            />

            {/* Section Name */}
            <span className="flex-1">{section.name}</span>

            {/* Right Side */}
            <div className="flex items-center gap-3">
              <code className="text-sm text-[#ce9178]">{section.placeholder}</code>
            </div>
          </div>
        ))}
      </div>

      {/* Preview Button */}
      <Button variant="outline" className="w-[200px]">
        <Eye className="w-4 h-4 mr-2" />
        Preview Data Structure
      </Button>
    </div>
  );
}
