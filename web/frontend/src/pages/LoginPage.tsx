import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import type { RegisterData } from '../contexts/AuthContext';

type Tab = 'login' | 'register';
type RegStep = 0 | 1 | 2;

const GENDER_OPTIONS = [
  { value: 'male', label: 'Мужской' },
  { value: 'female', label: 'Женский' },
  { value: 'other', label: 'Другой' },
];

const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function LoginPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab] = useState<Tab>('login');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Login state
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [showLoginPw, setShowLoginPw] = useState(false);

  // Register state
  const [regStep, setRegStep] = useState<RegStep>(0);
  const [regData, setRegData] = useState({
    username: '', password: '', confirm: '',
    first_name: '', last_name: '', date_of_birth: '', gender: 'male',
    blood_type: '', allergies: '', family_history: '',
  });
  const [showRegPw, setShowRegPw] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(loginData.username, loginData.password);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.message || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (regData.password !== regData.confirm) {
      setError('Пароли не совпадают');
      return;
    }
    if (regData.password.length < 8) {
      setError('Пароль должен содержать минимум 8 символов');
      return;
    }
    if (!/[a-zA-Zа-яА-ЯёЁ]/.test(regData.password) || !/\d/.test(regData.password)) {
      setError('Пароль должен содержать буквы и цифры');
      return;
    }

    setLoading(true);
    try {
      const payload: RegisterData = {
        username: regData.username,
        password: regData.password,
        first_name: regData.first_name,
        last_name: regData.last_name,
        date_of_birth: regData.date_of_birth,
        gender: regData.gender,
        blood_type: regData.blood_type || undefined,
        allergies: regData.allergies
          ? regData.allergies.split(',').map(s => ({ substance: s.trim() })).filter(a => a.substance)
          : undefined,
        family_history: regData.family_history
          ? regData.family_history.split(',').map(s => s.trim()).filter(Boolean)
          : undefined,
      };
      await register(payload);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.message || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  const canAdvanceStep0 = regData.username && regData.password && regData.confirm;
  const canAdvanceStep1 = regData.first_name && regData.last_name && regData.date_of_birth && regData.gender;

  const inputClass = 'w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal focus:border-transparent transition';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-medical-navy to-medical-teal rounded-2xl shadow-lg mb-4">
            <Heart className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Aibolit</h1>
          <p className="text-gray-500 text-sm mt-1">Медицинский портал пациента</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-100">
            <button
              onClick={() => { setTab('login'); setError(''); }}
              className={`flex-1 py-3.5 text-sm font-medium transition ${
                tab === 'login' ? 'text-medical-teal border-b-2 border-medical-teal bg-teal-50/30' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              Вход
            </button>
            <button
              onClick={() => { setTab('register'); setError(''); setRegStep(0); }}
              className={`flex-1 py-3.5 text-sm font-medium transition ${
                tab === 'register' ? 'text-medical-teal border-b-2 border-medical-teal bg-teal-50/30' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              Регистрация
            </button>
          </div>

          <div className="p-6">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Login form */}
            {tab === 'login' && (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Логин</label>
                  <input
                    type="text"
                    className={inputClass}
                    value={loginData.username}
                    onChange={e => setLoginData({ ...loginData, username: e.target.value })}
                    placeholder="Введите логин"
                    required
                    autoComplete="username"
                    autoFocus
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                  <div className="relative">
                    <input
                      type={showLoginPw ? 'text' : 'password'}
                      className={inputClass + ' pr-10'}
                      value={loginData.password}
                      onChange={e => setLoginData({ ...loginData, password: e.target.value })}
                      placeholder="Введите пароль"
                      required
                      autoComplete="current-password"
                    />
                    <button type="button" onClick={() => setShowLoginPw(!showLoginPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      {showLoginPw ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 bg-gradient-to-r from-medical-navy to-medical-teal text-white rounded-xl font-medium text-sm hover:shadow-lg transition disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading && <Loader2 size={16} className="animate-spin" />}
                  Войти
                </button>
              </form>
            )}

            {/* Register form */}
            {tab === 'register' && (
              <form onSubmit={handleRegister} className="space-y-4">
                {/* Step indicator */}
                <div className="flex items-center gap-2 mb-2">
                  {[0, 1, 2].map(s => (
                    <div key={s} className="flex items-center gap-2 flex-1">
                      <div className={`h-1.5 rounded-full flex-1 transition ${s <= regStep ? 'bg-medical-teal' : 'bg-gray-200'}`} />
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-400 text-center">
                  {regStep === 0 && 'Шаг 1: Учётные данные'}
                  {regStep === 1 && 'Шаг 2: Личные данные'}
                  {regStep === 2 && 'Шаг 3: Медицинские данные (необязательно)'}
                </p>

                {/* Step 0: Credentials */}
                {regStep === 0 && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Логин</label>
                      <input
                        type="text"
                        className={inputClass}
                        value={regData.username}
                        onChange={e => setRegData({ ...regData, username: e.target.value })}
                        placeholder="Придумайте логин"
                        required
                        autoComplete="username"
                        autoFocus
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                      <div className="relative">
                        <input
                          type={showRegPw ? 'text' : 'password'}
                          className={inputClass + ' pr-10'}
                          value={regData.password}
                          onChange={e => setRegData({ ...regData, password: e.target.value })}
                          placeholder="Минимум 8 символов (буквы + цифры)"
                          required
                          autoComplete="new-password"
                        />
                        <button type="button" onClick={() => setShowRegPw(!showRegPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                          {showRegPw ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Подтвердите пароль</label>
                      <input
                        type="password"
                        className={inputClass}
                        value={regData.confirm}
                        onChange={e => setRegData({ ...regData, confirm: e.target.value })}
                        placeholder="Повторите пароль"
                        required
                        autoComplete="new-password"
                      />
                    </div>
                    <button
                      type="button"
                      disabled={!canAdvanceStep0}
                      onClick={() => { setError(''); setRegStep(1); }}
                      className="w-full py-2.5 bg-gradient-to-r from-medical-navy to-medical-teal text-white rounded-xl font-medium text-sm hover:shadow-lg transition disabled:opacity-50"
                    >
                      Далее
                    </button>
                  </>
                )}

                {/* Step 1: Personal info */}
                {regStep === 1 && (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                        <input
                          type="text"
                          className={inputClass}
                          value={regData.first_name}
                          onChange={e => setRegData({ ...regData, first_name: e.target.value })}
                          placeholder="Иван"
                          required
                          autoFocus
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                        <input
                          type="text"
                          className={inputClass}
                          value={regData.last_name}
                          onChange={e => setRegData({ ...regData, last_name: e.target.value })}
                          placeholder="Иванов"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Дата рождения</label>
                      <input
                        type="date"
                        className={inputClass}
                        value={regData.date_of_birth}
                        onChange={e => setRegData({ ...regData, date_of_birth: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Пол</label>
                      <select
                        className={inputClass}
                        value={regData.gender}
                        onChange={e => setRegData({ ...regData, gender: e.target.value })}
                      >
                        {GENDER_OPTIONS.map(g => (
                          <option key={g.value} value={g.value}>{g.label}</option>
                        ))}
                      </select>
                    </div>
                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => setRegStep(0)}
                        className="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl font-medium text-sm hover:bg-gray-50 transition"
                      >
                        Назад
                      </button>
                      <button
                        type="button"
                        disabled={!canAdvanceStep1}
                        onClick={() => { setError(''); setRegStep(2); }}
                        className="flex-1 py-2.5 bg-gradient-to-r from-medical-navy to-medical-teal text-white rounded-xl font-medium text-sm hover:shadow-lg transition disabled:opacity-50"
                      >
                        Далее
                      </button>
                    </div>
                  </>
                )}

                {/* Step 2: Medical (optional) */}
                {regStep === 2 && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Группа крови</label>
                      <select
                        className={inputClass}
                        value={regData.blood_type}
                        onChange={e => setRegData({ ...regData, blood_type: e.target.value })}
                      >
                        <option value="">Не указана</option>
                        {BLOOD_TYPES.map(bt => (
                          <option key={bt} value={bt}>{bt}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Аллергии</label>
                      <input
                        type="text"
                        className={inputClass}
                        value={regData.allergies}
                        onChange={e => setRegData({ ...regData, allergies: e.target.value })}
                        placeholder="Через запятую: пенициллин, пыльца"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Семейный анамнез</label>
                      <input
                        type="text"
                        className={inputClass}
                        value={regData.family_history}
                        onChange={e => setRegData({ ...regData, family_history: e.target.value })}
                        placeholder="Через запятую: диабет у матери, ..."
                      />
                    </div>
                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => setRegStep(1)}
                        className="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl font-medium text-sm hover:bg-gray-50 transition"
                      >
                        Назад
                      </button>
                      <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 py-2.5 bg-gradient-to-r from-medical-navy to-medical-teal text-white rounded-xl font-medium text-sm hover:shadow-lg transition disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        {loading && <Loader2 size={16} className="animate-spin" />}
                        Зарегистрироваться
                      </button>
                    </div>
                  </>
                )}
              </form>
            )}
          </div>
        </div>

        {/* Disclaimer */}
        <p className="text-center text-xs text-gray-400 mt-6 leading-relaxed">
          Только для демо и обучения. Не для реальных пациентов.
        </p>
      </div>
    </div>
  );
}
