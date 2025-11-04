import { Checkbox } from './ui/checkbox';
import { Badge } from './ui/badge';

export type PromptType = 'paid' | 'unpaid' | 'crawler';

type TypeSelectionCheckboxProps = {
  selectedTypes: PromptType[];
  onTypesChange: (types: PromptType[]) => void;
};

export function TypeSelectionCheckbox({ selectedTypes, onTypesChange }: TypeSelectionCheckboxProps) {
  const handleTypeToggle = (type: PromptType) => {
    if (type === 'paid') return; // Paid cannot be unchecked
    
    if (selectedTypes.includes(type)) {
      onTypesChange(selectedTypes.filter(t => t !== type));
    } else {
      onTypesChange([...selectedTypes, type]);
    }
  };

  return (
    <div className="space-y-2">
      <label className="text-sm text-[#6c757d]">Prompt Types</label>
      
      <div className="flex items-center gap-6">
        {/* Paid - Always checked, disabled */}
        <div className="flex items-center gap-2">
          <Checkbox
            checked={true}
            disabled
            className="cursor-not-allowed opacity-70"
          />
          <span className="text-base">💰</span>
          <span className="text-sm">Paid</span>
          <Badge className="bg-[#e7f1ff] text-[#0d6efd] hover:bg-[#e7f1ff] text-[11px] px-2 py-0.5">
            Default
          </Badge>
        </div>

        {/* Unpaid - Optional */}
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => handleTypeToggle('unpaid')}
        >
          <Checkbox
            checked={selectedTypes.includes('unpaid')}
            onCheckedChange={() => handleTypeToggle('unpaid')}
          />
          <span className="text-base">🆓</span>
          <span className="text-sm">Unpaid</span>
        </div>

        {/* Web Crawler - Optional */}
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => handleTypeToggle('crawler')}
        >
          <Checkbox
            checked={selectedTypes.includes('crawler')}
            onCheckedChange={() => handleTypeToggle('crawler')}
          />
          <span className="text-base">🕷️</span>
          <span className="text-sm">Web Crawler</span>
        </div>
      </div>

      <p className="text-xs italic text-[#6c757d]">
        Select the prompt types to configure and test. Paid is always included.
      </p>
    </div>
  );
}
