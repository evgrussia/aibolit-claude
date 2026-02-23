# Skill: Image Generator

> Генерация графики и изображений

## Назначение

Создание визуальных материалов: иконки, hero images, UI assets, social media графика.

---

## Типы изображений

### 1. Иконки

```yaml
Форматы:
  - SVG (предпочтительно)
  - PNG (16x16, 24x24, 32x32, 48x48, 64x64)
  - ICO (для favicon)

Стили:
  - Line icons
  - Filled icons
  - Duotone icons

Спецификации:
  - Stroke width: 1.5-2px
  - Corner radius: consistent
  - Padding: 10-15%
```

### 2. Hero Images

```yaml
Размеры:
  - Desktop: 1920x1080, 1440x900
  - Mobile: 750x1334, 1080x1920
  - OG Image: 1200x630

Форматы:
  - JPG (фото)
  - PNG (графика с прозрачностью)
  - WebP (оптимизированный)
```

### 3. UI Assets

```yaml
Типы:
  - Backgrounds
  - Illustrations
  - Patterns
  - Gradients
  - Shadows

Форматы:
  - SVG для vectors
  - PNG для complex graphics
  - CSS для patterns/gradients
```

### 4. Social Media Graphics

```yaml
Размеры:
  Twitter/X:
    - Post: 1200x675
    - Header: 1500x500
    - Profile: 400x400

  LinkedIn:
    - Post: 1200x627
    - Cover: 1584x396

  Telegram:
    - Post: 1280x720

  Instagram:
    - Post: 1080x1080
    - Story: 1080x1920
```

### 5. App Assets

```yaml
Favicon:
  - favicon.ico (48x48 multi-size)
  - favicon-16x16.png
  - favicon-32x32.png
  - apple-touch-icon.png (180x180)

PWA Icons:
  - icon-192x192.png
  - icon-512x512.png

OG Images:
  - og-image.png (1200x630)
  - twitter-card.png (1200x600)
```

---

## Описание для генерации

### Формат запроса

```yaml
image_request:
  type: "icon|hero|ui_asset|social|app_asset"

  description: |
    [Детальное описание желаемого изображения]

  style:
    - "[Стиль 1: minimalist, flat, 3d, etc.]"
    - "[Цветовая схема]"

  dimensions:
    width: 1200
    height: 630

  format: "svg|png|jpg|webp"

  brand:
    colors:
      primary: "#3B82F6"
      secondary: "#8B5CF6"
    fonts: ["Inter", "JetBrains Mono"]
```

### Примеры промптов

```yaml
Icon:
  "Simple line icon of a document with a checkmark.
   Style: minimal, single stroke width 2px.
   Colors: #3B82F6 for checkmark, #374151 for document.
   Size: 24x24px, padding 2px."

Hero Image:
  "Abstract gradient background with floating geometric shapes.
   Colors: deep blue (#1E40AF) to purple (#7C3AED) gradient.
   Shapes: subtle circles and rectangles with glassmorphism effect.
   Size: 1920x1080px."

Social Media:
  "Product announcement graphic for Telegram.
   Show app screenshot on left, key features on right.
   Title: 'Новая версия 2.0'
   Brand colors: blue primary, white background.
   Size: 1280x720px."
```

---

## Инструменты

### Встроенные

```yaml
SVG Generation:
  - Описание → SVG код
  - Простые иконки и shapes

ASCII/Text Art:
  - Диаграммы в текстовом формате
  - Wireframes
```

### Внешние (рекомендуемые)

```yaml
AI Generation:
  - Midjourney
  - DALL-E 3
  - Stable Diffusion

Design Tools:
  - Figma (UI design)
  - Canva (social media)

Icon Libraries:
  - Heroicons
  - Lucide
  - Phosphor Icons
```

---

## Оптимизация

### Форматы по назначению

```yaml
SVG:
  - Иконки
  - Логотипы
  - Простые иллюстрации
  - Масштабируемая графика

PNG:
  - Сложные иллюстрации
  - Скриншоты
  - Графика с прозрачностью

JPG:
  - Фотографии
  - Hero images без прозрачности
  - Backgrounds

WebP:
  - Web-оптимизированные версии
  - Fallback для старых браузеров
```

### Размеры файлов

```yaml
Targets:
  - Icons: < 5KB
  - Hero images: < 200KB
  - Social graphics: < 150KB
  - App icons: < 50KB

Оптимизация:
  - SVG: SVGO
  - PNG: PNGQuant, TinyPNG
  - JPG: MozJPEG
  - WebP: Native compression
```

---

## Формат вывода

```yaml
image_generated:
  type: "[тип]"
  description: "[описание]"

  files:
    - path: "assets/images/hero.png"
      dimensions: "1920x1080"
      size: "150KB"
      format: "png"

  optimization:
    original_size: "500KB"
    optimized_size: "150KB"
    reduction: "70%"

  usage:
    recommended_for: ["landing page hero section"]
    alt_text: "[alt text для accessibility]"

  signature: "[Agent] Agent"
```

---

## Использование

| Агент | Изображения |
|-------|-------------|
| UI | Design system assets, UI kit graphics |
| Marketing | Social media, promotional graphics |
| Product | Product screenshots, mockups |
| Content | Blog illustrations |

---

*Навык v1.0 | Claude Code Agent System*
