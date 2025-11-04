import { Inbox, Mail } from 'lucide-react';
import { Button } from './ui/button';

type EmptyStateProps = {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function EmptyState({ 
  title = "No Triggers Available",
  description = "There are currently no news triggers set up in the system. Contact your administrator to create triggers.",
  actionLabel = "Contact Administrator",
  onAction
}: EmptyStateProps) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center max-w-[600px] px-10 py-12">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-[120px] h-[120px] rounded-full bg-[#f8f9fa] flex items-center justify-center">
            <Inbox className="w-16 h-16 text-[#dee2e6]" />
          </div>
        </div>

        {/* Message */}
        <h2 className="mb-3">{title}</h2>
        <p className="text-[#6c757d] mb-8 leading-relaxed max-w-[400px] mx-auto">
          {description}
        </p>

        {/* Action */}
        {onAction && (
          <Button 
            variant="outline" 
            onClick={onAction}
            className="w-[180px] h-11"
          >
            <Mail className="w-4 h-4 mr-2" />
            {actionLabel}
          </Button>
        )}
      </div>
    </div>
  );
}
