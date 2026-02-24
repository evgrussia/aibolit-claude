import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  HelpCircle, MessageCircle, MessageSquare, Activity, Pill,
  FileText, FlaskConical, HeartPulse, LayoutDashboard, Clock,
  Settings, ChevronRight, Lightbulb, AlertTriangle, Shield,
  Stethoscope, BookOpen, Search, ArrowRight,
} from 'lucide-react';

interface HelpSection {
  id: string;
  icon: React.ElementType;
  title: string;
  description: string;
  link: string;
  linkLabel: string;
  steps: string[];
  tips?: string[];
}

export default function HelpPage() {
  const { patientId } = useAuth();

  const sections: HelpSection[] = [
    {
      id: 'chat',
      icon: MessageCircle,
      title: 'Чат с AI-врачом',
      description: 'Многоходовой диалог с AI-врачом выбранной специализации. AI задаёт уточняющие вопросы, анализирует симптомы и даёт информационные рекомендации с учётом данных из вашей медицинской карты.',
      link: '/chat',
      linkLabel: 'Открыть чаты',
      steps: [
        'Перейдите в раздел "Чат с врачом" в боковом меню',
        'Нажмите "Новая консультация" для начала нового диалога',
        'Или перейдите через "AI Консультация" для подбора специалиста по жалобам',
        'Опишите свои симптомы в текстовом поле',
        'AI-врач ответит и задаст уточняющие вопросы',
        'Продолжайте диалог столько, сколько нужно',
        'Все консультации сохраняются в истории',
      ],
      tips: [
        'Описывайте симптомы максимально подробно: когда начались, что усиливает/ослабляет',
        'AI учитывает данные вашей карты — аллергии, препараты, анамнез',
        'Вы можете вернуться к любой прошлой консультации и продолжить диалог',
      ],
    },
    {
      id: 'consult',
      icon: MessageSquare,
      title: 'AI Консультация (Ресепшн)',
      description: 'Умный подбор специалиста по вашим жалобам. Система анализирует описание симптомов и рекомендует подходящего AI-врача из 35 специализаций.',
      link: '/consult',
      linkLabel: 'Начать консультацию',
      steps: [
        'Перейдите в раздел "AI Консультация"',
        'Опишите свои жалобы и симптомы в текстовом поле',
        'Нажмите "Подобрать специалиста" — AI проанализирует жалобы',
        'Система предложит подходящих специалистов с обоснованием',
        'Выберите врача — или нажмите "Выбрать самостоятельно" для полного списка',
        'Чат с выбранным специалистом начнётся автоматически',
      ],
      tips: [
        'Можно пропустить автоподбор и выбрать специалиста из полного списка',
        'AI учитывает комплекс жалоб — может предложить несколько специалистов',
      ],
    },
    {
      id: 'dashboard',
      icon: LayoutDashboard,
      title: 'Панель пациента (Dashboard)',
      description: 'Главная страница вашего личного кабинета. Показывает сводную информацию: данные карты, последние анализы, витальные показатели, активные диагнозы и хронологию событий.',
      link: patientId ? `/patients/${patientId}` : '/',
      linkLabel: 'Открыть панель',
      steps: [
        'Панель открывается автоматически после входа',
        'В верхней части — ваши персональные данные из карты',
        'Карточки показывают ключевые показатели: анализы, витальные, диагнозы',
        'Нажмите на любую карточку для перехода в подробный раздел',
      ],
    },
    {
      id: 'diagnostics',
      icon: Activity,
      title: 'AI-диагностика',
      description: 'Комплекс диагностических инструментов: расшифровка анализов, оценка витальных, расчёт скорости клубочковой фильтрации (СКФ) и сердечно-сосудистого риска.',
      link: '/diagnostics',
      linkLabel: 'Открыть диагностику',
      steps: [
        'Перейдите в раздел "Диагностика"',
        'Выберите нужный инструмент: анализы, витальные, СКФ или сердечно-сосудистый риск',
        'Введите данные в соответствующие поля',
        'Нажмите кнопку расчёта/анализа',
        'Получите результат с интерпретацией и рекомендациями',
      ],
      tips: [
        'Расшифровка анализов — введите название теста, значение и единицы измерения',
        'Оценка витальных — введите давление, пульс, температуру, сатурацию',
        'СКФ — рассчитывается по креатинину, возрасту, полу',
        'Сердечно-сосудистый риск — по шкале Framingham (возраст, холестерин, давление)',
      ],
    },
    {
      id: 'drugs',
      icon: Pill,
      title: 'Справочник лекарств',
      description: 'Поиск информации о лекарствах и проверка взаимодействий между препаратами. Справочные данные о показаниях, противопоказаниях и побочных эффектах.',
      link: '/drugs',
      linkLabel: 'Открыть справочник',
      steps: [
        'Перейдите в раздел "Лекарства"',
        'Используйте поиск для нахождения препарата по названию',
        'Для проверки взаимодействий выберите несколько препаратов',
        'Система покажет информацию о совместимости и рисках',
      ],
      tips: [
        'Ищите по торговому названию или действующему веществу',
        'Проверяйте взаимодействия ВСЕХ принимаемых вами препаратов одновременно',
        'Информация справочная — перед приёмом консультируйтесь с врачом',
      ],
    },
    {
      id: 'labs',
      icon: FlaskConical,
      title: 'Лабораторные анализы',
      description: 'Ведение результатов лабораторных анализов с AI-расшифровкой, отслеживанием динамики и цветовой индикацией отклонений от нормы.',
      link: patientId ? `/patients/${patientId}/labs` : '/',
      linkLabel: 'Мои анализы',
      steps: [
        'Перейдите в раздел "Анализы" в боковом меню',
        'Просмотрите список всех ваших анализов',
        'Нажмите на конкретный анализ для детальной расшифровки',
        'Графики показывают динамику показателей во времени',
        'Цветовая маркировка: зелёный — норма, жёлтый — отклонение, красный — критично',
      ],
    },
    {
      id: 'vitals',
      icon: HeartPulse,
      title: 'Витальные показатели',
      description: 'Мониторинг основных показателей здоровья: артериальное давление, пульс, температура, сатурация кислорода. Графики трендов и оповещения.',
      link: patientId ? `/patients/${patientId}/vitals` : '/',
      linkLabel: 'Мои витальные',
      steps: [
        'Перейдите в раздел "Витальные" в боковом меню',
        'Просмотрите текущие и исторические показатели',
        'Графики показывают тренды за выбранный период',
        'Система предупредит при критических значениях',
      ],
    },
    {
      id: 'timeline',
      icon: Clock,
      title: 'Хронология здоровья',
      description: 'Все медицинские события в хронологическом порядке: консультации, анализы, изменения витальных, новые диагнозы.',
      link: patientId ? `/patients/${patientId}/timeline` : '/',
      linkLabel: 'Моя хронология',
      steps: [
        'Перейдите в раздел "Хронология" в боковом меню',
        'Все события отображаются на временной шкале',
        'Нажмите на событие для просмотра деталей',
        'Используйте фильтры для отбора по типу события',
      ],
    },
    {
      id: 'documents',
      icon: FileText,
      title: 'Медицинские документы',
      description: 'Генерация медицинских документов на основе данных карты: выписки, направления, заключения. Экспорт в PDF.',
      link: '/documents',
      linkLabel: 'Мои документы',
      steps: [
        'Перейдите в раздел "Документы"',
        'Выберите тип документа для генерации',
        'AI сформирует документ на основе данных вашей карты',
        'Скачайте готовый документ в формате PDF',
        'Все сгенерированные документы сохраняются в архиве',
      ],
    },
    {
      id: 'settings',
      icon: Settings,
      title: 'Настройки аккаунта',
      description: 'Управление аккаунтом: смена пароля, удаление учётной записи.',
      link: '/settings',
      linkLabel: 'Открыть настройки',
      steps: [
        'Перейдите в "Настройки" внизу бокового меню',
        'Для смены пароля введите текущий и новый пароль',
        'Пароль должен содержать минимум 8 символов, буквы и цифры',
        'Удаление аккаунта — необратимая операция',
      ],
    },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <HelpCircle size={24} className="text-medical-teal" /> Помощь
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Подробное руководство по всем разделам системы Aibolit AI
        </p>
      </div>

      {/* Quick navigation */}
      <div className="bg-medical-teal/5 border border-medical-teal/20 rounded-xl p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-3">
          <Search size={16} className="text-medical-teal" />
          <h2 className="text-sm font-semibold text-gray-800">Быстрая навигация</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          {sections.map(({ id, icon: Icon, title }) => (
            <a
              key={id}
              href={`#help-${id}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-lg text-xs font-medium text-gray-600 hover:text-medical-teal hover:border-medical-teal/30 border border-gray-200 transition"
            >
              <Icon size={12} />
              {title}
            </a>
          ))}
        </div>
      </div>

      {/* Important disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 sm:p-5">
        <div className="flex items-start gap-3">
          <AlertTriangle size={18} className="text-amber-500 mt-0.5 shrink-0" />
          <div>
            <h3 className="text-sm font-semibold text-gray-800 mb-1">Важно</h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              Aibolit AI — информационный сервис. Все рекомендации AI-врачей носят
              исключительно информационный характер и не являются медицинской консультацией.
              При проблемах со здоровьем обращайтесь к реальному врачу.
              При угрозе жизни вызывайте скорую помощь: <strong>103</strong> (или <strong>112</strong>).
            </p>
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-5">
        {sections.map(({ id, icon: Icon, title, description, link, linkLabel, steps, tips }) => (
          <div
            key={id}
            id={`help-${id}`}
            className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden scroll-mt-4"
          >
            <div className="p-4 sm:p-5">
              {/* Header */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-medical-teal/10 flex items-center justify-center shrink-0">
                    <Icon size={18} className="text-medical-teal" />
                  </div>
                  <h2 className="text-base font-bold text-gray-900">{title}</h2>
                </div>
                <Link
                  to={link}
                  className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 bg-medical-teal/10 text-medical-teal rounded-lg text-xs font-medium hover:bg-medical-teal/20 transition shrink-0"
                >
                  {linkLabel}
                  <ChevronRight size={12} />
                </Link>
              </div>

              <p className="text-sm text-gray-600 leading-relaxed mb-4">{description}</p>

              {/* Steps */}
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2.5">
                  Как использовать
                </h3>
                <ol className="space-y-1.5">
                  {steps.map((step, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-sm text-gray-600">
                      <span className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center shrink-0 text-xs font-medium text-gray-500 mt-0.5">
                        {i + 1}
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* Tips */}
              {tips && tips.length > 0 && (
                <div className="bg-blue-50/50 rounded-lg p-3">
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <Lightbulb size={12} className="text-blue-500" />
                    <span className="text-xs font-semibold text-blue-700">Советы</span>
                  </div>
                  <ul className="space-y-1">
                    {tips.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-blue-700/80">
                        <span className="text-blue-400 mt-px">&#8226;</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Mobile link */}
              <Link
                to={link}
                className="sm:hidden mt-4 w-full inline-flex items-center justify-center gap-1.5 px-3 py-2.5 bg-medical-teal/10 text-medical-teal rounded-lg text-sm font-medium hover:bg-medical-teal/20 transition"
              >
                {linkLabel}
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        ))}
      </div>

      {/* Additional info */}
      <div className="grid sm:grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-medical-navy to-medical-navy-light rounded-xl p-5 text-white">
          <div className="flex items-center gap-2 mb-3">
            <Stethoscope size={18} className="text-medical-teal-light" />
            <h3 className="font-semibold text-sm">35 специализаций</h3>
          </div>
          <p className="text-xs text-blue-200 leading-relaxed">
            Кардиология, неврология, терапия, пульмонология, гастроэнтерология,
            эндокринология, урология, гинекология, дерматология, офтальмология,
            ортопедия, ревматология, аллергология, онкология, психиатрия,
            нефрология, гематология, инфектология, хирургия, педиатрия и другие.
          </p>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-amber-50 rounded-xl p-5 border border-red-100">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={18} className="text-red-500" />
            <h3 className="font-semibold text-sm text-gray-800">Система безопасности</h3>
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">
            AI автоматически обнаруживает 81 паттерн опасных симптомов (red flags):
            кардиологических, неврологических, аллергических, педиатрических и акушерских.
            При обнаружении — предупреждает и рекомендует вызвать скорую помощь.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen size={18} className="text-medical-teal" />
          <h3 className="font-semibold text-gray-800 text-sm">О проекте</h3>
        </div>
        <p className="text-sm text-gray-600 leading-relaxed">
          Aibolit AI — бесплатный демонстрационный проект, созданный для обучения
          и демонстрации возможностей AI в медицине. Использует модели Claude
          для генерации ответов на основе доказательной медицины. Все данные
          защищены шифрованием и не передаются третьим лицам.
        </p>
      </div>
    </div>
  );
}
