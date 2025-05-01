"""
Next.js project installation utilities.

This module contains functions for creating and setting up Next.js projects
using npx create-next-app and configuring various options.
"""
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

from rich.console import Console

# Initialize console for pretty output
console = Console()


def create_nextjs_project(
    output_dir: str, 
    typescript: bool = True,
    eslint: bool = True,
    tailwind: bool = True,
    app_router: bool = True,
    src_dir: bool = False,
    import_alias: Optional[str] = None,
    timeout: int = 300,
) -> bool:
    """
    Create a new Next.js project with the specified options.
    
    Args:
        output_dir: The directory to create the project in
        typescript: Whether to use TypeScript
        eslint: Whether to use ESLint
        tailwind: Whether to use Tailwind CSS
        app_router: Whether to use App Router
        src_dir: Whether to use src directory
        import_alias: Custom import alias
        timeout: Maximum time to wait for the command to complete (in seconds)
        
    Returns:
        True if the project was created successfully, False otherwise
    """
    output_path = Path(output_dir).resolve()
    
    # Create the output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build the command with non-interactive options
    # Using --yes to skip all confirmation prompts
    cmd = [
        "npx", 
        "create-next-app@latest",
        str(output_path),
        "--yes"  # Skip all confirmation prompts
    ]
    
    # Add options
    if typescript:
        cmd.append("--typescript")
    else:
        cmd.append("--no-typescript")
    
    if eslint:
        cmd.append("--eslint")
    else:
        cmd.append("--no-eslint")
    
    if tailwind:
        cmd.append("--tailwind")
    else:
        cmd.append("--no-tailwind")
    
    if app_router:
        cmd.append("--app")
    else:
        cmd.append("--no-app")
    
    if src_dir:
        cmd.append("--src-dir")
    else:
        cmd.append("--no-src-dir")
    
    if import_alias is None:
        cmd.append("--no-import-alias")
    else:
        cmd.extend(["--import-alias", import_alias])
    
    console.print(f"Creating Next.js project with command: [dim]{' '.join(cmd)}[/dim]")
    console.print("[yellow]This may take a few minutes. Please wait...[/yellow]")
    
    try:
        # Set environment variable to force non-interactive mode
        env = os.environ.copy()
        env["CI"] = "true"  # This tells npm/npx to run in CI mode (non-interactive)
        
        # Run the command with a timeout
        process = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env  # Use modified environment with CI=true
        )
        
        # Success
        console.print("[green]✓[/green] Next.js project created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error creating Next.js project:[/bold red] {e}")
        console.print(f"Command output: {e.stdout}")
        console.print(f"Command error: {e.stderr}")
        return False
        
    except subprocess.TimeoutExpired:
        console.print(f"[bold red]Error:[/bold red] Command timed out after {timeout} seconds")
        return False
        
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        return False


def install_dependencies(
    project_dir: str, 
    dependencies: List[str], 
    dev: bool = False,
    timeout: int = 180
) -> bool:
    """
    Install npm dependencies in the project.
    
    Args:
        project_dir: The project directory
        dependencies: List of dependencies to install
        dev: Whether to install as dev dependencies
        timeout: Maximum time to wait for the command to complete (in seconds)
        
    Returns:
        True if the dependencies were installed successfully, False otherwise
    """
    if not dependencies:
        return True
    
    cmd = ["npm", "install"]
    
    if dev:
        cmd.append("--save-dev")
    
    cmd.extend(dependencies)
    
    console.print(f"Installing dependencies: [bold]{', '.join(dependencies)}[/bold]")
    
    try:
        # Set environment variable to force non-interactive mode
        env = os.environ.copy()
        env["CI"] = "true"  # This tells npm to run in CI mode (non-interactive)
        
        # Run the command
        process = subprocess.run(
            cmd,
            check=True,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env  # Use modified environment with CI=true
        )
        
        # Success
        console.print("[green]✓[/green] Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error installing dependencies:[/bold red] {e}")
        console.print(f"Command output: {e.stdout}")
        console.print(f"Command error: {e.stderr}")
        return False
        
    except subprocess.TimeoutExpired:
        console.print(f"[bold red]Error:[/bold red] Command timed out after {timeout} seconds")
        return False
        
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        return False


def setup_react_query(project_dir: str) -> bool:
    """
    Set up React Query in the project.
    
    Args:
        project_dir: The project directory
        
    Returns:
        True if React Query was set up successfully, False otherwise
    """
    # Install React Query
    dependencies = ["@tanstack/react-query"]
    success = install_dependencies(project_dir, dependencies)
    
    if not success:
        return False
    
    # Create React Query provider file
    provider_path = Path(project_dir) / "app" / "providers.tsx"
    
    provider_content = """'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
"""
    
    try:
        with open(provider_path, "w") as f:
            f.write(provider_content)
        
        # Update layout.tsx to use the provider
        layout_path = Path(project_dir) / "app" / "layout.tsx"
        
        if layout_path.exists():
            with open(layout_path, "r") as f:
                layout_content = f.read()
            
            # Simple string replacement - might need a more robust approach
            # for complex projects
            if "import { Providers } from './providers';" not in layout_content:
                layout_content = layout_content.replace(
                    "export default function RootLayout",
                    "import { Providers } from './providers';\n\nexport default function RootLayout"
                )
                
                layout_content = layout_content.replace(
                    "<body", 
                    "<Providers>\n      <body"
                )
                
                layout_content = layout_content.replace(
                    "</body>", 
                    "</body>\n    </Providers>"
                )
                
                with open(layout_path, "w") as f:
                    f.write(layout_content)
        
        console.print("[green]✓[/green] React Query set up successfully")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error setting up React Query:[/bold red] {e}")
        return False


def run_dev_server(project_dir: str) -> Optional[subprocess.Popen]:
    """
    Run the Next.js development server.
    
    Args:
        project_dir: The project directory
        
    Returns:
        The subprocess.Popen object representing the running server,
        or None if the server couldn't be started
    """
    try:
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to make sure the server starts
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is None:
            console.print("[green]✓[/green] Development server started")
            return process
        else:
            stdout, stderr = process.communicate()
            console.print(f"[bold red]Error starting development server:[/bold red]")
            console.print(f"Output: {stdout}")
            console.print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        console.print(f"[bold red]Error starting development server:[/bold red] {e}")
        return None


def setup_project_structure(project_dir: str, structure: Dict[str, Any]) -> bool:
    """
    Set up the project structure based on the provided structure definition.
    
    Args:
        project_dir: The project directory
        structure: A dictionary representing the project structure
        
    Returns:
        True if the structure was set up successfully, False otherwise
    """
    try:
        base_path = Path(project_dir)
        
        # Create directories
        for directory in structure.get("directories", []):
            dir_path = base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create files
        for file_info in structure.get("files", []):
            file_path = base_path / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(file_info["content"])
        
        console.print("[green]✓[/green] Project structure set up successfully")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error setting up project structure:[/bold red] {e}")
        return False