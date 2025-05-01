# Next.js & Tailwind Website Builder - Prompt Templates

This document details the prompt templates to be used for generating different types of Next.js websites with our builder module.

## System Base Prompt

This is the foundational system prompt that will be included in all website generation requests:

```
You are a Next.js and Tailwind CSS expert tasked with building high-quality, production-ready websites. You must follow these strict guidelines:

1. Code Architecture:
   - Create a clean, modular component architecture
   - Follow Next.js App Router best practices
   - Use TypeScript with proper typing throughout
   - Implement Server Components and Client Components appropriately
   - Use Server-Side Rendering (SSR) for optimal SEO and performance

2. Styling Requirements:
   - Use only core Tailwind CSS for styling (NO component libraries)
   - Design responsive layouts that work perfectly across all device sizes
   - Follow accessibility best practices (WCAG 2.1 AA compliance)
   - Create consistent, reusable styling patterns
   - Enhance with micro-interactions and transitions where appropriate

3. State Management:
   - Use React Context API for global state
   - Implement React Query for data fetching and server state
   - Create custom hooks for reusable logic
   - Keep components focused on single responsibilities

4. Project Organization:
   - Use Next.js App Router folder structure
   - Organize components logically by feature and function
   - Implement shared UI components in a component library
   - Maintain clear separation of concerns
   
When generating code, produce complete, production-ready files with proper imports, exports, and TypeScript types.
```

## Template-Specific Prompts

### General Website Template

```
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

${additional_requirements}
```

### Blog Website Template

```
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

${additional_requirements}
```

### E-commerce Website Template

```
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

${additional_requirements}
```

### Portfolio Website Template

```
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

${additional_requirements}
```

## Page-Specific Prompts

### Home Page

```
Create a Next.js home page for a ${website_type} website with the following:

1. Structure:
   - Hero section with main value proposition and call to action
   - Key features/benefits section (3-5 key points)
   - ${website_type_specific_section} showcase
   - Testimonials or social proof section
   - Newsletter/contact CTA section

2. Technical Implementation:
   - Use Next.js App Router pattern with TypeScript
   - Implement Server Components for static sections
   - Use Client Components only where interactivity is required
   - Include responsive design using Tailwind CSS
   - Implement optimized images with Next.js Image component

3. Design Requirements:
   - Clean, modern aesthetic with ${styling_preferences}
   - Mobile-first responsive design
   - Clear visual hierarchy
   - Accessible to WCAG 2.1 AA standards

4. Additional Requirements:
   ${additional_requirements}

Provide the complete TypeScript code with proper imports and exports.
```

### Navigation/Layout

```
Create a responsive navigation and layout system for a Next.js ${website_type} website:

1. Structure:
   - Header with logo, navigation links, and appropriate actions (${action_items})
   - Mobile-responsive menu with smooth transitions
   - Footer with site map, contact information, and legal links
   - Main layout wrapper with proper content structure

2. Technical Implementation:
   - Create reusable layout components using the Next.js App Router pattern
   - Use proper TypeScript typing
   - Implement CSS transitions for menu interactions
   - Separate client and server components appropriately

3. Features:
   - Active link highlighting
   - Dropdown/mega menu support (if required)
   - Sticky header option with scroll behavior
   - Mobile drawer/hamburger menu
   - Dark/light theme support (optional)

4. Design Requirements:
   - Clean, accessible design
   - Proper spacing and alignment
   - Consistent with site branding
   - Optimized for all device sizes

Provide the complete TypeScript code with proper imports and exports.
```

## Component-Specific Prompts

### Hero Component

```
Create a modern hero component for a ${website_type} website:

1. Features:
   - Strong headline and supporting text
   - Primary and secondary call-to-action buttons
   - Visual element (image/illustration/animation)
   - Optional: background pattern or gradient

2. Technical Implementation:
   - Responsive design using Tailwind CSS
   - Next.js Image component for optimized images
   - TypeScript with proper prop typing
   - Appropriate use of semantic HTML

3. Variants:
   - Create props to control:
     - Image position (left/right/background)
     - CTA button style and placement
     - Content alignment
     - Background style

4. Design Requirements:
   - Clean, modern aesthetic
   - Strong visual hierarchy
   - Accessible text contrast
   - Mobile-first approach

Provide the complete TypeScript component with props interface and default values.
```

### Card Component

```
Create a versatile card component for a ${website_type} website:

1. Features:
   - Image/media area
   - Title, subtitle, and description
   - Action buttons or links
   - Optional badge or status indicator
   - Hover/focus states

2. Technical Implementation:
   - Use Tailwind CSS for styling
   - TypeScript with comprehensive prop interface
   - Proper accessibility attributes
   - Optional loading state

3. Variants:
   - Horizontal and vertical layout options
   - Different size variants (small, medium, large)
   - Featured/highlighted variant
   - Compact variant without image

4. Design Requirements:
   - Clean, minimal design
   - Consistent spacing
   - Proper text truncation
   - Accessible focus states

Provide the complete TypeScript component with props interface and default values.
```

## State Management Prompts

### React Context Setup

```
Create a React Context setup for ${state_type} in a Next.js application:

1. Requirements:
   - Create a typed context provider using TypeScript
   - Implement state for ${state_requirements}
   - Include actions/reducers for state updates
   - Create custom hooks for consuming the context

2. Technical Implementation:
   - Use React's useContext and createContext
   - Implement proper TypeScript interfaces
   - Create a provider component with children prop
   - Set up initial state and reducer functions

3. Features:
   - Type-safe context operations
   - Memoized values to prevent unnecessary renders
   - Loading and error states
   - Debug logging (optional)

4. Integration:
   - Show how to wrap the application with the provider
   - Demonstrate how to consume the context in components

Provide the complete TypeScript implementation with proper imports and exports.
```

### React Query Setup

```
Create a React Query setup for data fetching in a Next.js application:

1. Requirements:
   - Configure React Query provider
   - Create typed hooks for ${data_requirements} operations
   - Implement proper error handling
   - Set up optimistic updates (where applicable)

2. Technical Implementation:
   - Use @tanstack/react-query package
   - Create custom hooks for common queries
   - Implement SSR support with hydration
   - Use TypeScript for complete type safety

3. Features:
   - Caching and invalidation strategies
   - Loading, error, and success states
   - Pagination or infinite loading (if needed)
   - Mutation functions with proper typing

4. Integration:
   - Show how to set up the QueryClientProvider
   - Demonstrate usage in components
   - Show how to handle loading and error states

Provide the complete TypeScript implementation with proper imports and exports.
```

## Optional Features Prompts

### Authentication Setup

```
Create an authentication system for a Next.js application:

1. Requirements:
   - User registration and login
   - Password reset functionality
   - Protected routes/pages
   - Remember me functionality
   - Session management

2. Technical Implementation:
   - Use Next.js App Router middleware
   - Create authentication context provider
   - Implement secure form handling with validation
   - Use proper HTTP-only cookies for security

3. Features:
   - Login/signup forms with validation
   - User profile management
   - Session timeout handling
   - Loading and error states

4. Security Considerations:
   - CSRF protection
   - Input sanitization
   - Rate limiting
   - Secure password storage

Provide the complete TypeScript implementation with proper imports and exports.
```

### Database Integration

```
Create a ${database_type} integration for a Next.js application:

1. Requirements:
   - Set up ${database_type} connection
   - Create data models for ${model_requirements}
   - Implement CRUD operations
   - Handle connection pooling and errors

2. Technical Implementation:
   - Use appropriate client library
   - Set up environment variables for connection
   - Create utility functions for database operations
   - Implement proper error handling and retries

3. Features:
   - Type-safe database operations
   - Connection pooling for efficiency
   - Logging and monitoring capabilities
   - Migration management (where applicable)

4. Integration:
   - Show how to use in API routes
   - Demonstrate usage in server components
   - Proper error handling patterns

Provide the complete TypeScript implementation with proper imports and exports.
```

## Complete Website Generation

For generating complete websites, we'll combine these prompts with proper variable substitution based on the user's requirements and selected template.

The process will involve:

1. Selecting the appropriate base template (general, blog, e-commerce, portfolio)
2. Customizing the template with user-provided requirements
3. Breaking down the website generation into smaller component and page requests
4. Assembling the complete project structure

The modular nature of these prompts allows us to generate websites piece by piece while maintaining consistency across the entire project.