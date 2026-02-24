import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, FlaskConical, HeartPulse,
  Activity, Pill, FileText, Heart,
  MessageSquare, MessageCircle, Clock, LogOut, X, User, Settings,
} from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../../contexts/AuthContext';

const navClass = ({ isActive }: { isActive: boolean }) =>
  clsx(
    'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
    isActive
      ? 'bg-white/20 text-white shadow-sm'
      : 'text-blue-100 hover:bg-white/10 hover:text-white',
  );

interface SidebarProps {
  onClose?: () => void;
}

export default function Sidebar({ onClose }: SidebarProps) {
  const { patientId, username, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const handleNavClick = () => {
    onClose?.();
  };

  return (
    <aside className="w-64 min-h-screen bg-gradient-to-b from-medical-navy to-medical-navy-light flex flex-col">
      {/* Header: Logo + User + Close (mobile) */}
      <div className="px-6 py-5 flex items-center gap-3">
        <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center shrink-0">
          <Heart className="w-6 h-6 text-medical-teal-light" />
        </div>
        <div className="min-w-0 flex-1">
          <h1 className="text-white font-bold text-lg leading-tight">Aibolit</h1>
          {username ? (
            <div className="flex items-center gap-1 text-blue-200 text-xs truncate">
              <User size={10} className="shrink-0" />
              <span className="truncate">{username}</span>
            </div>
          ) : (
            <p className="text-blue-200 text-xs">Медицинский портал</p>
          )}
        </div>
        {onClose && (
          <button onClick={onClose} className="text-blue-200 hover:text-white md:hidden shrink-0">
            <X size={20} />
          </button>
        )}
      </div>

      <nav aria-label="Основная навигация" className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {patientId && (
          <>
            <p className="px-4 text-xs font-semibold text-blue-300 uppercase tracking-wider mb-2">
              Мои данные
            </p>
            <NavLink to={`/patients/${patientId}`} end className={navClass} onClick={handleNavClick}>
              <LayoutDashboard size={18} /> Панель
            </NavLink>
            <NavLink to={`/patients/${patientId}/timeline`} className={navClass} onClick={handleNavClick}>
              <Clock size={18} /> Хронология
            </NavLink>
            <NavLink to={`/patients/${patientId}/labs`} className={navClass} onClick={handleNavClick}>
              <FlaskConical size={18} /> Анализы
            </NavLink>
            <NavLink to={`/patients/${patientId}/vitals`} className={navClass} onClick={handleNavClick}>
              <HeartPulse size={18} /> Витальные
            </NavLink>
          </>
        )}

        <p className="px-4 pt-4 text-xs font-semibold text-blue-300 uppercase tracking-wider mb-2">
          Инструменты
        </p>
        <NavLink to="/chat" className={navClass} onClick={handleNavClick}>
          <MessageCircle size={18} /> Чат с врачом
        </NavLink>
        <NavLink to="/consult" className={navClass} onClick={handleNavClick}>
          <MessageSquare size={18} /> AI Консультация
        </NavLink>
        <NavLink to="/diagnostics" className={navClass} onClick={handleNavClick}>
          <Activity size={18} /> Диагностика
        </NavLink>
        <NavLink to="/drugs" className={navClass} onClick={handleNavClick}>
          <Pill size={18} /> Лекарства
        </NavLink>
        <NavLink to="/documents" className={navClass} onClick={handleNavClick}>
          <FileText size={18} /> Документы
        </NavLink>
      </nav>

      <div className="px-4 py-4 border-t border-white/10 space-y-2">
        <div className="text-blue-400 text-xs text-center space-y-0.5">
          <p>35 специализаций · 31 инструмент</p>
        </div>
        <div className="p-2 bg-white/5 rounded-lg">
          <p className="text-yellow-300 text-xs text-center leading-tight">
            Только для демо и обучения
          </p>
        </div>
        <NavLink to="/settings" className={navClass} onClick={handleNavClick}>
          <Settings size={16} /> Настройки
        </NavLink>
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-blue-200 hover:bg-white/10 hover:text-white transition"
        >
          <LogOut size={16} /> Выйти
        </button>
      </div>
    </aside>
  );
}
