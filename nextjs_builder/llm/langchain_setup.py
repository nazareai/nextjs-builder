"""
LangChain and OpenRouter integration for Next.js & Tailwind website builder.

This module provides utilities for setting up LangChain with OpenRouter
to interact with Claude-3.5-Sonnet and other LLM models.
"""
import os
from typing import Dict, Any, Optional, List, Union

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.schema.runnable import Runnable
from rich.console import Console

from nextjs_builder.config import load_config

# Initialize console for pretty output
console = Console()

# Load environment variables
load_dotenv()


def get_llm(
    model_name: str = "anthropic/claude-3.5-sonnet-20240620",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> ChatOpenAI:
    """
    Get a LangChain LLM using OpenRouter.
    
    Args:
        model_name: The OpenRouter model identifier
        temperature: The temperature for generation
        max_tokens: The maximum number of tokens to generate
        api_key: The OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
        base_url: The OpenRouter base URL (defaults to OPENROUTER_BASE_URL env var)
        
    Returns:
        A configured LangChain ChatOpenAI instance
    
    Raises:
        ValueError: If the API key is not provided
    """
    # Get API key and base URL from environment if not provided
    openrouter_api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    # Create the LLM
    llm = ChatOpenAI(
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return llm


def create_chain(
    prompt_template: str,
    llm: Optional[ChatOpenAI] = None,
    model_name: str = "anthropic/claude-3.5-sonnet-20240620",
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> LLMChain:
    """
    Create a LangChain chain with the given prompt template.
    
    Args:
        prompt_template: The prompt template string
        llm: Optional pre-configured LLM
        model_name: The model name to use if llm is not provided
        temperature: The temperature for generation
        max_tokens: The maximum number of tokens to generate
        
    Returns:
        A configured LLMChain
    """
    if llm is None:
        llm = get_llm(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
    prompt = PromptTemplate.from_template(prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain


def generate_with_prompt(
    prompt_template: str,
    input_variables: Dict[str, Any],
    model_name: str = "anthropic/claude-3.5-sonnet-20240620",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    retry_attempts: int = 3,
) -> str:
    """
    Generate text using a prompt template and input variables.
    
    Args:
        prompt_template: The prompt template string
        input_variables: The input variables for the prompt
        model_name: The OpenRouter model identifier
        temperature: The temperature for generation
        max_tokens: The maximum number of tokens to generate
        retry_attempts: The number of retry attempts on failure
        
    Returns:
        The generated text
        
    Raises:
        ValueError: If all retry attempts fail
    """
    llm = get_llm(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Try to generate with retries
    errors = []
    for attempt in range(retry_attempts):
        try:
            result = chain.run(input_variables)
            return result
        except Exception as e:
            errors.append(str(e))
            console.print(f"[yellow]Warning:[/yellow] Generation attempt {attempt + 1} failed: {e}")
            
            if attempt < retry_attempts - 1:
                console.print(f"Retrying... ({attempt + 2}/{retry_attempts})")
            else:
                error_msg = f"All {retry_attempts} generation attempts failed: {'; '.join(errors)}"
                console.print(f"[bold red]Error:[/bold red] {error_msg}")
                raise ValueError(error_msg)


def create_messages(
    system_prompt: str,
    conversation_history: List[Dict[str, str]],
) -> List[Union[SystemMessage, HumanMessage, AIMessage]]:
    """
    Create a list of LangChain messages from a system prompt and conversation history.
    
    Args:
        system_prompt: The system prompt
        conversation_history: A list of message dictionaries with 'role' and 'content'
        
    Returns:
        A list of LangChain messages
    """
    messages = [SystemMessage(content=system_prompt)]
    
    for message in conversation_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        # Ignore other roles
    
    return messages


class LLMManager:
    """
    Manager for LLM interactions with caching and configuration.
    """
    
    def __init__(
        self,
        model_name: str = "anthropic/claude-3.5-sonnet-20240620",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize the LLM manager.
        
        Args:
            model_name: The OpenRouter model identifier
            temperature: The temperature for generation
            max_tokens: The maximum number of tokens to generate
        """
        # Load configuration
        config = load_config()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.retry_attempts = config["llm"].get("retry_attempts", 3)
        
        # Create LLM
        self.llm = get_llm(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def generate_text(
        self,
        prompt: str,
        retry_attempts: Optional[int] = None,
    ) -> str:
        """
        Generate text using a raw prompt.
        
        Args:
            prompt: The text prompt
            retry_attempts: Number of retry attempts (defaults to instance setting)
            
        Returns:
            The generated text
        """
        retry_attempts = retry_attempts or self.retry_attempts
        
        # Try to generate with retries
        errors = []
        for attempt in range(retry_attempts):
            try:
                result = self.llm.predict(prompt)
                return result
            except Exception as e:
                errors.append(str(e))
                console.print(f"[yellow]Warning:[/yellow] Generation attempt {attempt + 1} failed: {e}")
                
                if attempt < retry_attempts - 1:
                    console.print(f"Retrying... ({attempt + 2}/{retry_attempts})")
                else:
                    error_msg = f"All {retry_attempts} generation attempts failed: {'; '.join(errors)}"
                    console.print(f"[bold red]Error:[/bold red] {error_msg}")
                    raise ValueError(error_msg)
    
    def generate_with_template(
        self,
        template: str,
        input_variables: Dict[str, Any],
        retry_attempts: Optional[int] = None,
    ) -> str:
        """
        Generate text using a template and input variables.
        
        Args:
            template: The prompt template string
            input_variables: The input variables for the template
            retry_attempts: Number of retry attempts (defaults to instance setting)
            
        Returns:
            The generated text
        """
        prompt_template = PromptTemplate.from_template(template)
        prompt = prompt_template.format(**input_variables)
        
        return self.generate_text(prompt, retry_attempts)
    
    def generate_with_chat_history(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        retry_attempts: Optional[int] = None,
    ) -> str:
        """
        Generate text using a system prompt and conversation history.
        
        Args:
            system_prompt: The system prompt
            conversation_history: A list of message dictionaries with 'role' and 'content'
            retry_attempts: Number of retry attempts (defaults to instance setting)
            
        Returns:
            The generated text
        """
        retry_attempts = retry_attempts or self.retry_attempts
        messages = create_messages(system_prompt, conversation_history)
        
        # Try to generate with retries
        errors = []
        for attempt in range(retry_attempts):
            try:
                return self.llm.predict_messages(messages).content
            except Exception as e:
                errors.append(str(e))
                console.print(f"[yellow]Warning:[/yellow] Generation attempt {attempt + 1} failed: {e}")
                
                if attempt < retry_attempts - 1:
                    console.print(f"Retrying... ({attempt + 2}/{retry_attempts})")
                else:
                    error_msg = f"All {retry_attempts} generation attempts failed: {'; '.join(errors)}"
                    console.print(f"[bold red]Error:[/bold red] {error_msg}")
                    raise ValueError(error_msg)