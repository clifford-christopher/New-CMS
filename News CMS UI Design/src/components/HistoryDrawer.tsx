import { X, User } from 'lucide-react';
import { Badge } from './ui/badge';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from './ui/sheet';

type HistoryDrawerProps = {
  onClose: () => void;
};

type Version = {
  id: string;
  version: string;
  timestamp: string;
  author: string;
  summary: string;
  isActive: boolean;
};

const versions: Version[] = [
  {
    id: '1',
    version: 'v1.3',
    timestamp: 'Oct 24, 2025, 2:30 PM',
    author: 'John Doe',
    summary: 'Model: Claude 3 | APIs: 2 | Prompt: 456 chars',
    isActive: true
  },
  {
    id: '2',
    version: 'v1.2',
    timestamp: 'Oct 23, 2025, 4:15 PM',
    author: 'Jane Smith',
    summary: 'Model: GPT-4 | APIs: 2 | Prompt: 423 chars',
    isActive: false
  },
  {
    id: '3',
    version: 'v1.1',
    timestamp: 'Oct 22, 2025, 10:00 AM',
    author: 'John Doe',
    summary: 'Model: Claude 3 | APIs: 2 | Prompt: 412 chars',
    isActive: false
  },
  {
    id: '4',
    version: 'v1.0',
    timestamp: 'Oct 20, 2025, 3:00 PM',
    author: 'John Doe',
    summary: 'Model: GPT-3.5 | APIs: 1 | Prompt: 380 chars',
    isActive: false
  },
  {
    id: '5',
    version: 'v0.9',
    timestamp: 'Oct 18, 2025, 11:30 AM',
    author: 'Jane Smith',
    summary: 'Model: Claude 3 | APIs: 2 | Prompt: 398 chars',
    isActive: false
  },
  {
    id: '6',
    version: 'v0.8',
    timestamp: 'Oct 15, 2025, 2:15 PM',
    author: 'John Doe',
    summary: 'Model: GPT-4 | APIs: 1 | Prompt: 356 chars',
    isActive: false
  }
];

export function HistoryDrawer({ onClose }: HistoryDrawerProps) {
  return (
    <Sheet open onOpenChange={onClose}>
      <SheetContent side="right" className="w-[600px] p-0">
        <SheetHeader className="sr-only">
          <SheetTitle>Configuration History</SheetTitle>
          <SheetDescription>
            View and manage previous configuration versions
          </SheetDescription>
        </SheetHeader>
        {/* Header */}
        <div className="border-b border-[#dee2e6] px-8 py-6 flex items-center justify-between">
          <h2>Configuration History</h2>
          <button 
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center hover:bg-[#f8f9fa] rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Version List */}
        <div className="p-6 space-y-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 88px)' }}>
          {versions.map((version) => (
            <div
              key={version.id}
              className={`rounded-lg p-4 transition-all cursor-pointer ${
                version.isActive
                  ? 'border-2 border-[#0d6efd] bg-white shadow-md'
                  : 'border border-[#dee2e6] bg-white hover:bg-[#f0f7ff]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <Badge className="bg-[#0d6efd] hover:bg-[#0d6efd]">
                  {version.version}
                </Badge>
                {version.isActive && (
                  <Badge className="bg-[#198754] hover:bg-[#198754]">
                    Active
                  </Badge>
                )}
              </div>

              <div className="space-y-2">
                <div className="text-sm text-[#6c757d]">
                  {version.timestamp}
                </div>
                <div className="flex items-center gap-2 text-sm text-[#6c757d]">
                  <User className="w-4 h-4" />
                  <span>{version.author}</span>
                </div>
                <div className="text-xs text-[#6c757d]">
                  {version.summary}
                </div>
                <button className="text-sm text-[#0d6efd] hover:underline">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}
