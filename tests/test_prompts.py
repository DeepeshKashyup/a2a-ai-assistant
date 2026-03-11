
from src.prompts.templates import PromptTemplateManager


class TestPromptTemplateManager:
    def test_loads_system_prompt(self) -> None:
        """Test the system prompt loads correctly."""
        manager = PromptTemplateManager()
        assert len(manager.system_prompt) > 0
        print("System Prompt:", manager.system_prompt)


    def test_render_chat_includes_question(self) -> None:
        """Test the chat prompt template renders correctly."""
        manager = PromptTemplateManager()
        question = "What is the capital of France?"
        rendered = manager.render_chat(question)
        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert question in rendered
        print("Rendered Chat Prompt:", rendered)