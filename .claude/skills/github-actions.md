# Skill: GitHub Actions

> CI/CD с GitHub Actions

## Назначение

Настройка и управление CI/CD пайплайнами с использованием GitHub Actions.

---

## Компоненты

### Workflow Structure

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

env:
  NODE_VERSION: "20"
  PYTHON_VERSION: "3.12"

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Step name
        run: command
```

### Triggers

```yaml
# Push to branches
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - '!**.md'

# Pull requests
on:
  pull_request:
    types: [opened, synchronize, reopened]

# Schedule (cron)
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

# Manual
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

### Jobs

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
```

---

## Common Patterns

### Python Project

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### Node.js Project

```yaml
name: Node.js CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test -- --coverage

      - name: Build
        run: npm run build
```

### Docker Build & Push

```yaml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### SSH Deploy

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/app
            git pull origin main
            docker compose pull
            docker compose up -d --build
```

---

## Secrets Management

```yaml
# Repository secrets
${{ secrets.SECRET_NAME }}

# Environment secrets
environment:
  name: production
  url: https://example.com

# OIDC for cloud providers (no secrets needed)
permissions:
  id-token: write
  contents: read
```

---

## Caching

```yaml
# NPM cache
- uses: actions/setup-node@v4
  with:
    cache: 'npm'

# Pip cache
- uses: actions/setup-python@v5
  with:
    cache: 'pip'

# Custom cache
- uses: actions/cache@v4
  with:
    path: ~/.cache/custom
    key: ${{ runner.os }}-custom-${{ hashFiles('**/lockfile') }}
    restore-keys: |
      ${{ runner.os }}-custom-
```

---

## Artifacts

```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/

# Download
- uses: actions/download-artifact@v4
  with:
    name: build-output
```

---

## Matrix Strategy

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [18, 20]
        exclude:
          - os: windows-latest
            node: 18
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

---

## Conditional Execution

```yaml
# If condition
- name: Deploy
  if: github.ref == 'refs/heads/main'

# Success/failure
- name: Notify on failure
  if: failure()

# Always run
- name: Cleanup
  if: always()

# Environment check
- name: Production deploy
  if: github.event.inputs.environment == 'production'
```

---

## Формат вывода

```yaml
github_actions_config:
  workflows:
    - name: "CI"
      file: ".github/workflows/ci.yml"
      triggers: ["push", "pull_request"]
      jobs: ["lint", "test", "build"]

    - name: "Deploy"
      file: ".github/workflows/deploy.yml"
      triggers: ["push to main"]
      jobs: ["deploy"]

  secrets_required:
    - name: "SSH_PRIVATE_KEY"
      description: "SSH key for deployment"
    - name: "SSH_HOST"
      description: "Server hostname"

  environments:
    - name: "production"
      url: "https://app.example.com"
      protection_rules: true

  signature: "DevOps Agent"
```

---

## Best Practices

```yaml
Security:
  - Минимальные permissions
  - Pin actions to SHA
  - Audit secrets regularly
  - Use environments for protection

Performance:
  - Cache dependencies
  - Use matrix for parallel jobs
  - Fail fast when possible
  - Optimize Docker builds

Maintainability:
  - Reusable workflows
  - Composite actions
  - Clear job names
  - Good documentation
```

---

*Навык v1.0 | Claude Code Agent System*
