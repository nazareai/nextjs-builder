"""
File operation utilities for Next.js & Tailwind website builder.

This module provides utility functions for file operations.
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from rich.console import Console

# Initialize console for pretty output
console = Console()


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path to ensure exists
        
    Returns:
        The Path object for the directory
    """
    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def write_file(path: Union[str, Path], content: str) -> bool:
    """
    Write content to a file, creating parent directories if necessary.
    
    Args:
        path: The file path
        content: The content to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return True
    except Exception as e:
        console.print(f"[bold red]Error writing file {path}:[/bold red] {e}")
        return False


def read_file(path: Union[str, Path]) -> Optional[str]:
    """
    Read content from a file.
    
    Args:
        path: The file path
        
    Returns:
        The file content, or None if the file couldn't be read
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading file {path}:[/bold red] {e}")
        return None


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        src: The source file path
        dst: The destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dst_path = Path(dst)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        console.print(f"[bold red]Error copying file from {src} to {dst}:[/bold red] {e}")
        return False


def load_json(path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Load JSON from a file.
    
    Args:
        path: The file path
        
    Returns:
        The parsed JSON, or None if the file couldn't be parsed
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]Error loading JSON from {path}:[/bold red] {e}")
        return None


def save_json(path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> bool:
    """
    Save data as JSON to a file.
    
    Args:
        path: The file path
        data: The data to save
        indent: The indentation level for the JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
            
        return True
    except Exception as e:
        console.print(f"[bold red]Error saving JSON to {path}:[/bold red] {e}")
        return False


def list_files(
    directory: Union[str, Path], 
    pattern: Optional[str] = None, 
    recursive: bool = False
) -> List[Path]:
    """
    List files in a directory, optionally filtered by pattern.
    
    Args:
        directory: The directory to list files from
        pattern: Optional glob pattern to filter files
        recursive: Whether to list files recursively
        
    Returns:
        List of file paths
    """
    try:
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return []
        
        if recursive:
            if pattern:
                return list(directory_path.rglob(pattern))
            else:
                return [p for p in directory_path.rglob("*") if p.is_file()]
        else:
            if pattern:
                return list(directory_path.glob(pattern))
            else:
                return [p for p in directory_path.glob("*") if p.is_file()]
    except Exception as e:
        console.print(f"[bold red]Error listing files in {directory}:[/bold red] {e}")
        return []


def delete_file(path: Union[str, Path]) -> bool:
    """
    Delete a file.
    
    Args:
        path: The file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(path).unlink()
        return True
    except Exception as e:
        console.print(f"[bold red]Error deleting file {path}:[/bold red] {e}")
        return False


def clean_directory(directory: Union[str, Path]) -> bool:
    """
    Clean a directory by removing all its contents.
    
    Args:
        directory: The directory to clean
        
    Returns:
        True if successful, False otherwise
    """
    try:
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return True
        
        for item in directory_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
                
        return True
    except Exception as e:
        console.print(f"[bold red]Error cleaning directory {directory}:[/bold red] {e}")
        return False


def is_valid_path(path: Union[str, Path]) -> bool:
    """
    Check if a path is valid.
    
    Args:
        path: The path to check
        
    Returns:
        True if the path is valid, False otherwise
    """
    try:
        Path(path).resolve()
        return True
    except Exception:
        return False