"""
Prompt template management for Next.js & Tailwind website builder.

This module handles loading, formatting, and managing prompt templates for
LLM interactions.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from rich.console import Console

from nextjs_builder.config import get_project_root

# Initialize console for pretty output
console = Console()

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


class PromptManager:
    """
    Manager for prompt templates.
    """
    
    def __init__(self):
        """Initialize the prompt manager."""
        self.project_root = get_project_root()
        self.prompts_dir = self.project_root / "prompts"
        self.cache = {}
        
        # Create prompts directory if it doesn't exist
        if not self.prompts_dir.exists():
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[yellow]Notice:[/yellow] Created prompts directory at {self.prompts_dir}")
            
            # Create some initial templates if the directory is empty
            self._create_default_templates()
    
    def _create_default_templates(self) -> None:
        """Create default prompt templates if they don't exist."""
        templates = {
            "component_base.txt": """
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
""",

            "page_base.txt": """
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
""",
        }
        
        # Create base directories
        component_dir = self.prompts_dir / "components"
        page_dir = self.prompts_dir / "pages"
        system_dir = self.prompts_dir / "system"
        template_dir = self.prompts_dir / "templates"
        
        for directory in [component_dir, page_dir, system_dir, template_dir]:
            directory.mkdir(exist_ok=True)
        
        # Create base system prompt
        with open(system_dir / "base_prompt.txt", "w") as f:
            f.write(SYSTEM_BASE_PROMPT)
        
        # Create component base prompt
        with open(component_dir / "component_base.txt", "w") as f:
            f.write(templates["component_base.txt"])
        
        # Create page base prompt
        with open(page_dir / "page_base.txt", "w") as f:
            f.write(templates["page_base.txt"])
    
    def load_prompt_template(self, template_name: str) -> str:
        """
        Load a prompt template from the prompts directory.
        
        Args:
            template_name: The name of the template file (without .txt extension)
            
        Returns:
            The prompt template as a string
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        # Check cache first
        if template_name in self.cache:
            return self.cache[template_name]
        
        # Look for the template in different directories
        possible_paths = [
            self.prompts_dir / f"{template_name}.txt",
            self.prompts_dir / "components" / f"{template_name}.txt",
            self.prompts_dir / "pages" / f"{template_name}.txt",
            self.prompts_dir / "system" / f"{template_name}.txt",
            self.prompts_dir / "templates" / f"{template_name}.txt",
        ]
        
        for path in possible_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    template = f.read()
                
                # Cache the template
                self.cache[template_name] = template
                return template
        
        # If we get here, the template wasn't found
        raise FileNotFoundError(f"Prompt template '{template_name}' not found")
    
    def get_system_prompt(self) -> str:
        """
        Get the base system prompt.
        
        Returns:
            The base system prompt
        """
        try:
            return self.load_prompt_template("system/base_prompt")
        except FileNotFoundError:
            # Return the default system prompt
            return SYSTEM_BASE_PROMPT
    
    def get_component_prompt(
        self,
        component_type: str,
        requirements: Dict[str, Any]
    ) -> str:
        """
        Get a prompt for generating a component.
        
        Args:
            component_type: The type of component to generate
            requirements: Dictionary of component requirements
            
        Returns:
            A prompt for generating the component
        """
        try:
            base_prompt = self.load_prompt_template("components/component_base")
        except FileNotFoundError:
            # Use the default component prompt
            base_prompt = """
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
"""
        
        # Format the requirements as bullet points
        formatted_requirements = "\n".join([f"- {key}: {value}" for key, value in requirements.items()])
        
        prompt = base_prompt.format(
            component_type=component_type,
            requirements=formatted_requirements
        )
        
        return self.get_system_prompt() + "\n\n" + prompt
    
    def get_page_prompt(
        self,
        page_type: str,
        requirements: Dict[str, Any]
    ) -> str:
        """
        Get a prompt for generating a page.
        
        Args:
            page_type: The type of page to generate
            requirements: Dictionary of page requirements
            
        Returns:
            A prompt for generating the page
        """
        try:
            base_prompt = self.load_prompt_template("pages/page_base")
        except FileNotFoundError:
            # Use the default page prompt
            base_prompt = """
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
"""
        
        # Format the requirements as bullet points
        formatted_requirements = "\n".join([f"- {key}: {value}" for key, value in requirements.items()])
        
        prompt = base_prompt.format(
            page_type=page_type,
            requirements=formatted_requirements
        )
        
        return self.get_system_prompt() + "\n\n" + prompt
    
    def get_template_prompt(
        self,
        template_type: str,
        additional_requirements: str = ""
    ) -> str:
        """
        Get a prompt for generating a website based on a template type.
        
        Args:
            template_type: The type of template (general, blog, ecommerce, portfolio)
            additional_requirements: Additional requirements for the template
            
        Returns:
            A prompt for generating the website
        """
        try:
            template_prompt = self.load_prompt_template(f"templates/{template_type}")
        except FileNotFoundError:
            # Try to load a default template
            if template_type == "general":
                template_prompt = """
Generate a professional general-purpose website with these features:

1. Pages:
   - Home: Showcase main value proposition with hero section, features grid, and CTA sections
   - About: Company/organization information with team member profiles
   - Services/Features: Detailed information about offerings with clear descriptions
   - Contact: Form with validation and location information
   - Legal: Privacy policy and terms of service pages

2. Components:
   - Modern, responsive navigation with mobile hamburger menu
   - Hero section with visual focus and clear CTA
   - Feature cards with icons and descriptions
   - Testimonial carousel or grid
   - Newsletter subscription with email validation
   - Footer with navigation, contact info, and social links

3. Design Patterns:
   - Clean, minimal aesthetic with whitespace
   - Strategic use of color accents for emphasis
   - Card-based UI for content organization
   - Subtle animations for interactivity
   - Consistent padding and spacing system

The site should be easily customizable for different industries while maintaining professional appearance and performance.
"""
            elif template_type == "blog":
                template_prompt = """
Generate a modern blog website with these features:

1. Pages:
   - Home: Featured posts, categories, and recent posts
   - Blog List: Paginated list of all blog posts with filtering
   - Single Post: Post content with author info, published date, categories, and related posts
   - Category/Tag Archive: Posts filtered by category or tag
   - About: Information about the blog and author(s)
   - Contact: Simple contact form

2. Components:
   - Post card with featured image, title, excerpt, and metadata
   - Author bio component with avatar and social links
   - Category/tag cloud or list
   - Search functionality with results page
   - Related posts component
   - Comments section (optional based on authentication)
   - Sharing buttons for social media
   - Table of contents for long-form content

3. Design Patterns:
   - Readable typography with proper hierarchy
   - Content-focused layout with minimal distractions
   - Clear categorization and taxonomy navigation
   - Support for various content types (text, images, videos, code blocks)
   - Reading time indicators and progress bar
   - Dark/light mode toggle
   - Responsive design for all devices
   - Rich text formatting with Markdown support

The blog should focus on content readability while maintaining fast load times and SEO optimization.
"""
            elif template_type == "ecommerce":
                template_prompt = """
Generate a professional e-commerce website with these features:

1. Pages:
   - Home: Featured products, categories, and promotions
   - Product Listing: Filterable and sortable product grid with pagination
   - Product Detail: Complete product information, images gallery, variants, related products
   - Cart: Cart management with quantity controls and price summaries
   - Checkout: Multi-step checkout process
   - Account: User registration, login, and profile management
   - Order History: Past orders and status tracking
   - FAQ/Help Center: Common questions and support information

2. Components:
   - Product card with image, title, price, and quick actions
   - Category navigation with dropdown menus
   - Search with autocomplete suggestions
   - Filtering sidebar with price ranges, categories, etc.
   - Image gallery with zoom functionality
   - Size/variant selector
   - Add to cart button with confirmation
   - Mini-cart drawer
   - Checkout forms with validation
   - Order summary component

3. Design Patterns:
   - Clean product photography emphasis
   - Consistent call-to-action buttons
   - Clear pricing and availability indicators
   - Cart and checkout progress indicators
   - Emphasis on trust signals (reviews, security badges, etc.)
   - Mobile-optimized product browsing experience

Implement React Context API for cart state management and React Query for product data fetching.
"""
            elif template_type == "portfolio":
                template_prompt = """
Generate a professional portfolio website with these features:

1. Pages:
   - Home: Introduction, featured projects, and skills overview
   - Projects/Work: Complete portfolio of work with filtering options
   - Project Detail: In-depth case studies with images, challenges, and outcomes
   - About: Personal/professional bio with experience and education
   - Contact: Contact form with social media links
   - Resume/CV: Professional experience in a structured format

2. Components:
   - Hero section with personal branding statement
   - Project cards with thumbnails and categories
   - Skills/technology showcase with visual indicators
   - Testimonials from clients/employers
   - Image lightbox/gallery for project showcases
   - Timeline for experience/education
   - Call-to-action sections for hiring/contact

3. Design Patterns:
   - Personal branding consistency
   - Visual hierarchy emphasizing work samples
   - Smooth animations and transitions
   - Balanced white space
   - Case study layouts that tell stories
   - Strategic use of color to highlight achievements
   - Responsive design that showcases work on all devices

Focus on showcasing the portfolio owner's unique skills and work while maintaining fast load times and visual impact.
"""
            else:
                # Default general template
                template_prompt = """
Generate a professional website with these features:

1. Pages:
   - Home: Main landing page with key information
   - About: Information about the organization/person
   - Services/Work: Showcase of offerings
   - Contact: Contact information and form

2. Components:
   - Navigation with responsive mobile view
   - Footer with links and information
   - Call-to-action sections
   - Content sections with images and text

3. Design Patterns:
   - Clean, modern design
   - Responsive layouts
   - Consistent typography
   - Accessible color scheme

Use Next.js App Router and Tailwind CSS for styling.
"""
        
        # Append additional requirements if provided
        if additional_requirements:
            template_prompt += f"\n\nAdditional Requirements:\n{additional_requirements}"
        
        return self.get_system_prompt() + "\n\n" + template_prompt


# Create a global instance of the PromptManager
prompt_manager = PromptManager()


def get_prompt_manager() -> PromptManager:
    """
    Get the global PromptManager instance.
    
    Returns:
        The global PromptManager instance
    """
    return prompt_manager