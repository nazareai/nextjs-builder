"""
Tests for the WebsiteBuilder class.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from nextjs_builder.generator.website_builder import WebsiteBuilder


@pytest.fixture
def mock_llm_manager():
    """
    Fixture for mocking the LLMManager.
    """
    with patch('nextjs_builder.llm.langchain_setup.LLMManager') as mock:
        # Mock the generate_text method to return a simple response
        instance = mock.return_value
        instance.generate_text.return_value = "```tsx\nexport default function Component() {\n  return <div>Test</div>;\n}\n```"
        yield instance


@pytest.fixture
def mock_template_manager():
    """
    Fixture for mocking the TemplateManager.
    """
    with patch('nextjs_builder.templates.template_manager.get_template_manager') as mock:
        # Mock the get_template method to return a simple template
        instance = mock.return_value
        mock_template = MagicMock()
        mock_template.name = "general"
        mock_template.components = ["Header", "Footer"]
        mock_template.pages = ["Home", "About"]
        mock_template.structure = {
            "directories": ["app/components", "app/lib"],
            "files": []
        }
        instance.get_template.return_value = mock_template
        yield instance


@pytest.fixture
def mock_installer():
    """
    Fixture for mocking the Next.js installer.
    """
    with patch('nextjs_builder.installer.nextjs_installer.create_nextjs_project') as mock_create:
        with patch('nextjs_builder.installer.nextjs_installer.install_dependencies') as mock_install:
            mock_create.return_value = True
            mock_install.return_value = True
            yield (mock_create, mock_install)


@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Fixture for creating a temporary output directory.
    """
    output_dir = tmp_path / "website"
    output_dir.mkdir()
    return output_dir


def test_website_builder_initialization():
    """Test that WebsiteBuilder initializes properly."""
    # Mock the necessary dependencies
    with patch('nextjs_builder.config.load_config') as mock_config:
        with patch('nextjs_builder.templates.template_manager.get_template_manager') as mock_tm:
            with patch('nextjs_builder.llm.prompt_manager.get_prompt_manager'):
                with patch('nextjs_builder.llm.langchain_setup.LLMManager'):
                    # Set up the mocks
                    mock_config.return_value = {"llm": {"model": "test", "temperature": 0.7, "max_tokens": 1000}}
                    mock_template = MagicMock()
                    mock_tm.return_value.get_template.return_value = mock_template
                    
                    # Create the WebsiteBuilder
                    builder = WebsiteBuilder(
                        description="Test website",
                        template_name="general",
                        output_dir="./test_output"
                    )
                    
                    # Check that the builder was initialized correctly
                    assert builder.description == "Test website"
                    assert builder.template_name == "general"
                    assert builder.output_dir == Path("./test_output").resolve()
                    assert builder.auth is False
                    assert builder.database is None
                    assert builder.verbose is False


@patch('nextjs_builder.config.load_config')
@patch('nextjs_builder.llm.prompt_manager.get_prompt_manager')
def test_generate_requirements(mock_pm, mock_config, mock_llm_manager, mock_template_manager):
    """Test the _generate_requirements method."""
    # Set up the mocks
    mock_config.return_value = {"llm": {"model": "test", "temperature": 0.7, "max_tokens": 1000}}
    mock_llm_manager.generate_text.return_value = """
    {
      "pages": [
        { "name": "Home", "route": "/", "purpose": "Main landing page" }
      ],
      "components": [
        { "name": "Header", "purpose": "Navigation and branding" }
      ],
      "features": [
        { "name": "Responsive Design", "description": "Works on all devices" }
      ],
      "styling": {
        "colorScheme": "Light with blue accents",
        "typography": "Modern sans-serif"
      },
      "seo": {
        "title": "Test Website",
        "description": "Test description"
      }
    }
    """
    
    # Create the WebsiteBuilder
    builder = WebsiteBuilder(
        description="Test website",
        template_name="general",
        output_dir="./test_output"
    )
    
    # Override the LLM manager with our mock
    builder.llm_manager = mock_llm_manager
    
    # Get requirements
    requirements = builder._generate_requirements()
    
    # Check that the llm_manager.generate_text was called
    assert mock_llm_manager.generate_text.called
    
    # Check the requirements
    assert "pages" in requirements
    assert "components" in requirements
    assert "features" in requirements
    assert "styling" in requirements
    assert "seo" in requirements


@patch('nextjs_builder.config.load_config')
@patch('nextjs_builder.llm.prompt_manager.get_prompt_manager')
def test_generate_component(mock_pm, mock_config, mock_llm_manager, mock_template_manager):
    """Test the _generate_component method."""
    # Set up the mocks
    mock_config.return_value = {"llm": {"model": "test", "temperature": 0.7, "max_tokens": 1000}}
    mock_llm_manager.generate_text.return_value = """
    ```tsx
    import React from 'react';
    
    interface HeaderProps {
      title: string;
    }
    
    export default function Header({ title }: HeaderProps) {
      return (
        <header className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <h1 className="text-xl font-bold">{title}</h1>
          </div>
        </header>
      );
    }
    ```
    """
    
    # Create the WebsiteBuilder
    builder = WebsiteBuilder(
        description="Test website",
        template_name="general",
        output_dir="./test_output"
    )
    
    # Override the LLM manager with our mock
    builder.llm_manager = mock_llm_manager
    
    # Generate a component
    component = builder._generate_component("Header", "Navigation and branding")
    
    # Check that the llm_manager.generate_text was called
    assert mock_llm_manager.generate_text.called
    
    # Check the component
    assert "export default function Header" in component
    assert "HeaderProps" in component
    assert "React" in component


@pytest.mark.skip(reason="Integration test requiring actual Next.js installation")
def test_website_builder_generate(temp_output_dir, mock_llm_manager, mock_template_manager, mock_installer):
    """
    Integration test for the generate method.
    This test is skipped by default because it requires actual Next.js installation.
    """
    # Create the WebsiteBuilder
    builder = WebsiteBuilder(
        description="Test website",
        template_name="general",
        output_dir=str(temp_output_dir),
    )
    
    # Override the LLM manager with our mock
    builder.llm_manager = mock_llm_manager
    
    # Generate the website
    result = builder.generate()
    
    # Check that the website was generated successfully
    assert result is True
    
    # Check that the installer was called
    mock_create, mock_install = mock_installer
    assert mock_create.called
    assert mock_install.called
    
    # Check that the output directory contains expected files
    # This would require more mocking to actually work
    # assert (temp_output_dir / "app" / "page.tsx").exists()
    # assert (temp_output_dir / "app" / "layout.tsx").exists()


if __name__ == "__main__":
    pytest.main(["-v", "test_website_builder.py"])