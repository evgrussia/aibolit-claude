# Реестр навыков (Skills)

> Все переиспользуемые навыки системы Claude Code Agent System — Aibolit AI

## Обзор

Система включает **13 специализированных навыков**, включая 6 медицинских навыков для проекта Aibolit AI.

---

## Основные навыки

| Навык | Файл | Описание |
|-------|------|----------|
| context-manager | [context-manager.md](context-manager.md) | Управление контекстом, summaries, checkpoints |
| verification-engine | [verification-engine.md](verification-engine.md) | Верификация реализации vs спецификации |
| document-generator | [document-generator.md](document-generator.md) | Генерация документации |
| image-generator | [image-generator.md](image-generator.md) | Генерация графики и изображений |
| web-research | [web-research.md](web-research.md) | Веб-исследования |

---

## Навыки разработки

| Навык | Файл | Описание |
|-------|------|----------|
| ssh-deployment | [ssh-deployment.md](ssh-deployment.md) | SSH операции на VPS |
| github-actions | [github-actions.md](github-actions.md) | CI/CD с GitHub Actions |

---

## Медицинские навыки (Aibolit AI)

| Навык | Файл | Описание |
|-------|------|----------|
| clinical-reasoning | [clinical-reasoning.md](clinical-reasoning.md) | Клиническое рассуждение AI: дифференциальная диагностика, evidence grading |
| medical-knowledge-base | [medical-knowledge-base.md](medical-knowledge-base.md) | Медицинские знания: клинические рекомендации, протоколы |
| medical-api-integration | [medical-api-integration.md](medical-api-integration.md) | Интеграция с 9 медицинскими API (PubMed, RxNorm, OpenFDA и др.) |
| medical-imaging-ml | [medical-imaging-ml.md](medical-imaging-ml.md) | AI-анализ медицинских изображений |
| medical-data-compliance | [medical-data-compliance.md](medical-data-compliance.md) | Регуляторное соответствие медданных (152-ФЗ, ФЗ-323) |
| doctor-escalation | [doctor-escalation.md](doctor-escalation.md) | Система эскалации к живым врачам (urgency scoring, handoff) |

**Ключевое правило:** `.claude/rules/05-medical-safety.md`

---

## Неиспользуемые навыки (архив)

Следующие навыки присутствуют в каталоге, но **не используются** в проекте Aibolit AI:

| Навык | Причина |
|-------|---------|
| langchain-development | Aibolit использует MCP + Claude, не LangChain |
| telegram-bot-api | Нет Telegram-интеграции |
| telegram-core-api | Нет Telegram-интеграции |
| ton-blockchain | Нет блокчейн-интеграции |
| yookassa-payments | Нет платёжной системы |

---

## Матрица использования

| Навык | Агенты |
|-------|--------|
| context-manager | Orchestrator, All agents |
| verification-engine | Review, QA |
| document-generator | All agents |
| image-generator | UI, Marketing |
| web-research | Research, Marketing |
| ssh-deployment | Coder, QA, DevOps, SRE |
| github-actions | DevOps |
| clinical-reasoning | AI-Agents, Medical-Domain |
| medical-knowledge-base | AI-Agents, Medical-Domain, Research |
| medical-api-integration | AI-Agents, Medical-Domain, Research, Coder |
| medical-imaging-ml | AI-Agents, Coder |
| medical-data-compliance | Compliance, Security, Architect |
| doctor-escalation | AI-Agents, Medical-Domain, Coder |

---

## Уровни навыков

| Навык | Уровень |
|-------|---------|
| context-manager | Basic |
| verification-engine | Intermediate |
| document-generator | Basic |
| image-generator | Intermediate |
| web-research | Basic |
| ssh-deployment | Advanced (Senior/Lead) |
| github-actions | Intermediate |
| clinical-reasoning | Advanced (Senior/Lead) |
| medical-knowledge-base | Advanced (Senior/Lead) |
| medical-api-integration | Advanced (Senior/Lead) |
| medical-imaging-ml | Advanced (Senior/Lead) |
| medical-data-compliance | Advanced (Senior/Lead) |
| doctor-escalation | Advanced (Senior/Lead) |

---

## Требования к credentials

| Навык | Credentials | Источник |
|-------|-------------|----------|
| ssh-deployment | SSH ключи | Локально или через env |
| github-actions | GitHub Token | GitHub repo secrets |
| medical-api-integration (PubMed) | NCBI API Key (optional) | ncbi.nlm.nih.gov/account |
| medical-api-integration (OpenFDA) | API Key (optional) | open.fda.gov |

---

*Реестр навыков v1.2 | Aibolit AI — Claude Code Agent System*
