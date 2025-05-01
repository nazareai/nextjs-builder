"""
Template management system for Next.js & Tailwind website builder.

This module provides functionality for managing templates for different 
website types (general, blog, e-commerce, portfolio).
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from rich.console import Console

from nextjs_builder.config import get_project_root

# Initialize console for pretty output
console = Console()


class Template:
    """
    Class representing a website template.
    """
    
    def __init__(
        self,
        name: str,
        label: str,
        description: str,
        components: List[str],
        pages: List[str],
        structure: Dict[str, Any]
    ):
        """
        Initialize a template.
        
        Args:
            name: Template identifier (e.g., "general", "blog")
            label: Display name for the template (e.g., "General Website")
            description: Description of the template
            components: List of components to generate
            pages: List of pages to generate
            structure: Project structure definition
        """
        self.name = name
        self.label = label
        self.description = description
        self.components = components
        self.pages = pages
        self.structure = structure
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """
        Create a Template instance from a dictionary.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            A Template instance
        """
        return cls(
            name=data["name"],
            label=data["label"],
            description=data["description"],
            components=data["components"],
            pages=data["pages"],
            structure=data["structure"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template to a dictionary.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "components": self.components,
            "pages": self.pages,
            "structure": self.structure
        }


class TemplateManager:
    """
    Manager for website templates.
    """
    
    def __init__(self):
        """Initialize the template manager."""
        self.project_root = get_project_root()
        self.templates_dir = self.project_root / "templates"
        self.templates: Dict[str, Template] = {}
        
        # Create templates directory if it doesn't exist
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load built-in templates
        self._load_default_templates()
        
        # Load custom templates
        self.load_templates_from_directory(self.templates_dir)
    
    def _load_default_templates(self) -> None:
        """Load built-in default templates."""
        # General template
        general_template = Template(
            name="general",
            label="General Website",
            description="A general-purpose website with home, about, and contact pages",
            components=[
                "Header",
                "Footer",
                "HeroSection",
                "FeatureCard",
                "FeatureGrid",
                "CTASection",
                "ContactForm",
                "TeamMember",
                "TeamGrid",
                "Testimonial"
            ],
            pages=[
                "Home",
                "About",
                "Services",
                "Contact"
            ],
            structure={
                "directories": [
                    "app/components",
                    "app/components/ui",
                    "app/components/sections",
                    "app/lib",
                    "app/lib/hooks",
                    "app/lib/utils",
                    "public/images"
                ],
                "files": []  # Will be populated during component generation
            }
        )
        
        # Blog template
        blog_template = Template(
            name="blog",
            label="Blog Website",
            description="A content-focused blog website with posts and categories",
            components=[
                "Header",
                "Footer",
                "HeroSection",
                "PostCard",
                "PostGrid",
                "CategoryList",
                "TagCloud",
                "AuthorBio",
                "RelatedPosts",
                "TableOfContents",
                "SearchBar"
            ],
            pages=[
                "Home",
                "Blog",
                "Post",
                "Category",
                "About",
                "Contact"
            ],
            structure={
                "directories": [
                    "app/components",
                    "app/components/ui",
                    "app/components/blog",
                    "app/lib",
                    "app/lib/hooks",
                    "app/lib/utils",
                    "app/blog",
                    "app/(content)",
                    "public/images",
                    "content/posts",
                    "content/authors"
                ],
                "files": []  # Will be populated during component generation
            }
        )
        
        # E-commerce template
        ecommerce_template = Template(
            name="ecommerce",
            label="E-commerce Website",
            description="An online store with product listings and checkout flow",
            components=[
                "Header",
                "Footer",
                "ProductCard",
                "ProductGrid",
                "ProductGallery",
                "CategoryFilter",
                "PriceFilter",
                "CartItem",
                "CartSummary",
                "CheckoutForm",
                "OrderSummary"
            ],
            pages=[
                "Home",
                "Products",
                "ProductDetail",
                "Cart",
                "Checkout",
                "OrderConfirmation",
                "Account"
            ],
            structure={
                "directories": [
                    "app/components",
                    "app/components/ui",
                    "app/components/products",
                    "app/components/checkout",
                    "app/lib",
                    "app/lib/hooks",
                    "app/lib/utils",
                    "app/lib/cart",
                    "app/(shop)",
                    "public/images",
                    "public/products"
                ],
                "files": []  # Will be populated during component generation
            }
        )
        
        # Portfolio template
        portfolio_template = Template(
            name="portfolio",
            label="Portfolio Website",
            description="A showcase website for creative professionals",
            components=[
                "Header",
                "Footer",
                "HeroSection",
                "ProjectCard",
                "ProjectGrid",
                "ProjectGallery",
                "SkillsSection",
                "ExperienceItem",
                "Timeline",
                "ContactForm"
            ],
            pages=[
                "Home",
                "Projects",
                "ProjectDetail",
                "About",
                "Resume",
                "Contact"
            ],
            structure={
                "directories": [
                    "app/components",
                    "app/components/ui",
                    "app/components/portfolio",
                    "app/lib",
                    "app/lib/hooks",
                    "app/lib/utils",
                    "app/(portfolio)",
                    "public/images",
                    "public/projects"
                ],
                "files": []  # Will be populated during component generation
            }
        )
        
        # Add the templates to the templates dictionary
        self.templates["general"] = general_template
        self.templates["blog"] = blog_template
        self.templates["ecommerce"] = ecommerce_template
        self.templates["portfolio"] = portfolio_template
        
        # Save the default templates to files
        for template_name, template in self.templates.items():
            template_dir = self.templates_dir / template_name
            template_dir.mkdir(exist_ok=True)
            
            with open(template_dir / "template.json", "w") as f:
                json.dump(template.to_dict(), f, indent=2)
    
    def load_templates_from_directory(self, directory: Path) -> None:
        """
        Load templates from a directory.
        
        Args:
            directory: Directory containing template definition files
        """
        if not directory.exists():
            return
        
        # Look for template.json files in subdirectories
        for template_dir in directory.iterdir():
            if not template_dir.is_dir():
                continue
            
            template_file = template_dir / "template.json"
            if not template_file.exists():
                continue
            
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                
                template = Template.from_dict(template_data)
                self.templates[template.name] = template
                console.print(f"[green]✓[/green] Loaded template: {template.label}")
                
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to load template from {template_file}: {e}")
    
    def get_template(self, name: str) -> Optional[Template]:
        """
        Get a template by name.
        
        Args:
            name: The name of the template to get
            
        Returns:
            The template, or None if not found
        """
        return self.templates.get(name)
    
    def get_template_names(self) -> List[str]:
        """
        Get a list of available template names.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())
    
    def get_template_info(self) -> List[Dict[str, str]]:
        """
        Get information about all available templates.
        
        Returns:
            List of dictionaries with template information
        """
        return [
            {
                "name": template.name,
                "label": template.label,
                "description": template.description
            }
            for template in self.templates.values()
        ]
    
    def register_template(self, template: Template) -> None:
        """
        Register a new template.
        
        Args:
            template: The template to register
        """
        self.templates[template.name] = template
        
        # Save the template to a file
        template_dir = self.templates_dir / template.name
        template_dir.mkdir(exist_ok=True)
        
        with open(template_dir / "template.json", "w") as f:
            json.dump(template.to_dict(), f, indent=2)
        
        console.print(f"[green]✓[/green] Registered template: {template.label}")


# Create a global instance of the TemplateManager
template_manager = TemplateManager()


def get_template_manager() -> TemplateManager:
    """
    Get the global TemplateManager instance.
    
    Returns:
        The global TemplateManager instance
    """
    return template_manager