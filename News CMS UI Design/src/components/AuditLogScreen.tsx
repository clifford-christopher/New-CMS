import { useState } from 'react';
import { Navbar } from './Navbar';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Download, AlertCircle } from 'lucide-react';

type AuditEntry = {
  timestamp: string;
  user: string;
  email: string;
  trigger: string;
  action: string;
  actionType: 'published' | 'draft' | 'rollback' | 'created' | 'failed';
  details: string;
  status: 'success' | 'failed';
};

const auditLog: AuditEntry[] = [
  {
    timestamp: 'Oct 28, 2025\n10:34 AM',
    user: 'John Doe',
    email: 'john.doe@company.com',
    trigger: 'Earnings Alert',
    action: 'Published',
    actionType: 'published',
    details: 'Published version 1.3 to production',
    status: 'success'
  },
  {
    timestamp: 'Oct 28, 2025\n08:15 AM',
    user: 'Jane Smith',
    email: 'jane.smith@company.com',
    trigger: 'Earnings Alert',
    action: 'Draft Saved',
    actionType: 'draft',
    details: 'Updated prompt template',
    status: 'success'
  },
  {
    timestamp: 'Oct 27, 2025\n04:42 PM',
    user: 'John Doe',
    email: 'john.doe@company.com',
    trigger: 'Price Target Update',
    action: 'Rollback',
    actionType: 'rollback',
    details: 'Rolled back to version 2.1 from version 2.2',
    status: 'success'
  },
  {
    timestamp: 'Oct 27, 2025\n02:30 PM',
    user: 'Jane Smith',
    email: 'jane.smith@company.com',
    trigger: 'Market Commentary',
    action: 'Published',
    actionType: 'published',
    details: 'Published version 1.5 to production',
    status: 'failed'
  },
  {
    timestamp: 'Oct 27, 2025\n11:20 AM',
    user: 'John Doe',
    email: 'john.doe@company.com',
    trigger: 'Analyst Grade Change',
    action: 'Configuration Created',
    actionType: 'created',
    details: 'Created new trigger configuration',
    status: 'success'
  },
  {
    timestamp: 'Oct 26, 2025\n03:15 PM',
    user: 'Jane Smith',
    email: 'jane.smith@company.com',
    trigger: 'Dividend Announcement',
    action: 'Draft Saved',
    actionType: 'draft',
    details: 'Initial configuration draft',
    status: 'success'
  },
  {
    timestamp: 'Oct 26, 2025\n01:45 PM',
    user: 'John Doe',
    email: 'john.doe@company.com',
    trigger: 'Earnings Alert',
    action: 'Published',
    actionType: 'published',
    details: 'Published version 1.2 to production',
    status: 'success'
  },
  {
    timestamp: 'Oct 25, 2025\n05:20 PM',
    user: 'Jane Smith',
    email: 'jane.smith@company.com',
    trigger: 'Market Commentary',
    action: 'Draft Saved',
    actionType: 'draft',
    details: 'Updated model settings',
    status: 'success'
  }
];

const actionTypeConfig = {
  published: { label: 'Published', className: 'bg-[#198754] hover:bg-[#198754]' },
  draft: { label: 'Draft Saved', className: 'bg-[#6c757d] hover:bg-[#6c757d]' },
  rollback: { label: 'Rollback', className: 'bg-[#ffc107] hover:bg-[#ffc107] text-[#212529]' },
  created: { label: 'Configuration Created', className: 'bg-[#0dcaf0] hover:bg-[#0dcaf0] text-[#212529]' },
  failed: { label: 'Failed', className: 'bg-[#dc3545] hover:bg-[#dc3545]' }
};

export function AuditLogScreen() {
  const [dateRange, setDateRange] = useState('last7days');
  const [triggerFilter, setTriggerFilter] = useState('all');
  const [userFilter, setUserFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);

  const totalEntries = auditLog.length;
  const entriesPerPage = 10;
  const totalPages = Math.ceil(totalEntries / entriesPerPage);

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <Navbar activeView="audit-log" />
      
      {/* Breadcrumb */}
      <div className="bg-white border-b border-[#dee2e6] px-6 md:px-12 py-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-[#0d6efd]">Dashboard</span>
          <span className="text-[#6c757d]">{'>'}</span>
          <span className="text-[#6c757d]">Audit Log</span>
        </div>
      </div>

      {/* Page Header */}
      <div className="px-6 md:px-12 py-8">
        <h1 className="mb-2">Audit Log</h1>
        <p className="text-[#6c757d]">Track all configuration changes and user actions</p>
      </div>

      {/* Filter Section */}
      <div className="px-6 md:px-12 mb-6">
        <div className="bg-white rounded-lg p-5 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Date Range Filter */}
            <div>
              <label className="text-xs text-[#6c757d] block mb-2">Date Range</label>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last7days">Last 7 days</SelectItem>
                  <SelectItem value="last30days">Last 30 days</SelectItem>
                  <SelectItem value="last90days">Last 90 days</SelectItem>
                  <SelectItem value="custom">Custom range</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Trigger Filter */}
            <div>
              <label className="text-xs text-[#6c757d] block mb-2">Trigger</label>
              <Select value={triggerFilter} onValueChange={setTriggerFilter}>
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Triggers</SelectItem>
                  <SelectItem value="earnings">Earnings Alert</SelectItem>
                  <SelectItem value="analyst">Analyst Grade Change</SelectItem>
                  <SelectItem value="price">Price Target Update</SelectItem>
                  <SelectItem value="market">Market Commentary</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* User Filter */}
            <div>
              <label className="text-xs text-[#6c757d] block mb-2">User</label>
              <Select value={userFilter} onValueChange={setUserFilter}>
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Users</SelectItem>
                  <SelectItem value="john">John Doe</SelectItem>
                  <SelectItem value="jane">Jane Smith</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Action Type Filter */}
            <div>
              <label className="text-xs text-[#6c757d] block mb-2">Action Type</label>
              <Select value={actionFilter} onValueChange={setActionFilter}>
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="published">Published</SelectItem>
                  <SelectItem value="draft">Draft Saved</SelectItem>
                  <SelectItem value="rollback">Rollback</SelectItem>
                  <SelectItem value="created">Created</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Apply Button */}
            <div className="flex items-end gap-2">
              <Button className="h-10 bg-[#0d6efd] hover:bg-[#0b5ed7]">
                Apply
              </Button>
              <button className="text-sm text-[#0d6efd] hover:underline whitespace-nowrap">
                Clear all filters
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="px-6 md:px-12 mb-8">
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {/* Export Button */}
          <div className="px-6 py-4 border-b border-[#dee2e6] flex justify-end">
            <Button variant="outline" className="h-10">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#f8f9fa]">
                <tr className="border-b-2 border-[#dee2e6]">
                  <th className="text-left px-6 py-4 text-sm text-[#6c757d] w-[140px]">Timestamp</th>
                  <th className="text-left px-6 py-4 text-sm text-[#6c757d] w-[150px]">User</th>
                  <th className="text-left px-6 py-4 text-sm text-[#6c757d] w-[200px]">Trigger</th>
                  <th className="text-left px-6 py-4 text-sm text-[#6c757d] w-[180px]">Action</th>
                  <th className="text-left px-6 py-4 text-sm text-[#6c757d]">Details</th>
                  <th className="text-left px-6 py-4 text-sm text-[#6c757d] w-[100px]">Status</th>
                  <th className="text-right px-6 py-4 text-sm text-[#6c757d] w-[80px]">Actions</th>
                </tr>
              </thead>
              <tbody>
                {auditLog.map((entry, index) => {
                  const actionConfig = actionTypeConfig[entry.actionType];
                  return (
                    <tr 
                      key={index} 
                      className="border-b border-[#f8f9fa] hover:bg-[#f8f9fa] transition-colors"
                    >
                      <td className="px-6 py-4 text-sm whitespace-pre-line">{entry.timestamp}</td>
                      <td className="px-6 py-4">
                        <div className="text-sm">{entry.user}</div>
                        <div className="text-xs text-[#6c757d]">{entry.email}</div>
                      </td>
                      <td className="px-6 py-4 text-sm">{entry.trigger}</td>
                      <td className="px-6 py-4">
                        <Badge className={actionConfig.className}>
                          {entry.action}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-[#6c757d]">{entry.details}</td>
                      <td className="px-6 py-4">
                        {entry.status === 'success' ? (
                          <Badge className="bg-[#198754] hover:bg-[#198754]">Success</Badge>
                        ) : (
                          <div className="flex items-center gap-1">
                            <AlertCircle className="w-4 h-4 text-[#dc3545]" />
                            <Badge className="bg-[#dc3545] hover:bg-[#dc3545]">Failed</Badge>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-sm text-[#0d6efd] hover:underline">
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="border-t border-[#dee2e6] px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-[#6c757d]">
              Showing 1-{Math.min(entriesPerPage, totalEntries)} of {totalEntries} entries
            </div>

            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(p => p - 1)}
              >
                Previous
              </Button>
              
              {[1, 2, 3, 4, 5].map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`w-9 h-9 rounded flex items-center justify-center text-sm transition-colors ${
                    currentPage === page
                      ? 'bg-[#0d6efd] text-white'
                      : 'text-[#6c757d] hover:bg-[#f8f9fa]'
                  }`}
                >
                  {page}
                </button>
              ))}
              
              <Button 
                variant="outline" 
                size="sm"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(p => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
