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

For data operations, including data download, chunking, and indexing refer to [Data_Operations](src/data/data_operations.md)


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