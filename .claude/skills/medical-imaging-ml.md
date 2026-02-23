# Skill: Medical Imaging ML

> AI-анализ медицинских изображений: рентген, дерматоскопия, переломы

## Назначение

Реализация ML-моделей для предварительного скрининга медицинских изображений в Aibolit AI. Все результаты — **только предварительный скрининг**, требующий подтверждения врачом.

---

## Использование

| Агент | Применение |
|-------|-----------|
| AI-Agents | Проектирование imaging pipeline |
| Coder | Реализация ML моделей и inference |
| Medical-Domain | Верификация клинической корректности |
| QA | Тестирование accuracy и safety |

---

## Критическое правило

```yaml
ОБЯЗАТЕЛЬНЫЙ ДИСКЛЕЙМЕР для КАЖДОГО результата анализа изображения:

"⚠️ Анализ изображения выполнен AI-моделью и является предварительным скринингом.
Это НЕ радиологическое заключение. Окончательную интерпретацию должен выполнить
врач-рентгенолог / дерматолог / травматолог."

AI imaging — это СКРИНИНГОВЫЙ ИНСТРУМЕНТ, а не диагностический.
```

---

## Модели

### 1. Chest X-Ray Analysis (TorchXRayVision)

```yaml
Модель: TorchXRayVision (открытый исходный код)
Репозиторий: https://github.com/mlmed/torchxrayvision
Лицензия: Apache 2.0

Возможности (14 патологий):
  - Atelectasis (ателектаз)
  - Cardiomegaly (кардиомегалия)
  - Consolidation (консолидация)
  - Edema (отёк)
  - Effusion (выпот)
  - Emphysema (эмфизема)
  - Fibrosis (фиброз)
  - Hernia (грыжа)
  - Infiltration (инфильтрация)
  - Mass (образование)
  - Nodule (узел)
  - Pleural Thickening (утолщение плевры)
  - Pneumonia (пневмония)
  - Pneumothorax (пневмоторакс)

Input:
  format: DICOM, PNG, JPEG
  preprocessing:
    - Resize to 224x224
    - Normalize to [0,1]
    - Convert to grayscale
    - Center crop (если не квадратное)

Output:
  - Для каждой патологии: probability (0.0-1.0)
  - Threshold для "подозрение": 0.5
  - Threshold для "высокая вероятность": 0.7

Performance:
  AUC: 0.75-0.85 (зависит от патологии)
  Ограничения: Не заменяет рентгенолога
```

### 2. Skin Lesion Classification

```yaml
Модель: Custom CNN (EfficientNet-B3 backbone, fine-tuned)
Датасет: ISIC Archive + HAM10000

Классы (7 типов):
  - Melanocytic nevi (меланоцитарный невус) — доброкачественный
  - Melanoma (меланома) — злокачественный, RED FLAG
  - Basal cell carcinoma (базальноклеточный рак) — злокачественный
  - Actinic keratoses (актинический кератоз) — предраковый
  - Benign keratosis (доброкачественный кератоз)
  - Dermatofibroma (дерматофиброма)
  - Vascular lesions (сосудистые поражения)

Input:
  format: JPEG, PNG
  preprocessing:
    - Resize to 300x300
    - Normalize (ImageNet stats)
    - Data augmentation (inference TTA x5)

Output:
  - Top-3 предположения с confidence
  - Если melanoma confidence > 0.3 → RED FLAG → эскалация

Red Flag Logic:
  IF melanoma_confidence > 0.3 OR basal_cell_confidence > 0.5:
    escalation_urgency = 4
    message = "Обнаружены признаки, требующие срочной консультации дерматолога/онколога"
```

### 3. Fracture Detection (опционально)

```yaml
Модель: YOLO v8 (fine-tuned на MURA + FracAtlas)
Статус: Планируется для v2.0

Возможности:
  - Детекция переломов на рентгенограммах конечностей
  - Bounding box + confidence
  - Тип: простой/оскольчатый/со смещением

Ограничения:
  - Только конечности (не позвоночник, не череп)
  - Скрининг, не диагностика
```

---

## Pipeline обработки изображений

### Workflow

```yaml
1. Upload & Validation:
   - Проверка формата (DICOM/JPEG/PNG)
   - Проверка размера (<20MB)
   - Проверка EXIF/DICOM metadata
   - Удаление персональных данных из DICOM header
   - Логирование: ai_imaging_upload

2. Preprocessing:
   - Конвертация в стандартный формат
   - Нормализация яркости/контраста
   - Resize до размера модели
   - Quality check (слишком тёмное/светлое → предупреждение)

3. Inference:
   - Выбор модели по типу изображения
   - Inference с TTA (test-time augmentation)
   - Получение probabilities

4. Post-processing:
   - Применение thresholds
   - Red flag check
   - Формирование human-readable результата
   - Генерация дисклеймера (imaging тип)

5. Response:
   - Текстовое описание находок
   - Confidence level для каждой
   - Рекомендация (к какому врачу обратиться)
   - Дисклеймер
   - Логирование: ai_imaging_analysis_completed

6. Storage:
   - Изображение: зашифрованное хранилище (AES-256)
   - Результат: в consultation record
   - Retention: 5 лет
   - Удаление по запросу пациента (с аудит-логом)
```

---

## DICOM обработка

```yaml
Извлечение метаданных:
  полезные:
    - Modality (модальность)
    - Body Part Examined
    - Study Date
    - View Position (PA/AP/Lateral)
    - Image Dimensions

  удаляемые (деперсонализация):
    - Patient Name
    - Patient ID
    - Date of Birth
    - Institution Name
    - Referring Physician
    - Все приватные теги

Библиотека: pydicom
Деперсонализация: Обязательна ДО любой обработки
```

---

## Ограничения и честность

```yaml
AI imaging НЕ может:
  - Заменить физикальный осмотр
  - Учесть клинический контекст целиком
  - Гарантировать обнаружение всех патологий
  - Работать с низкокачественными изображениями
  - Анализировать видео (только статические изображения)
  - Работать с МРТ и КТ (только рентген и фото)

AI imaging МОЖЕТ:
  - Предварительный скрининг на распространённые патологии
  - Сортировка по срочности (triage)
  - Привлечение внимания к подозрительным областям
  - Информирование пациента о возможных находках
```

---

## Метрики качества

```yaml
Обязательный мониторинг:
  - AUC-ROC для каждого класса
  - Sensitivity (recall) для злокачественных → >90%
  - False negative rate для RED FLAG → <5%
  - False positive rate → <30% (допустимо, лучше перестраховка)
  - Inference time → <5 секунд

A/B тестирование:
  - Сравнение версий моделей
  - Мониторинг drift (изменение распределения данных)
  - Регулярная ревалидация на новых данных
```

---

## Ссылки

- **AI-агенты:** `.claude/agents/ai-agents.md`
- **Clinical Reasoning:** `.claude/skills/clinical-reasoning.md`
- **Правила безопасности:** `.claude/rules/05-medical-safety.md`
- **Логирование:** `.claude/rules/04-logging.md`

---

*Спецификация навыка v1.0 | Aibolit AI — Claude Code Agent System*
