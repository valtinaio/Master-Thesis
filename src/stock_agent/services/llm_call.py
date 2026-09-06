from anthropic import Anthropic

from stock_agent.config import ANTHROPIC_API_KEY


class LLMCall:
    """Sends a prompt with context to an Anthropic model and returns its answer."""

    def __init__(self, model: str):
        """Stores the model name used for every call."""
        self.model = model

    def llm_call(self, context: list, system_prompt: str, prompt: str,
                 response_model=None, tool_name: str = None):
        """Merges context and prompt into one message and returns the answer content blocks.
        With a response_model the model must answer in the structure of that Pydantic model."""
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        # Join all context elements and the prompt into one text, separated by line breaks.
        merged_text = "\n".join(context + [prompt])

        # The extra arguments differ per call type, so they are collected in one dictionary
        # and unpacked into the request below.
        if response_model is None:
            options = {"thinking": {"type": "enabled", "budget_tokens": 1024}}
        else:
            # The schema of the Pydantic model becomes a tool the model has to fill in.
            # Thinking is left out here, because the API rejects it together with a forced tool.
            options = {
                "tools": [{
                    "name": tool_name,
                    "input_schema": response_model.model_json_schema(),
                }],
                "tool_choice": {"type": "tool", "name": tool_name},
            }

        response = client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": merged_text}],
            **options,
        )
        return response.content # Without a response_model: a ThinkingBlock (response.content[0])
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
                                # With a response_model: a ToolUseBlock, whose .input already
                                # holds the answer as a dictionary.
                                # Syntax of ToolUseBlock:
                                # ToolUseBlock(
                                #   id='toolu_01A09q90qw...',
                                #   input={'quotas': {...}},
                                #   name='llm_quota',
                                #   type='tool_use'
                                #   )
