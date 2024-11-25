from .schemas import LLMConfig, DatabaseConfig, AgentConfig

# Available LLMs
AVAILABLE_LLMS = {
    "gpt-4o-mini": LLMConfig(
        model_name="gpt-4o-mini",
        model_type="openai",
        parameters={"temperature": 0.7}
    ),
    # Add more models as needed
}

# Available Databases
AVAILABLE_DATABASES = ["ChromaDB"]  # Add more as needed

# Default Configurations
DEFAULT_LLM = AVAILABLE_LLMS["gpt-4o-mini"]

DEFAULT_DATABASE = DatabaseConfig(
    database_name="ChromaDB",
    collection_name="default_collection",
    k=4
)

DEFAULT_AGENT_CONFIG = AgentConfig(
    llm=DEFAULT_LLM,
    database=DEFAULT_DATABASE
)