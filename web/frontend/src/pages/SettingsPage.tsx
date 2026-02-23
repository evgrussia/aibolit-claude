import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { changePassword, deleteAccount } from '../api/auth';
import ConfirmDialog from '../components/shared/ConfirmDialog';
import Card from '../components/shared/Card';
import { Settings, Lock, Trash2, Loader2 } from 'lucide-react';

export default function SettingsPage() {
  const { username, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPw, setChangingPw] = useState(false);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error('Пароли не совпадают');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Пароль должен содержать минимум 8 символов');
      return;
    }
    if (!/[a-zA-Zа-яА-ЯёЁ]/.test(newPassword) || !/\d/.test(newPassword)) {
      toast.error('Пароль должен содержать буквы и цифры');
      return;
    }
    setChangingPw(true);
    try {
      await changePassword(oldPassword, newPassword);
      toast.success('Пароль успешно изменён');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        || (err as Error).message || 'Ошибка смены пароля';
      toast.error(msg);
    } finally {
      setChangingPw(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    try {
      await deleteAccount();
      toast.success('Аккаунт удалён');
      logout();
      navigate('/login', { replace: true });
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка удаления аккаунта');
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-xl">
      <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
        <Settings size={24} className="text-medical-teal" /> Настройки
      </h1>

      <Card title="Аккаунт" icon={<Lock size={18} />}>
        <p className="text-sm text-gray-500 mb-4">
          Вы вошли как <span className="font-medium text-gray-700">{username}</span>
        </p>

        <form onSubmit={handleChangePassword} className="space-y-3">
          <div>
            <label htmlFor="old-pw" className="block text-xs font-medium text-gray-600 mb-1">Текущий пароль</label>
            <input
              id="old-pw"
              type="password"
              value={oldPassword}
              onChange={e => setOldPassword(e.target.value)}
              required
              disabled={changingPw}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
            />
          </div>
          <div>
            <label htmlFor="new-pw" className="block text-xs font-medium text-gray-600 mb-1">Новый пароль</label>
            <input
              id="new-pw"
              type="password"
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              required
              disabled={changingPw}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
            />
          </div>
          <div>
            <label htmlFor="confirm-pw" className="block text-xs font-medium text-gray-600 mb-1">Подтвердите пароль</label>
            <input
              id="confirm-pw"
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              required
              disabled={changingPw}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={changingPw}
            className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
          >
            {changingPw ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Изменить пароль'}
          </button>
        </form>
      </Card>

      <Card title="Опасная зона">
        <p className="text-sm text-gray-500 mb-4">
          Удаление аккаунта необратимо. Ваша медицинская карта будет сохранена, но вход в систему станет невозможен.
        </p>
        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
        >
          <Trash2 size={16} /> Удалить аккаунт
        </button>
      </Card>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteAccount}
        title="Удалить аккаунт"
        message="Вы уверены? Это действие необратимо. Вы потеряете доступ к системе."
        confirmLabel="Удалить аккаунт"
        isPending={deleting}
      />
    </div>
  );
}
