import { useState, useEffect, useRef } from 'react';
import { CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { TypeSelectionCheckbox, PromptType } from './TypeSelectionCheckbox';

type DataStatus = 'not-configured' | 'ready' | 'fetching' | 'error';

type ContextBarProps = {
  triggerName: string;
  lastPublished?: string;
  version?: string;
  dataStatus?: DataStatus;
  stockId?: string;
  onStockIdChange?: (value: string) => void;
  selectedTypes?: PromptType[];
  onTypesChange?: (types: PromptType[]) => void;
};

export function ContextBar({ 
  triggerName, 
  lastPublished = '2 days ago (v1.2)', 
  version,
  dataStatus = 'ready',
  stockId: externalStockId,
  onStockIdChange,
  selectedTypes = ['paid'],
  onTypesChange
}: ContextBarProps) {
  const [internalStockId, setInternalStockId] = useState(externalStockId || 'TCS');
  const stockId = externalStockId !== undefined ? externalStockId : internalStockId;
  const debounceTimerRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const handleStockIdChange = (value: string) => {
    if (externalStockId === undefined) {
      setInternalStockId(value);
    }
    if (onStockIdChange) {
      onStockIdChange(value);
    }
  };

  const handleStockIdBlur = () => {
    // Trigger auto-fetch on blur
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      // Auto-fetch data for new stock ID
      console.log('Auto-fetching data for stock:', stockId);
    }, 500);
  };

  const getStatusBadge = () => {
    switch (dataStatus) {
      case 'not-configured':
        return (
          <Badge className="bg-[#6c757d] hover:bg-[#6c757d] text-white">
            Configure Data
          </Badge>
        );
      case 'fetching':
        return (
          <Badge className="bg-[#0dcaf0] hover:bg-[#0dcaf0] text-white flex items-center gap-1">
            <Loader2 className="w-3 h-3 animate-spin" />
            Fetching Data...
          </Badge>
        );
      case 'ready':
        return (
          <div className="flex items-center gap-2">
            <Badge className="bg-[#198754] hover:bg-[#198754] text-white flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              Data Ready
            </Badge>
            <span className="text-xs text-[#6c757d]">for {stockId}</span>
          </div>
        );
      case 'error':
        return (
          <Badge className="bg-[#dc3545] hover:bg-[#dc3545] text-white flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Configuration Error
          </Badge>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-5 mb-6 space-y-4">
      {/* Top Row */}
      <div className="flex items-center justify-between">
      {/* Left - Trigger Info */}
      <div>
        <h3 className="mb-1">{triggerName}</h3>
        <p className="text-sm text-[#6c757d]">Last published: {lastPublished}</p>
      </div>

        {/* Center - Stock ID Input */}
        <div className="flex flex-col">
          <label className="text-xs text-[#6c757d] mb-1">Test Stock ID</label>
          <Input
            value={stockId}
            onChange={(e) => handleStockIdChange(e.target.value)}
            onBlur={handleStockIdBlur}
            placeholder="Enter stock ID (e.g., TCS)"
            className="w-[200px] h-10"
          />
        </div>

        {/* Right - Configuration Status Badge */}
        <div className="flex items-center">
          {getStatusBadge()}
        </div>
      </div>

      {/* Bottom Row - Type Selection */}
      <div className="border-t border-[#dee2e6] pt-4">
        {onTypesChange ? (
          <TypeSelectionCheckbox
            selectedTypes={selectedTypes}
            onTypesChange={onTypesChange}
          />
        ) : (
          <TypeSelectionCheckbox
            selectedTypes={selectedTypes}
            onTypesChange={() => {}}
          />
        )}
      </div>
    </div>
  );
}
