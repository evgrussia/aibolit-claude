# Skill: LangChain Development

> Разработка AI-агентов на LangChain/LangGraph для медицинской мультиагентной системы Aibolit AI

## Назначение

Проектирование и реализация AI-агентов с использованием LangChain и LangGraph. Специализация — медицинская мультиагентная система (22 AI-доктора + агент-триажист) с обязательными safety guardrails.

**Ключевое правило:** `.claude/rules/05-medical-safety.md`

## Уровень

**Senior / Lead** — продвинутый навык

---

## Компоненты

### LangChain Core

```yaml
Models:
  - ChatOpenAI, ChatAnthropic
  - Ollama (local)
  - Model configuration (temperature, max_tokens)

Prompts:
  - PromptTemplate
  - ChatPromptTemplate
  - Few-shot examples
  - System messages

Chains:
  - LLMChain
  - Sequential chains
  - Router chains

Memory:
  - ConversationBufferMemory
  - ConversationSummaryMemory
  - VectorStoreRetrieverMemory
```

### LangGraph

```yaml
Concepts:
  - StateGraph
  - Nodes (functions)
  - Edges (transitions)
  - Conditional edges
  - Checkpointing

Patterns:
  - ReAct agent
  - Plan-and-Execute
  - Multi-agent systems
  - Human-in-the-loop
  - Supervisor pattern (медицинская оркестрация)
  - Medical safety guardrails pattern
```

### RAG (Retrieval-Augmented Generation)

```yaml
Components:
  - Document loaders
  - Text splitters
  - Embeddings
  - Vector stores
  - Retrievers
  - Rerankers
```

### Tools

```yaml
Built-in:
  - Web search
  - Calculator
  - Python REPL
  - File operations

Custom:
  - @tool decorator
  - StructuredTool
  - Tool schemas
```

---

## Архитектура агента

### Шаблон State

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    tool_results: dict
    iteration: int
```

### Шаблон Node

```python
from langchain_core.messages import HumanMessage, AIMessage

def process_node(state: AgentState) -> AgentState:
    """Process current state and return updated state."""

    messages = state["messages"]

    # Process logic here
    response = llm.invoke(messages)

    return {
        "messages": [response],
        "current_step": "next_step"
    }
```

### Шаблон Graph

```python
from langgraph.graph import StateGraph, END

def create_agent():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("process", process_node)
    graph.add_node("tool", tool_node)
    graph.add_node("respond", respond_node)

    # Add edges
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "process": "process",
            "respond": "respond",
            "end": END
        }
    )
    graph.add_edge("process", "tool")
    graph.add_edge("tool", "router")
    graph.add_edge("respond", END)

    # Set entry point
    graph.set_entry_point("router")

    return graph.compile()
```

---

## RAG Pipeline

### Document Processing

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load documents
loader = TextLoader("document.txt")
documents = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(documents)
```

### Embedding & Storage

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector

# Create embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Store in vector database
vectorstore = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection_string="postgresql://...",
    collection_name="documents"
)
```

### Retrieval

```python
# Create retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# With reranking
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

reranker = CohereRerank(top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=retriever
)
```

---

## Tools

### Создание Tool

```python
from langchain_core.tools import tool

@tool
def search_database(query: str) -> str:
    """Search the database for relevant information.

    Args:
        query: The search query string

    Returns:
        Search results as a string
    """
    # Implementation
    results = db.search(query)
    return str(results)
```

### Structured Tool

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str
    max_results: int = 10

def search_impl(query: str, max_results: int) -> str:
    # Implementation
    pass

search_tool = StructuredTool.from_function(
    func=search_impl,
    name="search",
    description="Search for information",
    args_schema=SearchInput
)
```

---

## Best Practices

### Prompts

```yaml
System Prompts:
  - Чёткие инструкции
  - Формат вывода
  - Ограничения
  - Примеры

Few-shot:
  - 2-5 примеров
  - Разнообразные cases
  - Edge cases

Chain-of-thought:
  - Step-by-step reasoning
  - Intermediate outputs
```

### Error Handling

```python
from langchain_core.runnables import RunnableConfig
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def safe_invoke(chain, input_data):
    try:
        return chain.invoke(input_data)
    except Exception as e:
        logger.error(f"Chain failed: {e}")
        raise
```

### Observability

```python
from langchain_core.tracers import LangChainTracer
from langsmith import Client

# Enable tracing
tracer = LangChainTracer(project_name="my-project")

# Invoke with tracing
result = chain.invoke(
    input_data,
    config={"callbacks": [tracer]}
)
```

---

## Deployment

### FastAPI Integration

```python
from fastapi import FastAPI
from langserve import add_routes

app = FastAPI()

# Add agent as API endpoint
add_routes(app, agent, path="/agent")
```

### Streaming

```python
async def stream_response(agent, input_data):
    async for chunk in agent.astream(input_data):
        yield chunk
```

---

## Medical Agent Patterns (Aibolit AI)

### Medical Supervisor Pattern (LangGraph)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage
import operator

class MedicalAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    patient_id: str
    consultation_id: str
    agent_code: str  # cardiologist, neurologist, etc.
    symptoms: list[dict]
    medical_history: dict
    current_step: str
    differential_diagnoses: list[dict]
    confidence_level: float
    red_flags: list[str]
    escalation_needed: bool
    disclaimer_added: bool
    evidence_sources: list[str]
    tool_results: dict

def create_medical_supervisor():
    """
    Supervisor (Triage Agent) → Specialist Agents (22)
    Каждый specialist agent имеет обязательные safety nodes.
    """
    graph = StateGraph(MedicalAgentState)

    # Supervisor nodes
    graph.add_node("triage", triage_node)          # Определяет специализацию
    graph.add_node("specialist", specialist_node)    # Вызывает нужного агента
    graph.add_node("safety_check", safety_check_node)  # ОБЯЗАТЕЛЬНЫЙ
    graph.add_node("escalation", escalation_node)    # ОБЯЗАТЕЛЬНЫЙ
    graph.add_node("disclaimer", disclaimer_node)    # ОБЯЗАТЕЛЬНЫЙ
    graph.add_node("respond", respond_node)

    # Routing
    graph.set_entry_point("triage")
    graph.add_conditional_edges(
        "triage",
        triage_decision,
        {
            "specialist": "specialist",
            "escalation": "escalation",  # Urgent → сразу к врачу
        }
    )
    graph.add_edge("specialist", "safety_check")
    graph.add_conditional_edges(
        "safety_check",
        safety_decision,
        {
            "escalation": "escalation",  # Red flag → к врачу
            "disclaimer": "disclaimer",  # OK → добавить дисклеймер
        }
    )
    graph.add_edge("disclaimer", "respond")
    graph.add_edge("escalation", "respond")
    graph.add_edge("respond", END)

    return graph.compile(checkpointer=checkpointer)
```

### Mandatory Safety Nodes

```python
def safety_check_node(state: MedicalAgentState) -> MedicalAgentState:
    """
    ОБЯЗАТЕЛЬНЫЙ NODE в каждом medical agent graph.
    Проверяет red flags после каждого шага анализа.
    См. rules/05-medical-safety.md
    """
    red_flags = detect_red_flags(state["symptoms"], state["tool_results"])
    confidence = state["confidence_level"]

    escalation_needed = (
        len(red_flags) > 0 or
        confidence < 0.3 or
        state.get("patient_requests_doctor", False) or
        state.get("consecutive_uncertain", 0) >= 3
    )

    return {
        "red_flags": red_flags,
        "escalation_needed": escalation_needed,
        "current_step": "safety_checked"
    }

def escalation_node(state: MedicalAgentState) -> MedicalAgentState:
    """
    ОБЯЗАТЕЛЬНЫЙ NODE. Инициирует эскалацию к живому врачу.
    Триггеры: red_flag (urgency 4-5), confidence < 0.3,
    пациент просит врача, 3+ неопределённых результатов.
    """
    urgency = calculate_urgency(state["red_flags"])

    AuditLogService.log_medical(
        'doctor_escalation_triggered',
        data={
            'consultation_id': state["consultation_id"],
            'reason': state["red_flags"],
            'urgency_level': urgency,
        },
        actor='system',
    )

    return {
        "escalation_needed": True,
        "current_step": "escalated"
    }

def disclaimer_node(state: MedicalAgentState) -> MedicalAgentState:
    """
    ОБЯЗАТЕЛЬНЫЙ NODE. Добавляет дисклеймер к каждому ответу.
    Шаблоны из rules/05-medical-safety.md.
    """
    disclaimer = generate_disclaimer(
        response_type=state["current_step"],
        confidence=state["confidence_level"],
        has_red_flags=len(state["red_flags"]) > 0,
    )

    return {
        "disclaimer_added": True,
        "messages": [AIMessage(content=disclaimer)]
    }
```

### Medical Specialist Agent Template

```python
def create_specialist_agent(agent_code: str, tools: list):
    """
    Шаблон для создания specialist agent (1 из 22).
    Каждый specialist ОБЯЗАН иметь safety_check → escalation → disclaimer.
    """
    graph = StateGraph(MedicalAgentState)

    # Specialist-specific nodes
    graph.add_node("analyze_symptoms", analyze_symptoms_node)
    graph.add_node("differential_diagnosis", differential_diagnosis_node)
    graph.add_node("use_tool", tool_node)
    graph.add_node("formulate_response", formulate_response_node)

    # ОБЯЗАТЕЛЬНЫЕ safety nodes
    graph.add_node("safety_check", safety_check_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("disclaimer", disclaimer_node)

    # Flow: analyze → differential → tools → safety → response
    graph.set_entry_point("analyze_symptoms")
    graph.add_edge("analyze_symptoms", "differential_diagnosis")
    graph.add_conditional_edges(
        "differential_diagnosis",
        needs_tools_decision,
        {"use_tool": "use_tool", "safety_check": "safety_check"}
    )
    graph.add_edge("use_tool", "differential_diagnosis")  # Loop back
    graph.add_conditional_edges(
        "safety_check",
        safety_decision,
        {"escalation": "escalation", "disclaimer": "disclaimer"}
    )
    graph.add_edge("disclaimer", "formulate_response")
    graph.add_edge("escalation", "formulate_response")
    graph.add_edge("formulate_response", END)

    return graph.compile(checkpointer=checkpointer)
```

---

## Medical Tools

### Общие медицинские инструменты

```python
from langchain_core.tools import tool
from pydantic import BaseModel

@tool
def symptom_analyzer(symptoms: list[str], patient_age: int, patient_sex: str) -> dict:
    """Анализ и классификация симптомов по тяжести и системам органов.

    Args:
        symptoms: Список симптомов пациента
        patient_age: Возраст пациента
        patient_sex: Пол пациента (M/F)

    Returns:
        Классификация симптомов с urgency scoring
    """
    # Classify by organ system, severity, duration
    # Check against red_flags from 05-medical-safety.md
    pass

@tool
def lab_interpreter(test_name: str, value: float, unit: str, patient_age: int, patient_sex: str) -> dict:
    """Интерпретация лабораторных анализов с учётом норм по возрасту и полу.

    Args:
        test_name: Название анализа (например, 'hemoglobin', 'glucose')
        value: Числовое значение
        unit: Единица измерения
        patient_age: Возраст пациента
        patient_sex: Пол пациента

    Returns:
        Интерпретация: normal/low/high/critical с reference range
    """
    # Compare with age/sex-specific norms from lab_norms collection
    pass

@tool
def drug_interaction_checker(drug_list: list[str]) -> dict:
    """Проверка взаимодействия между лекарствами (RxNorm + DrugBank).

    Args:
        drug_list: Список лекарств пациента

    Returns:
        Найденные взаимодействия с severity (minor/moderate/major/contraindicated)
    """
    # Query RxNorm API + DrugBank Open Data
    pass

@tool
def icd10_lookup(query: str, language: str = "ru") -> dict:
    """Поиск по МКБ-10 классификации.

    Args:
        query: Поисковый запрос (название болезни или код)
        language: Язык (ru/en)

    Returns:
        Код МКБ-10, название, категория, родительские коды
    """
    pass

@tool
def red_flag_detector(symptoms: list[str], vital_signs: dict | None = None) -> dict:
    """Детектор опасных состояний. Проверяет симптомы на наличие red flags.

    Args:
        symptoms: Список симптомов
        vital_signs: Витальные показатели (опционально)

    Returns:
        Найденные red flags с urgency level (1-5)
    """
    # Check against red_flags from 05-medical-safety.md
    pass

@tool
def vital_signs_evaluator(vitals: dict) -> dict:
    """Оценка витальных показателей.

    Args:
        vitals: Словарь с показателями (bp_systolic, bp_diastolic, heart_rate, temperature, spo2, respiratory_rate)

    Returns:
        Оценка каждого параметра: normal/borderline/abnormal/critical
    """
    pass
```

### Специализированные инструменты (примеры)

```python
# Кардиолог
@tool
def cardiac_risk_calculator(age: int, sex: str, total_cholesterol: float,
                            hdl: float, systolic_bp: float, smoker: bool,
                            diabetes: bool) -> dict:
    """Калькулятор кардиоваскулярного риска (SCORE / Framingham)."""
    pass

# Дерматолог
@tool
def skin_image_analyzer(image_path: str) -> dict:
    """AI-анализ изображений кожи. Screening tool — НЕ диагностический прибор."""
    # Uses skin lesion classification model
    # ОБЯЗАТЕЛЬНО: confidence threshold + disclaimer
    pass

# Пульмонолог
@tool
def chest_xray_analyzer(image_path: str) -> dict:
    """AI-анализ рентгена грудной клетки (TorchXRayVision). Screening tool."""
    # Uses TorchXRayVision model
    # Returns: findings, probabilities, confidence
    pass
```

---

## Medical Memory

### Patient Context Memory

```python
class MedicalMemoryManager:
    """
    Управление памятью для медицинских консультаций.
    Отличия от generic memory:
    - Медицинские данные шифруются
    - Retention 5 лет (вместо 90 дней)
    - Доступ только по patient_id + authentication
    """

    def __init__(self, patient_id: str, encryption_key: str):
        self.patient_id = patient_id
        self.encryption_key = encryption_key

    def get_consultation_history(self, limit: int = 10) -> list:
        """Получить историю консультаций пациента (зашифрованную)."""
        pass

    def get_medical_record(self) -> dict:
        """Получить медкарту пациента (зашифрованную)."""
        pass

    def save_consultation(self, consultation: dict) -> None:
        """Сохранить результат консультации (с шифрованием)."""
        pass
```

### Consultation Session Memory

```yaml
Стратегия памяти для медицинской сессии:

Short-term (в рамках одной консультации):
  - ConversationBufferMemory для текущего диалога
  - Symptoms accumulator (собранные симптомы)
  - Tool results cache (результаты инструментов)

Long-term (между консультациями):
  - VectorStore для истории консультаций пациента
  - Summarized medical history
  - Medication list (текущие лекарства)
  - Allergy list (аллергии)

Правила:
  - Медицинские данные ВСЕГДА шифруются при сохранении
  - Доступ к памяти только через authenticated patient_id
  - Retention: 5 лет для консультаций, 25 лет для медкарты
  - При отзыве согласия — удалить все данные пациента
```

---

## Medical Checkpointing

### Checkpoint Strategy

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Medical checkpointer с шифрованием
checkpointer = PostgresSaver.from_conn_string(
    conn_string="postgresql://...",
    # Все checkpoints шифруются — медицинские данные
)
```

```yaml
Обязательные checkpoints в медицинских консультациях:

1. after_triage:
   сохраняем: urgency_level, assigned_specialist, initial_symptoms
   цель: восстановление при сбое

2. after_symptom_analysis:
   сохраняем: classified_symptoms, organ_systems, severity
   цель: возможность вернуться к анализу

3. after_differential_diagnosis:
   сохраняем: differential_diagnoses, confidence_levels, evidence_sources
   цель: аудит диагностического процесса

4. after_safety_check:
   сохраняем: red_flags, escalation_decision, safety_score
   цель: аудит безопасности (критически важно!)

5. after_response:
   сохраняем: full_response, disclaimer_type, evidence_grade
   цель: полный audit trail консультации

Retention для medical checkpoints: 5 лет
Шифрование: AES-256 at rest
```

---

## Medical RAG Specifics

### Отличия от generic RAG

```yaml
Chunking:
  clinical_guidelines:
    strategy: "По секциям (показания, противопоказания, лечение)"
    chunk_size: 1500
    overlap: 300
    separators: ["\n## ", "\n### ", "\n\n", "\n"]

  pubmed_abstracts:
    strategy: "Целиком (не разбивать)"
    max_size: 3000

  icd10:
    strategy: "По кодам и описаниям"
    chunk_size: 500
    overlap: 0

Retrieval:
  type: "hybrid"  # semantic + keyword
  semantic_weight: 0.7
  keyword_weight: 0.3  # Медицинские термины часто exact match
  metadata_filters:
    - specialization  # Фильтр по специализации агента
    - year           # Только актуальные рекомендации
    - evidence_grade # Приоритет Grade A/B
  reranking: true
  reranker: "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Или Cohere Rerank

Embedding:
  preferred: "biomedical embeddings (если доступны)"
  fallback: "text-embedding-3-small"
  note: "Медицинская терминология требует специальных embeddings"

Collections:
  clinical_guidelines: "Клинические рекомендации Минздрав"
  pubmed_abstracts: "PubMed абстракты"
  icd10: "МКБ-10 классификация"
  drug_interactions: "Взаимодействия лекарств (DrugBank + RxNorm)"
  lab_norms: "Лабораторные нормы по возрасту и полу"
```

---

## Формат вывода

```yaml
langchain_implementation:
  type: "agent|chain|rag"
  name: "[Название]"

  architecture:
    pattern: "ReAct|Plan-Execute|Multi-Agent"
    llm: "gpt-4|claude-3"
    tools: ["tool1", "tool2"]

  components:
    - name: "[Component]"
      type: "node|tool|retriever"
      file: "[path]"

  configuration:
    temperature: 0.7
    max_tokens: 4096
    checkpoint: true

  tests:
    - "test_basic_flow"
    - "test_error_handling"

  documentation:
    - "/docs/ai/agent.md"

  signature: "AI-Agents Agent"
```

---

## Использование

| Агент | Использование |
|-------|---------------|
| AI-Agents | Основной пользователь — проектирование медицинских агентов |
| Coder | Реализация медицинских агентов под руководством AI-Agents |
| Medical-Domain | Верификация клинической корректности AI-агентов |
| QA | Тестирование медицинских agent flows |

---

*Навык v1.1 | Aibolit AI — Claude Code Agent System*
