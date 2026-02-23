# Skill: Web Research

> Исследования в интернете: рынок, конкуренты, технологии

## Назначение

Проведение веб-исследований для сбора информации о рынке, конкурентах, трендах и технологиях.

---

## Типы исследований

### 1. Market Research

```yaml
Цель: Понять рынок и его динамику

Исследовать:
  - Размер рынка (TAM/SAM/SOM)
  - Динамика роста
  - Ключевые игроки
  - Сегменты рынка
  - Барьеры входа
  - Регуляторные факторы

Источники:
  - Statista, IBISWorld
  - Industry reports
  - News articles
  - Company reports
```

### 2. Competitive Analysis

```yaml
Цель: Понять конкурентов

Исследовать:
  - Прямые конкуренты
  - Косвенные конкуренты
  - Features comparison
  - Pricing models
  - Strengths/Weaknesses
  - Market positioning

Источники:
  - Competitor websites
  - Product Hunt
  - G2, Capterra reviews
  - Social media
  - App stores
```

### 3. Technology Research

```yaml
Цель: Выбрать технологии

Исследовать:
  - Frameworks comparison
  - Best practices
  - Performance benchmarks
  - Community size
  - Learning curve
  - Ecosystem

Источники:
  - GitHub (stars, issues, activity)
  - Stack Overflow trends
  - npm/PyPI downloads
  - Documentation
  - Tech blogs
```

### 4. User Research

```yaml
Цель: Понять пользователей

Исследовать:
  - Pain points
  - Current solutions
  - Feature requests
  - Feedback patterns
  - User behavior

Источники:
  - Reddit, forums
  - Social media discussions
  - Review sites
  - Support tickets (if available)
```

### 5. Trend Analysis

```yaml
Цель: Выявить тренды

Исследовать:
  - Emerging technologies
  - Behavior changes
  - Market shifts
  - Regulatory changes

Источники:
  - Google Trends
  - Tech news (TechCrunch, Hacker News)
  - Industry publications
  - Research papers
```

---

## Процесс исследования

### Step 1: Define Scope

```yaml
Определить:
  - Цель исследования
  - Ключевые вопросы
  - Глубина исследования
  - Временные рамки
```

### Step 2: Gather Data

```yaml
Действия:
  - Поиск по ключевым запросам
  - Анализ top-10 результатов
  - Сбор количественных данных
  - Сбор качественных insights
  - Документирование источников
```

### Step 3: Analyze

```yaml
Действия:
  - Структурировать данные
  - Выявить patterns
  - Сделать выводы
  - Идентифицировать gaps
```

### Step 4: Report

```yaml
Действия:
  - Создать summary
  - Добавить визуализации
  - Дать рекомендации
  - Указать источники
```

---

## Шаблон Competitive Analysis

```yaml
competitor_analysis:
  competitor: "[Название]"
  url: "[URL]"
  type: "direct|indirect"

  overview:
    description: "[Что делают]"
    founded: "YYYY"
    funding: "$XM"
    team_size: "~X people"

  product:
    target_audience: "[Для кого]"
    core_features:
      - "[Feature 1]"
      - "[Feature 2]"
    unique_value: "[УТП]"

  pricing:
    model: "freemium|subscription|one-time"
    tiers:
      - name: "Free"
        price: "$0"
        features: ["..."]
      - name: "Pro"
        price: "$X/mo"
        features: ["..."]

  strengths:
    - "[Сила 1]"
    - "[Сила 2]"

  weaknesses:
    - "[Слабость 1]"
    - "[Слабость 2]"

  market_position:
    positioning: "[Как позиционируют себя]"
    reviews_score: "4.5/5"
    user_sentiment: "positive|mixed|negative"

  source_urls:
    - "[URL 1]"
    - "[URL 2]"
```

---

## Формат вывода

```yaml
research_result:
  type: "market|competitive|technology|user|trend"
  topic: "[Тема исследования]"
  date: "YYYY-MM-DD"

  summary: |
    [Краткое резюме findings]

  key_findings:
    - finding: "[Finding 1]"
      confidence: "high|medium|low"
      source: "[URL]"
    - finding: "[Finding 2]"
      confidence: "high|medium|low"
      source: "[URL]"

  data:
    quantitative:
      - metric: "[Метрика]"
        value: "[Значение]"
        source: "[Источник]"
    qualitative:
      - insight: "[Insight]"
        evidence: "[Доказательство]"

  gaps_identified:
    - "[Gap 1]"
    - "[Gap 2]"

  recommendations:
    - "[Рекомендация 1]"
    - "[Рекомендация 2]"

  sources:
    - url: "[URL]"
      type: "primary|secondary"
      reliability: "high|medium|low"

  limitations:
    - "[Ограничение исследования]"

  signature: "Research Agent"
```

---

## Best Practices

```yaml
Source Evaluation:
  - Проверяй дату публикации
  - Оценивай авторитетность источника
  - Cross-reference несколько источников
  - Отмечай bias источника

Data Quality:
  - Отличай факты от мнений
  - Указывай confidence level
  - Документируй methodology
  - Признавай limitations

Documentation:
  - Сохраняй все URL
  - Делай скриншоты важного
  - Timestamp все findings
  - Структурируй данные
```

---

## Использование

| Агент | Исследования |
|-------|--------------|
| Research | Все типы |
| Product | Market, User research |
| Marketing | Competitive, Trend |
| Architect | Technology research |
| Analytics | Market benchmarks |

---

*Навык v1.0 | Claude Code Agent System*
