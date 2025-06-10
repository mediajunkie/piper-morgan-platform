import os
import json
import anthropic
from typing import Dict, List, Optional
from config import app_config
from llm_adapter import LLMAdapter # This import will now work correctly
from exceptions import LLMGenerationError, LLMParseError
from logger_config import logger

_anthropic_client = None

def get_anthropic_client():
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

class ClaudeClient(LLMAdapter): # This inheritance is now valid
    def __init__(self, model: str = app_config.ANTHROPIC_DEFAULT_MODEL):
        self.client = get_anthropic_client()
        self.model = model
        logger.info(f"ClaudeClient initialized with model: {self.model}")

    def query(self,
              prompt: str,
              context: Optional[str] = None,
              max_tokens: int = app_config.ANTHROPIC_MAX_TOKENS,
              temperature: float = app_config.ANTHROPIC_TEMPERATURE) -> str:
        logger.info(f"Querying Claude (model: {self.model}).")
        logger.debug(f"Prompt: {prompt[:200]}...")

        messages = [{"role": "user", "content": prompt}]
        system_message = None
        if context:
            system_message = f"Context: {context}"
            logger.debug(f"Context added to system message: {system_message[:200]}...")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                system=system_message if system_message else None,
                temperature=temperature
            )
            logger.debug(f"Raw LLM response: {response.content[0].text[:200]}...")
            return response.content[0].text
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
                         max_tokens: int = app_config.ANTHROPIC_MAX_TOKENS, # Added parameter with default
                         temperature: float = 0.0) -> Dict: # Typically 0.0 for structured
        logger.info(f"Querying Claude for structured response (model: {self.model}).")
        logger.debug(f"Prompt: {prompt[:200]}...")

        format_instructions = json.dumps(response_format, indent=2)
        full_prompt = f"{prompt}\n\nThe response *must* be a JSON object matching this structure:\n```json\n{format_instructions}\n```"

        messages = [{"role": "user", "content": full_prompt}]
        system_message = "You are a helpful AI assistant. Your task is to generate a structured JSON response.\nAdhere strictly to the requested JSON format. Do not include any other text or markdown fences."
        if context:
            system_message = f"Context: {context}\n{system_message}"
            logger.debug(f"Context added to system message: {system_message[:200]}...")

        logger.debug(f"Structured Query - Model: {self.model}")
        logger.debug(f"Structured Query - System payload: {system_message[:200]}...")
        logger.debug(f"Structured Query - Messages payload: {json.dumps(messages, indent=2)}")
        logger.debug(f"Structured Query - Max tokens: {max_tokens}")
        logger.debug(f"Structured Query - Temperature: {temperature}")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                system=system_message,
                temperature=temperature
            )
            raw_text = response.content[0].text
            logger.debug(f"Raw LLM structured response: {raw_text[:200]}...")

            json_str = raw_text
            if raw_text.strip().startswith("```json") and raw_text.strip().endswith("```"):
                json_str = raw_text.strip()[len("```json"):len(raw_text.strip())-len("```")].strip()
            elif raw_text.strip().startswith("{") and raw_text.strip().endswith("}"):
                json_str = raw_text.strip()
            else:
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