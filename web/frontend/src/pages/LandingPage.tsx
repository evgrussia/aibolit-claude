import { Link } from 'react-router-dom';
import {
  Heart, MessageCircle, Activity, Pill, FileText, FlaskConical,
  HeartPulse, Shield, Stethoscope, Brain, Eye, Bone,
  Baby, Syringe, Microscope, Sparkles, ArrowRight, CheckCircle2,
  Smartphone, Lock, Clock, Users, ChevronRight, AlertTriangle,
  BookOpen, Zap, Globe,
} from 'lucide-react';

const SPECIALIZATIONS = [
  { icon: Heart, name: 'Кардиология', desc: 'Сердце и сосуды' },
  { icon: Brain, name: 'Неврология', desc: 'Нервная система' },
  { icon: Stethoscope, name: 'Терапия', desc: 'Общая медицина' },
  { icon: Activity, name: 'Пульмонология', desc: 'Лёгкие и дыхание' },
  { icon: Eye, name: 'Офтальмология', desc: 'Зрение' },
  { icon: Bone, name: 'Ортопедия', desc: 'Опорно-двигательный' },
  { icon: FlaskConical, name: 'Эндокринология', desc: 'Гормоны и обмен' },
  { icon: Baby, name: 'Педиатрия', desc: 'Детское здоровье' },
  { icon: Syringe, name: 'Аллергология', desc: 'Аллергии' },
  { icon: Microscope, name: 'Онкология', desc: 'Новообразования' },
  { icon: HeartPulse, name: 'Гастроэнтерология', desc: 'ЖКТ' },
  { icon: Shield, name: 'Дерматология', desc: 'Кожа' },
];

const FEATURES = [
  {
    icon: MessageCircle,
    title: 'AI-чат с врачом',
    desc: 'Многоходовой диалог с AI-врачом выбранной специализации. Врач задаёт уточняющие вопросы, анализирует симптомы и даёт информационные рекомендации.',
    details: [
      'Выбор из 35 медицинских специализаций',
      'Умный ресепшн — AI подбирает специалиста по жалобам',
      'SSE-стриминг ответов в реальном времени',
      'Сохранение истории всех консультаций',
      'Учёт данных из медицинской карты пациента',
    ],
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Activity,
    title: 'AI-диагностика',
    desc: 'Комплекс инструментов для анализа состояния здоровья на основе введённых данных.',
    details: [
      'Расшифровка лабораторных анализов',
      'Оценка витальных показателей',
      'Расчёт скорости клубочковой фильтрации (СКФ)',
      'Расчёт сердечно-сосудистого риска',
      'Визуализация трендов показателей',
    ],
    color: 'from-emerald-500 to-teal-500',
  },
  {
    icon: Pill,
    title: 'Справочник лекарств',
    desc: 'Инструменты для работы с лекарственными препаратами и проверки их совместимости.',
    details: [
      'Поиск по названию и действующему веществу',
      'Информация о показаниях и противопоказаниях',
      'Проверка взаимодействий между препаратами',
      'Рекомендации по дозировке (справочные)',
      'Предупреждения о побочных эффектах',
    ],
    color: 'from-violet-500 to-purple-500',
  },
  {
    icon: FileText,
    title: 'Медицинские документы',
    desc: 'Генерация и хранение медицинских документов на основе данных из карты пациента.',
    details: [
      'Генерация медицинских выписок',
      'Создание направлений к специалистам',
      'Формирование заключений',
      'PDF-экспорт документов',
      'Архив всех сгенерированных документов',
    ],
    color: 'from-amber-500 to-orange-500',
  },
  {
    icon: FlaskConical,
    title: 'Лабораторные анализы',
    desc: 'Ведение и анализ результатов лабораторных исследований с отслеживанием динамики.',
    details: [
      'Ввод результатов анализов',
      'AI-расшифровка с пояснениями',
      'Графики динамики показателей',
      'Цветовая индикация отклонений',
      'Сравнение с референсными значениями',
    ],
    color: 'from-pink-500 to-rose-500',
  },
  {
    icon: HeartPulse,
    title: 'Мониторинг витальных',
    desc: 'Отслеживание основных показателей здоровья с визуализацией трендов.',
    details: [
      'Артериальное давление (систолическое/диастолическое)',
      'Пульс и сатурация кислорода',
      'Температура тела',
      'Графики и тренды',
      'Оповещения при критических значениях',
    ],
    color: 'from-red-500 to-pink-500',
  },
];

const SAFETY_FEATURES = [
  {
    icon: AlertTriangle,
    title: 'Система Red Flags',
    desc: 'Автоматическое обнаружение опасных симптомов (81 паттерн): кардиологических, неврологических, аллергических, педиатрических и других экстренных состояний.',
  },
  {
    icon: Shield,
    title: 'Медицинские дисклеймеры',
    desc: 'Каждый ответ AI сопровождается предупреждением, что рекомендации носят информационный характер и не заменяют консультацию врача.',
  },
  {
    icon: Lock,
    title: 'Защита данных',
    desc: 'JWT-аутентификация, шифрование, маскирование медицинских данных в логах. Соответствие требованиям 152-ФЗ.',
  },
  {
    icon: BookOpen,
    title: 'Доказательная медицина',
    desc: 'AI опирается на клинические рекомендации Минздрав РФ, WHO, PubMed, Cochrane Library. Указывает уровень доказательности.',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <header className="relative overflow-hidden bg-gradient-to-br from-medical-navy via-medical-navy-light to-medical-teal">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-medical-teal-light rounded-full blur-3xl" />
        </div>

        <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <Heart className="w-6 h-6 text-medical-teal-light" />
            </div>
            <span className="text-white font-bold text-xl">Aibolit AI</span>
          </div>
          <Link
            to="/login"
            className="px-5 py-2.5 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-xl text-sm font-medium transition border border-white/20"
          >
            Войти
          </Link>
        </nav>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 sm:pt-20 sm:pb-28">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 backdrop-blur-sm rounded-full text-sm text-blue-100 mb-6 border border-white/10">
              <Sparkles size={14} className="text-medical-teal-light" />
              35 медицинских специализаций
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Ваш личный
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-medical-teal-light to-cyan-300">
                AI-медицинский
              </span>
              <br />
              помощник
            </h1>
            <p className="text-lg sm:text-xl text-blue-100 leading-relaxed mb-8 max-w-2xl">
              Бесплатный портал пациента с AI-врачами 35 специализаций.
              Информационные консультации, анализ симптомов, расшифровка анализов,
              проверка лекарств — на основе доказательной медицины.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-7 py-3.5 bg-white text-medical-navy rounded-xl font-semibold hover:shadow-lg hover:shadow-white/20 transition group"
              >
                Начать бесплатно
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="#features"
                className="inline-flex items-center gap-2 px-7 py-3.5 bg-white/10 backdrop-blur-sm text-white rounded-xl font-medium hover:bg-white/20 transition border border-white/20"
              >
                Узнать больше
              </a>
            </div>
          </div>
        </div>

        {/* Stats bar */}
        <div className="relative z-10 border-t border-white/10 bg-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">35</div>
              <div className="text-sm text-blue-200">Специализаций</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">31</div>
              <div className="text-sm text-blue-200">Инструмент</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">81</div>
              <div className="text-sm text-blue-200">Red Flag паттерн</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-bold text-white">24/7</div>
              <div className="text-sm text-blue-200">Доступность</div>
            </div>
          </div>
        </div>
      </header>

      {/* Specializations */}
      <section className="py-16 sm:py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              35 медицинских специализаций
            </h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              Выберите врача нужной специализации или опишите жалобы — AI-ресепшн
              подберёт подходящего специалиста автоматически
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {SPECIALIZATIONS.map(({ icon: Icon, name, desc }) => (
              <div
                key={name}
                className="bg-white rounded-xl p-4 border border-gray-100 hover:border-medical-teal/30 hover:shadow-md transition group"
              >
                <div className="w-10 h-10 rounded-lg bg-medical-teal/10 flex items-center justify-center mb-3 group-hover:bg-medical-teal/20 transition">
                  <Icon size={20} className="text-medical-teal" />
                </div>
                <h3 className="font-semibold text-gray-800 text-sm mb-0.5">{name}</h3>
                <p className="text-xs text-gray-400">{desc}</p>
              </div>
            ))}
          </div>

          <p className="text-center text-sm text-gray-400 mt-6">
            ...и ещё 23 специализации: урология, гинекология, психиатрия, ревматология,
            нефрология, гематология, инфектология, хирургия и другие
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Полный набор инструментов
            </h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              Всё необходимое для информационного сопровождения вашего здоровья в одном месте
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map(({ icon: Icon, title, desc, details, color }) => (
              <div
                key={title}
                className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-xl hover:shadow-gray-100/50 transition group"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 shadow-lg shadow-${color.split(' ')[0].replace('from-', '')}/20`}>
                  <Icon size={22} className="text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-500 mb-4 leading-relaxed">{desc}</p>
                <ul className="space-y-2">
                  {details.map((detail) => (
                    <li key={detail} className="flex items-start gap-2 text-sm text-gray-600">
                      <CheckCircle2 size={14} className="text-medical-teal mt-0.5 shrink-0" />
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 sm:py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Как это работает
            </h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              Три простых шага до информационной консультации
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              {
                step: '1',
                title: 'Регистрация',
                desc: 'Создайте аккаунт за 2 минуты. Укажите базовые данные и медицинскую информацию (аллергии, семейный анамнез).',
                icon: Users,
              },
              {
                step: '2',
                title: 'Опишите жалобы',
                desc: 'Расскажите о симптомах. AI-ресепшн проанализирует жалобы и подберёт подходящего специалиста из 35 направлений.',
                icon: MessageCircle,
              },
              {
                step: '3',
                title: 'Получите рекомендации',
                desc: 'AI-врач проведёт диалог, задаст уточняющие вопросы и предоставит информационные рекомендации с учётом вашей карты.',
                icon: Sparkles,
              },
            ].map(({ step, title, desc, icon: Icon }) => (
              <div key={step} className="text-center">
                <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-medical-navy to-medical-teal shadow-lg mb-5">
                  <Icon size={24} className="text-white" />
                  <div className="absolute -top-2 -right-2 w-7 h-7 bg-white rounded-full flex items-center justify-center shadow-md">
                    <span className="text-sm font-bold text-medical-navy">{step}</span>
                  </div>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Safety */}
      <section className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-red-50 rounded-full text-sm text-red-700 mb-4">
              <Shield size={14} />
              Безопасность — приоритет
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Многоуровневая система безопасности
            </h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              AI-система постоянно контролирует безопасность рекомендаций и предупреждает
              об опасных симптомах
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {SAFETY_FEATURES.map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="bg-gradient-to-b from-white to-slate-50 rounded-xl border border-gray-100 p-5 hover:shadow-md transition"
              >
                <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center mb-4">
                  <Icon size={18} className="text-red-500" />
                </div>
                <h3 className="font-bold text-gray-900 text-sm mb-2">{title}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech & Platform */}
      <section className="py-16 sm:py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Платформа и технологии
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              { icon: Smartphone, title: 'PWA приложение', desc: 'Работает как нативное приложение на телефоне. Установите через браузер — иконка на рабочем столе.' },
              { icon: Zap, title: 'Стриминг ответов', desc: 'Ответы AI появляются в реальном времени по мере генерации. Никакого ожидания загрузки.' },
              { icon: Clock, title: 'История консультаций', desc: 'Все диалоги сохраняются. Вернитесь к любой консультации и продолжите разговор с того места.' },
              { icon: Lock, title: 'Аутентификация', desc: 'JWT-токены, хеширование паролей SHA-256, защита от перебора, rate limiting.' },
              { icon: Globe, title: 'Открытый и бесплатный', desc: 'Полностью бесплатный проект для демонстрации и обучения. Без рекламы и подписок.' },
              { icon: BookOpen, title: 'Медицинская база', desc: 'Справочники МКБ-10, лекарственных средств, клинических рекомендаций и лабораторных норм.' },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="flex gap-4 p-4 bg-white rounded-xl border border-gray-100">
                <div className="w-10 h-10 rounded-lg bg-medical-teal/10 flex items-center justify-center shrink-0">
                  <Icon size={18} className="text-medical-teal" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 text-sm mb-1">{title}</h3>
                  <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Important Disclaimer */}
      <section className="py-12 bg-amber-50 border-y border-amber-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <AlertTriangle size={24} className="text-amber-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-gray-900 mb-3">Важная информация</h3>
          <p className="text-sm text-gray-700 leading-relaxed max-w-2xl mx-auto">
            Aibolit AI — информационный сервис, созданный для демонстрации и обучения.
            Он <strong>не является</strong> медицинским учреждением и <strong>не заменяет</strong> консультацию
            реального врача. Все рекомендации носят исключительно информационный характер.
            При проблемах со здоровьем обращайтесь к квалифицированному специалисту.
            При угрозе жизни вызывайте скорую помощь: <strong>103</strong> (или <strong>112</strong>).
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 sm:py-20 bg-gradient-to-br from-medical-navy via-medical-navy-light to-medical-teal">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Попробуйте прямо сейчас
          </h2>
          <p className="text-lg text-blue-100 mb-8 max-w-xl mx-auto">
            Регистрация занимает 2 минуты. Все функции доступны бесплатно.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-medical-navy rounded-xl font-semibold text-lg hover:shadow-xl hover:shadow-white/20 transition group"
          >
            Создать аккаунт
            <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Heart size={18} className="text-medical-teal" />
              <span className="text-white font-semibold">Aibolit AI</span>
              <span className="text-xs text-gray-500 ml-2">v1.0</span>
            </div>
            <p className="text-xs text-center sm:text-right leading-relaxed">
              Демонстрационный проект. Не для реальной медицинской помощи.
              <br />
              35 специализаций &middot; Доказательная медицина &middot; Открытый и бесплатный
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
