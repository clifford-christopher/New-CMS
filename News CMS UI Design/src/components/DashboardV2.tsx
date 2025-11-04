import { useState } from 'react';
import { Navbar } from './Navbar';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { CheckCircle, Clock, TrendingUp } from 'lucide-react';
import type { TriggerConfig } from '../App';

type DashboardV2Props = {
  onConfigureTrigger: (trigger: TriggerConfig) => void;
};

const triggers: TriggerConfig[] = [
  {
    id: '1',
    name: 'Earnings Alert',
    status: 'configured',
    description: 'Generates news articles when companies release quarterly earnings reports.',
    lastUpdated: 'Oct 24, 2025, 2:30 PM'
  },
  {
    id: '2',
    name: 'Analyst Grade Change',
    status: 'configured',
    description: 'Creates updates when analysts change their recommendations for stocks.',
    lastUpdated: 'Oct 23, 2025, 4:15 PM'
  },
  {
    id: '3',
    name: 'Price Target Update',
    status: 'unconfigured',
    description: 'Detects price target changes from analysts.',
    lastUpdated: 'Never configured'
  },
  {
    id: '4',
    name: 'Market Commentary',
    status: 'in-progress',
    description: 'Generates market analysis and commentary.',
    lastUpdated: 'Oct 22, 2025, 10:00 AM'
  },
  {
    id: '5',
    name: 'Dividend Announcement',
    status: 'unconfigured',
    description: 'Reports on dividend declarations and changes.',
    lastUpdated: 'Never configured'
  }
];

const recentActivity = [
  { time: '2 hours ago', trigger: 'Earnings Alert', user: 'John Doe', action: 'Published v1.3', status: 'success' },
  { time: '5 hours ago', trigger: 'Analyst Grade Change', user: 'Jane Smith', action: 'Draft saved', status: 'draft' },
  { time: 'Yesterday at 4:15 PM', trigger: 'Earnings Alert', user: 'John Doe', action: 'Published v1.2', status: 'success' },
  { time: 'Yesterday at 2:30 PM', trigger: 'Market Commentary', user: 'Jane Smith', action: 'Configuration created', status: 'info' },
  { time: '2 days ago', trigger: 'Price Target Update', user: 'John Doe', action: 'Draft saved', status: 'draft' }
];

const statusConfig = {
  configured: { label: 'Configured', className: 'bg-[#198754] hover:bg-[#198754] text-white' },
  'in-progress': { label: 'In Progress', className: 'bg-[#ffc107] hover:bg-[#ffc107] text-[#212529]' },
  unconfigured: { label: 'Unconfigured', className: 'bg-[#6c757d] hover:bg-[#6c757d] text-white' }
};

const actionStatusConfig = {
  success: { label: 'Published', className: 'bg-[#198754] hover:bg-[#198754]' },
  draft: { label: 'Draft', className: 'bg-[#6c757d] hover:bg-[#6c757d]' },
  info: { label: 'Created', className: 'bg-[#0dcaf0] hover:bg-[#0dcaf0] text-[#212529]' }
};

export function DashboardV2({ onConfigureTrigger }: DashboardV2Props) {
  const [selectedTriggerId, setSelectedTriggerId] = useState<string>('');

  const handleConfigure = () => {
    const trigger = triggers.find(t => t.id === selectedTriggerId);
    if (trigger) {
      onConfigureTrigger(trigger);
    }
  };

  const configuredCount = triggers.filter(t => t.status === 'configured').length;

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <Navbar activeView="dashboard" showConfigurationLink={false} />
      
      {/* Page Header */}
      <div className="px-6 md:px-12 py-10">
        <h1 className="mb-2">News Trigger Dashboard</h1>
        <p className="text-[#6c757d]">Configure and manage AI-powered news generation triggers</p>
      </div>

      {/* Trigger Selector Section */}
      <div className="flex justify-center px-6 mb-12">
        <div className="w-full max-w-[600px] bg-white rounded-lg shadow-md p-8">
          <h3 className="mb-4">Select Trigger to Configure</h3>
          
          <Select value={selectedTriggerId} onValueChange={setSelectedTriggerId}>
            <SelectTrigger className="w-full h-12 mb-4">
              <SelectValue placeholder="Choose a trigger..." />
            </SelectTrigger>
            <SelectContent>
              {triggers.map((trigger) => {
                const config = statusConfig[trigger.status];
                return (
                  <SelectItem key={trigger.id} value={trigger.id}>
                    <div className="flex items-center justify-between w-full pr-4">
                      <span>{trigger.name}</span>
                      <Badge className={`ml-4 ${config.className}`}>
                        {config.label}
                      </Badge>
                    </div>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>

          <Button
            onClick={handleConfigure}
            disabled={!selectedTriggerId}
            className="w-full h-12 bg-[#0d6efd] hover:bg-[#0b5ed7] disabled:bg-[#e9ecef] disabled:text-[#6c757d]"
          >
            Configure Selected Trigger
          </Button>
        </div>
      </div>

      {/* Quick Stats Section */}
      <div className="flex justify-center px-6 mb-12">
        <div className="w-full max-w-[1200px] grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Triggers Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-[#e7f1ff] text-[#0d6efd] mb-3">
              <span className="text-2xl">{triggers.length}</span>
            </div>
            <div className="text-sm text-[#6c757d] mb-1">Total Triggers</div>
            <div className="text-3xl">{triggers.length}</div>
          </div>

          {/* Configured Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-[#d1f4e0] mb-3">
              <CheckCircle className="w-6 h-6 text-[#198754]" />
            </div>
            <div className="text-sm text-[#6c757d] mb-1">Configured</div>
            <div className="text-3xl">{configuredCount}</div>
          </div>

          {/* Recent Activity Card */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-[#fff3cd] mb-3">
              <Clock className="w-6 h-6 text-[#ffc107]" />
            </div>
            <div className="text-sm text-[#6c757d] mb-1">Last Updated</div>
            <div className="text-xl">2 hours ago</div>
          </div>
        </div>
      </div>

      {/* Recent Activity Section */}
      <div className="flex justify-center px-6 pb-12">
        <div className="w-full max-w-[1200px]">
          <h4 className="mb-4">Recent Configuration Changes</h4>
          
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#f8f9fa] border-b border-[#dee2e6]">
                  <tr>
                    <th className="text-left px-6 py-3 text-sm text-[#6c757d]">Timestamp</th>
                    <th className="text-left px-6 py-3 text-sm text-[#6c757d]">Trigger Name</th>
                    <th className="text-left px-6 py-3 text-sm text-[#6c757d]">User</th>
                    <th className="text-left px-6 py-3 text-sm text-[#6c757d]">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActivity.map((activity, index) => {
                    const actionConfig = actionStatusConfig[activity.status as keyof typeof actionStatusConfig];
                    return (
                      <tr key={index} className="border-b border-[#f8f9fa] last:border-b-0">
                        <td className="px-6 py-4 text-sm text-[#6c757d]">{activity.time}</td>
                        <td className="px-6 py-4 text-sm">{activity.trigger}</td>
                        <td className="px-6 py-4 text-sm text-[#6c757d]">{activity.user}</td>
                        <td className="px-6 py-4">
                          <Badge className={actionConfig.className}>
                            {activity.action}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
