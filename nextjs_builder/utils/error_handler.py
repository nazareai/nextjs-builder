"""
Error handling for Next.js & Tailwind website builder.

This module provides error handling utilities and custom exceptions.
"""
import sys
import traceback
from typing import Dict, Any, List, Optional, Union, Type

from rich.console import Console
from rich.panel import Panel

# Initialize console for pretty output
console = Console()


class WebsiteBuilderError(Exception):
    """Base exception for all website builder errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Optional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ConfigError(WebsiteBuilderError):
    """Exception raised for configuration errors."""
    pass


class InstallationError(WebsiteBuilderError):
    """Exception raised for installation errors."""
    pass


class ValidationError(WebsiteBuilderError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, issues: List[str], details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            issues: List of specific validation issues
            details: Optional additional details
        """
        self.issues = issues
        super().__init__(message, details)


class LLMError(WebsiteBuilderError):
    """Exception raised for LLM API errors."""
    pass


class TemplateError(WebsiteBuilderError):
    """Exception raised for template errors."""
    pass


class FileOperationError(WebsiteBuilderError):
    """Exception raised for file operation errors."""
    pass


def print_error(
    error: Exception, 
    verbose: bool = False,
    exit_program: bool = False,
    exit_code: int = 1
) -> None:
    """
    Print an error message to the console.
    
    Args:
        error: The exception to print
        verbose: Whether to print verbose error information
        exit_program: Whether to exit the program after printing
        exit_code: The exit code to use if exiting
    """
    error_type = error.__class__.__name__
    
    if isinstance(error, WebsiteBuilderError):
        console.print(
            Panel(
                f"[bold red]{error_type}:[/bold red] {error.message}",
                border_style="red",
                title="Error",
                padding=(1, 2)
            )
        )
        
        if hasattr(error, "issues") and error.issues:
            console.print("[bold red]Issues:[/bold red]")
            for issue in error.issues:
                console.print(f"  • {issue}")
        
        if error.details and verbose:
            console.print("[bold red]Details:[/bold red]")
            console.print(error.details)
    else:
        console.print(
            Panel(
                f"[bold red]{error_type}:[/bold red] {str(error)}",
                border_style="red",
                title="Error",
                padding=(1, 2)
            )
        )
    
    if verbose:
        console.print("[bold red]Traceback:[/bold red]")
        console.print_exception()
    
    if exit_program:
        sys.exit(exit_code)


def handle_exception(
    func: callable,
    *args,
    error_types: Optional[List[Type[Exception]]] = None,
    verbose: bool = False,
    exit_on_error: bool = False,
    **kwargs
) -> Any:
    """
    Handle exceptions in a function call.
    
    Args:
        func: The function to call
        *args: Arguments to pass to the function
        error_types: Types of exceptions to catch
        verbose: Whether to print verbose error information
        exit_on_error: Whether to exit the program on error
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The return value of the function or None if an exception was caught
    """
    error_types = error_types or [Exception]
    
    try:
        return func(*args, **kwargs)
    except tuple(error_types) as e:
        print_error(e, verbose, exit_on_error)
        return None


def safe_function(
    error_types: Optional[List[Type[Exception]]] = None,
    verbose: bool = False,
    exit_on_error: bool = False
) -> callable:
    """
    Decorator to handle exceptions in a function.
    
    Args:
        error_types: Types of exceptions to catch
        verbose: Whether to print verbose error information
        exit_on_error: Whether to exit the program on error
        
    Returns:
        Decorated function
    """
    def decorator(func: callable) -> callable:
        def wrapper(*args, **kwargs) -> Any:
            return handle_exception(
                func,
                *args,
                error_types=error_types,
                verbose=verbose,
                exit_on_error=exit_on_error,
                **kwargs
            )
        return wrapper
    return decorator


def try_operation(
    operation_name: str,
    func: callable,
    *args,
    error_types: Optional[List[Type[Exception]]] = None,
    verbose: bool = False,
    exit_on_error: bool = False,
    **kwargs
) -> Any:
    """
    Try an operation and handle exceptions.
    
    Args:
        operation_name: Name of the operation for display
        func: The function to call
        *args: Arguments to pass to the function
        error_types: Types of exceptions to catch
        verbose: Whether to print verbose error information
        exit_on_error: Whether to exit the program on error
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The return value of the function or None if an exception was caught
    """
    error_types = error_types or [Exception]
    
    try:
        result = func(*args, **kwargs)
        console.print(f"[green]✓[/green] {operation_name} completed successfully")
        return result
    except tuple(error_types) as e:
        console.print(f"[bold red]✗[/bold red] {operation_name} failed")
        print_error(e, verbose, exit_on_error)
        return None


def get_error_suggestions(error: Exception) -> List[str]:
    """
    Get suggestions for fixing an error.
    
    Args:
        error: The exception to get suggestions for
        
    Returns:
        List of suggestions
    """
    suggestions = []
    error_message = str(error).lower()
    
    # Node.js/npm related errors
    if "node" in error_message or "npm" in error_message:
        suggestions.append("Make sure Node.js (v14+) and npm are installed and available in your PATH")
        suggestions.append("Try running 'node --version' and 'npm --version' to check your installation")
        suggestions.append("If Node.js is installed but the commands aren't found, you may need to restart your terminal")
        
    # File permissions
    if "permission" in error_message or "access" in error_message:
        suggestions.append("Check that you have the necessary permissions to write to the output directory")
        suggestions.append("Try running the command with administrator privileges")
        
    # Network errors
    if "network" in error_message or "connection" in error_message or "timeout" in error_message:
        suggestions.append("Check your internet connection")
        suggestions.append("If you're behind a proxy or firewall, make sure it allows connections to npm and OpenRouter")
        
    # API errors
    if "api" in error_message or "openrouter" in error_message:
        suggestions.append("Verify that your OPENROUTER_API_KEY environment variable is correctly set")
        suggestions.append("Check that you have sufficient API credits and aren't hitting rate limits")
        
    # TypeScript/ESLint errors
    if "typescript" in error_message or "eslint" in error_message or "parsing" in error_message:
        suggestions.append("There might be issues with the generated code. Try inspecting the error messages for clues")
        suggestions.append("Run 'npx tsc --noEmit' in the project directory to check for TypeScript errors")
        
    # If no specific suggestions, provide general ones
    if not suggestions:
        suggestions.append("Check the error message for clues about what went wrong")
        suggestions.append("Ensure all prerequisites are installed and environment variables are set")
        suggestions.append("Try running the command with the --verbose flag for more information")
        
    return suggestions


def print_error_with_suggestions(
    error: Exception,
    verbose: bool = False,
    exit_program: bool = False
) -> None:
    """
    Print an error message with suggestions for fixing it.
    
    Args:
        error: The exception to print
        verbose: Whether to print verbose error information
        exit_program: Whether to exit the program after printing
    """
    print_error(error, verbose, exit_program=False)
    
    suggestions = get_error_suggestions(error)
    if suggestions:
        console.print("\n[bold yellow]Suggestions to fix the issue:[/bold yellow]")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"  {i}. {suggestion}")
        
    if exit_program:
        sys.exit(1)