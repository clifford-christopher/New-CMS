import { Clock, History } from 'lucide-react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import type { TriggerConfig } from '../App';
import { useState } from 'react';

type TriggerCardProps = {
  trigger: TriggerConfig;
  onConfigure: () => void;
};

const statusConfig = {
  configured: { label: 'Configured', variant: 'default' as const, className: 'bg-[#198754] hover:bg-[#198754]' },
  'in-progress': { label: 'In Progress', variant: 'secondary' as const, className: 'bg-[#ffc107] text-[#212529] hover:bg-[#ffc107]' },
  unconfigured: { label: 'Unconfigured', variant: 'secondary' as const, className: 'bg-[#6c757d] hover:bg-[#6c757d]' }
};

export function TriggerCard({ trigger, onConfigure }: TriggerCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const config = statusConfig[trigger.status];

  return (
    <div 
      className="bg-white border border-[#dee2e6] rounded p-5 transition-all duration-200 w-full max-w-[380px]"
      style={{
        boxShadow: isHovered 
          ? '0 8px 16px rgba(0,0,0,0.15)' 
          : '0 2px 4px rgba(0,0,0,0.075)',
        transform: isHovered ? 'scale(1.02)' : 'scale(1)'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start justify-between mb-4">
        <h3>{trigger.name}</h3>
        <Badge className={config.className}>
          {config.label}
        </Badge>
      </div>

      <p className="text-[#6c757d] mb-5 line-clamp-3">
        {trigger.description}
      </p>

      <div className="flex items-center gap-2 text-sm text-[#6c757d] mb-4">
        <Clock className="w-4 h-4" />
        <span>Last Updated: {trigger.lastUpdated}</span>
      </div>

      <div className="flex items-center gap-2">
        <Button 
          onClick={onConfigure}
          className="flex-1 bg-[#0d6efd] hover:bg-[#0b5ed7]"
        >
          Configure
        </Button>
        <Button 
          variant="outline" 
          size="icon"
          className="w-9 h-9 rounded-full border-[#6c757d]"
        >
          <History className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
