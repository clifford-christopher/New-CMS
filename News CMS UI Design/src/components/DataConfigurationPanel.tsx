import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronUp, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';

type DataSection = {
  id: string;
  name: string;
};

const dataSections: DataSection[] = [
  { id: '1', name: 'Section 1: Company Information' },
  { id: '2', name: 'Section 2: Quarterly Income Statement' },
  { id: '3', name: 'Section 3: Annual Income Statement' },
  { id: '4', name: 'Section 4: Balance Sheet' },
  { id: '5', name: 'Section 5: Cash Flow Statement' },
  { id: '6', name: 'Section 6: Key Financial Ratios & Metrics' },
  { id: '7', name: 'Section 7: Valuation Metrics' },
  { id: '8', name: 'Section 8: Shareholding Pattern' },
  { id: '9', name: 'Section 9: Stock Price & Returns Analysis' },
  { id: '10', name: 'Section 10: Technical Analysis' },
  { id: '11', name: 'Section 11: Quality Assessment' },
  { id: '12', name: 'Section 12: Financial Trend Analysis' },
  { id: '13', name: 'Section 13: Proprietary Score & Advisory' },
  { id: '14', name: 'Section 14: Peer Comparison' }
];

// Backend default selections (sections 1, 2, 3, 5, 7)
const DEFAULT_SELECTIONS = ['1', '2', '3', '5', '7'];

type DataConfigurationPanelProps = {
  onDataConfigured?: (sections: string[]) => void;
};

const earningsJSON = `{
  "symbol": "AAPL",
  "quarter": "Q4 2024",
  "revenue": "119.58B",
  "eps": "2.18",
  "earnings_date": "2024-10-31",
  "summary": "Apple reported strong Q4 results..."
}`;

const priceJSON = `{
  "symbol": "AAPL",
  "current_price": "178.45",
  "change": "+2.34",
  "change_percent": "+1.33%",
  "volume": "52,847,391"
}`;

export function DataConfigurationPanel({ onDataConfigured }: DataConfigurationPanelProps) {
  // Initialize with backend default selections
  const [selectedSections, setSelectedSections] = useState<string[]>(DEFAULT_SELECTIONS);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [dataFetched, setDataFetched] = useState(false);
  const [isDefaultConfiguration, setIsDefaultConfiguration] = useState(true);
  const [expandedJSON, setExpandedJSON] = useState<string[]>(['earnings', 'price']);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleSection = (id: string) => {
    setSelectedSections(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
    // User has modified selections, no longer default
    setIsDefaultConfiguration(false);
  };

  const selectAll = () => {
    setSelectedSections(dataSections.map(s => s.id));
    setIsDefaultConfiguration(false);
  };

  const clearAll = () => {
    setSelectedSections([]);
    setIsDefaultConfiguration(false);
  };

  const toggleJSON = (id: string) => {
    setExpandedJSON(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleUseThisData = () => {
    setDataFetched(true);
    setIsDropdownOpen(false);
    setIsDefaultConfiguration(false);
    // Notify parent component
    if (onDataConfigured) {
      onDataConfigured(selectedSections);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="mb-4">
        <h3 className="mb-4">Data Configuration</h3>
        <p className="text-sm text-[#6c757d]">
          Default data sections are pre-selected based on this trigger's configuration. Modify your selection if needed, then fetch data.
        </p>
      </div>

      {/* Section Selection Dropdown */}
      <div className="mb-6" ref={dropdownRef}>
        <label className="text-sm block mb-2">
          Select Data Sections to Include
        </label>

        {/* Dropdown Button */}
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="w-full h-12 border border-[#ced4da] rounded bg-white px-4 flex items-center justify-between hover:border-[#0d6efd] transition-colors"
        >
          <span className={selectedSections.length > 0 ? 'text-[#0d6efd]' : 'text-[#6c757d]'}>
            {selectedSections.length > 0
              ? `${selectedSections.length} section${selectedSections.length === 1 ? '' : 's'} selected`
              : 'Choose sections...'}
          </span>
          {isDropdownOpen ? (
            <ChevronUp className="w-4 h-4 text-[#6c757d]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[#6c757d]" />
          )}
        </button>

        {/* Default Configuration Badge */}
        {isDefaultConfiguration && !dataFetched && (
          <div className="mt-1">
            <span className="text-xs bg-[#e7f1ff] text-[#0d6efd] px-2 py-0.5 rounded">
              Default configuration
            </span>
          </div>
        )}

        {/* Dropdown Menu */}
        {isDropdownOpen && (
          <div className="absolute z-50 w-[calc(100%-48px)] max-w-[1528px] mt-2 bg-white border border-[#ced4da] rounded shadow-lg max-h-[400px] overflow-y-auto">
            {/* Dropdown Items */}
            <div className="py-2">
              {dataSections.map((section) => (
                <div
                  key={section.id}
                  onClick={() => toggleSection(section.id)}
                  className="h-12 px-4 flex items-center gap-3 hover:bg-[#f8f9fa] cursor-pointer border-b border-[#f8f9fa] last:border-b-0"
                >
                  <Checkbox
                    checked={selectedSections.includes(section.id)}
                    onCheckedChange={() => toggleSection(section.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <span className="text-sm">{section.name}</span>
                </div>
              ))}
            </div>

            {/* Dropdown Footer */}
            <div className="sticky bottom-0 bg-[#f8f9fa] border-t border-[#dee2e6] px-4 py-3 flex items-center justify-between">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  clearAll();
                }}
                className="text-sm text-[#0d6efd] hover:underline"
              >
                Clear All
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  selectAll();
                }}
                className="text-sm text-[#0d6efd] hover:underline"
              >
                Select All
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Use This Data Button */}
      <div className="mb-8">
        <Button
          onClick={handleUseThisData}
          disabled={selectedSections.length === 0}
          className="w-[200px] h-12 bg-[#0d6efd] hover:bg-[#0b5ed7] disabled:bg-[#e9ecef] disabled:text-[#6c757d] disabled:cursor-not-allowed"
          title={selectedSections.length === 0 ? "Please select at least one data section" : "Fetch data for selected sections and proceed to section management"}
        >
          Use This Data
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
        <p className="text-xs text-[#6c757d] mt-2">
          {selectedSections.length > 0 
            ? `This will fetch data for ${selectedSections.length} selected section${selectedSections.length === 1 ? '' : 's'}`
            : 'Please select at least one data section'}
        </p>
      </div>

      {dataFetched && selectedSections.length > 0 && (
        <div className="mb-6 p-4 bg-[#d1e7dd] border border-[#badbcc] rounded flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-[#0f5132]" />
          <span className="text-sm text-[#0f5132]">
            Successfully fetched data from {selectedSections.length} section{selectedSections.length === 1 ? '' : 's'}
          </span>
        </div>
      )}

      {/* Raw JSON Display - Only show if data has been fetched */}
      {dataFetched && selectedSections.length > 0 && (
        <div className="border-t border-[#dee2e6] pt-6 mb-8">
        <h4 className="mb-4">Raw JSON Response</h4>

        <div className="space-y-4">
          {/* Earnings API JSON */}
          <Collapsible open={expandedJSON.includes('earnings')} onOpenChange={() => toggleJSON('earnings')}>
            <div className="border border-[#dee2e6] rounded-lg overflow-hidden">
              <CollapsibleTrigger className="w-full bg-[#f8f9fa] px-4 py-3 flex items-center justify-between hover:bg-[#e9ecef] transition-colors">
                <span>Earnings API Response</span>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-[#6c757d]">Fetched: 2 seconds ago</span>
                  {expandedJSON.includes('earnings') ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CollapsibleTrigger>

              <CollapsibleContent>
                <div className="bg-[#2d2d2d] p-4 overflow-x-auto">
                  <pre className="text-sm font-mono leading-relaxed">
                    <code className="text-[#d4d4d4]">{earningsJSON}</code>
                  </pre>
                </div>
              </CollapsibleContent>
            </div>
          </Collapsible>

          {/* Price Data API JSON */}
          <Collapsible open={expandedJSON.includes('price')} onOpenChange={() => toggleJSON('price')}>
            <div className="border border-[#dee2e6] rounded-lg overflow-hidden">
              <CollapsibleTrigger className="w-full bg-[#f8f9fa] px-4 py-3 flex items-center justify-between hover:bg-[#e9ecef] transition-colors">
                <span>Price Data API Response</span>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-[#6c757d]">Fetched: 2 seconds ago</span>
                  {expandedJSON.includes('price') ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CollapsibleTrigger>

              <CollapsibleContent>
                <div className="bg-[#2d2d2d] p-4 overflow-x-auto">
                  <pre className="text-sm font-mono leading-relaxed">
                    <code className="text-[#d4d4d4]">{priceJSON}</code>
                  </pre>
                </div>
              </CollapsibleContent>
            </div>
          </Collapsible>
        </div>
      </div>
      )}

      {/* Structured Data Preview - Only show if data has been fetched */}
      {dataFetched && selectedSections.length > 0 && (
        <div className="border-t border-[#dee2e6] pt-6">
        <div className="mb-4">
          <h3>Structured Data Preview</h3>
          <p className="text-sm text-[#6c757d]">Parser output organized into sections</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          {/* Earnings Summary Card */}
          <div className="bg-white border border-[#dee2e6] rounded-md p-4">
            <div className="mb-3">
              <h4 className="text-lg">Earnings Summary</h4>
              <span className="text-xs text-[#6c757d]">Source: Earnings API</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Revenue: $119.58B (↑ 6% YoY)</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>EPS: $2.18 (↑ 11% YoY)</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Quarter: Q4 2024</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Earnings Date: Oct 31, 2024</span>
              </div>
            </div>
          </div>

          {/* Price Information Card */}
          <div className="bg-white border border-[#dee2e6] rounded-md p-4">
            <div className="mb-3">
              <h4 className="text-lg">Price Information</h4>
              <span className="text-xs text-[#6c757d]">Source: Price Data API</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Current: $178.45</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Change: +$2.34 (+1.33%)</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Volume: 52.8M shares</span>
              </div>
            </div>
          </div>

          {/* Company Context Card */}
          <div className="bg-white border border-[#dee2e6] rounded-md p-4">
            <div className="mb-3">
              <h4 className="text-lg">Company Context</h4>
              <span className="text-xs text-[#6c757d]">Source: Multiple APIs</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Symbol: AAPL</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Company: Apple Inc.</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Sector: Technology</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-[#198754]" />
                <span>Market Cap: $2.75T</span>
              </div>
            </div>
          </div>
        </div>

        <Button className="w-full h-11 bg-[#0d6efd] hover:bg-[#0b5ed7]">
          Use This Data in Prompt
        </Button>
      </div>
      )}
    </div>
  );
}
