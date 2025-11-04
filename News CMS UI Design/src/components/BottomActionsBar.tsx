import { Clock, Save } from 'lucide-react';
import { Button } from './ui/button';

type BottomActionsBarProps = {
  onPublish: () => void;
  onViewHistory: () => void;
  publishEnabled?: boolean;
};

export function BottomActionsBar({ onPublish, onViewHistory, publishEnabled = true }: BottomActionsBarProps) {
  return (
    <div 
      className="bg-white border-t border-[#dee2e6] px-6 md:px-12 py-4 flex items-center justify-between"
      style={{ boxShadow: '0 -2px 8px rgba(0,0,0,0.1)' }}
    >
      <div className="flex items-center gap-4">
        <Button variant="secondary" className="bg-[#6c757d] text-white hover:bg-[#5c636a]">
          <Save className="w-4 h-4 mr-2" />
          Save Draft
        </Button>
        <Button 
          variant="secondary" 
          onClick={onViewHistory}
          className="bg-[#6c757d] text-white hover:bg-[#5c636a]"
        >
          <Clock className="w-4 h-4 mr-2" />
          View History
        </Button>
      </div>

      <div className="flex flex-col items-end gap-1">
        <Button
          onClick={onPublish}
          disabled={!publishEnabled}
          size="lg"
          className={`h-12 px-8 text-lg ${
            publishEnabled
              ? 'bg-[#0d6efd] hover:bg-[#0b5ed7]'
              : 'bg-[#e9ecef] text-[#6c757d] cursor-not-allowed'
          }`}
        >
          Publish
        </Button>
        {!publishEnabled && (
          <span className="text-xs text-[#dc3545]">
            Complete configuration and test before publishing
          </span>
        )}
      </div>
    </div>
  );
}
