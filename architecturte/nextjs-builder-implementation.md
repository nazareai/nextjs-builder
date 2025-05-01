# Next.js & Tailwind Website Builder - Implementation Guide

This guide provides detailed implementation instructions for creating our Next.js and Tailwind website builder module.

## Initial File Setup

### requirements.txt

```python
# LangChain dependencies
langchain>=0.0.267
langchain-openai>=0.0.5
langchain-core>=0.1.1

# OpenRouter integration
openrouter>=0.3.0

# CLI handling
click>=8.1.7
rich>=13.4.2

# Development tools
pytest>=7.3.1
black>=23.3.0
isort>=5.12.0

# Other utilities
python-dotenv>=1.0.0
pydantic>=2.4.2
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="nextjs-builder",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "langchain>=0.0.267",
        "langchain-openai>=0.0.5",
        "langchain-core>=0.1.1",
        "openrouter>=0.3.0",
        "click>=8.1.7",
        "rich>=13.4.2",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
    ],
    entry_points="""
        [console_scripts]
        nextjs-builder=nextjs_builder.cli:main
    """,
)
```

### Project Structure

Create the following directory structure:

```
nextjs-builder/
├── README.md
├── requirements.txt
├── setup.py
├── test.py
├── prompts/
│   └── __init__.py
└── src/
    ├── __init__.py
    ├── cli.py
    └── llm/
        └── __init__.py
```

## LangChain OpenRouter Integration

### src/llm/langchain_setup.py

```python
"""
LangChain and OpenRouter integration.
"""
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

def get_llm(model_name: str = "anthropic/claude-3-5-sonnet-20240620"):
    """
    Get a LangChain LLM using OpenRouter.
    
    Args:
        model_name: The OpenRouter model identifier
        
    Returns:
        A configured LangChain ChatOpenAI instance
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    llm = ChatOpenAI(
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        model_name=model_name,
    )
    
    return llm

def create_chain(prompt_template: str, llm=None, model_name: str = "anthropic/claude-3-5-sonnet-20240620") -> LLMChain:
    """
    Create a LangChain chain with the given prompt template.
    
    Args:
        prompt_template: The prompt template string
        llm: Optional pre-configured LLM
        model_name: The model name to use if llm is not provided
        
    Returns:
        A configured LLMChain
    """
    if llm is None:
        llm = get_llm(model_name)
        
    prompt = PromptTemplate.from_template(prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain
```

### src/llm/prompt_manager.py

```python
"""
Manages prompt templates for the Next.js website builder.
"""
import os
from pathlib import Path
from typing import Dict, Optional, Any

# Base system prompt
SYSTEM_BASE_PROMPT = """
You are a Next.js and Tailwind CSS expert who creates high-quality, production-ready website code. You follow these principles:

1. Code Structure:
   - Use clean, modular component architecture
   - Follow Next.js App Router best practices
   - Implement SSR data fetching patterns for optimal performance
   - Use TypeScript with proper typing

2. Styling:
   - Use core Tailwind CSS exclusively (no component libraries)
   - Create responsive designs that work across all devices
   - Follow accessibility best practices
   - Maintain consistent styling patterns

3. State Management:
   - Use React Context API for app-wide state
   - Implement React Query for data fetching and server state
   - Create custom hooks for reusable logic
   - Keep components focused and single-purpose

Your task is to generate code for a website based on the user's requirements.
"""

def load_prompt_template(template_name: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        template_name: The name of the template file (without .txt extension)
        
    Returns:
        The prompt template as a string
    """
    base_dir = Path(__file__).parent.parent.parent
    prompts_dir = base_dir / "prompts"
    
    template_path = prompts_dir / f"{template_name}.txt"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template '{template_name}' not found")
    
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    return template

def get_component_prompt(component_type: str, requirements: Dict[str, Any]) -> str:
    """
    Get a prompt for generating a component.
    
    Args:
        component_type: The type of component to generate
        requirements: Dictionary of component requirements
        
    Returns:
        A prompt for generating the component
    """
    base_prompt = load_prompt_template("component_base")
    
    # Format the requirements as bullet points
    formatted_requirements = "\n".join([f"- {key}: {value}" for key, value in requirements.items()])
    
    prompt = base_prompt.format(
        component_type=component_type,
        requirements=formatted_requirements
    )
    
    return SYSTEM_BASE_PROMPT + "\n\n" + prompt

def get_page_prompt(page_type: str, requirements: Dict[str, Any]) -> str:
    """
    Get a prompt for generating a page.
    
    Args:
        page_type: The type of page to generate
        requirements: Dictionary of page requirements
        
    Returns:
        A prompt for generating the page
    """
    base_prompt = load_prompt_template("page_base")
    
    # Format the requirements as bullet points
    formatted_requirements = "\n".join([f"- {key}: {value}" for key, value in requirements.items()])
    
    prompt = base_prompt.format(
        page_type=page_type,
        requirements=formatted_requirements
    )
    
    return SYSTEM_BASE_PROMPT + "\n\n" + prompt
```

## CLI Interface

### test.py (Main Entry Point)

```python
#!/usr/bin/env python3
"""
Main entry point for the Next.js website builder CLI.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import main

if __name__ == "__main__":
    main()
```

### src/cli.py

```python
"""
Command-line interface for the Next.js website builder.
"""
import os
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from src.installer.nextjs_installer import create_nextjs_project
from src.llm.langchain_setup import get_llm, create_chain
from src.llm.prompt_manager import SYSTEM_BASE_PROMPT

console = Console()

@click.command()
@click.argument("description")
@click.option("--template", "-t", type=click.Choice(["general", "blog", "ecommerce", "portfolio"]), 
              default="general", help="Website template to use")
@click.option("--auth/--no-auth", default=False, help="Include authentication")
@click.option("--db", type=click.Choice(["none", "mongodb", "postgres", "supabase"]), 
              default="none", help="Database integration")
@click.option("--output", "-o", default="./website", help="Output directory")
def main(description: str, template: str, auth: bool, db: str, output: str):
    """
    Build a Next.js website based on the provided description.
    
    DESCRIPTION is a text describing the website you want to build.
    """
    console.print(Panel(f"[bold green]Next.js Website Builder[/bold green]"))
    console.print(f"Description: {description}")
    console.print(f"Template: {template}")
    console.print(f"Authentication: {'Yes' if auth else 'No'}")
    console.print(f"Database: {db}")
    console.print(f"Output directory: {output}")
    
    # Ensure environment variables are set
    check_environment()
    
    with Progress() as progress:
        # Step 1: Create Next.js project
        task1 = progress.add_task("[cyan]Creating Next.js project...", total=1)
        create_nextjs_project(output)
        progress.update(task1, completed=1)
        
        # Step 2: Generate website code
        task2 = progress.add_task("[cyan]Generating website code...", total=1)
        # This will be implemented later
        progress.update(task2, completed=1)
        
        # Step 3: Install dependencies
        task3 = progress.add_task("[cyan]Installing dependencies...", total=1)
        # This will be implemented later
        progress.update(task3, completed=1)
        
    console.print(Panel("[bold green]Website created successfully![/bold green]"))
    console.print(f"To run your website, navigate to the output directory and run:")
    console.print(f"[bold]cd {output} && npm run dev[/bold]")

def check_environment():
    """
    Check if required environment variables are set.
    """
    required_vars = ["OPENROUTER_API_KEY", "OPENROUTER_BASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        console.print(f"[bold red]Error:[/bold red] The following environment variables are missing:")
        for var in missing_vars:
            console.print(f"- {var}")
        console.print("\nPlease set these variables in a .env file or in your environment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Next.js Project Installation

### src/installer/nextjs_installer.py

```python
"""
Next.js project installation utilities.
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

def create_nextjs_project(output_dir: str) -> bool:
    """
    Create a new Next.js project with the specified options.
    
    Args:
        output_dir: The directory to create the project in
        
    Returns:
        True if the project was created successfully
    """
    output_path = Path(output_dir).resolve()
    
    # Create the output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build the command
    cmd = [
        "npx", 
        "create-next-app@latest",
        str(output_path),
        "--typescript",
        "--eslint",
        "--tailwind",
        "--app",
        "--no-src-dir",
        "--no-import-alias"
    ]
    
    try:
        # Run the command
        process = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        # If we get here, the command was successful
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating Next.js project: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return False

def install_dependencies(project_dir: str, dependencies: List[str], dev: bool = False) -> bool:
    """
    Install npm dependencies in the project.
    
    Args:
        project_dir: The project directory
        dependencies: List of dependencies to install
        dev: Whether to install as dev dependencies
        
    Returns:
        True if the dependencies were installed successfully
    """
    cmd = ["npm", "install"]
    
    if dev:
        cmd.append("--save-dev")
        
    cmd.extend(dependencies)
    
    try:
        subprocess.run(
            cmd,
            check=True,
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return False

def setup_react_query(project_dir: str) -> bool:
    """
    Set up React Query in the project.
    
    Args:
        project_dir: The project directory
        
    Returns:
        True if React Query was set up successfully
    """
    # Install React Query
    dependencies = ["@tanstack/react-query"]
    return install_dependencies(project_dir, dependencies)
```

## Prompt Templates

### prompts/component_base.txt

```
You are a Next.js component expert. Create a {component_type} component with the following requirements:

{requirements}

Please provide the complete TypeScript code for this component using Tailwind CSS for styling.
The component should be responsive, accessible, and follow modern React best practices.
Include detailed comments explaining the component's functionality.

IMPORTANT RULES:
- Use only core Tailwind CSS for styling (no component libraries)
- Follow accessibility best practices (proper ARIA attributes, semantic HTML)
- Include TypeScript typing for all props
- Include proper error handling
- Keep the component focused on a single responsibility
```

### prompts/page_base.txt

```
You are a Next.js page expert. Create a {page_type} page with the following requirements:

{requirements}

Please provide the complete TypeScript code for this page using Next.js App Router and Tailwind CSS for styling.
The page should use Server-Side Rendering (SSR) for optimal SEO performance.

IMPORTANT RULES:
- Use Next.js App Router with TypeScript
- Implement SSR data fetching patterns
- Use only core Tailwind CSS for styling (no component libraries)
- Follow accessibility best practices
- Include loading and error states
- Keep the code modular and maintainable
```

## Next Steps for Implementation

After setting up these initial files, you should:

1. Implement template generators for each website type (general, blog, e-commerce, portfolio)
2. Create the component generation system
3. Implement the page generation system
4. Add state management generation
5. Implement auxiliary features (authentication, database integration)
6. Add validation and self-healing capabilities

When ready for implementation, switch to Code mode and start by creating these core files.