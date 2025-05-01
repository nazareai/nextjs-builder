"""
Command-line interface for the Next.js & Tailwind website builder.

This module provides the CLI interface for generating Next.js websites
based on natural language descriptions.
"""
import os
import sys
from typing import Optional
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

from nextjs_builder.config import load_config, check_environment
from nextjs_builder.generator.website_builder import WebsiteBuilder
from nextjs_builder.templates.template_manager import get_template_manager
from nextjs_builder.utils.error_handler import print_error_with_suggestions

# Initialize Rich console for pretty output
console = Console()


@click.command()
@click.argument("description")
@click.option(
    "--template", "-t", 
    type=click.Choice(["general", "blog", "ecommerce", "portfolio"]), 
    default="general", 
    help="Website template to use"
)
@click.option(
    "--auth/--no-auth", 
    default=False, 
    help="Include authentication"
)
@click.option(
    "--db", 
    type=click.Choice(["none", "mongodb", "postgres", "supabase"]), 
    default="none", 
    help="Database integration"
)
@click.option(
    "--output", "-o", 
    default="./website", 
    help="Output directory for the generated website"
)
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose logging"
)
@click.option(
    "--skip-validation", 
    is_flag=True, 
    help="Skip validation and fixing steps which may take significant time"
)
@click.option(
    "--validation-timeout", 
    default=120,
    type=int,
    help="Maximum time in seconds for the validation process (default: 120)"
)
def main(
    description: str, 
    template: str, 
    auth: bool, 
    db: str, 
    output: str, 
    verbose: bool,
    skip_validation: bool,
    validation_timeout: int
) -> int:
    """
    Build a Next.js website based on the provided description.
    
    DESCRIPTION is a text describing the website you want to build.
    """
    try:
        # Display welcome message
        console.print(
            Panel.fit(
                "[bold blue]Next.js & Tailwind Website Builder[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            )
        )

        # Print parameters
        console.print(f"[bold]Description:[/bold] {description}")
        console.print(f"[bold]Template:[/bold] {template}")
        console.print(f"[bold]Authentication:[/bold] {'Enabled' if auth else 'Disabled'}")
        console.print(f"[bold]Database:[/bold] {db}")
        console.print(f"[bold]Output directory:[/bold] {output}")
        console.print("")
        
        # Information about automatic process
        console.print(
            Panel(
                "This is a fully automated process that will run without requiring input.\n"
                "The tool will create a Next.js project, generate code, and validate the result.\n"
                "You'll see progress updates throughout the process.\n\n"
                "[bold]Note:[/bold] This may take several minutes to complete, especially during validation.",
                title="Automated Website Generation",
                border_style="green",
                padding=(1, 2),
            )
        )
        
        # Information about automatic validation and fixing
        if not skip_validation:
            console.print(
                Panel(
                    "The generated website will be automatically validated and fixed for common issues "
                    "to ensure proper functionality. This includes TypeScript errors, React hooks usage, "
                    "and accessibility problems.\n\n"
                    f"A {validation_timeout} second timeout is set to ensure the validation process doesn't get stuck. "
                    "You can adjust this with the --validation-timeout option or skip validation entirely with --skip-validation.",
                    title="Automatic Validation",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
        else:
            console.print(
                Panel(
                    "Validation has been skipped with --skip-validation. The website will be generated without "
                    "checking for TypeScript errors, accessibility, or other issues.\n\n"
                    "You can run your own validation later with tools like ESLint and TypeScript.",
                    title="Validation Skipped",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )

        # Check environment variables and dependencies
        check_environment()

        # Load configuration
        config = load_config()
        
        # Get template manager and verify template
        template_manager = get_template_manager()
        available_templates = template_manager.get_template_names()
        
        if template not in available_templates:
            console.print(f"[bold red]Error:[/bold red] Template '{template}' not found.")
            console.print(f"Available templates: {', '.join(available_templates)}")
            return 1
        
        # Initialize the website builder
        builder = WebsiteBuilder(
            description=description,
            template_name=template,
            auth=auth,
            database=db if db != "none" else None,
            output_dir=output,
            verbose=verbose
        )
        
        # Generate the website
        success = builder.generate(skip_validation=skip_validation)
        
        if success:
            console.print(
                Panel(
                    f"[bold green]Website generated successfully![/bold green]\n\n"
                    f"To run your website:\n"
                    f"  cd {output}\n"
                    f"  npm run dev\n\n"
                    f"Then access your website at: [bold]http://localhost:3000[/bold]",
                    border_style="green",
                    padding=(1, 2),
                )
            )
            return 0
        else:
            console.print("[bold red]✗[/bold red] Website generation failed")
            console.print(
                "\nIf you encounter issues with the generated website, try the following:"
                "\n1. Make sure all required dependencies are installed"
                "\n2. Verify that Node.js and npm are properly configured"
                "\n3. Try running the generator with the --verbose flag for more details"
                "\n4. Use --skip-validation to bypass validation if it's causing issues"
            )
            return 1

    except Exception as e:
        print_error_with_suggestions(e, verbose, exit_program=False)
        return 1


if __name__ == "__main__":
    sys.exit(main())