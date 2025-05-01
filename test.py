#!/usr/bin/env python3
"""
Command-line entry point for Next.js & Tailwind website builder.

Usage:
  python test.py "Build a company website with a home page, about page, and contact form"

Options:
  --template, -t    Website template to use (general, blog, ecommerce, portfolio)
  --auth/--no-auth  Include authentication
  --db              Database integration (none, mongodb, postgres, supabase)
  --output, -o      Output directory for the website
  --verbose, -v     Enable verbose logging
  --skip-validation Skip validation and fixing steps
  --validation-timeout Timeout for validation process in seconds (default: 60)
"""
import sys
from nextjs_builder.cli import main

if __name__ == "__main__":
    # Set default timeout lower for faster testing
    if '--validation-timeout' not in sys.argv and '-t' not in sys.argv:
        sys.argv.extend(['--validation-timeout', '60'])
    
    # Default to skip validation if not explicitly specified
    if '--skip-validation' not in sys.argv and '--no-skip-validation' not in sys.argv:
        print("Note: Using --skip-validation by default. Use --no-skip-validation to enable validation.")
        sys.argv.append('--skip-validation')
    
    main()