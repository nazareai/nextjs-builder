"""
Configuration module for the Next.js & Tailwind website builder.

This module handles loading configuration from files and environment variables,
as well as checking for required dependencies and environment setup.
"""
import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

import dotenv
from rich.console import Console

# Initialize console for pretty output
console = Console()

# Default configuration values
DEFAULT_CONFIG = {
    "llm": {
        "model": "anthropic/claude-3.5-sonnet-20240620",
        "temperature": 0.7,
        "max_tokens": 2000,
        "retry_attempts": 3
    },
    "templates": {
        "default": "general",
        "custom_templates_dir": "./custom-templates"
    },
    "installation": {
        "node_version": ">=14.0.0",
        "npm_version": ">=7.0.0",
        "default_dependencies": [
            "@tanstack/react-query",
            "next",
            "react",
            "react-dom"
        ]
    },
    "validation": {
        "run_eslint": True,
        "run_typescript_check": True
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file and/or environment variables.
    
    Args:
        config_path: Path to the configuration file (optional)
        
    Returns:
        Dictionary containing the configuration
    """
    # Load .env file if it exists
    dotenv.load_dotenv()
    
    # Start with default configuration
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from config file if specified or if default exists
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = Path("nextjs-builder.config.json")
    
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                # Deep merge configs
                deep_merge(config, file_config)
            console.print(f"Loaded configuration from {config_file}")
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to load configuration file: {e}")
    
    # Override with environment variables
    if os.environ.get("OPENROUTER_API_KEY"):
        config["llm"]["api_key"] = os.environ.get("OPENROUTER_API_KEY")
    
    if os.environ.get("OPENROUTER_BASE_URL"):
        config["llm"]["base_url"] = os.environ.get("OPENROUTER_BASE_URL")
    
    if os.environ.get("NEXTJS_BUILDER_DEFAULT_TEMPLATE"):
        config["templates"]["default"] = os.environ.get("NEXTJS_BUILDER_DEFAULT_TEMPLATE")
    
    return config


def check_environment() -> bool:
    """
    Check if the required dependencies and environment variables are available.
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    # Check for required environment variables
    required_vars = ["OPENROUTER_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        console.print("[bold red]Error:[/bold red] Missing required environment variables:")
        for var in missing_vars:
            console.print(f"  - {var}")
        console.print("\nPlease set these variables in a .env file or in your environment.")
        sys.exit(1)
    
    # Check for Node.js and npm
    try:
        node_version = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        
        npm_version = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        
        console.print(f"[green]✓[/green] Node.js {node_version}")
        console.print(f"[green]✓[/green] npm {npm_version}")
    except subprocess.CalledProcessError:
        console.print("[bold red]Error:[/bold red] Node.js and npm are required.")
        console.print("Please install Node.js (version 14+) from https://nodejs.org/")
        sys.exit(1)
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] Node.js and npm are required.")
        console.print("Please install Node.js (version 14+) from https://nodejs.org/")
        sys.exit(1)
    
    return True


def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """
    Deep merge two dictionaries, modifying the target in place.
    
    Args:
        target: Target dictionary to merge into
        source: Source dictionary to merge from
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            deep_merge(target[key], value)
        else:
            target[key] = value


def get_project_root() -> Path:
    """
    Get the absolute path to the project root.
    
    Returns:
        Path object pointing to the project root
    """
    return Path(__file__).parent.parent.absolute()