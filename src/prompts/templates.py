"""Prompt template manager - loads templates from configs/prompts.yaml. """

# ===============================================================================
# Test : python -c "from src.prompts.templates import PromptTemplateManager; 
# p = PromptTemplateManager(); print(p.render_chat('test'))"
# ===============================================================================
import structlog
from src.utils.helpers import load_yaml
from pathlib import Path

logger = structlog.get_logger()

_PROMPTS_PATH = Path(__file__).parent.parent.parent / "configs" / "prompts.yaml"

class PromptTemplateManager:
    """Loads and manages prompt templates from a YAML configuration file."""

    def __init__(self, config_path: str = _PROMPTS_PATH) -> None:
        self._templates = load_yaml(config_path)
        logger.info("Prompt templates loaded", path = str(config_path), template_count = len(self._templates))

    def get_template(self, template_name: str, default: str = None) -> str:
        """Retrieve a prompt template by name."""
        template = self._templates.get(template_name, default)
        return template
    
    @property
    def system_prompt(self) -> str:
        """Return the base system prompt."""
        return self.get_template("system_prompt", "You are a helpful AI assistant.")
    
    def render_chat(self, question: str) -> str:
        """Render a basic chat prompt."""
        chat_template = self.get_template("chat_template", "User question: {question}")
        return chat_template.format(question=question)
    
    def render_rag(self, question: str, context: str) -> str:
        """Render a RAG prompt with question and retrieved context."""
        rag_template = self.get_template("rag_template", "Context: {context}\n\nQuestion: {question}\n\nAnswer:")
        return rag_template.format(context=context, question=question)
    
    def get_few_shots(self) -> list[dict]:
        """Return few-shot examples from config."""
        return self.get_template("few_shots_examples", [])
