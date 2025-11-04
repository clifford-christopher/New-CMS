import { ChevronRight } from 'lucide-react';

type BreadcrumbProps = {
  triggerName: string;
  onBack: () => void;
};

export function Breadcrumb({ triggerName, onBack }: BreadcrumbProps) {
  return (
    <div className="bg-white border-b border-[#dee2e6] px-6 md:px-12 py-3">
      <div className="flex items-center gap-2 text-sm">
        <button 
          onClick={onBack}
          className="text-[#0d6efd] hover:underline"
        >
          Dashboard
        </button>
        <ChevronRight className="w-4 h-4 text-[#6c757d]" />
        <span className="text-[#0d6efd]">{triggerName}</span>
        <ChevronRight className="w-4 h-4 text-[#6c757d]" />
        <span className="text-[#6c757d]">Prompt Engineering</span>
      </div>
    </div>
  );
}
