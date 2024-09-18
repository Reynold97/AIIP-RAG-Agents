# RAG Agents Comparison

## Simple RAG Agent

Here's a breakdown of Simple RAG Agent flow:

1. The process starts with the retrieval node.
2. The retrieved documents are passed to the generation node.

```mermaid
graph TD
    A[Start] --> B[Retriever Node]
    B --> C[Generator Node]
    C --> D[End]
```

---

## Complex RAG Agent

Here's a breakdown of Complex RAG Agent flow:

1. The process starts with routing the question.
2. Based on the routing, it goes to either:
   - DB Query Rewrite
   - Websearch Query Rewrite
   - Simple Question Node
3. The DB Query Rewrite and Websearch Query Rewrite lead to their respective retrieval nodes.
4. Retrieved documents are filtered.
5. If relevant documents are found:
   - They go through Knowledge Extraction
   - Then to the Generator Node
6. The generated answer is evaluated.
7. Based on the evaluation, it either:
   - Ends the process
   - Gives feedback and tries again
   - Gives up if max attempts are reached
8. The Simple Question Node leads directly to the end.

```mermaid
graph TD
    A[Start] --> B{Route Question}
    B -->|Vectorstore| C[DB Query Rewrite]
    B -->|Websearch| D[Websearch Query Rewrite]
    B -->|QA LM| E[Simple Question Node]
    
    C --> F[Retrieval Node]
    D --> G[Web Search Node]
    
    F --> H[Filter Docs Node]
    G --> H
    
    H --> I{Relevant Documents?}
    I -->|Yes| J[Knowledge Extraction]
    I -->|No, Vectorstore| C
    I -->|No, Websearch| D
    I -->|No, Max Attempts| K[Give Up Node]
    
    J --> L[Generator Node]
    
    L --> M{Answer Evaluation}
    M -->|Useful| N[End]
    M -->|Not Relevant| O[Query Feedback]
    M -->|Hallucination| P[Generation Feedback]
    M -->|Max Generations| K
    
    O --> Q{Search Mode}
    Q -->|Vectorstore| C
    Q -->|Websearch| D
    
    P --> L
    
    E --> N
    K --> N
```