import { X, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';

type PublishModalProps = {
  triggerName: string;
  onClose: () => void;
};

export function PublishModal({ triggerName, onClose }: PublishModalProps) {
  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-[700px] p-0">
        {/* Header */}
        <DialogHeader className="border-b border-[#dee2e6] px-8 py-6">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl">
              Publish Configuration to Production
            </DialogTitle>
            <button 
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center hover:bg-[#f8f9fa] rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <DialogDescription className="sr-only">
            Confirm publishing the {triggerName} configuration to production
          </DialogDescription>
        </DialogHeader>

        {/* Body */}
        <div className="px-8 py-6 space-y-6">
          {/* Validation Checklist */}
          <div>
            <h4 className="mb-4">Configuration Validation</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-[#198754]" />
                <span>APIs configured (Earnings API, Price Data API)</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-[#198754]" />
                <span>Prompt created and validated (456 characters)</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-[#198754]" />
                <span>Tested with models (Claude 3 Sonnet)</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-[#198754]" />
                <span>Stock ID validated (AAPL)</span>
              </div>
            </div>
          </div>

          {/* Warning Box */}
          <div className="bg-[#fff3cd] border border-[#ffc107] rounded-md px-4 py-3 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-[#ffc107] flex-shrink-0 mt-0.5" />
            <span className="text-sm">
              ⚠ Last test was 2 hours ago - consider re-testing
            </span>
          </div>

          {/* Configuration Summary */}
          <div>
            <h4 className="mb-4">Configuration Summary</h4>
            <div className="space-y-2 text-sm">
              <div>Trigger: {triggerName}</div>
              <div>APIs: Earnings API, Price Data API</div>
              <div>
                Prompt: Generate a news article based on...{' '}
                <button className="text-[#0d6efd] hover:underline">Show More</button>
              </div>
              <div>Model: Claude 3 Sonnet (temp: 0.7, max tokens: 500)</div>
            </div>
          </div>

          {/* Warning Message */}
          <div className="bg-[#f8d7da] border border-[#dc3545] rounded-md px-4 py-3">
            <span className="text-sm text-[#842029]">
              This will replace the current production configuration. Previous version will remain in history.
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-[#f8f9fa] border-t border-[#dee2e6] px-8 py-6 flex items-center justify-between">
          <Button 
            variant="secondary"
            onClick={onClose}
            className="bg-[#6c757d] text-white hover:bg-[#5c636a]"
          >
            Cancel
          </Button>
          <Button 
            onClick={() => {
              onClose();
              // Handle publish
            }}
            className="h-12 bg-[#dc3545] hover:bg-[#bb2d3b] text-white px-8"
          >
            Publish to Production
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
