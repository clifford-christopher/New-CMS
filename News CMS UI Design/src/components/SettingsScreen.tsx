import { useState } from 'react';
import { Navbar } from './Navbar';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Badge } from './ui/badge';

type TabType = 'profile' | 'preferences' | 'notifications' | 'security' | 'api-keys';

export function SettingsScreen() {
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [fullName, setFullName] = useState('John Doe');
  const [email, setEmail] = useState('john.doe@company.com');
  const [defaultStockId, setDefaultStockId] = useState('AAPL');
  const [editorTheme, setEditorTheme] = useState('light');
  const [hasChanges, setHasChanges] = useState(false);

  const tabs = [
    { id: 'profile' as TabType, label: 'Profile' },
    { id: 'preferences' as TabType, label: 'Preferences' },
    { id: 'notifications' as TabType, label: 'Notifications' },
    { id: 'security' as TabType, label: 'Security' },
    { id: 'api-keys' as TabType, label: 'API Keys' }
  ];

  const handleSave = () => {
    // Save logic here
    setHasChanges(false);
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <Navbar activeView="settings" />
      
      {/* Breadcrumb */}
      <div className="bg-white border-b border-[#dee2e6] px-6 md:px-12 py-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-[#0d6efd]">Dashboard</span>
          <span className="text-[#6c757d]">{'>'}</span>
          <span className="text-[#6c757d]">Settings</span>
        </div>
      </div>

      {/* Page Header */}
      <div className="px-6 md:px-12 py-8">
        <h1 className="mb-2">Settings</h1>
        <p className="text-[#6c757d]">Manage your profile and application preferences</p>
      </div>

      {/* Settings Container */}
      <div className="flex justify-center px-6 pb-12">
        <div className="w-full max-w-[900px] bg-white rounded-lg shadow-sm p-8">
          <div className="flex gap-8">
            {/* Left Sidebar Tabs */}
            <div className="w-[200px] flex-shrink-0">
              <div className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-2 rounded transition-colors ${
                      activeTab === tab.id
                        ? 'text-[#0d6efd] bg-[#e7f1ff] border-l-3 border-[#0d6efd]'
                        : 'text-[#6c757d] hover:bg-[#f8f9fa]'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Right Content Area */}
            <div className="flex-1 border-l border-[#dee2e6] pl-8">
              {activeTab === 'profile' && (
                <div>
                  {/* User Information Section */}
                  <div className="mb-8">
                    <h3 className="mb-5">User Information</h3>
                    
                    <div className="space-y-5">
                      {/* Full Name */}
                      <div>
                        <Label htmlFor="fullName" className="mb-2 block">
                          Full Name
                        </Label>
                        <Input
                          id="fullName"
                          value={fullName}
                          onChange={(e) => {
                            setFullName(e.target.value);
                            setHasChanges(true);
                          }}
                          className="h-10"
                        />
                      </div>

                      {/* Email Address */}
                      <div>
                        <Label htmlFor="email" className="mb-2 block">
                          Email Address
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          value={email}
                          onChange={(e) => {
                            setEmail(e.target.value);
                            setHasChanges(true);
                          }}
                          className="h-10"
                        />
                        <p className="text-xs text-[#6c757d] mt-2">
                          This email is used for notifications and account recovery
                        </p>
                      </div>

                      {/* Role */}
                      <div>
                        <Label className="mb-2 block">Role</Label>
                        <Badge variant="secondary" className="bg-[#6c757d] hover:bg-[#6c757d]">
                          Content Manager
                        </Badge>
                        <p className="text-xs text-[#6c757d] mt-2">
                          Contact administrator to change your role
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Preferences Section */}
                  <div className="border-t border-[#dee2e6] pt-6">
                    <h3 className="mb-5">Preferences</h3>
                    
                    <div className="space-y-5">
                      {/* Default Stock ID */}
                      <div>
                        <Label htmlFor="stockId" className="mb-2 block">
                          Default Stock ID for Testing
                        </Label>
                        <Input
                          id="stockId"
                          value={defaultStockId}
                          onChange={(e) => {
                            setDefaultStockId(e.target.value);
                            setHasChanges(true);
                          }}
                          className="h-10 w-[200px]"
                        />
                      </div>

                      {/* Editor Theme */}
                      <div>
                        <Label className="mb-3 block">Prompt Editor Theme</Label>
                        <RadioGroup 
                          value={editorTheme} 
                          onValueChange={(value) => {
                            setEditorTheme(value);
                            setHasChanges(true);
                          }}
                          className="flex gap-4"
                        >
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="light" id="light" />
                            <Label htmlFor="light" className="cursor-pointer">
                              Light
                            </Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="dark" id="dark" />
                            <Label htmlFor="dark" className="cursor-pointer">
                              Dark
                            </Label>
                          </div>
                        </RadioGroup>
                      </div>
                    </div>
                  </div>

                  {/* Save Button */}
                  <div className="mt-8">
                    <Button
                      onClick={handleSave}
                      disabled={!hasChanges}
                      className="bg-[#0d6efd] hover:bg-[#0b5ed7] disabled:bg-[#e9ecef] disabled:text-[#6c757d]"
                    >
                      Save Changes
                    </Button>
                  </div>
                </div>
              )}

              {activeTab === 'preferences' && (
                <div className="text-[#6c757d] text-center py-12">
                  <p>Preferences settings coming soon...</p>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div className="text-[#6c757d] text-center py-12">
                  <p>Notification settings coming soon...</p>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="text-[#6c757d] text-center py-12">
                  <p>Security settings coming soon...</p>
                </div>
              )}

              {activeTab === 'api-keys' && (
                <div className="text-[#6c757d] text-center py-12">
                  <p>API key management coming soon...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
