# Brand Monitoring System - Architecture Diagram

## Complete System Architecture

```mermaid
graph TB
    subgraph "🌐 User Interface Layer"
        UI[Flask Web Frontend<br/>enhanced_app.py]
        API[REST API Endpoints<br/>/api/run-search<br/>/api/run-sentiment<br/>/api/run-demo]
        DEMO[Demo Scripts<br/>demo_brand_monitoring.py]
        TEMPLATE[HTML Templates<br/>index.html]
    end
    
    subgraph "🤖 Core Application Layer"
        AGENT[Brand Monitoring Agent<br/>brand_monitoring_agent.py]
        CREW[CrewAI Framework<br/>Agent + Crew + Tasks]
        TOOLS[Custom Tools<br/>@tool decorators]
        STORAGE[Data Storage<br/>data_storage.py]
    end
    
    subgraph "🔧 Data Processing Layer"
        SEARCH[Brand Search Tool<br/>search_brand_mentions]
        SCRAPE[Content Scraping Tool<br/>scrape_platform_content]
        SENTIMENT[Sentiment Analysis Tool<br/>analyze_brand_sentiment]
        REPORT[Report Generation Tool<br/>generate_brand_report]
        WEBSEARCH[Web Search Tool<br/>web_search_duckduckgo]
    end
    
    subgraph "☁️ External Services"
        BRIGHTDATA[BrightData Proxy<br/>Web Scraping Service]
        BEDROCK[AWS Bedrock AI<br/>Claude 3.5 Sonnet]
        DUCKDUCKGO[DuckDuckGo Search<br/>Fallback Search Engine]
    end
    
    subgraph "💾 Data Storage Layer"
        JSON[JSON Results Storage<br/>results/*.json]
        FILES[File System<br/>Local Storage]
        MOCK[Mock Data Generator<br/>Testing Fallback]
    end
    
    subgraph "🧪 Testing & Validation"
        TESTS[Test Suite<br/>test-demo/]
        DEMO_TESTS[Demo Validation<br/>Step-by-step Testing]
        RATE_LIMIT[Rate Limiting Tests<br/>3-second delays]
        COMPONENT[Component Tests<br/>Individual Tool Testing]
    end
    
    subgraph "🔄 Rate Limiting & Error Handling"
        RATE_CONTROL[Rate Limiting<br/>3-second intervals]
        FALLBACK[Fallback Mechanisms<br/>DuckDuckGo → Mock Data]
        ERROR_HANDLE[Error Recovery<br/>Graceful Degradation]
    end
    
    %% User Interface Connections
    UI --> API
    API --> AGENT
    DEMO --> AGENT
    TEMPLATE --> UI
    
    %% Core Application Connections
    AGENT --> CREW
    CREW --> TOOLS
    AGENT --> STORAGE
    
    %% Data Processing Connections
    TOOLS --> SEARCH
    TOOLS --> SCRAPE
    TOOLS --> SENTIMENT
    TOOLS --> REPORT
    TOOLS --> WEBSEARCH
    
    %% External Service Connections
    SEARCH --> BRIGHTDATA
    SEARCH --> DUCKDUCKGO
    SCRAPE --> BRIGHTDATA
    SENTIMENT --> BEDROCK
    REPORT --> BEDROCK
    WEBSEARCH --> DUCKDUCKGO
    
    %% Data Storage Connections
    AGENT --> JSON
    API --> FILES
    STORAGE --> JSON
    SCRAPE --> MOCK
    
    %% Testing Connections
    TESTS --> AGENT
    DEMO_TESTS --> DEMO
    RATE_LIMIT --> TOOLS
    COMPONENT --> SEARCH
    COMPONENT --> SENTIMENT
    COMPONENT --> REPORT
    
    %% Rate Limiting Connections
    RATE_CONTROL --> SEARCH
    RATE_CONTROL --> SENTIMENT
    FALLBACK --> BRIGHTDATA
    FALLBACK --> BEDROCK
    ERROR_HANDLE --> TOOLS
    
    %% Styling
    classDef userInterface fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef coreApp fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataProcessing fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef externalServices fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef dataStorage fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef testing fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef rateLimiting fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    
    class UI,API,DEMO,TEMPLATE userInterface
    class AGENT,CREW,TOOLS,STORAGE coreApp
    class SEARCH,SCRAPE,SENTIMENT,REPORT,WEBSEARCH dataProcessing
    class BRIGHTDATA,BEDROCK,DUCKDUCKGO externalServices
    class JSON,FILES,MOCK dataStorage
    class TESTS,DEMO_TESTS,RATE_LIMIT,COMPONENT testing
    class RATE_CONTROL,FALLBACK,ERROR_HANDLE rateLimiting
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Agent
    participant SearchTool
    participant SentimentTool
    participant ReportTool
    participant BrightData
    participant Bedrock
    participant Storage
    
    User->>Frontend: Start Brand Monitoring
    Frontend->>Agent: Initialize Brand Search
    Agent->>SearchTool: search_brand_mentions()
    
    Note over SearchTool: Rate Limiting (3s delay)
    SearchTool->>BrightData: Search for brand mentions
    alt BrightData Success
        BrightData-->>SearchTool: Return search results
    else BrightData Failure
        SearchTool->>SearchTool: Fallback to DuckDuckGo
    end
    
    SearchTool-->>Agent: Return formatted results
    Agent->>Agent: Wait 3 seconds (rate limiting)
    
    Agent->>SentimentTool: analyze_brand_sentiment()
    SentimentTool->>Bedrock: Analyze sentiment with Claude 3.5
    Bedrock-->>SentimentTool: Return sentiment analysis
    SentimentTool-->>Agent: Return sentiment results
    
    Agent->>Agent: Wait 3 seconds (rate limiting)
    
    Agent->>ReportTool: generate_brand_report()
    ReportTool->>Bedrock: Generate comprehensive report
    Bedrock-->>ReportTool: Return formatted report
    ReportTool-->>Agent: Return final report
    
    Agent->>Storage: Save results to JSON
    Storage-->>Agent: Confirm save
    Agent-->>Frontend: Return complete analysis
    Frontend-->>User: Display results dashboard
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Input Layer"
        A[Brand Name Input]
        B[Configuration Parameters]
    end
    
    subgraph "Processing Pipeline"
        C[Search & Discovery]
        D[Content Extraction]
        E[Sentiment Analysis]
        F[Report Generation]
    end
    
    subgraph "Output Layer"
        G[JSON Results]
        H[Web Dashboard]
        I[Markdown Reports]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    
    %% Rate limiting indicators
    C -.->|3s delay| D
    D -.->|3s delay| E
    E -.->|3s delay| F
```

## Technology Stack Architecture

```mermaid
graph TB
    subgraph "Frontend Technologies"
        FLASK[Flask Web Framework]
        HTML[HTML5 Templates]
        CSS[CSS3 Styling]
        JS[JavaScript]
    end
    
    subgraph "Backend Technologies"
        PYTHON[Python 3.10+]
        CREWAI[CrewAI Framework]
        BOTO3[AWS SDK]
        REQUESTS[HTTP Requests]
    end
    
    subgraph "AI & ML Services"
        BEDROCK[AWS Bedrock]
        CLAUDE[Claude 3.5 Sonnet]
        SENTIMENT[Sentiment Analysis]
    end
    
    subgraph "Data Sources"
        BRIGHTDATA[BrightData Proxy]
        DUCKDUCKGO[DuckDuckGo API]
        MOCK[Mock Data Generator]
    end
    
    subgraph "Storage & Persistence"
        JSON[JSON Files]
        FILESYSTEM[Local File System]
        MEMORY[In-Memory Cache]
    end
    
    FLASK --> PYTHON
    HTML --> FLASK
    CSS --> HTML
    JS --> HTML
    
    PYTHON --> CREWAI
    PYTHON --> BOTO3
    PYTHON --> REQUESTS
    
    CREWAI --> BEDROCK
    BOTO3 --> BEDROCK
    BEDROCK --> CLAUDE
    CLAUDE --> SENTIMENT
    
    REQUESTS --> BRIGHTDATA
    REQUESTS --> DUCKDUCKGO
    PYTHON --> MOCK
    
    PYTHON --> JSON
    JSON --> FILESYSTEM
    FLASK --> MEMORY
```

## Key Features Highlighted

### 🔄 **Rate Limiting Flow**
- 3-second delays between major operations
- Exponential backoff for failed requests
- Graceful degradation with fallbacks

### 🛡️ **Error Handling Strategy**
- BrightData → DuckDuckGo → Mock Data
- Bedrock failures → Local processing
- Network timeouts → Retry mechanisms

### 📊 **Data Processing Pipeline**
1. **Search**: Find brand mentions
2. **Scrape**: Extract content
3. **Analyze**: Sentiment analysis
4. **Report**: Generate insights
5. **Store**: Persist results

### 🧪 **Testing Architecture**
- Individual component testing
- Integration testing
- Demo validation
- Rate limiting verification

This architecture ensures robust, scalable, and maintainable brand monitoring with comprehensive error handling and testing capabilities.
