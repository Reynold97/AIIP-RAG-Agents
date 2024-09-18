# Agent-RAG

## Enviroment

Create a python enviroment either with `python-venv` or `conda` and activate it.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Make a .env file with the following structure:

`OAUTHLIB_INSECURE_TRANSPORT=1` #To bypass HTPPS requirements during development

## Usage
...

## Todos
- Ollama server
- Dockerization
- Use Supabase for user management with SQL and vector database with pgvector
- Endpoint to process folder is failing
- Add endpoint to explore the vector database, to add more visibility of the chunks
- Modify the complex agent to use any indexer, right know is fixed to chroma indexer
- Add Azure OCR to extract more quality data from PDFs
- Test streaming Responses
- Add Verbosity to the agents
- Update Documentation
- Add logging and code description
- Add a node to capture the topic of the contents that are being added to the database, and dinamically add it to the prompts marked with #***#


## RAG Agents Comparison

### Simple RAG Agent

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

### Complex RAG Agent

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