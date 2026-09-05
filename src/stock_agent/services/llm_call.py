from anthropic import Anthropic

from stock_agent.config import ANTHROPIC_API_KEY


class LLMCall:
    """Sends a prompt with context to an Anthropic model and returns its answer."""

    def __init__(self, model: str):
        """Stores the model name used for every call."""
        self.model = model

    def llm_call(self, context: list, system_prompt: str, prompt: str):
        """Merges context and prompt into one message and returns the answer content blocks."""
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        # Join all context elements and the prompt into one text, separated by line breaks.
        merged_text = "\n".join(context + [prompt])
        response = client.messages.create(
            model=self.model,
            max_tokens=2000,
            thinking={"type": "enabled", "budget_tokens": 1024},
            system=system_prompt,
            messages=[{"role": "user", "content": merged_text}],
        )
        return response.content # Returns a ThinkingBlock (response.content[0])
                                # and a TextBlock (response.content[1]). 
                                # Syntax of ThinkingBlock:
                                # ThinkingBlock(
                                #   signature='EpYHCpoBCBEYAipAanGIVGlgtR2...',
                                #   thinking='thinking text...',
                                #   type='thinking'
                                #   )
                                # Syntax of TextBlock
                                # TextBlock(
                                #   citations=None,
                                #   text="final answer...",
                                #   type='text'
                                #   )
