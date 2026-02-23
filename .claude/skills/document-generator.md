# Skill: Document Generator

> Генерация документации разных типов

## Назначение

Создание структурированной документации: README, API docs, user guides, technical docs.

---

## Типы документов

### 1. README

```yaml
Структура:
  - Project name & badges
  - Description
  - Features
  - Quick Start
  - Installation
  - Usage
  - Configuration
  - API Reference (brief)
  - Contributing
  - License

Выход: README.md
```

### 2. API Documentation

```yaml
Структура:
  - Overview
  - Authentication
  - Base URL
  - Endpoints (по ресурсам)
    - Method, URL, Description
    - Parameters
    - Request body
    - Response
    - Examples
  - Error codes

Формат: OpenAPI 3.0 или Markdown

Выход: /docs/api/
```

### 3. User Guide

```yaml
Структура:
  - Introduction
  - Getting Started
  - Features walkthrough
  - FAQ
  - Troubleshooting
  - Support

Выход: /docs/user-guide/
```

### 4. Technical Documentation

```yaml
Структура:
  - Architecture overview
  - System components
  - Data flow
  - Integration points
  - Deployment
  - Maintenance

Выход: /docs/technical/
```

### 5. Changelog

```yaml
Формат: Keep a Changelog

Структура:
  ## [Version] - YYYY-MM-DD
  ### Added
  - New feature

  ### Changed
  - Updated behavior

  ### Fixed
  - Bug fix

  ### Removed
  - Deprecated feature

Выход: CHANGELOG.md
```

---

## Шаблоны

### README.md

```markdown
# Project Name

[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)]()

Short description of the project.

## Features

- ✅ Feature 1
- ✅ Feature 2
- ✅ Feature 3

## Quick Start

\`\`\`bash
# Clone
git clone https://github.com/user/repo.git

# Install
cd repo
pip install -r requirements.txt

# Run
python main.py
\`\`\`

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 16+

### Steps
1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Configure environment variables
5. Run migrations
6. Start the server

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `false` |
| `DATABASE_URL` | Database connection | - |

## Usage

[Usage examples]

## API

See [API Documentation](/docs/api/)

## Contributing

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

MIT License
```

### API Endpoint

```markdown
## Create Article

Create a new article.

**Endpoint:** `POST /api/articles/`

**Authentication:** Required

### Request

**Headers:**
| Header | Value |
|--------|-------|
| Authorization | Bearer {token} |
| Content-Type | application/json |

**Body:**
\`\`\`json
{
  "title": "string (required, max 200)",
  "content": "string (required)",
  "status": "draft|published (default: draft)"
}
\`\`\`

### Response

**201 Created:**
\`\`\`json
{
  "id": "uuid",
  "title": "string",
  "slug": "string",
  "content": "string",
  "status": "string",
  "author_id": "uuid",
  "created_at": "datetime"
}
\`\`\`

**400 Bad Request:**
\`\`\`json
{
  "title": ["This field is required."]
}
\`\`\`

**401 Unauthorized:**
\`\`\`json
{
  "detail": "Authentication credentials were not provided."
}
\`\`\`

### Example

\`\`\`bash
curl -X POST https://api.example.com/api/articles/ \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -d '{"title": "My Article", "content": "Article content"}'
\`\`\`
```

---

## Принципы

```yaml
Clarity:
  - Простой язык
  - Короткие предложения
  - Избегай жаргона

Structure:
  - Логичная иерархия
  - Консистентное форматирование
  - Навигация (TOC)

Examples:
  - Code examples для каждого endpoint
  - Copy-paste ready
  - Working examples

Maintenance:
  - Версионирование
  - Last updated date
  - Change history
```

---

## Формат вывода

```yaml
document_generated:
  type: "readme|api|user_guide|technical|changelog"
  path: "[путь к файлу]"
  format: "markdown|openapi|html"

  content:
    sections: 10
    words: 1500
    code_examples: 5

  quality:
    spell_check: "passed"
    links_valid: "passed"
    examples_tested: "passed"

  signature: "[Agent] Agent"
```

---

## Использование

| Агент | Документы |
|-------|-----------|
| Product | PRD, Vision, User Stories |
| Architect | Architecture docs, ADRs |
| Dev | Technical specs, README |
| DevOps | Deployment docs, Runbooks |
| Marketing | User guides, Help articles |
| All | Changelogs |

---

*Навык v1.0 | Claude Code Agent System*
