import { useState } from 'react';
import { AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from './ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';

type ErrorStateProps = {
  title?: string;
  message?: string;
  technicalDetails?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
};

export function ErrorState({
  title = "Failed to Load Data",
  message = "Unable to fetch data from Earnings API. The request timed out after 5 seconds.",
  technicalDetails,
  onRetry,
  onDismiss
}: ErrorStateProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="w-full max-w-[500px] bg-[#ffebe9] border-l-4 border-[#dc3545] rounded p-5">
      <div className="flex gap-4">
        {/* Icon */}
        <div className="flex-shrink-0">
          <AlertCircle className="w-8 h-8 text-[#dc3545]" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h4 className="text-[#dc3545] mb-2">{title}</h4>

          {/* Message */}
          <p className="text-sm mb-4 leading-relaxed">{message}</p>

          {/* Technical Details (Collapsible) */}
          {technicalDetails && (
            <Collapsible open={showDetails} onOpenChange={setShowDetails} className="mb-4">
              <CollapsibleTrigger className="text-sm text-[#0d6efd] hover:underline flex items-center gap-1">
                View technical details
                {showDetails ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-2">
                <div className="bg-white border border-[#dee2e6] rounded p-3">
                  <pre className="text-xs text-[#6c757d] font-mono whitespace-pre-wrap">
                    {technicalDetails || `Error code: ETIMEDOUT
Endpoint: /api/earnings/AAPL
Timestamp: ${new Date().toISOString()}`}
                  </pre>
                </div>
              </CollapsibleContent>
            </Collapsible>
          )}

          {/* Actions */}
          {(onRetry || onDismiss) && (
            <div className="flex items-center gap-3">
              {onRetry && (
                <Button 
                  onClick={onRetry}
                  className="bg-[#0d6efd] hover:bg-[#0b5ed7] h-9 px-6"
                  size="sm"
                >
                  Retry
                </Button>
              )}
              {onDismiss && (
                <Button 
                  onClick={onDismiss}
                  variant="outline"
                  className="h-9 px-6"
                  size="sm"
                >
                  Dismiss
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
