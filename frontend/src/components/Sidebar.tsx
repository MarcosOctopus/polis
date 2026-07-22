'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  Activity,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  Shield,
  Send,
  MapPin,
  Trophy,
} from 'lucide-react';

const navItems = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'Mensagens', href: '/messages', icon: Send },
  { label: 'Agentes', href: '/agents', icon: Bot },
  { label: 'Conversas', href: '/conversations', icon: MessageSquare },
  { label: 'Mapa', href: '/mapa', icon: MapPin },
  { label: 'Ranking', href: '/ranking', icon: Trophy },
  { label: 'Monitoramento', href: '/monitoring', icon: Activity },
  { label: 'Relatórios', href: '/reports', icon: BarChart3 },
  { label: 'Segurança', href: '/security', icon: Shield },
  { label: 'Configurações', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isLoginPage = pathname === '/login';

  if (isLoginPage) return null;

  return (
    <aside
      className={`h-screen bg-gray-950 border-r border-gray-800 flex flex-col transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">P</span>
          </div>
          {!collapsed && (
            <span className="text-white font-bold text-lg tracking-tight">
              Polis
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <item.icon
                className={`w-5 h-5 flex-shrink-0 ${
                  isActive ? 'text-cyan-400' : 'text-gray-500 group-hover:text-gray-300'
                }`}
              />
              {!collapsed && (
                <span className="text-sm font-medium truncate">
                  {item.label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-gray-800 p-3">
        {user && !collapsed && (
          <div className="px-3 py-2 mb-2">
            <p className="text-sm font-medium text-white truncate">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!collapsed && <span className="text-sm font-medium">Sair</span>}
        </button>

        {/* Collapse button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full mt-2 px-3 py-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-gray-800/50 transition-all duration-200"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>
    </aside>
  );
}
