import { useState } from 'react';
import { Checkbox } from './ui/checkbox';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Slider } from './ui/slider';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Sparkles, Info } from 'lucide-react';
import type { PromptType } from './TypeSelectionCheckbox';

type Model = {
  id: string;
  provider: string;
  name: string;
  description: string;
  temperature: number;
  maxTokens: number;
  estimatedCost: string;
  selected: boolean;
  metrics?: {
    tokens: number;
    time: number;
    actualCost: string;
  };
};

type ModelSelectionProps = {
  selectedTypes?: PromptType[];
};

export function ModelSelection({ selectedTypes = ['paid'] }: ModelSelectionProps) {
  const [models, setModels] = useState<Model[]>([
    { 
      id: '1', 
      provider: 'OpenAI', 
      name: 'GPT-4', 
      description: 'Most capable model, best for complex reasoning',
      temperature: 0.7, 
      maxTokens: 500, 
      estimatedCost: '0.12', 
      selected: true,
      metrics: { tokens: 456, time: 8.3, actualCost: '0.08' }
    },
    { 
      id: '2', 
      provider: 'OpenAI', 
      name: 'GPT-3.5 Turbo', 
      description: 'Faster and more cost-effective',
      temperature: 0.7, 
      maxTokens: 500, 
      estimatedCost: '0.02', 
      selected: false 
    },
    { 
      id: '3', 
      provider: 'Anthropic', 
      name: 'Claude 3 Sonnet', 
      description: 'Balanced performance and speed',
      temperature: 0.7, 
      maxTokens: 500, 
      estimatedCost: '0.08', 
      selected: true,
      metrics: { tokens: 412, time: 6.7, actualCost: '0.06' }
    },
    { 
      id: '4', 
      provider: 'Anthropic', 
      name: 'Claude 3 Opus', 
      description: 'Most powerful model for complex tasks',
      temperature: 0.7, 
      maxTokens: 500, 
      estimatedCost: '0.15', 
      selected: false 
    },
    { 
      id: '5', 
      provider: 'Google', 
      name: 'Gemini Pro', 
      description: 'Fast and efficient for most tasks',
      temperature: 0.7, 
      maxTokens: 500, 
      estimatedCost: '0.05', 
      selected: false 
    }
  ]);

  const toggleModel = (id: string) => {
    setModels(prev => prev.map(m => m.id === id ? { ...m, selected: !m.selected } : m));
  };

  const updateTemperature = (id: string, temp: number) => {
    setModels(prev => prev.map(m => m.id === id ? { ...m, temperature: temp } : m));
  };

  const updateMaxTokens = (id: string, tokens: number) => {
    setModels(prev => prev.map(m => m.id === id ? { ...m, maxTokens: tokens } : m));
  };

  const selectedModels = models.filter(m => m.selected);
  const totalEstimatedCost = selectedModels.reduce((sum, m) => sum + parseFloat(m.estimatedCost), 0).toFixed(2);
  const totalGenerations = selectedTypes.length * selectedModels.length;

  const groupedModels = models.reduce((acc, model) => {
    if (!acc[model.provider]) acc[model.provider] = [];
    acc[model.provider].push(model);
    return acc;
  }, {} as Record<string, Model[]>);

  const getTimeColor = (time: number) => {
    if (time < 5) return 'text-[#198754]'; // green
    if (time < 15) return 'text-[#ffc107]'; // yellow
    return 'text-[#dc3545]'; // red
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-3 mb-2">
        <h3>Model Selection & Testing</h3>
        <Badge className="bg-[#e9ecef] text-[#6c757d] hover:bg-[#e9ecef]">
          (Used for All Types)
        </Badge>
      </div>
      
      <p className="text-sm text-[#6c757d] mb-4">
        Select one or more models to test across all checked prompt types. You can compare outputs side-by-side.
      </p>

      {/* Info Callout */}
      {totalGenerations > 0 && (
        <div className="bg-[#e7f1ff] border-l-3 border-[#0d6efd] rounded p-3 mb-6 flex items-start gap-2">
          <Info className="w-4 h-4 text-[#0d6efd] mt-0.5 flex-shrink-0" />
          <span className="text-sm text-[#212529]">
            Will generate for: <strong>{selectedTypes.map(t => t.charAt(0).toUpperCase() + t.slice(1)).join(', ')}</strong> ({selectedTypes.length} type{selectedTypes.length > 1 ? 's' : ''} × {selectedModels.length} model{selectedModels.length > 1 ? 's' : ''} = {totalGenerations} generations)
          </span>
        </div>
      )}

      <div className="space-y-6">
        {Object.entries(groupedModels).map(([provider, providerModels]) => (
          <div key={provider}>
            <h4 className="mb-3">{provider}</h4>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {providerModels.map((model) => (
                <div
                  key={model.id}
                  className={`rounded-md p-4 border-2 transition-all ${
                    model.selected 
                      ? 'border-[#0d6efd] bg-white' 
                      : 'border-[#dee2e6] bg-white'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-3">
                    <Checkbox
                      checked={model.selected}
                      onCheckedChange={() => toggleModel(model.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="text-lg mb-1">{model.name}</div>
                      <div className="text-sm text-[#6c757d]">{model.description}</div>
                    </div>
                  </div>

                  <div className="space-y-3 mb-3">
                    <div>
                      <Label className="text-xs text-[#6c757d] mb-1.5 block">
                        Temperature
                      </Label>
                      <Slider
                        value={[model.temperature]}
                        onValueChange={(val) => updateTemperature(model.id, val[0])}
                        max={1}
                        step={0.1}
                        className="w-[200px]"
                      />
                      <div className="text-xs text-[#6c757d] mt-1">
                        {model.temperature.toFixed(1)}
                      </div>
                    </div>

                    <div>
                      <Label htmlFor={`tokens-${model.id}`} className="text-xs text-[#6c757d] mb-1.5 block">
                        Max Tokens
                      </Label>
                      <Input
                        id={`tokens-${model.id}`}
                        type="number"
                        value={model.maxTokens}
                        onChange={(e) => updateMaxTokens(model.id, parseInt(e.target.value) || 0)}
                        className="w-[100px]"
                      />
                    </div>
                  </div>

                  <div className="text-right text-xs text-[#6c757d]">
                    Estimated: ~${model.estimatedCost} per generation
                  </div>

                  {/* Post-Generation Metrics */}
                  {model.metrics && (
                    <div className="mt-3 pt-3 border-t border-[#dee2e6]">
                      <div className="bg-[#f8f9fa] rounded p-3 space-y-1">
                        <div className="text-xs text-[#212529] mb-2">
                          ⚡ <strong>GENERATION METRICS</strong>
                        </div>
                        <div className="text-xs text-[#212529]">
                          🎯 Tokens: {model.metrics.tokens}
                        </div>
                        <div className={`text-xs ${getTimeColor(model.metrics.time)}`}>
                          ⏱️ Time: {model.metrics.time}s
                        </div>
                        <div className="text-xs text-[#198754]">
                          💰 Actual Cost: ${model.metrics.actualCost}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Cost Summary */}
      <div className="bg-[#fff3cd] border-l-4 border-[#ffc107] rounded p-4 mt-6 flex items-center justify-between">
        <div>
          <div className="text-sm text-[#212529]">
            Selected models: {selectedModels.length}
          </div>
          <div className="text-sm text-[#6c757d] mt-1">
            {selectedModels.map(m => m.name).join(', ') || 'None'}
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-[#6c757d]">Estimated cost:</div>
          <div className="text-2xl text-[#212529]">${totalEstimatedCost}</div>
        </div>
      </div>

      {/* Generate Button */}
      <Button 
        disabled={selectedModels.length === 0}
        className="w-full h-14 mt-6 bg-[#0d6efd] hover:bg-[#0b5ed7] disabled:bg-[#e9ecef] disabled:text-[#6c757d] text-lg"
      >
        <Sparkles className="w-5 h-5 mr-3" />
        Generate with Selected Models
      </Button>
    </div>
  );
}
