import os
import json
import anthropic
from typing import Dict, List, Optional
from config import app_config
from llm_adapter import LLMAdapter
from exceptions import LLMGenerationError, LLMParseError
from logger_config import logger # Import logger

_anthropic_client = None

def get_anthropic_client():
    """Returns a singleton Anthropic client instance."""
    global _anthropic_client
    if _anthropic_client is None:
        api_key = app_config.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
        try:
            _anthropic_client = anthropic.Anthropic(api_key=api_key)
            logger.info("Anthropic client initialized.")
        except Exception as e:
            logger.exception("Failed to initialize Anthropic client.")
            raise LLMGenerationError(f"Failed to initialize Anthropic client: {e}") from e
    return _anthropic_client

class ClaudeClient(LLMAdapter):
    def __init__(self, model: str = app_config.ANTHROPIC_DEFAULT_MODEL):
        self.client = get_anthropic_client()
        self.model = model
        logger.info(f"ClaudeClient initialized with model: {self.model}")

    def query(self,
              prompt: str,
              context: Optional[str] = None,
              max_tokens: int = app_config.ANTHROPIC_MAX_TOKENS,
              temperature: float = app_config.ANTHROPIC_TEMPERATURE) -> str:
        """
        Queries the Claude LLM for a free-form text response.
        """
        messages = [{"role": "user", "content": prompt}]
        if context:
            # Insert context at the beginning of the messages list
            messages.insert(0, {"role": "user", "content": f"Context: {context}"})

        try:
            # This is the line that caused the IndentationError if misaligned
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error during query: Status {e.status_code} - {e.response}")
            raise LLMGenerationError(f"Anthropic API error during query: {e.status_code} - {e.response}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during Claude query.")
            raise LLMGenerationError(f"An unexpected error occurred during Claude query: {e}") from e

    def query_structured(self,
                         prompt: str,
                         response_format: Dict,
                         context: Optional[str] = None,
                         max_tokens: int = app_config.ANTHROPIC_MAX_TOKENS,
                         temperature: float = 0.0) -> Dict: # Structured queries often use lower temp
        """
        Queries the Claude LLM for a structured (JSON) response.
        """
        system_prompt = f"""
        You are a highly skilled AI assistant.
        Your task is to respond with a JSON object that strictly adheres to the following JSON schema.
        Do NOT include any other text, explanations, or formatting outside the JSON object.
        ONLY return the JSON object.

        JSON Schema:
        ```json
        {json.dumps(response_format, indent=2)}
        ```
        """
        messages = [{"role": "user", "content": prompt}]
        if context:
            messages.insert(0, {"role": "user", "content": f"Context: {context}"})

        logger.debug(f"Structured Query - System Prompt: {system_prompt}")
        logger.debug(f"Structured Query - Messages: {messages}")
        logger.debug(f"Structured Query - Model: {self.model}")
        logger.debug(f"Structured Query - Max tokens: {max_tokens}")
        logger.debug(f"Structured Query - Temperature: {temperature}")

        raw_text = ""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
            )
            raw_text = message.content[0].text
            logger.debug(f"Raw LLM structured response: {raw_text}")

            # Anthropic models sometimes return JSON within markdown.
            # Clean it up if necessary.
            if raw_text.strip().startswith("```json") and raw_text.strip().endswith("```"):
                json_str = raw_text.strip()[len("```json"):len(raw_text.strip())-len("```")].strip()
            elif raw_text.strip().startswith("{") and raw_text.strip().endswith("}"):
                json_str = raw_text.strip()
            else:
                # Attempt to extract JSON even if not perfectly wrapped
                start = raw_text.find("{")
                end = raw_text.rfind("}")
                if start != -1 and end != -1 and start < end:
                    json_str = raw_text[start : end + 1]
                else:
                    json_str = raw_text

            parsed_json = json.loads(json_str.strip())
            logger.info("Claude structured query successful, JSON parsed.")
            return parsed_json
        except json.JSONDecodeError as e:
            logger.error(f"LLM generated invalid JSON: {e}")
            logger.debug(f"Raw LLM response causing JSONDecodeError: {raw_text}")
            raise LLMParseError(f"LLM generated invalid JSON: {e}") from e
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error during structured query: Status {e.status_code} - {e.response}")
            raise LLMGenerationError(f"Anthropic API error during structured query: {e.status_code} - {e.response}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during Claude structured query.")
            raise LLMGenerationError(f"An unexpected error occurred during Claude structured query: {e}") from e