# Next.js & Tailwind Website Builder - Implementation Guide

This document serves as a comprehensive guide for implementing the Next.js and Tailwind website builder module from the architectural design to working code. It provides a roadmap for developers to follow when converting the design documents into a functional system.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Documentation Summary](#documentation-summary)
3. [Implementation Checklist](#implementation-checklist)
4. [Key Files Implementation](#key-files-implementation)
5. [Development Workflow](#development-workflow)
6. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
7. [Moving to Code Mode](#moving-to-code-mode)

## Project Overview

The Next.js & Tailwind Website Builder is a Python module that generates customized websites using:

- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS (core only, no component libraries)
- LangChain for AI integration
- OpenRouter with Claude-3.5-Sonnet

The module accepts natural language descriptions of websites and generates complete, production-ready code through a CLI interface.

## Documentation Summary

We've created a comprehensive set of design documents:

| Document | Purpose | Key Sections |
|----------|---------|--------------|
| [README.md](./README.md) | Project overview and getting started | Features, installation, usage examples |
| [nextjs-builder-plan.md](./nextjs-builder-plan.md) | High-level architecture and plan | Project structure, architecture diagram |
| [nextjs-builder-implementation.md](./nextjs-builder-implementation.md) | Detailed implementation specifications | Code structure, key modules |
| [nextjs-builder-prompts.md](./nextjs-builder-prompts.md) | LLM prompt templates | System prompts, specialized prompts |
| [nextjs-builder-api-design.md](./nextjs-builder-api-design.md) | API specifications | Class definitions, interfaces |
| [nextjs-builder-roadmap.md](./nextjs-builder-roadmap.md) | Development phases and future plans | Implementation phases, future features |
| [nextjs-builder-testing.md](./nextjs-builder-testing.md) | Testing strategy | Test types, validation criteria |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines | Development workflow, standards |

## Implementation Checklist

Follow this checklist to implement the module in a systematic manner:

### Phase 1: Foundation Setup

- [ ] Initialize project structure
- [ ] Create setup.py and requirements.txt
- [ ] Set up basic CLI interface (test.py)
- [ ] Implement configuration management
- [ ] Create LangChain OpenRouter integration
- [ ] Set up logging and error handling

### Phase 2: Next.js Installation

- [ ] Implement Next.js project creation
- [ ] Create post-installation setup
- [ ] Add dependency management
- [ ] Set up basic file structure generation
- [ ] Implement configuration file generation

### Phase 3: Prompt System

- [ ] Create prompt template management system
- [ ] Implement system prompt handling
- [ ] Set up component-specific prompts
- [ ] Create page-specific prompts
- [ ] Implement template-specific prompts
- [ ] Add prompt variable substitution

### Phase 4: Code Generation

- [ ] Implement component generation logic
- [ ] Create page generation logic
- [ ] Set up state management generation
- [ ] Implement project structure generation
- [ ] Add code formatting and optimization
- [ ] Create validation system

### Phase 5: Templates

- [ ] Implement general website template
- [ ] Create blog website template
- [ ] Implement e-commerce template
- [ ] Create portfolio template
- [ ] Add template customization logic
- [ ] Implement template selection

### Phase 6: Optional Features

- [ ] Implement authentication integration
- [ ] Create database connection setup
- [ ] Add image optimization handling
- [ ] Implement responsive design utilities
- [ ] Create SEO optimization helpers

### Phase 7: Testing & Documentation

- [ ] Set up testing framework
- [ ] Write unit tests
- [ ] Create integration tests
- [ ] Implement end-to-end tests
- [ ] Add code examples
- [ ] Complete documentation

## Key Files Implementation

This section provides guidance on implementing the most critical files in the system.

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
from src.generator.website_builder import WebsiteBuilder

console = Console()

@click.command()
@click.argument("description")
@click.option("--template", "-t", type=click.Choice(["general", "blog", "ecommerce", "portfolio"]), 
              default="general", help="Website template to use")
@click.option("--auth/--no-auth", default=False, help="Include authentication")
@click.option("--db", type=click.Choice(["none", "mongodb", "postgres", "supabase"]), 
              default="none", help="Database integration")
@click.option("--output", "-o", default="./website", help="Output directory")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(description: str, template: str, auth: bool, db: str, output: str, verbose: bool):
    """
    Build a Next.js website based on the provided description.
    
    DESCRIPTION is a text describing the website you want to build.
    """
    # Implementation here
    pass

if __name__ == "__main__":
    main()
```

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

# Implementation here
```

### src/generator/website_builder.py

```python
"""
Main website builder class for generating Next.js websites.
"""
from typing import Dict, Any, List, Optional
import os
import subprocess
from pathlib import Path

from src.llm.langchain_setup import get_llm, create_chain
from src.installer.nextjs_installer import create_nextjs_project
from src.templates.template_manager import TemplateManager

class WebsiteBuilder:
    """
    Main class for building Next.js websites based on descriptions.
    """
    # Implementation here
```

## Development Workflow

Follow this workflow when implementing the module:

1. **Begin with Core Infrastructure**
   - Start with project setup and configuration
   - Implement basic CLI interface
   - Set up LangChain integration with OpenRouter

2. **Implement in Small, Testable Increments**
   - Add features one at a time
   - Write tests for each component
   - Verify functionality before moving to the next feature

3. **Use Test-Driven Development**
   - Write tests before implementing features
   - Run tests frequently to catch issues early
   - Use the test suite to validate your implementation

4. **Track Progress with the Checklist**
   - Use the implementation checklist to track progress
   - Mark items as complete as you finish them
   - Periodically reassess priorities based on progress

## Debugging and Troubleshooting

### Common Issues

1. **LLM API Connection Problems**
   - Check API keys and environment variables
   - Verify network connectivity
   - Examine API response for error messages

2. **Next.js Installation Failures**
   - Verify Node.js and npm versions
   - Check for permissions issues
   - Look for conflicting dependencies

3. **Code Generation Errors**
   - Examine LLM responses for unexpected formats
   - Check prompt templates for issues
   - Verify that generated code is valid TypeScript

4. **Template Application Problems**
   - Validate template selection logic
   - Check file paths and references
   - Verify that template components are properly linked

### Debugging Tools

- Use the `--verbose` flag for detailed logging
- Examine generated code and intermediate files
- Use breakpoints and logging in key processing steps
- Test components in isolation

## Moving to Code Mode

When you're ready to transition from architecture planning to implementation:

1. **Switch to Code Mode**
   - Use the `switch_mode` tool to transition to Code mode
   - This will allow you to create and edit actual Python files

2. **Implement Core Files First**
   - Start with the essential files outlined above
   - Build the foundation before adding complex features

3. **Follow a Modular Approach**
   - Implement one module at a time
   - Test each module thoroughly before moving on
   - Use the implementation checklist to guide your work

4. **Iterate Based on Testing**
   - Run tests frequently
   - Refine implementations based on test results
   - Address issues as they arise

## Starting Implementation

To begin implementing the module, follow these steps:

1. **Create the basic project structure**
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

2. **Implement setup.py and requirements.txt**
   - Define dependencies and package metadata
   - Set up entry points and package configuration

3. **Create the basic CLI interface**
   - Implement command-line argument parsing
   - Add basic error handling and logging

4. **Set up LangChain integration**
   - Implement OpenRouter connection
   - Create prompt template handling

5. **Implement Next.js project creation**
   - Create functions to run npx commands
   - Add post-installation setup

6. **Continue with code generation components**
   - Follow the implementation checklist
   - Build out remaining functionality

By following this implementation guide, you can systematically convert the architectural design into working code while maintaining a clear focus on the project's goals and requirements.