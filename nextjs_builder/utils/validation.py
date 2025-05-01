"""
Validation utilities for Next.js & Tailwind website builder.

This module provides validation functions for checking generated code.
"""
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

from rich.console import Console

# Initialize console for pretty output
console = Console()


class ValidationError(Exception):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, issues: List[str]):
        self.message = message
        self.issues = issues
        super().__init__(f"{message}: {', '.join(issues)}")


def validate_typescript(file_path: Union[str, Path], timeout: int = 10) -> Tuple[bool, List[str]]:
    """
    Validate TypeScript code in a file using the TypeScript compiler.
    
    Args:
        file_path: Path to the TypeScript file
        timeout: Timeout in seconds for TypeScript validation
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    try:
        # Check if the file exists
        if not Path(file_path).exists():
            return False, ["File does not exist"]
        
        # Run TypeScript compiler to check types - with timeout
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", str(file_path)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                # Parse error messages
                error_lines = result.stderr.strip().split("\n")
                return False, [line for line in error_lines if line.strip()]
            
            return True, []
        except subprocess.TimeoutExpired:
            # If TypeScript validation times out, we'll skip detailed validation
            console.print(f"[yellow]TypeScript validation timed out for {file_path}. Skipping detailed validation.[/yellow]")
            return True, ["TypeScript validation timed out. Continuing with basic validation."]
    except Exception as e:
        return False, [f"Error validating TypeScript: {e}"]


def validate_eslint(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate JavaScript/TypeScript code in a file using ESLint.
    
    Args:
        file_path: Path to the JavaScript/TypeScript file
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    try:
        # Check if the file exists
        if not Path(file_path).exists():
            return False, ["File does not exist"]
        
        # Run ESLint to check code quality
        result = subprocess.run(
            ["npx", "eslint", "--no-eslintrc", "--format", "json", str(file_path)],
            capture_output=True,
            text=True
        )
        
        # Parse the JSON output
        if result.stdout:
            try:
                eslint_results = json.loads(result.stdout)
                
                # Check if there are any messages
                if eslint_results and eslint_results[0].get("messages"):
                    issues = []
                    
                    for message in eslint_results[0]["messages"]:
                        line = message.get("line", 0)
                        column = message.get("column", 0)
                        msg = message.get("message", "Unknown issue")
                        severity = "Error" if message.get("severity") == 2 else "Warning"
                        
                        issues.append(f"{severity} at line {line}, column {column}: {msg}")
                    
                    if any(issue.startswith("Error") for issue in issues):
                        return False, issues
                    else:
                        # Only warnings, consider it valid but report the warnings
                        return True, issues
                
                # No messages, consider it valid
                return True, []
            except json.JSONDecodeError:
                # If the JSON parsing fails, check if there were any errors
                if result.returncode != 0:
                    return False, [result.stderr.strip()]
                else:
                    return True, []
        else:
            # No output, check if there were any errors
            if result.returncode != 0:
                return False, [result.stderr.strip()]
            else:
                return True, []
    except Exception as e:
        return False, [f"Error validating with ESLint: {e}"]


def validate_next_js_page(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate a Next.js page file.
    
    Args:
        file_path: Path to the Next.js page file
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        # Check if the file exists
        if not Path(file_path).exists():
            return False, ["File does not exist"]
        
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for default export
        if not re.search(r'export\s+default\s+function', content):
            issues.append("Missing default export function")
        
        # For App Router, check for proper metadata export if not a client component
        if not content.startswith("'use client'") and "page.tsx" in str(file_path):
            if not re.search(r'export\s+const\s+metadata', content):
                issues.append("Missing metadata export in server component page")
        
        # Check for proper imports
        if "React" in content and not re.search(r'import\s+React', content):
            issues.append("Using React without importing it")
        
        # Run TypeScript validation
        ts_valid, ts_issues = validate_typescript(file_path)
        if not ts_valid:
            issues.extend(ts_issues)
        
        # Check for accessibility issues (basic checks)
        if "<img" in content and not re.search(r'<img[^>]+alt=', content):
            issues.append("Image without alt attribute")
        
        # Check for bad practices
        if "document.getElementById" in content and "'use client'" not in content:
            issues.append("Using document in a server component")
        
        if "useState" in content and "'use client'" not in content:
            issues.append("Using useState in a server component")
        
        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Error validating Next.js page: {e}"]


def validate_next_js_component(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate a Next.js component file.
    
    Args:
        file_path: Path to the Next.js component file
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        # Check if the file exists
        if not Path(file_path).exists():
            return False, ["File does not exist"]
        
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for default export
        if not re.search(r'export\s+default\s+function', content) and not re.search(r'export\s+default\s+\w+', content):
            issues.append("Missing default export")
        
        # Check prop types with TypeScript interface or type
        if not re.search(r'interface\s+\w+Props', content) and not re.search(r'type\s+\w+Props', content):
            issues.append("Missing TypeScript props interface/type")
        
        # Check for proper imports
        if "React" in content and not re.search(r'import\s+React', content):
            issues.append("Using React without importing it")
        
        # Run TypeScript validation
        ts_valid, ts_issues = validate_typescript(file_path)
        if not ts_valid:
            issues.extend(ts_issues)
        
        # Check for accessibility issues (basic checks)
        if "<img" in content and not re.search(r'<img[^>]+alt=', content):
            issues.append("Image without alt attribute")
        
        if "<button" in content and not re.search(r'<button[^>]+type=', content):
            issues.append("Button without type attribute")
        
        # Check for bad practices
        if "document.getElementById" in content and "'use client'" not in content:
            issues.append("Using document in a server component")
        
        if "useState" in content and "'use client'" not in content:
            issues.append("Using useState in a server component")
        
        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Error validating Next.js component: {e}"]


def validate_tailwind_usage(file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate Tailwind CSS usage in a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        # Check if the file exists
        if not Path(file_path).exists():
            return False, ["File does not exist"]
        
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for inline styles (should use Tailwind instead)
        if re.search(r'style={{', content) or re.search(r'style=\{', content):
            issues.append("Using inline styles instead of Tailwind classes")
        
        # Check for CSS/SCSS imports (should use Tailwind instead)
        if re.search(r'import\s+[\'"].*\.css[\'"]', content) or re.search(r'import\s+[\'"].*\.scss[\'"]', content):
            # Ignore global CSS import in layout
            if "layout.tsx" not in str(file_path) or not re.search(r'import\s+[\'"](\.\/)?globals\.css[\'"]', content):
                issues.append("Importing CSS/SCSS files instead of using Tailwind")
        
        # Check for proper className usage
        if re.search(r'className=[\'"][^\'"]+ [^\'"]+[\'"]', content) and not re.search(r'className={`', content):
            # Multiple classes should use string interpolation or join
            if not re.search(r'className={\s*[\w\s]*\.join\(', content):
                issues.append("Multiple Tailwind classes should use template literals or className={...}")
        
        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Error validating Tailwind usage: {e}"]


def validate_project_structure(project_dir: Union[str, Path]) -> Tuple[bool, List[str]]:
    """
    Validate the Next.js project structure.
    
    Args:
        project_dir: Path to the Next.js project directory
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    issues = []
    project_path = Path(project_dir)
    
    try:
        # Check for essential files
        essential_files = [
            "package.json",
            "tsconfig.json",
            "tailwind.config.js",
            "app/layout.tsx",
            "app/page.tsx",
        ]
        
        for file in essential_files:
            if not (project_path / file).exists():
                issues.append(f"Missing essential file: {file}")
        
        # Check for proper App Router structure
        if not (project_path / "app").is_dir():
            issues.append("Missing app directory, required for App Router")
        
        # Check for next.config.js
        if not (project_path / "next.config.js").exists() and not (project_path / "next.config.ts").exists():
            issues.append("Missing next.config.js/ts file")
        
        # Check package.json for Next.js dependency
        if (project_path / "package.json").exists():
            with open(project_path / "package.json", "r", encoding="utf-8") as f:
                package_data = json.load(f)
                
                if "dependencies" not in package_data or "next" not in package_data["dependencies"]:
                    issues.append("Next.js dependency not found in package.json")
                
                if "dependencies" not in package_data or "react" not in package_data["dependencies"]:
                    issues.append("React dependency not found in package.json")
                
                if "scripts" not in package_data or "dev" not in package_data["scripts"]:
                    issues.append("Missing 'dev' script in package.json")
        
        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Error validating project structure: {e}"]


def validate_website(project_dir: Union[str, Path], verbose: bool = False, max_files: int = 50) -> Dict[str, Any]:
    """
    Validate the entire Next.js website.
    
    Args:
        project_dir: Path to the Next.js project directory
        verbose: Whether to print verbose output
        max_files: Maximum number of files to validate to prevent performance issues
        
    Returns:
        A dictionary with validation results
    """
    project_path = Path(project_dir)
    results = {
        "valid": True,
        "structure": {
            "valid": True,
            "issues": []
        },
        "pages": {
            "valid": True,
            "issues": {}
        },
        "components": {
            "valid": True,
            "issues": {}
        },
        "tailwind": {
            "valid": True,
            "issues": {}
        }
    }
    
    # Print status for better user feedback
    if verbose:
        console.print("Validating project structure...")
    
    # Validate project structure
    structure_valid, structure_issues = validate_project_structure(project_path)
    results["structure"]["valid"] = structure_valid
    results["structure"]["issues"] = structure_issues
    
    if not structure_valid:
        results["valid"] = False
    
    # Print status update
    if verbose:
        console.print("Validating pages...")
    
    # Validate pages
    page_files = []
    
    # Find all page.tsx files, with limit
    for page_file in project_path.glob("app/**/page.tsx"):
        page_files.append(page_file)
        if len(page_files) >= max_files:
            console.print(f"[yellow]Warning: Reached maximum file limit ({max_files}). Skipping remaining page files.[/yellow]")
            break
    
    # Add the root page
    root_page = project_path / "app" / "page.tsx"
    if root_page.exists() and root_page not in page_files and len(page_files) < max_files:
        page_files.append(root_page)
    
    # Process pages with progress updates
    total_pages = len(page_files)
    for i, page_file in enumerate(page_files):
        if verbose and i % 5 == 0:  # Update every 5 files
            console.print(f"Validating page {i+1}/{total_pages}: {page_file.relative_to(project_path)}")
            
        relative_path = page_file.relative_to(project_path)
        page_valid, page_issues = validate_next_js_page(page_file)
        
        if not page_valid:
            results["pages"]["valid"] = False
            results["valid"] = False
            results["pages"]["issues"][str(relative_path)] = page_issues
        
        # Also validate Tailwind usage
        tw_valid, tw_issues = validate_tailwind_usage(page_file)
        if not tw_valid:
            results["tailwind"]["valid"] = False
            results["valid"] = False
            results["tailwind"]["issues"][str(relative_path)] = tw_issues
    
    # Print status update
    if verbose:
        console.print("Validating components...")
    
    # Validate components
    component_files = []
    
    # Find component files, with limit
    for ext in ["tsx", "jsx"]:
        component_files.extend(list(project_path.glob(f"app/components/**/*.{ext}"))[:max_files//2])
        component_files.extend(list(project_path.glob(f"components/**/*.{ext}"))[:max_files//2])
        if len(component_files) >= max_files:
            console.print(f"[yellow]Warning: Reached maximum file limit ({max_files}). Skipping remaining component files.[/yellow]")
            break
    
    # Process components with progress updates
    total_components = len(component_files)
    for i, component_file in enumerate(component_files):
        if verbose and i % 5 == 0:  # Update every 5 files
            console.print(f"Validating component {i+1}/{total_components}: {component_file.relative_to(project_path)}")
            
        relative_path = component_file.relative_to(project_path)
        comp_valid, comp_issues = validate_next_js_component(component_file)
        
        if not comp_valid:
            results["components"]["valid"] = False
            results["valid"] = False
            results["components"]["issues"][str(relative_path)] = comp_issues
        
        # Also validate Tailwind usage
        tw_valid, tw_issues = validate_tailwind_usage(component_file)
        if not tw_valid:
            results["tailwind"]["valid"] = False
            results["valid"] = False
            results["tailwind"]["issues"][str(relative_path)] = tw_issues
    
    if verbose:
        console.print("Website validation complete.")
        
    return results


def fix_common_issues(file_path: Union[str, Path], issues: List[str]) -> bool:
    """
    Attempt to fix common issues in a file.
    
    Args:
        file_path: Path to the file
        issues: List of issues to fix
        
    Returns:
        True if any fixes were applied, False otherwise
    """
    try:
        # Check if the file exists
        if not Path(file_path).exists():
            return False
        
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        modified = False
        
        # Fix missing React import
        if "Using React without importing it" in " ".join(issues) and "React" in content and not re.search(r'import\s+React', content):
            content = "import React from 'react';\n" + content
            modified = True
        
        # Fix missing alt attribute on images
        if "Image without alt attribute" in " ".join(issues):
            content = re.sub(r'(<img[^>]+)(?!alt=)([^>]*>)', r'\1 alt="Image" \2', content)
            modified = True
        
        # Fix missing type attribute on buttons
        if "Button without type attribute" in " ".join(issues):
            content = re.sub(r'(<button[^>]+)(?!type=)([^>]*>)', r'\1 type="button" \2', content)
            modified = True
        
        # Fix using document in a server component
        if "Using document in a server component" in " ".join(issues):
            content = "'use client';\n\n" + content
            modified = True
        
        # Fix using useState in a server component
        if "Using useState in a server component" in " ".join(issues):
            content = "'use client';\n\n" + content
            modified = True
        
        if modified:
            # Write the modified content back to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return True
        
        return False
    except Exception as e:
        console.print(f"[bold red]Error fixing issues in {file_path}:[/bold red] {e}")
        return False


def fix_project_issues(project_dir: Union[str, Path], validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt to fix issues in a project based on validation results.
    
    Args:
        project_dir: Path to the Next.js project directory
        validation_results: Validation results from validate_website
        
    Returns:
        Updated validation results
    """
    project_path = Path(project_dir)
    fixes_applied = False
    
    # Fix page issues
    for page_path, issues in validation_results["pages"]["issues"].items():
        if fix_common_issues(project_path / page_path, issues):
            console.print(f"[green]✓[/green] Fixed issues in {page_path}")
            fixes_applied = True
    
    # Fix component issues
    for component_path, issues in validation_results["components"]["issues"].items():
        if fix_common_issues(project_path / component_path, issues):
            console.print(f"[green]✓[/green] Fixed issues in {component_path}")
            fixes_applied = True
    
    # If fixes were applied, re-validate the website
    if fixes_applied:
        return validate_website(project_dir)
    
    return validation_results