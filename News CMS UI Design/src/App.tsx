import { useState } from 'react';
import { DashboardV2 } from './components/DashboardV2';
import { ConfigurationWorkspace } from './components/ConfigurationWorkspace';
import { Toaster } from './components/ui/sonner';

export type TriggerConfig = {
  id: string;
  name: string;
  status: 'configured' | 'in-progress' | 'unconfigured';
  description: string;
  lastUpdated: string;
};

export type View = 'dashboard' | 'configuration';

function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [selectedTrigger, setSelectedTrigger] = useState<TriggerConfig | null>(null);

  const handleConfigureTrigger = (trigger: TriggerConfig) => {
    setSelectedTrigger(trigger);
    setCurrentView('configuration');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setSelectedTrigger(null);
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      {currentView === 'dashboard' && (
        <DashboardV2 onConfigureTrigger={handleConfigureTrigger} />
      )}
      
      {currentView === 'configuration' && selectedTrigger && (
        <ConfigurationWorkspace 
          trigger={selectedTrigger}
          onBack={handleBackToDashboard}
        />
      )}

      <Toaster />
    </div>
  );
}

export default App;
