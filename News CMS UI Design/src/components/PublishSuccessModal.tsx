import { CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogDescription, DialogTitle } from './ui/dialog';
import { useEffect, useState } from 'react';

type PublishSuccessModalProps = {
  onClose: () => void;
  onViewConfig?: () => void;
  onReturnToDashboard?: () => void;
};

export function PublishSuccessModal({ 
  onClose, 
  onViewConfig,
  onReturnToDashboard 
}: PublishSuccessModalProps) {
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onClose();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onClose]);

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-[600px] p-10">
        <DialogTitle className="sr-only">
          Configuration Published Successfully
        </DialogTitle>
        <DialogDescription className="sr-only">
          Version 1.3 has been published to production
        </DialogDescription>
        {/* Success Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 rounded-full bg-[#d1f4e0] flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-[#198754]" />
          </div>
        </div>

        {/* Success Message */}
        <div className="text-center mb-8">
          <h2 className="mb-3">Configuration Published Successfully</h2>
          <p className="text-[#6c757d]">Version 1.3 is now live in production</p>
        </div>

        {/* Metadata Box */}
        <div className="bg-[#f8f9fa] border border-[#dee2e6] rounded-md p-5 mb-8 space-y-3 text-center">
          <div className="text-sm">
            <span className="text-[#212529]">Published by:</span>{' '}
            <span className="text-[#212529]">John Doe</span>
          </div>
          <div className="text-sm text-[#6c757d]">
            Timestamp: {new Date().toLocaleString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric',
              hour: 'numeric',
              minute: '2-digit',
              hour12: true
            })}
          </div>
          <div className="text-sm">
            <span className="text-[#212529]">Version:</span>{' '}
            <span className="text-[#212529]">1.3</span>
          </div>
          <div className="text-sm text-[#6c757d]">
            Previous version: 1.2
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-4 mb-4">
          <Button
            onClick={onViewConfig}
            className="w-[180px] h-10 bg-[#0d6efd] hover:bg-[#0b5ed7]"
          >
            View Published Config
          </Button>
          <Button
            onClick={onReturnToDashboard}
            variant="outline"
            className="w-[180px] h-10"
          >
            Return to Dashboard
          </Button>
        </div>

        {/* Auto-close Timer */}
        <p className="text-xs text-[#6c757d] text-center">
          This dialog will close in {countdown} seconds...
        </p>
      </DialogContent>
    </Dialog>
  );
}
