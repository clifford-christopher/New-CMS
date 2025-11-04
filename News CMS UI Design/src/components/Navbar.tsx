import { Menu } from 'lucide-react';

type NavbarProps = {
  isMobile?: boolean;
  activeView?: 'dashboard' | 'configuration';
  showConfigurationLink?: boolean;
  onNavigate?: (view: 'dashboard') => void;
};

export function Navbar({ 
  isMobile = false, 
  activeView = 'dashboard', 
  showConfigurationLink = false,
  onNavigate 
}: NavbarProps) {
  const handleNavClick = (e: React.MouseEvent, view: 'dashboard') => {
    e.preventDefault();
    if (onNavigate) {
      onNavigate(view);
    }
  };

  return (
    <nav className="bg-[#212529] h-16 flex items-center px-6 md:px-12 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="w-[200px] flex items-center">
          <span className="text-2xl text-white">News CMS</span>
        </div>
      </div>

      {!isMobile ? (
        <>
          <div className="flex items-center gap-8 mx-auto">
            <a 
              href="#" 
              onClick={(e) => handleNavClick(e, 'dashboard')}
              className={`px-5 py-5 transition-all ${
                activeView === 'dashboard'
                  ? 'text-white border-b-2 border-[#0d6efd]'
                  : 'text-[#adb5bd] hover:text-white'
              }`}
            >
              Dashboard
            </a>
            {showConfigurationLink && (
              <span 
                className={`px-5 py-5 transition-all ${
                  activeView === 'configuration'
                    ? 'text-white border-b-2 border-[#0d6efd]'
                    : 'text-[#adb5bd]'
                }`}
              >
                Configuration Workspace
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <div className="w-8 h-8 rounded-full bg-[#6c757d] flex items-center justify-center">
              <span className="text-sm text-white">AU</span>
            </div>
            <span className="text-sm text-[#adb5bd]">Admin User</span>
          </div>
        </>
      ) : (
        <div className="flex items-center gap-3 ml-auto">
          <div className="w-8 h-8 rounded-full bg-[#6c757d] flex items-center justify-center">
            <span className="text-sm text-white">AU</span>
          </div>
          <button className="p-2">
            <Menu className="w-6 h-6 text-white" />
          </button>
        </div>
      )}
    </nav>
  );
}
