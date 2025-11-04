import { useState } from 'react';
import { Copy, ChevronDown, ChevronUp, Star } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import type { PromptType } from './TypeSelectionCheckbox';

type ModelResult = {
  modelName: string;
  content: string;
  tokens: number;
  time: number;
  cost: string;
  rating: number;
};

type TypeResults = {
  type: PromptType;
  results: ModelResult[];
};

type ResultsComparisonPanelProps = {
  selectedTypes?: PromptType[];
};

const mockResults: TypeResults[] = [
  {
    type: 'paid',
    results: [
      {
        modelName: 'GPT-4',
        content: `Apple Reports Strong Q4 Earnings, Beating Expectations

Apple Inc. (AAPL) delivered robust fourth-quarter results on October 31, 2024, with revenue reaching $119.58 billion and earnings per share of $2.18, surpassing Wall Street forecasts.

Key Financial Highlights

The tech giant's Q4 2024 performance demonstrated continued momentum, with revenue beating analyst expectations. The company's EPS of $2.18 represents solid execution in a competitive market environment.

Market Sentiment and Price Action

Investor sentiment remains decidedly positive, with sentiment analysis showing a score of 0.78 and high confidence at 92%. The stock has shown strong recent performance, gaining $4.32 (2.48%) over the past week and $12.15 (7.31%) over the month, currently trading at $178.45.`,
        tokens: 456,
        time: 8.3,
        cost: '0.08',
        rating: 4.5
      },
      {
        modelName: 'Claude 3 Sonnet',
        content: `Tech Giant Apple Exceeds Earnings Expectations

Apple Inc. delivered impressive fourth-quarter results that surpassed Wall Street forecasts, with revenue reaching $119.58 billion and earnings per share of $2.18. The performance marks a 6% revenue increase compared to the same period last year.

The iPhone maker's success stems from sustained consumer demand and expansion in its services division. CEO Tim Cook highlighted the company's "ecosystem strength" as a key driver of growth.

Financial Performance Details

Apple's quarterly revenue of $119.58B represents strong execution across product lines. The $2.18 EPS exceeded consensus estimates, reflecting operational efficiency and pricing power in premium markets.`,
        tokens: 412,
        time: 6.7,
        cost: '0.06',
        rating: 4
      }
    ]
  },
  {
    type: 'unpaid',
    results: [
      {
        modelName: 'GPT-4',
        content: `Apple Q4 Results

Apple reported Q4 earnings with revenue of $119.58B and EPS of $2.18. Results exceeded expectations showing 6% growth.

Key metrics:
- Revenue: $119.58B
- EPS: $2.18
- Growth: 6% YoY

Stock trading at $178.45 with positive sentiment.`,
        tokens: 145,
        time: 3.2,
        cost: '0.02',
        rating: 3.5
      },
      {
        modelName: 'Claude 3 Sonnet',
        content: `Apple Q4 Earnings Beat Forecasts

Apple Inc. posted strong Q4 results with $119.58B revenue and $2.18 EPS, beating estimates.

Performance highlights:
- Revenue growth of 6%
- EPS surpassed consensus
- Stock at $178.45

Positive market sentiment continues.`,
        tokens: 138,
        time: 2.8,
        cost: '0.02',
        rating: 3
      }
    ]
  },
  {
    type: 'crawler',
    results: [
      {
        modelName: 'GPT-4',
        content: `Apple Q4 Earnings Analysis (Web Sources)

According to multiple financial news sources, Apple Inc. reported fourth-quarter earnings that exceeded analyst expectations.

Data from public sources:
- Reuters: Revenue $119.58B (vs. est. $118.2B)
- Bloomberg: EPS $2.18 (vs. est. $2.13)
- Yahoo Finance: Stock up 2.48% week-over-week

Sources consulted: Reuters, Bloomberg, Yahoo Finance, MarketWatch`,
        tokens: 198,
        time: 5.4,
        cost: '0.04',
        rating: 4
      },
      {
        modelName: 'Claude 3 Sonnet',
        content: `Apple Q4 Results from Public Data

Aggregated from financial news websites, Apple's Q4 performance showed strong results across metrics.

Key findings from sources:
- Revenue: $119.58B (Reuters, Bloomberg)
- EPS: $2.18 (MarketWatch)
- Sentiment: Positive (multiple sources)

Data sources: Reuters, Bloomberg, MarketWatch, CNBC`,
        tokens: 186,
        time: 4.9,
        cost: '0.03',
        rating: 3.5
      }
    ]
  }
];

export function ResultsComparisonPanel({ selectedTypes = ['paid'] }: ResultsComparisonPanelProps) {
  const [expandedGroups, setExpandedGroups] = useState<PromptType[]>(['paid']);

  const toggleGroup = (type: PromptType) => {
    setExpandedGroups(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const getTypeIcon = (type: PromptType) => {
    switch (type) {
      case 'paid': return '💰';
      case 'unpaid': return '🆓';
      case 'crawler': return '🕷️';
    }
  };

  const getTypeLabel = (type: PromptType) => {
    switch (type) {
      case 'paid': return 'PAID RESULTS';
      case 'unpaid': return 'UNPAID RESULTS';
      case 'crawler': return 'WEB CRAWLER RESULTS';
    }
  };

  const getTypeColor = (type: PromptType) => {
    switch (type) {
      case 'paid': return { bg: 'bg-[#e7f1ff]', border: 'border-[#0d6efd]', text: 'text-[#0d6efd]' };
      case 'unpaid': return { bg: 'bg-[#d1f4e0]', border: 'border-[#198754]', text: 'text-[#198754]' };
      case 'crawler': return { bg: 'bg-[#fff3cd]', border: 'border-[#ffc107]', text: 'text-[#dc7609]' };
    }
  };

  const getTimeColor = (time: number) => {
    if (time < 5) return 'text-[#198754]';
    if (time < 15) return 'text-[#ffc107]';
    return 'text-[#dc3545]';
  };

  const filteredResults = mockResults.filter(group => selectedTypes.includes(group.type));
  const totalCost = filteredResults.reduce((sum, group) => 
    sum + group.results.reduce((s, r) => s + parseFloat(r.cost), 0), 0
  ).toFixed(2);
  const totalGenerations = filteredResults.reduce((sum, group) => sum + group.results.length, 0);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="mb-2">Generation Results</h3>
        <p className="text-sm text-[#6c757d] mb-6">
          Compare outputs from different models across prompt types
        </p>

        {filteredResults.map((group) => {
          const colors = getTypeColor(group.type);
          const isExpanded = expandedGroups.includes(group.type);

          return (
            <div key={group.type} className="mb-6 last:mb-0">
              {/* Group Header */}
              <button
                onClick={() => toggleGroup(group.type)}
                className={`w-full ${colors.bg} border-l-4 ${colors.border} rounded-md p-4 flex items-center justify-between cursor-pointer hover:opacity-90 transition-opacity`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{getTypeIcon(group.type)}</span>
                  <span className={`text-lg ${colors.text}`}>
                    {getTypeLabel(group.type)}
                  </span>
                </div>
                {isExpanded ? (
                  <ChevronUp className={`w-5 h-5 ${colors.text}`} />
                ) : (
                  <ChevronDown className={`w-5 h-5 ${colors.text}`} />
                )}
              </button>

              {/* Results Grid */}
              {isExpanded && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
                  {group.results.map((result, idx) => (
                    <div key={idx} className="border border-[#dee2e6] rounded-md overflow-hidden">
                      {/* Header */}
                      <div className="bg-[#f8f9fa] border-b border-[#dee2e6] p-4 flex items-center justify-between">
                        <div>
                          <div className="text-sm">{result.modelName}</div>
                          <div className="text-xs text-[#6c757d] mt-0.5">
                            temp: 0.7 | tokens: {result.tokens}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className="bg-[#198754] hover:bg-[#198754] text-white">
                            Success
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="p-4 max-h-[600px] overflow-y-auto">
                        <div className="whitespace-pre-wrap text-sm leading-relaxed">
                          {result.content}
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="bg-[#f8f9fa] border-t border-[#dee2e6] p-3 flex items-center justify-between text-sm">
                        <div className="flex items-center gap-4">
                          <span className="text-[#212529]">🎯 {result.tokens}</span>
                          <span className={getTimeColor(result.time)}>⏱️ {result.time}s</span>
                          <span className="text-[#198754]">💰 ${result.cost}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < Math.floor(result.rating)
                                  ? 'fill-[#ffc107] text-[#ffc107]'
                                  : i < result.rating
                                  ? 'fill-[#ffc107] text-[#ffc107] opacity-50'
                                  : 'fill-none text-[#dee2e6]'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {/* Total Cost Summary */}
        <div className="bg-[#e7f1ff] rounded p-4 mt-6 flex items-center justify-between">
          <span className="text-sm text-[#212529]">
            Total Generations: {totalGenerations} ({selectedTypes.length} types × 2 models)
          </span>
          <span className="text-lg text-[#198754]">
            Total Actual Cost: ${totalCost}
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4 mt-6">
          <Button variant="outline">Regenerate</Button>
          <Button variant="secondary">Save to Iteration History</Button>
          <Button className="bg-[#0d6efd] hover:bg-[#0b5ed7] ml-auto">
            Use for Publishing
          </Button>
        </div>
      </div>
    </div>
  );
}
