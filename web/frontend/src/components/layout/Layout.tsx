import { useState, useCallback, useEffect, useRef } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';
import Breadcrumbs from '../shared/Breadcrumbs';

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const prevPathRef = useRef(location.pathname);

  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  // Close sidebar on route change (mobile)
  useEffect(() => {
    if (prevPathRef.current !== location.pathname) {
      setSidebarOpen(false);
      prevPathRef.current = location.pathname;
    }
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-3 focus:bg-medical-teal focus:text-white focus:rounded-lg focus:m-2">
        Перейти к содержимому
      </a>

      {/* Desktop sidebar — always visible */}
      <div className="hidden md:block shrink-0">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={closeSidebar} />
          <div className="relative z-50 w-64 h-full">
            <Sidebar onClose={closeSidebar} />
          </div>
        </div>
      )}

      <main id="main-content" role="main" className="flex-1 overflow-auto min-w-0">
        {/* Mobile header with hamburger */}
        <div className="md:hidden sticky top-0 z-30 bg-white border-b border-gray-100 px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1.5 rounded-lg text-gray-600 hover:bg-gray-100 transition"
            aria-label="Открыть меню"
          >
            <Menu size={22} />
          </button>
          <span className="text-sm font-semibold text-gray-800">Aibolit</span>
        </div>

        <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 md:py-6">
          <Breadcrumbs />
          <Outlet />
        </div>
      </main>
    </div>
  );
}
