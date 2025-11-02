# Frontend CSS Architecture

The CSS has been separated into modular files for better organization and easier debugging.

## File Structure

```
frontend/src/
├── index.css                          # Global styles & Tailwind base
├── App.css                            # Main app container styles
└── components/
    ├── Header.css                     # Header component styles
    ├── UploadSection.css              # Upload form styles
    ├── ResultsSection.css             # Results display styles
    └── LoadingSpinner.css             # Loading animation styles
```

## File Descriptions

### `index.css` (Global Styles)
- Tailwind CSS directives
- Base body styles
- Custom scrollbar styles
- **No component-specific styles**

### `App.css` (Main Application)
Contains styles for:
- `.app-container` - Main app wrapper with gradient background
- `.hero-title`, `.hero-subtitle`, `.hero-description` - Hero section
- `.error-alert` - Error message display
- `.empty-state` - Empty results placeholder
- `.feature-cards`, `.feature-card` - Feature showcase section
- `.app-footer` - Footer styles

### `Header.css` (Header Component)
Contains styles for:
- `.header-container` - Header wrapper
- `.header-brand` - Logo and branding
- `.header-logo` - Logo icon
- `.theme-toggle-btn` - Theme switcher button
- `.header-nav` - Navigation links

### `UploadSection.css` (Upload Form)
Contains styles for:
- `.upload-card` - Form container
- `.form-group`, `.form-label` - Form elements
- `.form-input`, `.form-textarea` - Input fields
- `.dropzone` - File upload drag-and-drop area
- `.file-preview` - Selected file display
- `.submit-btn` - Submit button with loading state

### `ResultsSection.css` (Results Display)
Contains styles for:
- `.score-card` - Match score display with variants (excellent, good, moderate, low)
- `.info-card` - Candidate information card
- `.summary-card` - AI summary display
- `.skills-card` - Skills extraction display
- `.metadata-card` - Analysis metadata
- `.action-buttons` - Action button group

### `LoadingSpinner.css` (Loading Animation)
Contains styles for:
- `.loading-container` - Loading state wrapper
- `.spinner-wrapper`, `.spinner-circle` - Animated spinner
- `.progress-steps` - Step-by-step progress indicator
- `.step-indicator` - Individual step states (completed, active, pending)

## Component Import Pattern

Each component imports its corresponding CSS file:

```jsx
// Header.jsx
import './Header.css'

// UploadSection.jsx
import './UploadSection.css'

// ResultsSection.jsx
import './ResultsSection.css'

// LoadingSpinner.jsx
import './LoadingSpinner.css'

// App.jsx
import './App.css'
```

## Benefits of This Structure

1. **Better Organization**: Each component's styles are in their own file
2. **Easier Debugging**: Find and fix styling issues quickly
3. **Maintainability**: Update component styles without affecting others
4. **Scalability**: Add new components with their own CSS files
5. **Clear Naming**: Class names clearly indicate their purpose
6. **No Style Conflicts**: Component-specific class names prevent collisions

## Dark Mode Support

All CSS files include dark mode variants using the `.dark` class:

```css
.card {
  background-color: white;
}

.dark .card {
  background-color: rgb(31, 41, 55);
}
```

## Naming Conventions

- **BEM-inspired**: Component-based naming (e.g., `.header-container`, `.header-brand`)
- **Descriptive**: Names clearly indicate purpose (e.g., `.dropzone`, `.file-preview`)
- **State modifiers**: Classes for states (e.g., `.active`, `.disabled`, `.completed`)
- **Variants**: Modifier classes (e.g., `.score-card.excellent`, `.score-card.good`)

## Debugging Tips

1. **Component-specific issues**: Check the component's CSS file
2. **Layout issues**: Check App.css for main structure
3. **Global issues**: Check index.css for base styles
4. **Dark mode issues**: Search for `.dark` class in relevant CSS file
5. **Animation issues**: Check for `@keyframes` and `animation` properties

## Future Enhancements

- Consider CSS Modules for scoped styles
- Add CSS variables for theme customization
- Implement responsive breakpoint mixins
- Add print-specific styles
