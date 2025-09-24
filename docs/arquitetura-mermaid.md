# 🏗️ Arquitetura do Sistema - Diagramas Mermaid

## 📊 Visão Geral da Arquitetura

```mermaid
graph TB
    subgraph "Cliente (Browser)"
        UI[("🌐 Interface Web<br/>localhost:3001")]
        HTML["📄 index.html<br/>Chat Interface"]
        JS["🔧 JavaScript<br/>Fetch API & SSE"]
    end

    subgraph "Frontend Server"
        PY_FRONT["🐍 serve_frontend.py<br/>HTTP Server<br/>Port: 3001"]
    end

    subgraph "Backend API"
        FASTAPI["⚡ FastAPI Server<br/>server.py<br/>Port: 8991"]

        subgraph "Endpoints"
            EP_HEALTH["/api/health"]
            EP_SDK["/api/sdk-status"]
            EP_CHAT["/api/chat"]
            EP_SESSIONS["/api/sessions"]
        end

        subgraph "Core Modules"
            HANDLER["claude_handler.py"]
            SESSION["session_manager.py"]
        end

        subgraph "Middleware"
            CORS["CORS"]
            RATE["Rate Limiter"]
            EXCEPTION["Exception Handler"]
        end
    end

    subgraph "Claude SDK"
        SDK_CLIENT["client.py"]
        SDK_QUERY["query.py"]
        SDK_INTERNAL["_internal/"]
    end

    subgraph "External Services"
        CLAUDE["🤖 Claude AI"]
        NEO4J["🗄️ Neo4j"]
        FLOW["⛓️ Flow MCP"]
    end

    UI --> HTML
    HTML --> JS
    JS -.->|HTTP Requests| FASTAPI

    PY_FRONT -.->|Serve Static| HTML

    FASTAPI --> EP_HEALTH
    FASTAPI --> EP_SDK
    FASTAPI --> EP_CHAT
    FASTAPI --> EP_SESSIONS

    EP_CHAT --> HANDLER
    HANDLER --> SESSION

    FASTAPI --> CORS
    FASTAPI --> RATE
    FASTAPI --> EXCEPTION

    HANDLER --> SDK_CLIENT
    SDK_CLIENT --> SDK_QUERY
    SDK_QUERY --> SDK_INTERNAL

    SDK_CLIENT --> CLAUDE
    SESSION --> NEO4J
    HANDLER --> FLOW

    style UI fill:#2d3748,stroke:#00ff00,color:#00ff00
    style FASTAPI fill:#1a202c,stroke:#00ff00,color:#00ff00
    style CLAUDE fill:#4a5568,stroke:#00ffff,color:#00ffff
    style NEO4J fill:#4a5568,stroke:#00ffff,color:#00ffff
    style FLOW fill:#4a5568,stroke:#00ffff,color:#00ffff
```

## 🔄 Fluxo de Comunicação

```mermaid
sequenceDiagram
    participant User as 👤 Usuário
    participant Browser as 🌐 Browser
    participant Frontend as 📄 Frontend<br/>(3001)
    participant API as ⚡ API<br/>(8991)
    participant Claude as 🤖 Claude SDK
    participant Services as 🗄️ Services<br/>(Neo4j/Flow)

    User->>Browser: Digite mensagem
    Browser->>Frontend: Input event
    Frontend->>API: POST /api/chat<br/>{message, session_id}

    API->>API: Validate request
    API->>API: Get/Create session

    API->>Claude: Create query
    Claude->>Claude: Process message

    loop SSE Stream
        Claude-->>API: Content chunks
        API-->>Frontend: SSE: {type: "content", text: "..."}
        Frontend-->>Browser: Render markdown
        Browser-->>User: Display response
    end

    Claude-->>Services: Store memory
    Services-->>Claude: Context

    API-->>Frontend: SSE: {type: "done"}
    Frontend->>Browser: Complete render
```

## 📦 Estrutura de Componentes

```mermaid
graph LR
    subgraph "Frontend Components"
        direction TB
        INDEX["index.html"]
        CHAT["Chat UI"]
        STATUS["Status Panel"]
        DEBUG["Debug Panel"]

        INDEX --> CHAT
        INDEX --> STATUS
        INDEX --> DEBUG
    end

    subgraph "API Components"
        direction TB
        SERVER["server.py"]
        ROUTES["Routes"]
        MIDDLEWARE["Middleware"]
        SERVICES["Services"]

        SERVER --> ROUTES
        SERVER --> MIDDLEWARE
        ROUTES --> SERVICES
    end

    subgraph "SDK Components"
        direction TB
        CLIENT["Client"]
        QUERY["Query Manager"]
        TRANSPORT["Transport Layer"]

        CLIENT --> QUERY
        QUERY --> TRANSPORT
    end
```

## 🔀 Fluxo de Dados

```mermaid
flowchart LR
    subgraph Input
        MSG["Mensagem do Usuário"]
        SESSION["Session ID"]
        PROJECT["Project ID"]
    end

    subgraph Processing
        VALIDATE["Validação"]
        ENHANCE["Enriquecimento"]
        STREAM["Streaming"]
    end

    subgraph Output
        SSE["SSE Events"]
        JSON["JSON Response"]
        ERROR["Error Handling"]
    end

    MSG --> VALIDATE
    SESSION --> VALIDATE
    PROJECT --> VALIDATE

    VALIDATE --> ENHANCE
    ENHANCE --> STREAM

    STREAM --> SSE
    STREAM --> JSON
    VALIDATE --> ERROR
```

## 🛡️ Arquitetura de Segurança

```mermaid
graph TD
    REQUEST["HTTP Request"] --> CORS["CORS Check"]
    CORS --> RATE["Rate Limiter<br/>100 req/min"]
    RATE --> AUTH["Auth Check<br/>(future)"]
    AUTH --> VALIDATE["Input Validation"]
    VALIDATE --> HANDLER["Request Handler"]

    HANDLER --> SUCCESS["✅ Success Response"]
    HANDLER --> ERROR["❌ Error Response"]

    CORS -.->|Blocked| REJECT1["🚫 CORS Error"]
    RATE -.->|Exceeded| REJECT2["🚫 429 Too Many Requests"]
    AUTH -.->|Failed| REJECT3["🚫 401 Unauthorized"]
    VALIDATE -.->|Invalid| REJECT4["🚫 400 Bad Request"]

    style SUCCESS fill:#48bb78
    style ERROR fill:#f56565
    style REJECT1 fill:#fc8181
    style REJECT2 fill:#fc8181
    style REJECT3 fill:#fc8181
    style REJECT4 fill:#fc8181
```

## 🔌 Integração de Serviços

```mermaid
graph TD
    API["FastAPI Backend"] --> |Query| CLAUDE["Claude AI"]
    API --> |Store/Retrieve| NEO4J["Neo4j Database"]
    API --> |Blockchain Ops| FLOW["Flow MCP Tools"]

    CLAUDE --> |Response| API
    NEO4J --> |Context| API
    FLOW --> |TX Data| API

    subgraph "Neo4j Operations"
        LEARN["Store Learning"]
        CONTEXT["Get Context"]
        MEMORY["Retrieve Memory"]
    end

    subgraph "Flow Operations"
        CONTRACTS["Smart Contracts"]
        WALLET["Wallet Ops"]
        DEFI["DeFi Tools"]
    end

    NEO4J --> LEARN
    NEO4J --> CONTEXT
    NEO4J --> MEMORY

    FLOW --> CONTRACTS
    FLOW --> WALLET
    FLOW --> DEFI
```

## 📈 Estados da Aplicação

```mermaid
stateDiagram-v2
    [*] --> Idle: App Start

    Idle --> Connecting: User sends message
    Connecting --> SessionCreated: New session
    Connecting --> SessionRestored: Existing session

    SessionCreated --> Processing
    SessionRestored --> Processing

    Processing --> Streaming: Claude responds
    Streaming --> Streaming: Content chunks
    Streaming --> Complete: Response done

    Complete --> Idle: Ready for next

    Connecting --> Error: Connection failed
    Processing --> Error: Processing failed
    Streaming --> Error: Stream error

    Error --> Idle: Error handled
```

## 🚀 Deploy Pipeline

```mermaid
graph LR
    DEV["Development<br/>localhost"] --> TEST["Testing<br/>CI/CD"]
    TEST --> STAGE["Staging<br/>Preview"]
    STAGE --> PROD["Production<br/>Live"]

    subgraph "Port Mapping"
        DEV_PORTS["Frontend: 3001<br/>Backend: 8991"]
        TEST_PORTS["Frontend: 3001<br/>Backend: 8991"]
        STAGE_PORTS["Frontend: 443<br/>Backend: 443/api"]
        PROD_PORTS["Frontend: 443<br/>Backend: 443/api"]
    end

    DEV --> DEV_PORTS
    TEST --> TEST_PORTS
    STAGE --> STAGE_PORTS
    PROD --> PROD_PORTS
```

## 💾 Estrutura de Dados

```mermaid
classDiagram
    class ChatRequest {
        +string message
        +string session_id
        +string project_id
        +dict metadata
    }

    class ChatResponse {
        +string type
        +string content
        +string session_id
        +dict metadata
    }

    class Session {
        +string id
        +datetime created_at
        +list messages
        +dict context
    }

    class ClaudeQuery {
        +string prompt
        +dict parameters
        +stream response
    }

    ChatRequest --> Session : creates/updates
    Session --> ClaudeQuery : generates
    ClaudeQuery --> ChatResponse : produces
    ChatResponse --> Session : updates
```

## 📊 Métricas e Monitoramento

```mermaid
graph TB
    subgraph "Metrics Collection"
        API_METRICS["API Metrics"]
        SDK_METRICS["SDK Metrics"]
        SESSION_METRICS["Session Metrics"]
    end

    subgraph "Monitoring"
        LATENCY["Response Latency"]
        TOKENS["Token Usage"]
        ERRORS["Error Rate"]
        SESSIONS["Active Sessions"]
    end

    subgraph "Alerts"
        HIGH_LATENCY["⚠️ High Latency > 5s"]
        HIGH_TOKENS["⚠️ Token Limit"]
        HIGH_ERRORS["🚨 Error Rate > 5%"]
    end

    API_METRICS --> LATENCY
    SDK_METRICS --> TOKENS
    SESSION_METRICS --> SESSIONS
    API_METRICS --> ERRORS

    LATENCY --> HIGH_LATENCY
    TOKENS --> HIGH_TOKENS
    ERRORS --> HIGH_ERRORS
```

---

## 🔗 Como Visualizar os Diagramas

### Opção 1: GitHub
- Copie o código Mermaid e cole em um arquivo `.md` no GitHub
- O GitHub renderiza automaticamente

### Opção 2: Mermaid Live Editor
- Acesse: https://mermaid.live
- Cole o código Mermaid
- Exporte como PNG/SVG

### Opção 3: VS Code
- Instale a extensão "Markdown Preview Mermaid Support"
- Abra este arquivo no VS Code
- Use o preview (Ctrl+Shift+V)

### Opção 4: Obsidian
- Cole o código em uma nota
- Obsidian renderiza nativamente

---

## 📝 Legenda dos Ícones

- 🌐 **Frontend/Browser**
- ⚡ **FastAPI Backend**
- 🤖 **Claude AI**
- 🗄️ **Database (Neo4j)**
- ⛓️ **Blockchain (Flow)**
- 📄 **HTML/Documents**
- 🔧 **Scripts/Tools**
- ✅ **Success**
- ❌ **Error**
- ⚠️ **Warning**
- 🚨 **Critical Alert**