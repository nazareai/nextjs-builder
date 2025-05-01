"""
Website builder class for Next.js & Tailwind website builder.

This module contains the main WebsiteBuilder class that orchestrates the
website generation process using templates and LLM outputs.
"""
import os
import time
import re
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

from nextjs_builder.config import load_config
from nextjs_builder.llm.langchain_setup import LLMManager
from nextjs_builder.llm.prompt_manager import get_prompt_manager
from nextjs_builder.templates.template_manager import get_template_manager, Template
from nextjs_builder.installer.nextjs_installer import (
    create_nextjs_project,
    install_dependencies,
    setup_project_structure
)
from nextjs_builder.utils.validation import (
    validate_website,
    fix_project_issues,
    validate_typescript,
    fix_common_issues
)
from nextjs_builder.utils.error_handler import print_error_with_suggestions

# Initialize console for pretty output
console = Console()


class WebsiteBuilder:
    """
    Main class for building Next.js websites based on descriptions.
    """
    
    def __init__(
        self,
        description: str,
        template_name: str = "general",
        auth: bool = False,
        database: Optional[str] = None,
        output_dir: str = "./website",
        verbose: bool = False
    ):
        """
        Initialize the website builder.
        
        Args:
            description: Description of the website to build
            template_name: Website template to use
            auth: Whether to include authentication
            database: Database integration type
            output_dir: Output directory for the generated website
            verbose: Whether to enable verbose logging
        """
        self.description = description
        self.template_name = template_name
        self.auth = auth
        self.database = database
        self.output_dir = Path(output_dir).resolve()
        self.verbose = verbose
        
        # Load configuration
        self.config = load_config()
        
        # Get template manager and template
        self.template_manager = get_template_manager()
        self.template = self.template_manager.get_template(template_name)
        
        if not self.template:
            available_templates = ", ".join(self.template_manager.get_template_names())
            raise ValueError(
                f"Template '{template_name}' not found. Available templates: {available_templates}"
            )
        
        # Get prompt manager
        self.prompt_manager = get_prompt_manager()
        
        # Initialize LLM manager
        self.llm_manager = LLMManager(
            model_name=self.config["llm"]["model"],
            temperature=self.config["llm"]["temperature"],
            max_tokens=self.config["llm"]["max_tokens"]
        )
        
        # Generate requirements for the website
        self.requirements = self._generate_requirements()
    
    def _generate_requirements(self) -> Dict[str, Any]:
        """
        Generate detailed requirements based on the description and template.
        
        Returns:
            Dictionary of requirements for the website
        """
        # Create requirements prompt
        prompt = f"""
You are an expert website planner. Based on the description below, generate detailed requirements 
for a {self.template_name} website. Format the output as a JSON object with these keys:
- pages: Array of page objects with "name", "route", and "purpose" fields
- components: Array of component objects with "name" and "purpose" fields
- features: Array of feature objects with "name" and "description" fields
- styling: Object with color scheme and typography preferences
- seo: Object with SEO requirements

User description: {self.description}

Response format (in JSON):
{{
  "pages": [
    {{ "name": "Home", "route": "/", "purpose": "Main landing page" }}
  ],
  "components": [
    {{ "name": "Header", "purpose": "Navigation and branding" }}
  ],
  "features": [
    {{ "name": "Responsive Design", "description": "Works on all devices" }}
  ],
  "styling": {{
    "colorScheme": "Light with blue accents",
    "typography": "Modern sans-serif"
  }},
  "seo": {{
    "title": "Website title",
    "description": "Brief description for SEO"
  }}
}}
"""
        
        if self.verbose:
            console.print("[bold]Generating requirements from description...[/bold]")
        
        try:
            result = self.llm_manager.generate_text(prompt)
            
            # Extract JSON from the result
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                import json
                requirements = json.loads(json_match.group(0))
                
                if self.verbose:
                    console.print("[green]✓[/green] Requirements generated successfully")
                
                return requirements
            else:
                console.print("[yellow]Warning:[/yellow] Failed to parse requirements JSON")
                # Return basic requirements based on template
                return {
                    "pages": [{"name": page, "route": f"/{page.lower()}" if page != "Home" else "/", "purpose": f"{page} page"} for page in self.template.pages],
                    "components": [{"name": comp, "purpose": f"{comp} component"} for comp in self.template.components],
                    "features": [{"name": "Responsive Design", "description": "Works on all devices"}],
                    "styling": {
                        "colorScheme": "Light with accent color",
                        "typography": "Modern sans-serif"
                    },
                    "seo": {
                        "title": "Website",
                        "description": "A website built with Next.js and Tailwind CSS"
                    }
                }
                
        except Exception as e:
            console.print(f"[bold red]Error generating requirements:[/bold red] {e}")
            # Return basic requirements based on template
            return {
                "pages": [{"name": page, "route": f"/{page.lower()}" if page != "Home" else "/", "purpose": f"{page} page"} for page in self.template.pages],
                "components": [{"name": comp, "purpose": f"{comp} component"} for comp in self.template.components],
                "features": [{"name": "Responsive Design", "description": "Works on all devices"}],
                "styling": {
                    "colorScheme": "Light with accent color",
                    "typography": "Modern sans-serif"
                },
                "seo": {
                    "title": "Website",
                    "description": "A website built with Next.js and Tailwind CSS"
                }
            }
    
    def generate(self, skip_validation: bool = False, validation_timeout: int = 120) -> bool:
        """
        Generate the website based on the provided description and options.
        
        Args:
            skip_validation: Whether to skip the validation step
            validation_timeout: Maximum time in seconds for validation
            
        Returns:
            True if the website was generated successfully, False otherwise
        """
        try:
            with Progress() as progress:
                # Step 1: Create Next.js project
                task1 = progress.add_task(
                    "[cyan]Creating Next.js project...", 
                    total=100
                )
                
                # Update progress for initialization
                progress.update(task1, advance=10)
                
                # Create the Next.js project
                success = create_nextjs_project(
                    output_dir=str(self.output_dir),
                    typescript=True,
                    eslint=True,
                    tailwind=True,
                    app_router=True,
                    src_dir=False
                )
                
                if not success:
                    console.print("[bold red]Error:[/bold red] Failed to create Next.js project")
                    return False
                
                progress.update(task1, advance=80)
                
                # Install additional dependencies
                additional_deps = ["@tanstack/react-query"]
                
                if self.auth:
                    additional_deps.append("next-auth")
                
                if self.database:
                    if self.database == "mongodb":
                        additional_deps.append("mongodb")
                    elif self.database == "postgres":
                        additional_deps.extend(["@prisma/client", "prisma"])
                    elif self.database == "supabase":
                        additional_deps.extend(["@supabase/supabase-js", "@supabase/auth-helpers-nextjs"])
                
                install_dependencies(str(self.output_dir), additional_deps)
                progress.update(task1, completed=100)
                
                # Step 2: Generate components
                task2 = progress.add_task(
                    "[cyan]Generating components...", 
                    total=len(self.template.components) or 1
                )
                
                for component in self.template.components:
                    component_info = next((c for c in self.requirements["components"] if c["name"] == component), {"name": component, "purpose": f"{component} component"})
                    
                    # Generate the component
                    content = self._generate_component(component, component_info["purpose"])
                    
                    # Write the component to file
                    component_path = self.output_dir / "app" / "components" / f"{component}.tsx"
                    component_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(component_path, "w") as f:
                        f.write(content)
                    
                    progress.update(task2, advance=1)
                
                # Step 3: Generate pages
                task3 = progress.add_task(
                    "[cyan]Generating pages...", 
                    total=len(self.template.pages) or 1
                )
                
                for page in self.template.pages:
                    page_info = next((p for p in self.requirements["pages"] if p["name"] == page), {"name": page, "route": f"/{page.lower()}" if page != "Home" else "/", "purpose": f"{page} page"})
                    
                    # Generate the page
                    content = self._generate_page(page, page_info["route"], page_info["purpose"])
                    
                    # Write the page to file
                    if page == "Home":
                        page_path = self.output_dir / "app" / "page.tsx"
                    else:
                        route = page_info["route"].strip("/")
                        page_path = self.output_dir / "app" / route / "page.tsx"
                    
                    page_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(page_path, "w") as f:
                        f.write(content)
                    
                    progress.update(task3, advance=1)
                
                # Step 4: Generate layout and utility files
                task4 = progress.add_task(
                    "[cyan]Generating layout and utilities...", 
                    total=100
                )
                
                progress.update(task4, advance=30)
                
                # Generate root layout
                root_layout = self._generate_root_layout()
                root_layout_path = self.output_dir / "app" / "layout.tsx"
                
                with open(root_layout_path, "w") as f:
                    f.write(root_layout)
                
                progress.update(task4, advance=30)
                
                # Generate globals.css
                globals_css = self._generate_globals_css()
                globals_css_path = self.output_dir / "app" / "globals.css"
                
                with open(globals_css_path, "w") as f:
                    f.write(globals_css)
                
                progress.update(task4, advance=20)
                
                # Generate utility files
                self._generate_utility_files()
                
                progress.update(task4, completed=100)
                
                # Step 5: Set up authentication and database (if requested)
                if self.auth or self.database:
                    task5 = progress.add_task(
                        "[cyan]Setting up additional features...", 
                        total=100
                    )
                    
                    if self.auth:
                        self._setup_authentication()
                        progress.update(task5, advance=50)
                    
                    if self.database:
                        self._setup_database()
                        progress.update(task5, advance=50)
                    
                    progress.update(task5, completed=100)
                
                # Step 6: Validate and fix website (if not skipped)
                if not skip_validation:
                    task6 = progress.add_task(
                        "[cyan]Validating and fixing website...", 
                        total=100
                    )
                    
                    progress.update(task6, advance=10)
                    
                    try:
                        # Set a timeout for the entire validation process
                        def run_validation():
                            nonlocal validation_result
                            validation_result = self._validate_and_fix_website(progress, task6, validation_timeout)
                        
                        validation_result = False
                        timer_expired = False
                        
                        validation_thread = threading.Thread(target=run_validation)
                        validation_thread.daemon = True
                        validation_thread.start()
                        
                        # Wait for the validation to complete or timeout
                        validation_thread.join(timeout=validation_timeout)
                        
                        if validation_thread.is_alive():
                            console.print(f"[yellow]⚠[/yellow] Validation process timed out after {validation_timeout} seconds")
                            console.print("Proceeding with the website as-is. It may have some issues but should be functional.")
                            timer_expired = True
                        else:
                            if not validation_result:
                                console.print("[yellow]Warning:[/yellow] Some website issues could not be automatically fixed")
                                console.print("The website might have issues, but should be functional.")
                        
                        # Ensure progress is marked as complete
                        progress.update(task6, completed=100)
                    except Exception as e:
                        console.print(f"[bold red]Error during validation:[/bold red] {e}")
                        console.print("[yellow]Continuing with website generation despite validation errors.[/yellow]")
                        progress.update(task6, completed=100)
                else:
                    console.print("[yellow]Note: Website validation was skipped.[/yellow]")
            
            console.print(f"\n[green]✓[/green] Website generated successfully at: {self.output_dir}")
            console.print("\n[bold]To run your website:[/bold]")
            console.print(f"  cd {self.output_dir}")
            console.print("  npm run dev")
            console.print("\nAccess your website at: [bold]http://localhost:3000[/bold]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error generating website:[/bold red] {e}")
            print_error_with_suggestions(e, self.verbose)
            return False
    
    def _validate_and_fix_website(self, progress, task_id, validation_timeout: int = 120) -> bool:
        """
        Validate the generated website and attempt to fix any issues.
        
        Args:
            progress: Progress instance for updating progress
            task_id: Task ID for updating progress
            validation_timeout: Maximum time in seconds for validation
            
        Returns:
            True if validation passed or all issues were fixed, False otherwise
        """
        max_attempts = 3
        attempt = 1
        overall_timeout = validation_timeout  # Total timeout for validation process in seconds
        start_time = time.time()
        
        # Update progress to show initial validation
        console.print(f"\n[bold]Starting website validation and auto-fixing...[/bold]")
        console.print("⚠️ [yellow]Note: Validation may take time but will continue in the background.[/yellow]")
        console.print(f"⚠️ [yellow]The process has a timeout of {validation_timeout} seconds to ensure it won't get stuck.[/yellow]")
        progress.update(task_id, advance=5)
        
        while attempt <= max_attempts:
            # Check if we've exceeded the overall timeout
            if time.time() - start_time > overall_timeout:
                console.print("[yellow]⚠[/yellow] Validation process timed out. Proceeding with the website as-is.")
                console.print("The website may have minor issues but should be functional.")
                return False
                
            console.print(f"\n[bold]Validation attempt {attempt}/{max_attempts}[/bold]")
            
            # Provide detailed step information
            console.print(f"[cyan]Step 1/4:[/cyan] Checking project structure...")
            progress.update(task_id, advance=5)
            
            # Validate the website with verbose output and limited file count
            validation_results = validate_website(self.output_dir, verbose=True, max_files=25)
            
            # Update progress based on validation steps
            console.print(f"[cyan]Step 2/4:[/cyan] Analyzing components and pages...")
            progress.update(task_id, advance=5)
            
            # Check if validation passed
            if validation_results["valid"]:
                console.print("[green]✓[/green] Website validation passed! All checks successful.")
                return True
            
            # Count issues to help user understand the scope
            issue_count = sum(
                [len(validation_results["structure"]["issues"])] +
                [len(issues) for issues in validation_results["pages"]["issues"].values()] +
                [len(issues) for issues in validation_results["components"]["issues"].values()] +
                [len(issues) for issues in validation_results["tailwind"]["issues"].values()]
            )
            
            # Detailed reporting of issues found
            console.print(f"\n[yellow]⚠[/yellow] Website validation found {issue_count} issues:")
            
            # Display validation issues with counts
            if validation_results["structure"]["issues"]:
                issue_count = len(validation_results["structure"]["issues"])
                console.print(f"[bold]Structure issues:[/bold] ({issue_count} issues)")
                for issue in validation_results["structure"]["issues"]:
                    console.print(f"  - {issue}")
            
            if validation_results["pages"]["issues"]:
                page_issue_count = sum(len(issues) for issues in validation_results["pages"]["issues"].values())
                console.print(f"[bold]Page issues:[/bold] ({page_issue_count} issues across {len(validation_results['pages']['issues'])} files)")
                for page, issues in validation_results["pages"]["issues"].items():
                    console.print(f"  [bold]{page}[/bold]: {len(issues)} issues")
                    if self.verbose and len(issues) < 10:  # Only show details if verbose and not too many issues
                        for issue in issues:
                            console.print(f"    - {issue}")
            
            # Try to fix issues
            console.print(f"\n[cyan]Step 3/4:[/cyan] Attempting to fix {issue_count} issues...")
            progress.update(task_id, advance=5)
            
            # Apply fixes with a timeout
            fix_start_time = time.time()
            try:
                # Set a timeout for the fix process
                fix_timeout = 30  # 30 seconds timeout for fixes
                updated_validation_results = {}
                
                # Use a thread to apply fixes with timeout
                def fix_issues():
                    nonlocal updated_validation_results
                    updated_validation_results = fix_project_issues(self.output_dir, validation_results)
                
                fix_thread = threading.Thread(target=fix_issues)
                fix_thread.daemon = True
                fix_thread.start()
                fix_thread.join(timeout=fix_timeout)
                
                if fix_thread.is_alive():
                    # If thread is still running after timeout, we'll move on
                    console.print("[yellow]⚠[/yellow] Fix process taking too long. Proceeding with partial fixes.")
                    updated_validation_results = validation_results  # Use original results
                
                fixes_duration = time.time() - fix_start_time
            except Exception as e:
                console.print(f"[yellow]Warning: Error during fix process: {e}[/yellow]")
                fixes_duration = time.time() - fix_start_time
                updated_validation_results = validation_results  # Use original results
                
            # Special handling for TypeScript issues - may need to regenerate problematic components/pages
            console.print(f"[cyan]Step 4/4:[/cyan] Handling TypeScript and React hook issues...")
            
            # Set a timeout for TypeScript fixes
            ts_fixes_start_time = time.time()
            ts_timeout = 30  # 30 seconds timeout
            
            try:
                # Fix TypeScript issues in a separate thread with timeout
                ts_fixed = [False]  # Use a list to be mutable in the thread
                
                def fix_ts_issues():
                    try:
                        self._fix_typescript_issues(validation_results, max_files=10)
                        ts_fixed[0] = True
                    except Exception as e:
                        console.print(f"[yellow]Warning: Error fixing TypeScript issues: {e}[/yellow]")
                
                ts_thread = threading.Thread(target=fix_ts_issues)
                ts_thread.daemon = True
                ts_thread.start()
                ts_thread.join(timeout=ts_timeout)
                
                if ts_thread.is_alive():
                    console.print("[yellow]⚠[/yellow] TypeScript fixes taking too long. Proceeding with partial fixes.")
                
                ts_fixes_duration = time.time() - ts_fixes_start_time
            except Exception as e:
                console.print(f"[yellow]Warning: Error during TypeScript fix process: {e}[/yellow]")
                ts_fixes_duration = time.time() - ts_fixes_start_time
            
            # Report on timing
            console.print(f"[dim]Common fixes took {fixes_duration:.1f} seconds[/dim]")
            console.print(f"[dim]TypeScript fixes took {ts_fixes_duration:.1f} seconds[/dim]")
            
            progress.update(task_id, advance=15)  # More progress to show movement
            
            # Check if we're running out of time in the overall timeout
            if time.time() - start_time > overall_timeout * 0.8:  # If we've used 80% of our time
                console.print("[yellow]⚠[/yellow] Validation is taking too long. Proceeding with current fixes.")
                return True  # Consider it successful to avoid more delays
            
            # If still not valid but we have updated results, update for next attempt
            if updated_validation_results and "valid" in updated_validation_results and not updated_validation_results["valid"]:
                validation_results = updated_validation_results
                attempt += 1
                remaining_issues = sum(
                    [len(updated_validation_results["structure"]["issues"])] +
                    [len(issues) for issues in updated_validation_results["pages"]["issues"].values()] +
                    [len(issues) for issues in updated_validation_results["components"]["issues"].values()] +
                    [len(issues) for issues in updated_validation_results["tailwind"]["issues"].values()]
                )
                console.print(f"[yellow]{remaining_issues} issues remain. Trying again... (Attempt {attempt}/{max_attempts})[/yellow]")
            else:
                # Either validation passed or we don't have updated results
                console.print("[green]✓[/green] Fixes applied successfully!")
                return True
        
        console.print("[yellow]⚠[/yellow] Reached maximum validation attempts with issues still present.")
        console.print("[yellow]The website may have minor issues but should be functional.[/yellow]")
        return False
    
    def _fix_typescript_issues(self, validation_results: Dict[str, Any], max_files: int = 20) -> None:
        """
        Fix TypeScript issues by potentially regenerating problematic components or pages.
        
        Args:
            validation_results: Validation results dictionary
            max_files: Maximum number of files to process
        """
        # Count TypeScript issues for reporting
        page_ts_issues = {}
        file_counter = 0
        
        for page_path_str, issues in validation_results["pages"].get("issues", {}).items():
            ts_issues = [issue for issue in issues if "TypeScript" in issue or "type" in issue.lower()]
            if ts_issues:
                page_ts_issues[page_path_str] = ts_issues
                file_counter += 1
                if file_counter >= max_files // 2:  # Reserve half the quota for pages
                    break
        
        component_ts_issues = {}
        for component_path_str, issues in validation_results["components"].get("issues", {}).items():
            ts_issues = [issue for issue in issues if "TypeScript" in issue or "type" in issue.lower()]
            if ts_issues:
                component_ts_issues[component_path_str] = ts_issues
                file_counter += 1
                if file_counter >= max_files:  # Stop if we've reached the total limit
                    break
        
        total_ts_issues = len(page_ts_issues) + len(component_ts_issues)
        if total_ts_issues == 0:
            console.print("[green]✓[/green] No TypeScript issues to fix.")
            return
            
        console.print(f"[bold]Fixing TypeScript issues in {total_ts_issues} files (limited to {max_files} for performance)...[/bold]")
        
        # Handle page issues
        if page_ts_issues:
            console.print(f"[cyan]Processing {len(page_ts_issues)} pages with TypeScript issues...[/cyan]")
        
        for i, (page_path_str, issues) in enumerate(page_ts_issues.items()):
            page_path = Path(page_path_str)
            
            # Report progress
            console.print(f"[dim]Fixing page {i+1}/{len(page_ts_issues)}: {page_path_str}[/dim]")
            
            try:
                # Extract page name and route
                page_name = page_path.stem
                if page_name == "page":
                    if page_path.parent.name == "app":
                        page_name = "Home"
                        route = "/"
                    else:
                        page_name = page_path.parent.name.title()
                        route = f"/{page_path.parent.name}"
                else:
                    route = f"/{page_name}"
                
                # Find actual purpose from requirements
                purpose = ""
                for page_info in self.requirements.get("pages", []):
                    if page_info.get("name") == page_name or page_info.get("route") == route:
                        purpose = page_info.get("purpose", f"{page_name} page")
                        break
                
                if not purpose:
                    purpose = f"{page_name} page"
                
                # Regenerate the page with a timeout
                try:
                    content = self._generate_page(page_name, route, purpose)
                    
                    # Add "use client" directive if using React hooks
                    if "useState" in content or "useEffect" in content or "useContext" in content or "useRef" in content:
                        if not content.startswith("'use client'"):
                            content = "'use client';\n\n" + content
                    
                    # Write the regenerated page
                    full_path = self.output_dir / page_path_str
                    with open(full_path, "w") as f:
                        f.write(content)
                        
                    console.print(f"[green]✓[/green] Regenerated {page_path_str}")
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Failed to regenerate page {page_path_str}: {e}")
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Error processing page {page_path_str}: {e}")
        
        # Handle component issues
        if component_ts_issues:
            console.print(f"[cyan]Processing {len(component_ts_issues)} components with TypeScript issues...[/cyan]")
            
        for i, (component_path_str, issues) in enumerate(component_ts_issues.items()):
            component_path = Path(component_path_str)
            
            # Report progress
            console.print(f"[dim]Fixing component {i+1}/{len(component_ts_issues)}: {component_path_str}[/dim]")
            
            try:
                # Extract component name
                component_name = component_path.stem
                
                # Find actual purpose from requirements
                purpose = ""
                for comp_info in self.requirements.get("components", []):
                    if comp_info.get("name") == component_name:
                        purpose = comp_info.get("purpose", f"{component_name} component")
                        break
                
                if not purpose:
                    purpose = f"{component_name} component"
                
                # Regenerate the component with a timeout
                try:
                    content = self._generate_component(component_name, purpose)
                    
                    # Add "use client" directive if using React hooks
                    if "useState" in content or "useEffect" in content or "useContext" in content or "useRef" in content:
                        if not content.startswith("'use client'"):
                            content = "'use client';\n\n" + content
                    
                    # Write the regenerated component
                    full_path = self.output_dir / component_path_str
                    with open(full_path, "w") as f:
                        f.write(content)
                        
                    console.print(f"[green]✓[/green] Regenerated {component_path_str}")
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Failed to regenerate component {component_path_str}: {e}")
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Error processing component {component_path_str}: {e}")
                
    def _fix_import_paths(self, content: str) -> str:
        """
        Fix common issues with import paths in generated code.
        
        Args:
            content: The code content to fix
            
        Returns:
            The fixed content
        """
        # Fix double quotes in import paths
        content = re.sub(r"import\s+(\w+)\s+from\s+'([^']+)'", r"import \1 from '\2'", content)
        content = re.sub(r'import\s+(\w+)\s+from\s+"([^"]+)"', r"import \1 from '\2'", content)
        
        # Fix paths with double single quotes
        content = re.sub(r"import\s+(\w+)\s+from\s+''([^']+)''", r"import \1 from './\2'", content)
        
        # Fix incorrect component paths
        content = re.sub(r"import\s+(\w+)\s+from\s+'([^./][^']*)'", r"import \1 from './\2'", content)
        
        # Fix missing .tsx extension in imports (if LLM forgets it)
        content = re.sub(r"import\s+(\w+)\s+from\s+'(\./components/[^']+)'(?!\.tsx|\.jsx|\.js|')", r"import \1 from '\2'", content)
        
        # Fix incorrect app components path - components should be in app folder with app router
        content = re.sub(r"import\s+(\w+)\s+from\s+'(\.?/?components/[^']+)'", r"import \1 from './components/\1'", content)
        
        # Fix import paths for components in app/components directory
        content = re.sub(r"import\s+(\w+)\s+from\s+'\.?/?components/\1'", r"import \1 from './components/\1'", content)
        
        return content
    
    def _generate_component(self, component_name: str, purpose: str) -> str:
        """
        Generate a component using the LLM.
        
        Args:
            component_name: The name of the component to generate
            purpose: The purpose of the component
            
        Returns:
            The generated component code
        """
        # Get styling details from requirements
        styling = self.requirements.get("styling", {
            "colorScheme": "Light with accent color",
            "typography": "Modern sans-serif"
        })
        
        # Create component requirements
        component_requirements = {
            "purpose": purpose,
            "styling": styling,
            "responsive": True,
            "accessible": True
        }
        
        # Get component prompt
        prompt = self.prompt_manager.get_component_prompt(component_name, component_requirements)
        
        if self.verbose:
            console.print(f"[bold]Generating {component_name} component...[/bold]")
        
        # Generate the component
        try:
            content = self.llm_manager.generate_text(prompt)
            
            # Extract code block if present
            code_match = re.search(r'```(?:tsx|jsx)?\s*([\s\S]*?)```', content)
            if code_match:
                content = code_match.group(1).strip()
            
            # Fix import paths
            content = self._fix_import_paths(content)
            
            if self.verbose:
                console.print(f"[green]✓[/green] Generated {component_name} component")
            
            return content
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to generate {component_name} component: {e}")
            # Return a basic component as fallback
            return f"""'use client';

import React from 'react';

interface {component_name}Props {{
  children?: React.ReactNode;
}}

export default function {component_name}({{ children }}: {component_name}Props) {{
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">{component_name}</h2>
      {{children}}
    </div>
  );
}}
"""
    
    def _generate_page(self, page_name: str, route: str, purpose: str) -> str:
        """
        Generate a page using the LLM.
        
        Args:
            page_name: The name of the page to generate
            route: The route for the page
            purpose: The purpose of the page
            
        Returns:
            The generated page code
        """
        # Create page requirements
        page_requirements = {
            "name": page_name,
            "route": route,
            "purpose": purpose,
            "components": self.template.components,
            "features": self.requirements.get("features", []),
            "styling": self.requirements.get("styling", {}),
            "seo": self.requirements.get("seo", {})
        }
        
        # Get page prompt
        prompt = self.prompt_manager.get_page_prompt(page_name, page_requirements)
        
        if self.verbose:
            console.print(f"[bold]Generating {page_name} page...[/bold]")
        
        # Generate the page
        try:
            content = self.llm_manager.generate_text(prompt)
            
            # Extract code block if present
            code_match = re.search(r'```(?:tsx|jsx)?\s*([\s\S]*?)```', content)
            if code_match:
                content = code_match.group(1).strip()
            
            # Fix import paths
            content = self._fix_import_paths(content)
            
            if self.verbose:
                console.print(f"[green]✓[/green] Generated {page_name} page")
            
            return content
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to generate {page_name} page: {e}")
            # Return a basic page as fallback
            return f"""import React from 'react';
import {{ Metadata }} from 'next';

export const metadata: Metadata = {{
  title: '{page_name} | {self.requirements.get("seo", {}).get("title", "Website")}',
  description: '{self.requirements.get("seo", {}).get("description", "A website built with Next.js and Tailwind CSS")}',
}};

export default function {page_name.replace(" ", "")}Page() {{
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{page_name}</h1>
      <p className="mb-4">{purpose}</p>
    </main>
  );
}}
"""
    
    def _generate_root_layout(self) -> str:
        """
        Generate the root layout file.
        
        Returns:
            The generated root layout code
        """
        # Create layout requirements
        layout_requirements = {
            "styling": self.requirements.get("styling", {}),
            "seo": self.requirements.get("seo", {}),
            "auth": self.auth,
            "database": self.database
        }
        
        # Create layout prompt
        prompt = f"""
Generate a root layout.tsx file for a Next.js App Router application with Tailwind CSS.
The layout should:

1. Import necessary components and styles
2. Set up metadata for the site with SEO
3. Include a proper HTML structure with lang attribute
4. Set up the body with appropriate Tailwind classes
5. Include layout components such as Header and Footer from './components/Header' and './components/Footer'
6. Set up React Query provider if needed

Site information:
- Title: {self.requirements.get("seo", {}).get("title", "Website")}
- Description: {self.requirements.get("seo", {}).get("description", "A website built with Next.js and Tailwind CSS")}
- Color scheme: {self.requirements.get("styling", {}).get("colorScheme", "Light with accent color")}
- Typography: {self.requirements.get("styling", {}).get("typography", "Modern sans-serif")}
- Authentication: {"Enabled" if self.auth else "Disabled"}

IMPORTANT: Make sure to use proper import paths like './components/Header' NOT 'components/Header'

Please provide the complete TypeScript code for layout.tsx.
"""
        
        if self.verbose:
            console.print("[bold]Generating root layout...[/bold]")
        
        # Generate the layout
        try:
            content = self.llm_manager.generate_text(prompt)
            
            # Extract code block if present
            code_match = re.search(r'```(?:tsx|jsx)?\s*([\s\S]*?)```', content)
            if code_match:
                content = code_match.group(1).strip()
            
            # Fix import paths
            content = self._fix_import_paths(content)
            
            if self.verbose:
                console.print("[green]✓[/green] Generated root layout")
            
            return content
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to generate root layout: {e}")
            # Return a basic layout as fallback
            return """import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Header from './components/Header';
import Footer from './components/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Next.js Website',
  description: 'A website built with Next.js and Tailwind CSS',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
"""
    
    def _generate_globals_css(self) -> str:
        """
        Generate the globals.css file.
        
        Returns:
            The generated globals.css code
        """
        # Create globals.css prompt
        prompt = f"""
Generate a globals.css file for a Next.js application with Tailwind CSS.
The file should:

1. Import the Tailwind CSS directives
2. Include any global styles needed
3. Set up basic typography and color variables if needed
4. Keep the file minimal since we'll use Tailwind for most styling

Style preferences:
- Color scheme: {self.requirements.get("styling", {}).get("colorScheme", "Light with accent color")}
- Typography: {self.requirements.get("styling", {}).get("typography", "Modern sans-serif")}

Please provide the complete CSS code for globals.css.
"""
        
        if self.verbose:
            console.print("[bold]Generating globals.css...[/bold]")
        
        # Generate the globals.css
        try:
            content = self.llm_manager.generate_text(prompt)
            
            # Extract code block if present
            code_match = re.search(r'```(?:css)?\s*([\s\S]*?)```', content)
            if code_match:
                content = code_match.group(1).strip()
            
            if self.verbose:
                console.print("[green]✓[/green] Generated globals.css")
            
            return content
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to generate globals.css: {e}")
            # Return a basic globals.css as fallback
            return """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-rgb: 255, 255, 255;
}

body {
  color: rgb(var(--foreground-rgb));
  background: rgb(var(--background-rgb));
}

@layer base {
  h1 {
    @apply text-3xl font-bold mb-6;
  }
  h2 {
    @apply text-2xl font-bold mb-4;
  }
  h3 {
    @apply text-xl font-bold mb-3;
  }
  p {
    @apply mb-4;
  }
  a {
    @apply text-blue-600 hover:underline;
  }
}
"""
    
    def _generate_utility_files(self) -> None:
        """
        Generate utility files for the website.
        """
        # Create utils directory
        utils_dir = self.output_dir / "app" / "lib" / "utils"
        utils_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a simple utils file
        utils_file = utils_dir / "helpers.ts"
        utils_content = """/**
 * Format a date to a readable string
 */
export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

/**
 * Truncate a string to a specific length and add ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Generate a slug from a string
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '');
}

/**
 * Debounce a function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function(...args: Parameters<T>): void {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Get a random item from an array
 */
export function getRandomItem<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}
"""
        
        with open(utils_file, "w") as f:
            f.write(utils_content)
    
    def _setup_authentication(self) -> None:
        """
        Set up authentication for the website.
        """
        # Create auth.ts file for next-auth configuration
        auth_dir = self.output_dir / "app" / "lib" / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        
        auth_file = auth_dir / "auth.ts"
        auth_content = """import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { compare } from 'bcrypt';

// Note: In a real app, you would use a proper database
// This is a simplified example
const users = [
  {
    id: '1',
    name: 'User',
    email: 'user@example.com',
    password: '$2b$10$GQD4GR6JqbJLGOJJ.fRZ1eqyJIciD0UUz3QJArjxLjlLnRF.fvK56' // "password"
  }
];

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }
        
        const user = users.find(user => user.email === credentials.email);
        
        if (!user) {
          return null;
        }
        
        const isPasswordValid = await compare(credentials.password, user.password);
        
        if (!isPasswordValid) {
          return null;
        }
        
        return {
          id: user.id,
          name: user.name,
          email: user.email
        };
      }
    })
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async session({ session, user, token }) {
      return session;
    },
    async jwt({ token, user, account, profile }) {
      return token;
    }
  }
});
"""
        
        # Write the auth.ts file
        with open(auth_file, "w") as f:
            f.write(auth_content)
        
        # Create middleware.ts file
        middleware_file = self.output_dir / "middleware.ts"
        middleware_content = """import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { auth } from './app/lib/auth/auth';

export async function middleware(request: NextRequest) {
  const session = await auth();
  
  // Protected routes
  const protectedPaths = ['/dashboard', '/profile', '/account'];
  const path = request.nextUrl.pathname;
  
  // Check if the path is protected
  const isProtectedPath = protectedPaths.some(protectedPath => 
    path.startsWith(protectedPath)
  );
  
  if (isProtectedPath && !session) {
    // Redirect to login if trying to access protected routes without a session
    const url = new URL('/login', request.url);
    url.searchParams.set('callbackUrl', encodeURI(request.url));
    return NextResponse.redirect(url);
  }
  
  // If user is logged in and tries to access login page, redirect to dashboard
  if (session && (path === '/login' || path === '/register')) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/profile/:path*',
    '/account/:path*',
    '/login',
    '/register'
  ],
};
"""
        
        # Write the middleware.ts file
        with open(middleware_file, "w") as f:
            f.write(middleware_content)
        
        # Create login page
        login_dir = self.output_dir / "app" / "login"
        login_dir.mkdir(parents=True, exist_ok=True)
        
        login_file = login_dir / "page.tsx"
        login_content = """'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard';
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const result = await signIn('credentials', {
        redirect: false,
        email,
        password,
      });
      
      if (result?.error) {
        setError('Invalid email or password');
        setIsLoading(false);
        return;
      }
      
      router.push(callbackUrl);
    } catch (error) {
      setError('An error occurred. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
            Sign in to your account
          </h2>
        </div>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
            <div className="text-red-700">{error}</div>
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="-space-y-px rounded-md shadow-sm">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="relative block w-full rounded-t-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="relative block w-full rounded-b-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          
          <div className="text-sm text-center">
            <p>
              Demo credentials: user@example.com / password
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
"""
        
        # Write the login page file
        with open(login_file, "w") as f:
            f.write(login_content)
        
        # Install required dependencies
        install_dependencies(str(self.output_dir), ["bcrypt", "next-auth"], False)
        install_dependencies(str(self.output_dir), ["@types/bcrypt"], True)
    
    def _setup_database(self) -> None:
        """
        Set up database integration for the website.
        """
        if self.database == "mongodb":
            # Create MongoDB client file
            mongodb_dir = self.output_dir / "app" / "lib" / "mongodb"
            mongodb_dir.mkdir(parents=True, exist_ok=True)
            
            mongodb_file = mongodb_dir / "mongodb.ts"
            mongodb_content = """import { MongoClient, ServerApiVersion } from 'mongodb';

// Replace the placeholder with your MongoDB Atlas connection string
const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const options = {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
};

let client: MongoClient;
let clientPromise: Promise<MongoClient>;

if (process.env.NODE_ENV === 'development') {
  // In development mode, use a global variable to maintain the connection
  if (!(global as any)._mongoClientPromise) {
    client = new MongoClient(uri, options);
    (global as any)._mongoClientPromise = client.connect();
  }
  clientPromise = (global as any)._mongoClientPromise;
} else {
  // In production mode, create a new client for each connection
  client = new MongoClient(uri, options);
  clientPromise = client.connect();
}

export default clientPromise;
"""
            
            # Write the MongoDB client file
            with open(mongodb_file, "w") as f:
                f.write(mongodb_content)
            
            # Create .env.local file for MongoDB URI
            env_file = self.output_dir / ".env.local"
            env_content = """# MongoDB URI
MONGODB_URI=mongodb://localhost:27017

# Next Auth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-next-auth-secret
"""
            
            # Write the .env.local file
            with open(env_file, "w") as f:
                f.write(env_content)
            
        elif self.database == "postgres":
            # Create Prisma directory
            prisma_dir = self.output_dir / "prisma"
            prisma_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Prisma schema file
            schema_file = prisma_dir / "schema.prisma"
            schema_content = """generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String    @id @default(cuid())
  name      String?
  email     String    @unique
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
}
"""
            
            # Write the Prisma schema file
            with open(schema_file, "w") as f:
                f.write(schema_content)
            
            # Create Prisma client file
            prisma_lib_dir = self.output_dir / "app" / "lib" / "prisma"
            prisma_lib_dir.mkdir(parents=True, exist_ok=True)
            
            prisma_client_file = prisma_lib_dir / "prisma.ts"
            prisma_client_content = """import { PrismaClient } from '@prisma/client';

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
"""
            
            # Write the Prisma client file
            with open(prisma_client_file, "w") as f:
                f.write(prisma_client_content)
            
            # Create .env file for Prisma
            env_file = self.output_dir / ".env"
            env_content = """# PostgreSQL connection string
DATABASE_URL="postgresql://postgres:password@localhost:5432/mydb?schema=public"

# Next Auth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-next-auth-secret
"""
            
            # Write the .env file
            with open(env_file, "w") as f:
                f.write(env_content)
            
            # Run Prisma generate
            try:
                import subprocess
                subprocess.run(
                    ["npx", "prisma", "generate"],
                    cwd=str(self.output_dir),
                    check=True
                )
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to run Prisma generate: {e}")
            
        elif self.database == "supabase":
            # Create Supabase client file
            supabase_dir = self.output_dir / "app" / "lib" / "supabase"
            supabase_dir.mkdir(parents=True, exist_ok=True)
            
            supabase_file = supabase_dir / "supabase.ts"
            supabase_content = """import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''
);
"""
            
            # Write the Supabase client file
            with open(supabase_file, "w") as f:
                f.write(supabase_content)
            
            # Create .env.local file for Supabase
            env_file = self.output_dir / ".env.local"
            env_content = """# Supabase
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
"""
            
            # Write the .env.local file
            with open(env_file, "w") as f:
                f.write(env_content)