import { Navbar } from './Navbar';
import { TriggerCard } from './TriggerCard';
import { Button } from './ui/button';
import type { TriggerConfig } from '../App';

type DashboardProps = {
  onConfigureTrigger: (trigger: TriggerConfig) => void;
};

const triggers: TriggerConfig[] = [
  {
    id: '1',
    name: 'Earnings Alert',
    status: 'configured',
    description: 'Generates news articles when companies release quarterly earnings reports. Includes revenue, EPS, and analyst commentary.',
    lastUpdated: 'Oct 24, 2025, 2:30 PM'
  },
  {
    id: '2',
    name: 'Analyst Grade Change',
    status: 'in-progress',
    description: 'Creates updates when analysts change their recommendations for stocks. Covers upgrades, downgrades, and target price changes.',
    lastUpdated: 'Oct 23, 2025, 4:15 PM'
  },
  {
    id: '3',
    name: 'Price Movement Alert',
    status: 'unconfigured',
    description: 'Detects significant price changes and generates breaking news alerts. Configurable thresholds for percentage moves.',
    lastUpdated: 'Never configured'
  },
  {
    id: '4',
    name: 'Dividend Announcement',
    status: 'configured',
    description: 'Reports on dividend declarations, increases, decreases, and special dividends from public companies.',
    lastUpdated: 'Oct 22, 2025, 10:00 AM'
  },
  {
    id: '5',
    name: 'Merger & Acquisition',
    status: 'configured',
    description: 'Covers M&A activity including acquisitions, mergers, spinoffs, and major corporate restructuring events.',
    lastUpdated: 'Oct 21, 2025, 3:45 PM'
  },
  {
    id: '6',
    name: 'Product Launch',
    status: 'unconfigured',
    description: 'Announces new products and services from companies. Includes tech launches, vehicle releases, and consumer products.',
    lastUpdated: 'Never configured'
  }
];

export function Dashboard({ onConfigureTrigger }: DashboardProps) {
  return (
    <div className="min-h-screen">
      <Navbar />
      
      <div className="bg-[#f8f9fa] px-6 md:px-12 py-6 border-b border-[#dee2e6]">
        <div className="flex items-center justify-between">
          <h1>News Trigger Dashboard</h1>
          <Button variant="secondary">View System Status</Button>
        </div>
      </div>

      <div className="px-6 md:px-12 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 max-w-[1824px]">
          {triggers.map((trigger) => (
            <TriggerCard
              key={trigger.id}
              trigger={trigger}
              onConfigure={() => onConfigureTrigger(trigger)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
