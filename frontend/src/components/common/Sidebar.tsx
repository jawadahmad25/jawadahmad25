import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  LayoutDashboard, Database, Brain, BarChart3, FileText,
  BookOpen, Zap, Settings, Moon, Sun,
} from 'lucide-react';

interface SidebarProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/datasets', label: 'Datasets', icon: Database },
  { path: '/models', label: 'ML Models', icon: Brain },
  { path: '/visualizations', label: 'Visualizations', icon: BarChart3 },
  { path: '/publications', label: 'Publications', icon: FileText },
  { path: '/knowledge-base', label: 'Knowledge Base', icon: BookOpen },
  { path: '/quick-actions', label: 'Quick Actions', icon: Zap },
];

export default function Sidebar({ darkMode, onToggleDarkMode }: SidebarProps) {
  return (
    <aside className="w-64 border-r border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-900 flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-surface-200 dark:border-surface-700">
        <h1 className="text-lg font-bold text-surface-900 dark:text-white">
          Antenna ML Hub
        </h1>
        <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">
          Research Assistant
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              clsx('sidebar-link', isActive && 'sidebar-link-active')
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-surface-200 dark:border-surface-700 space-y-1">
        <button
          onClick={onToggleDarkMode}
          className="sidebar-link w-full"
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
        <div className="sidebar-link cursor-default">
          <Settings size={18} />
          <span>Settings</span>
        </div>
      </div>
    </aside>
  );
}
