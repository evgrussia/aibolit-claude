---
title: "Design System"
created_by: "UI Agent"
created_at: "2025-02-24"
version: "1.0"
---

# Design System — Aibolit AI

> Дизайн-система медицинского портала Aibolit AI: цвета, типографика, компоненты, паттерны

---

## 1. Принципы дизайна

### Основные принципы

| Принцип | Описание | Реализация |
|---------|----------|------------|
| **Доверие** | Пациент доверяет медицинской системе | Спокойные тона, чистый UI, профессиональная типографика |
| **Чистота** | Медицинская эстетика — ничего лишнего | Много белого пространства, минимальный визуальный шум |
| **Доступность** | Доступно для людей с ограничениями | WCAG 2.1 AA, контрастность >= 4.5:1, фокусные состояния |
| **Безопасность** | Критическая информация заметна | Красные баннеры для emergency, жёлтые для предупреждений |
| **Понятность** | Медицинские данные читаемы для пациента | Простой язык, визуальные индикаторы, health literacy |
| **Mobile-first** | PWA для мобильного использования | Responsive, touch-friendly, sidebar -> hamburger |

### Тон дизайна

- **Не клинически-холодный:** теплые акценты, скруглённые углы, плавные анимации
- **Не развлекательный:** никаких ярких градиентов, геймификации, отвлекающих элементов
- **Профессионально-дружелюбный:** как хорошая частная клиника — чисто, современно, заботливо

---

## 2. Цветовая палитра

### Основные цвета (Tailwind custom tokens)

Определены в `tailwind.config.js` как расширение палитры:

| Токен | Hex | Tailwind-класс | Назначение |
|-------|-----|----------------|------------|
| `medical-navy` | `#1e3a5f` | `bg-medical-navy` | Sidebar фон, заголовки, основной акцент |
| `medical-navy-light` | `#2d5a8e` | `bg-medical-navy-light` | Градиент sidebar |
| `medical-teal` | `#0891b2` | `bg-medical-teal`, `text-medical-teal` | Основной акцентный цвет, ссылки, иконки, фокус |
| `medical-teal-light` | `#22d3ee` | `text-medical-teal-light` | Акценты в sidebar, подсветки |
| `medical-light` | `#f0f9ff` | `bg-medical-light` | Светлый фон блоков |
| `medical-bg` | `#f8fafc` | `bg-medical-bg` | Фон приложения |

### Семантические цвета

| Токен | Hex | Tailwind-класс | Медицинский контекст |
|-------|-----|----------------|---------------------|
| `medical-success` | `#10b981` (emerald-500) | `bg-medical-success` | Норма, здоровые показатели, успех |
| `medical-success-light` | `#d1fae5` | `bg-medical-success-light` | Фон нормальных значений |
| `medical-warning` | `#f59e0b` (amber-500) | `bg-medical-warning` | Повышенные показатели, внимание |
| `medical-warning-light` | `#fef3c7` | `bg-medical-warning-light` | Фон предупреждений, дисклеймеры |
| `medical-danger` | `#dc2626` (red-600) | `bg-medical-danger` | Критические показатели, emergency |
| `medical-danger-light` | `#fecaca` | `bg-medical-danger-light` | Фон критических состояний |

### Дополнительные цвета (стандартный Tailwind)

| Использование | Класс | Контекст |
|---------------|-------|----------|
| Info badge | `bg-cyan-100 text-cyan-700` | Информационные бейджи |
| Neutral badge | `bg-gray-100 text-gray-600` | Нейтральные бейджи |
| Фон карточек | `bg-white` | Все карточки и контейнеры |
| Основной текст | `text-gray-800` | Заголовки |
| Вторичный текст | `text-gray-500`, `text-gray-400` | Описания, подсказки |
| Границы | `border-gray-100`, `border-gray-200` | Разделители, рамки карточек |

### Цветовые пороги для витальных показателей

Определены в `constants/medical.ts` -> `VITALS_THRESHOLDS`:

```typescript
bp:   { warning: 140, danger: 180 }       // АД
hr:   { lowDanger: 50, lowWarning: 60,     // ЧСС
         highWarning: 100, highDanger: 120 }
temp: { warning: 37.5 }                    // Температура
spo2: { danger: 95 }                       // SpO2
```

| Состояние | Цвет | Пример |
|-----------|------|--------|
| Норма | `emerald-500` / `emerald-100` | АД < 140, ЧСС 60-100 |
| Предупреждение | `amber-500` / `amber-100` | АД 140-179, ЧСС 50-60 или 100-120 |
| Критическое | `red-600` / `red-100` | АД >= 180, ЧСС < 50 или > 120, SpO2 < 95 |

### Цвета стадий ХБП (CKD_COLORS)

```
G1:  #10b981 (emerald)  — Норма
G2:  #84cc16 (lime)     — Лёгкое снижение
G3a: #f59e0b (amber)    — Умеренное снижение
G3b: #f97316 (orange)   — Значимое снижение
G4:  #dc2626 (red)      — Выраженное снижение
G5:  #7f1d1d (red-900)  — Почечная недостаточность
```

---

## 3. Типографика

### Шрифтовой стек

```css
font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
```

- **Inter** — основной шрифт, загружается через Google Fonts
- **Segoe UI** — fallback для Windows
- **system-ui** — fallback для всех платформ

### Шкала размеров текста

| Элемент | Tailwind-класс | Размер | Контекст |
|---------|---------------|--------|----------|
| Заголовок h1 | `text-2xl font-bold` | 24px | Заголовок страницы |
| Заголовок h2 | `text-xl font-semibold` | 20px | Секция страницы |
| Заголовок h3 | `text-lg font-semibold` | 18px | Заголовок карточки |
| Заголовок карточки | `font-semibold text-gray-800` | 16px (base) | Card title |
| Основной текст | `text-sm` | 14px | Тело текста, формы |
| Мелкий текст | `text-xs` | 12px | Подсказки, бейджи, дисклеймеры |
| Микро-текст | `text-[10px]` | 10px | Теги навыков, метки |

### Цвета текста

| Назначение | Класс | Пример |
|------------|-------|--------|
| Заголовки | `text-gray-800` | Название страницы |
| Основной текст | `text-gray-700` | Описания, тело |
| Вторичный текст | `text-gray-500` | Подзаголовки |
| Третичный текст | `text-gray-400` | Placeholders, мелкие подписи |
| Акцентный | `text-medical-teal` | Ссылки, активные элементы |
| Ошибка | `text-red-700` | Сообщения об ошибках |
| Успех | `text-emerald-700` | Подтверждения |
| Предупреждение | `text-amber-700` | Дисклеймеры |

---

## 4. Сетка и отступы

### Контейнер основного контента

```html
<div class="max-w-7xl mx-auto px-4 md:px-6 py-4 md:py-6">
```

- Максимальная ширина: 80rem (1280px)
- Горизонтальные отступы: 16px (mobile) / 24px (desktop)
- Вертикальные отступы: 16px (mobile) / 24px (desktop)

### Компоновка Sidebar + Content

```
+--------+-----------------------------------+
| 256px  |          Flex-1 (content)         |
| Sidebar|   max-w-7xl mx-auto              |
|        |   px-4 md:px-6 py-4 md:py-6      |
|        |                                   |
| hidden |   Hamburger на mobile             |
| md:block                                   |
+--------+-----------------------------------+
```

### Сетки компонентов

| Контекст | Класс | Описание |
|----------|-------|----------|
| Специализации | `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3` | Сетка карточек специалистов |
| Dashboard виджеты | `grid grid-cols-1 md:grid-cols-2 gap-4` | Основные секции |
| Формы | Однородная `space-y-4` | Вертикальная компоновка полей |
| Табличные данные | `space-y-2` | Строки таблицы |

### Стандартные отступы

| Токен | Значение | Использование |
|-------|----------|---------------|
| `gap-1` | 4px | Между мелкими элементами (теги) |
| `gap-2` | 8px | Между иконкой и текстом |
| `gap-3` | 12px | Между элементами навигации, карточками |
| `gap-4` | 16px | Между секциями, карточками |
| `gap-6` | 24px | Между крупными секциями |
| `p-3` | 12px | Padding мелких блоков (баннеры) |
| `p-4` | 16px | Padding карточек (мобильный) |
| `p-5` | 20px | Padding карточек (стандартный) |
| `p-6` | 24px | Padding модалок |

---

## 5. Компоненты UI

### 5.1. Layout-компоненты

#### Layout (`components/layout/Layout.tsx`)
- **Назначение:** Корневой layout с sidebar + main content area
- **Props:** нет (использует `<Outlet />` из react-router)
- **Поведение:** Desktop: sidebar всегда видим. Mobile: sidebar за hamburger-меню с overlay

#### Sidebar (`components/layout/Sidebar.tsx`)
- **Назначение:** Боковая навигация с логотипом, навигационными ссылками и футером
- **Props:** `onClose?: () => void` (для закрытия на мобильных)
- **Стиль:** Градиент `from-medical-navy to-medical-navy-light`, иконки Lucide

#### Breadcrumbs (`components/shared/Breadcrumbs.tsx`)
- **Назначение:** Навигационные хлебные крошки (автоматически по URL)
- **Props:** нет (берёт данные из `useLocation()` и `useParams()`)
- **Поведение:** Скрывается если глубина <= 1 сегмента

---

### 5.2. Shared UI-компоненты

#### Card (`components/shared/Card.tsx`)
- **Назначение:** Универсальный контейнер для контента
- **Props:** `children`, `className?`, `title?`, `icon?`
- **Стиль:** `bg-white rounded-xl shadow-md border border-gray-100`
- **Анимация:** Framer Motion: fade-in + slide-up (opacity 0->1, y 10->0)

#### Badge (`components/shared/Badge.tsx`)
- **Назначение:** Статусные метки и теги
- **Props:** `children`, `variant?: 'success' | 'warning' | 'danger' | 'info' | 'gray'`, `className?`
- **Стиль:** `rounded-full text-xs font-medium`, цвет зависит от variant
- **Оптимизация:** Обёрнут в `React.memo`

#### Modal (`components/shared/Modal.tsx`)
- **Назначение:** Модальное окно для форм и подтверждений
- **Props:** `isOpen`, `onClose`, `title`, `children`
- **Поведение:** Закрытие по Escape, блокировка scroll, overlay. Mobile: rounded-t-2xl (sheet снизу), desktop: rounded-2xl (центр)
- **Анимация:** Framer Motion: spring-анимация

#### Skeleton (`components/shared/Skeleton.tsx`)
- **Назначение:** Placeholder при загрузке данных
- **Экспорт:** `Skeleton` (базовый), `PatientCardSkeleton`, `TableSkeleton`
- **Props (Skeleton):** `className?`, `style?`
- **Props (TableSkeleton):** `rows?: number`, `cols?: number`
- **Стиль:** `animate-pulse bg-gray-200 rounded`

#### LoadingSpinner (`components/shared/LoadingSpinner.tsx`)
- **Назначение:** Спиннер загрузки
- **Props:** нет
- **Стиль:** Кольцо `border-medical-teal`, 32x32px, `animate-spin`

#### ErrorBoundary (`components/shared/ErrorBoundary.tsx`)
- **Назначение:** Перехват ошибок React-рендеринга
- **Props:** `children`, `fallback?`
- **Поведение:** Показывает fallback UI с кнопкой "Попробовать снова"

#### ApiError (`components/shared/ApiError.tsx`)
- **Назначение:** Отображение ошибки API-запроса
- **Props:** `message: string`, `onRetry?: () => void`
- **Стиль:** `bg-red-50 border-red-200 rounded-xl`, иконка AlertCircle

#### ConfirmDialog (`components/shared/ConfirmDialog.tsx`)
- **Назначение:** Диалог подтверждения деструктивного действия
- **Props:** `isOpen`, `onClose`, `onConfirm`, `title`, `message`, `confirmLabel?`, `isPending?`
- **Стиль:** Кнопка подтверждения `bg-red-500`

#### HelpTooltip (`components/shared/HelpTooltip.tsx`)
- **Назначение:** Подсказка при наведении/клике на иконку
- **Props:** `text: string`, `className?`
- **Поведение:** Hover на desktop, click на mobile. Закрытие по клику вне

#### InfoBanner (`components/shared/InfoBanner.tsx`)
- **Назначение:** Информационный баннер с возможностью сворачивания
- **Props:** `variant?: 'info' | 'tip' | 'warning'`, `title`, `children`, `collapsible?`, `defaultOpen?`
- **Стиль:** `info` = blue, `tip` = amber, `warning` = orange

---

### 5.3. Медицинские компоненты

#### MedicalDisclaimer (`components/shared/MedicalDisclaimer.tsx`)
- **Назначение:** Обязательный дисклеймер на всех AI-ответах
- **Props:** `type?: 'general' | 'lab_analysis' | 'diagnosis' | 'medication'`, `text?`, `className?`
- **Стиль:** `bg-amber-50 border-amber-200 rounded-xl`, иконка AlertTriangle
- **Правило:** Присутствует в КАЖДОМ ответе AI-системы

#### EmergencyBanner (`components/shared/EmergencyBanner.tsx`)
- **Назначение:** Экстренное предупреждение с кнопками вызова скорой
- **Props:** `message?`, `className?`
- **Стиль:** `bg-red-50 border-2 border-red-300 rounded-xl`, role="alert"
- **Кнопки:** Прямые ссылки `tel:103` и `tel:112`
- **Правило:** Показывается НЕМЕДЛЕННО при обнаружении red flags

#### statusBadge (`components/diagnostics/statusBadge.tsx`)
- **Назначение:** Функция для отображения статуса анализа (норма/критический/предупреждение)
- **Логика:** Содержит "норм" / "normal" -> success, "крит" / "critical" -> danger, иначе -> warning

---

### 5.4. Компоненты данных пациента

#### PatientCard (`components/patients/PatientCard.tsx`)
- **Назначение:** Карточка пациента с основной информацией

#### VitalsGauges (`components/patients/VitalsGauges.tsx`)
- **Назначение:** Визуальные индикаторы витальных показателей

#### DiagnosesList (`components/patients/DiagnosesList.tsx`)
- **Назначение:** Список диагнозов пациента (МКБ-10)

#### MedicationsList (`components/patients/MedicationsList.tsx`)
- **Назначение:** Список текущих назначений

---

### 5.5. Формы

#### AddVitalsForm (`components/forms/AddVitalsForm.tsx`)
- **Назначение:** Добавление витальных показателей (в Modal)

#### AddLabResultForm (`components/forms/AddLabResultForm.tsx`)
- **Назначение:** Добавление результата анализа

#### AddDiagnosisForm (`components/forms/AddDiagnosisForm.tsx`)
- **Назначение:** Добавление диагноза

#### AddMedicationForm (`components/forms/AddMedicationForm.tsx`)
- **Назначение:** Добавление назначения

#### AddAllergyForm (`components/forms/AddAllergyForm.tsx`)
- **Назначение:** Добавление аллергии

#### EditProfileForm (`components/forms/EditProfileForm.tsx`)
- **Назначение:** Редактирование профиля пациента

#### LabFileUpload (`components/forms/LabFileUpload.tsx`)
- **Назначение:** Загрузка файла с анализами

### Общий стиль форм

```
Поля:
  input: "w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm
          focus:outline-none focus:ring-2 focus:ring-medical-teal/30
          focus:border-medical-teal"
  label: "block text-sm font-medium text-gray-700 mb-1"

Кнопки:
  primary:   "px-5 py-2 bg-medical-teal text-white rounded-lg
              hover:bg-medical-navy transition-colors"
  secondary: "px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100
              rounded-lg hover:bg-gray-200 transition-colors"
  danger:    "px-4 py-2 text-sm font-medium text-white bg-red-500
              rounded-lg hover:bg-red-600 transition-colors"
  disabled:  "disabled:opacity-50 disabled:cursor-not-allowed"
```

---

### 5.6. Компоненты консультаций

#### SpecialtyGrid (`components/consult/SpecialtyGrid.tsx`)
- **Назначение:** Сетка специализаций с поиском и группировкой по 5 категориям

#### TriageResult (`components/consult/TriageResult.tsx`)
- **Назначение:** Результат маршрутизации с рекомендуемыми специалистами и red flags

#### ConsultationLoading (`components/consult/ConsultationLoading.tsx`)
- **Назначение:** Индикатор загрузки консультации

#### ConsultationResultCard (`components/consult/ConsultationResultCard.tsx`)
- **Назначение:** Карточка результата консультации

#### ConsultationCard (`components/consultations/ConsultationCard.tsx`)
- **Назначение:** Карточка в списке консультаций

---

### 5.7. Диагностические компоненты

#### LabAnalysisTab (`components/diagnostics/LabAnalysisTab.tsx`)
- **Назначение:** Таб расшифровки анализов AI

#### VitalsAssessTab (`components/diagnostics/VitalsAssessTab.tsx`)
- **Назначение:** Таб оценки витальных показателей

#### GfrCalculatorTab (`components/diagnostics/GfrCalculatorTab.tsx`)
- **Назначение:** Калькулятор скорости клубочковой фильтрации

#### CvRiskTab (`components/diagnostics/CvRiskTab.tsx`)
- **Назначение:** Калькулятор кардиоваскулярного риска

---

### 5.8. Графики

#### BloodPressureChart (`components/charts/BloodPressureChart.tsx`)
- **Назначение:** График тренда артериального давления

#### LabTrendChart (`components/charts/LabTrendChart.tsx`)
- **Назначение:** График тренда лабораторных показателей

---

### 5.9. Лекарственные компоненты

#### DrugSearchSection (`components/drugs/DrugSearchSection.tsx`)
- **Назначение:** Секция поиска лекарств

#### InteractionSection (`components/drugs/InteractionSection.tsx`)
- **Назначение:** Секция проверки взаимодействий

---

### 5.10. Документы

#### DocumentViewer (`components/documents/DocumentViewer.tsx`)
- **Назначение:** Просмотрщик документов

#### MyDocumentsTab, PrescriptionTab, ReferralTab
- **Назначение:** Табы документов (мои документы, рецепты, направления)

---

### 5.11. Контексты

#### AuthContext (`contexts/AuthContext.tsx`)
- **Назначение:** Аутентификация и авторизация
- **Предоставляет:** `isAuthenticated`, `isLoading`, `patientId`, `username`, `login()`, `register()`, `logout()`

#### ToastContext (`contexts/ToastContext.tsx`)
- **Назначение:** Уведомления (toast notifications)
- **Предоставляет:** `success(message)`, `error(message)`, `info(message)`
- **Поведение:** Максимум 5 одновременно, автоскрытие через 4 секунды
- **Стиль:** success = emerald, error = red, info = blue

---

## 6. Иконографика

### Библиотека

**Lucide React** — основная библиотека иконок.

### Размеры иконок

| Контекст | Размер | Пример |
|----------|--------|--------|
| Навигация sidebar | 18px | `<LayoutDashboard size={18} />` |
| Кнопки с текстом | 16px | `<Settings size={16} />` |
| Внутри Badge/Tag | 14px | `<AlertTriangle size={14} />` |
| Иконки в баннерах | 20px | `<Phone size={20} />` |
| Логотип в sidebar | 24px (w-6 h-6) | `<Heart className="w-6 h-6" />` |
| HelpTooltip | 14px | `<HelpCircle size={14} />` |

### Используемые иконки

| Иконка | Компонент | Контекст |
|--------|-----------|----------|
| `Heart` | Sidebar | Логотип Aibolit |
| `LayoutDashboard` | Sidebar | Панель |
| `Clock` | Sidebar | Хронология |
| `FlaskConical` | Sidebar | Анализы |
| `HeartPulse` | Sidebar | Витальные |
| `MessageCircle` | Sidebar | Чат с врачом |
| `MessageSquare` | Sidebar | AI Консультация |
| `Activity` | Sidebar | Диагностика |
| `Pill` | Sidebar | Лекарства |
| `FileText` | Sidebar | Документы |
| `Settings` | Sidebar | Настройки |
| `LogOut` | Sidebar | Выход |
| `Menu` | Layout | Hamburger (mobile) |
| `X` | Modal, Sidebar | Закрытие |
| `AlertTriangle` | MedicalDisclaimer, InfoBanner | Предупреждение |
| `Phone` | EmergencyBanner | Экстренный вызов |
| `AlertCircle` | ApiError | Ошибка |
| `Search` | SpecialtyGrid | Поиск |
| `Stethoscope` | TriageResult | Специалист |
| `ArrowRight` | TriageResult | Переход |
| `ChevronRight` | Breadcrumbs | Разделитель |
| `ChevronDown/Up` | InfoBanner | Раскрытие/сворачивание |
| `Eye/EyeOff` | LoginPage | Показать/скрыть пароль |
| `Loader2` | LoginPage | Загрузка |
| `HelpCircle` | HelpTooltip | Справка |
| `Info` | InfoBanner, Toast | Информация |
| `CheckCircle2` | Toast | Успех |
| `XCircle` | Toast | Ошибка |
| `Lightbulb` | InfoBanner | Совет |
| `User` | Sidebar | Пользователь |

---

## 7. Responsive Breakpoints (Mobile-first)

### Tailwind breakpoints

| Брейкпоинт | Минимальная ширина | Контекст |
|------------|-------------------|----------|
| По умолчанию (mobile) | 0px | Телефоны (портрет) |
| `sm` | 640px | Телефоны (ландшафт), маленькие планшеты |
| `md` | 768px | Планшеты (портрет) |
| `lg` | 1024px | Планшеты (ландшафт), ноутбуки |
| `xl` | 1280px | Десктоп |
| `2xl` | 1536px | Большие мониторы |

### Адаптивное поведение по компонентам

| Компонент | Mobile (<768px) | Desktop (>=768px) |
|-----------|----------------|-------------------|
| Sidebar | Скрыт, открывается через hamburger + overlay | Всегда видим, 256px |
| Контент padding | `px-4 py-4` | `px-6 py-6` |
| Modal | Sheet снизу (`rounded-t-2xl`, полная ширина) | Центр экрана (`rounded-2xl`, max-width 32rem) |
| SpecialtyGrid | 1 колонка | 2 колонки (sm) / 3 колонки (lg) |
| Dashboard виджеты | 1 колонка | 2 колонки (md) |
| Mobile header | Sticky header с hamburger | Скрыт |
| Toast | Полная ширина внизу | max-width 24rem, справа внизу |

### PWA-рекомендации

- Touch targets минимум 44x44px (рекомендация Apple HIG)
- Padding кнопок: минимум `py-2 px-4` (32px высоты)
- Безопасная зона для bottom navigation (если будет добавлена)
- `scroll-smooth` для плавной прокрутки
- `overflow-hidden` на body при открытом modal

---

## 8. Accessibility (a11y) — WCAG 2.1 AA

### Реализованные практики

| Требование | Реализация | Компонент |
|------------|------------|-----------|
| Skip to content | `<a href="#main-content" class="sr-only focus:not-sr-only">` | Layout |
| Landmarks | `<nav aria-label>`, `<main role="main">`, `<aside>` | Layout, Sidebar, Breadcrumbs |
| ARIA labels | `aria-label="Основная навигация"`, `aria-label="Открыть меню"` | Sidebar, Layout |
| Modal accessibility | `role="dialog"`, `aria-modal="true"`, `aria-label={title}` | Modal |
| Alert role | `role="alert"` | EmergencyBanner, ErrorBoundary, ApiError |
| Live region | `role="status" aria-live="polite"` | ToastContext |
| Focus management | Escape для закрытия modal | Modal |
| Breadcrumbs | `<nav aria-label="Навигационная цепочка">` | Breadcrumbs |

### Требования к контрастности

| Пара | Ratio | Статус |
|------|-------|--------|
| `text-gray-800` на `bg-white` | ~15:1 | Пройден AA/AAA |
| `text-gray-500` на `bg-white` | ~7:1 | Пройден AA |
| `text-medical-teal` на `bg-white` | ~4.5:1 | Пройден AA |
| `text-white` на `bg-medical-navy` | ~10:1 | Пройден AA/AAA |
| `text-red-700` на `bg-red-50` | ~8:1 | Пройден AA |
| `text-amber-700` на `bg-amber-50` | ~6:1 | Пройден AA |

### Фокусные состояния

```css
Стандартный фокус для input:
  focus:outline-none focus:ring-2 focus:ring-medical-teal/30 focus:border-medical-teal

Кнопки навигации:
  hover:bg-white/10 hover:text-white (sidebar)
  hover:bg-gray-100 transition-colors (content area)
```

### Семантическая разметка

- Все формы: `<label>` привязаны к `<input>` (через `htmlFor` или вложенность)
- Навигация: `<nav>` с `aria-label`
- Таблицы: `<table>`, `<thead>`, `<tbody>`, `<th scope>`
- Заголовки: иерархия h1 -> h2 -> h3 (без пропусков)
- Интерактивные элементы: все имеют состояния hover, focus, disabled

---

## 9. Медицинские UI-паттерны

### 9.1. Дисклеймер (MedicalDisclaimer)

Обязательный компонент на каждом экране с AI-ответом.

```
+----------------------------------------------+
| [AlertTriangle] Информация предоставлена     |
|  AI-ассистентом и носит исключительно        |
|  информационный характер...                   |
+----------------------------------------------+
  bg-amber-50, border-amber-200, rounded-xl
  Иконка: amber-500
  Текст: text-xs text-amber-700
```

Типы: `general`, `lab_analysis`, `diagnosis`, `medication`

### 9.2. Emergency Banner (EmergencyBanner)

Показывается при обнаружении red flags.

```
+----------------------------------------------+
| [Phone] ВНИМАНИЕ! Обнаружены критические     |
|  показатели, требующие экстренной            |
|  медицинской помощи!                          |
|                                              |
|  [103]  [112]  Немедленно вызовите скорую!   |
+----------------------------------------------+
  bg-red-50, border-2 border-red-300, rounded-xl
  role="alert"
  Кнопки: bg-red-600, hover:bg-red-700
  Ссылки: tel:103, tel:112
```

### 9.3. Severity Badges (statusBadge)

Визуальная кодировка степени тяжести.

| Состояние | Badge variant | Цвет | Пример |
|-----------|---------------|------|--------|
| Норма / Normal | `success` | emerald-100/700 | "Норма", "Результат в пределах нормы" |
| Предупреждение | `warning` | amber-100/700 | "Повышено", "Требует внимания" |
| Критическое | `danger` | red-100/700 | "Критическое", "Выше нормы значительно" |
| Информация | `info` | cyan-100/700 | "В процессе", "Ожидает" |
| Нейтральное | `gray` | gray-100/600 | "Не определено" |

### 9.4. Уровни уверенности AI

Визуальное отображение confidence level:

| Уровень | Значение | Цвет текста | Отображение |
|---------|----------|-------------|-------------|
| Высокая | >80% | `text-emerald-600` | "Высокая вероятность" + процент |
| Умеренная | 50-80% | `text-amber-600` | "Умеренная вероятность" + процент |
| Низкая | 20-50% | `text-gray-500` | "Возможная причина" |
| Очень низкая | <20% | `text-gray-400` | "Маловероятно" |

Используется в TriageResult для отображения релевантности специалистов.

### 9.5. Red Flags индикация

Компоненты для отображения тревожных симптомов:

```
Внутри TriageResult (amber — предупреждение):
+----------------------------------------------+
| [AlertTriangle] Обратите внимание            |
|   Описание red flag 1                        |
|   Описание red flag 2                        |
+----------------------------------------------+
  bg-amber-50, border-amber-200, rounded-xl

При emergency (red — экстренный):
  -> EmergencyBanner (см. выше)
```

---

## 10. Анимации и переходы

### Используемые библиотеки

- **Framer Motion** — анимации компонентов (Card, Modal, Toast)
- **Tailwind `transition-*`** — CSS-переходы (hover, focus)
- **Tailwind `animate-*`** — CSS-анимации (pulse, spin)

### Стандартные значения

| Анимация | Настройки | Использование |
|----------|-----------|---------------|
| Card появление | `opacity: 0->1, y: 10->0, duration: 0.3s` | Все Card компоненты |
| Modal появление | `spring, damping: 25, stiffness: 300` | Modal |
| Modal overlay | `opacity: 0->1` | Modal backdrop |
| Toast slide-in | `opacity: 0->1, x: 80->0, scale: 0.95->1` | Toast notifications |
| Skeleton pulse | `animate-pulse` (CSS) | Skeleton loaders |
| Spinner | `animate-spin` (CSS) | LoadingSpinner |
| Hover transitions | `transition-colors`, `transition-all duration-200` | Кнопки, навигация |
| Shadow on hover | `hover:shadow-md` | Карточки специалистов |

---

*Документ создан: UI Agent | Дата: 2025-02-24*
