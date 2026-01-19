/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Kometa brand colors
        kometa: {
          gold: '#e5a00d',
          'gold-light': '#f0b020',
          'gold-dark': '#cc8f0c',
        },
        // Semantic status colors
        success: {
          DEFAULT: '#22c55e',
          bg: 'rgba(34, 197, 94, 0.1)',
        },
        warning: {
          DEFAULT: '#f59e0b',
          bg: 'rgba(245, 158, 11, 0.1)',
        },
        error: {
          DEFAULT: '#ef4444',
          bg: 'rgba(239, 68, 68, 0.1)',
        },
        info: {
          DEFAULT: '#3b82f6',
          bg: 'rgba(59, 130, 246, 0.1)',
        },
        // Surface colors (using CSS variables for theme support)
        surface: {
          base: 'var(--bg-base)',
          primary: 'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          tertiary: 'var(--bg-tertiary)',
          elevated: 'var(--bg-elevated)',
        },
        // Border colors
        border: {
          DEFAULT: 'var(--border-color)',
          subtle: 'var(--border-subtle)',
          strong: 'var(--border-strong)',
        },
        // Text colors
        content: {
          DEFAULT: 'var(--text-color)',
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
          disabled: 'var(--text-disabled)',
          inverse: 'var(--text-inverse)',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: ['SF Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace'],
      },
      fontSize: {
        xs: ['11px', { lineHeight: '1.25' }],
        sm: ['13px', { lineHeight: '1.25' }],
        base: ['14px', { lineHeight: '1.5' }],
        md: ['16px', { lineHeight: '1.5' }],
        lg: ['18px', { lineHeight: '1.5' }],
        xl: ['24px', { lineHeight: '1.25' }],
        '2xl': ['32px', { lineHeight: '1.25' }],
      },
      spacing: {
        0: '0',
        0.5: '2px',
        1: '4px',
        2: '8px',
        3: '12px',
        4: '16px',
        5: '24px',
        6: '32px',
        8: '48px',
        10: '64px',
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        full: '9999px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(0, 0, 0, 0.2)',
        md: '0 4px 12px rgba(0, 0, 0, 0.25)',
        lg: '0 8px 24px rgba(0, 0, 0, 0.3)',
        xl: '0 16px 48px rgba(0, 0, 0, 0.4)',
        inset: 'inset 0 1px 2px rgba(0, 0, 0, 0.2)',
        focus: '0 0 0 3px rgba(229, 160, 13, 0.3)',
        'focus-error': '0 0 0 3px rgba(239, 68, 68, 0.3)',
      },
      maxWidth: {
        sm: '640px',
        md: '960px',
        lg: '1200px',
        xl: '1400px',
      },
      transitionDuration: {
        fast: '100ms',
        normal: '150ms',
        slow: '300ms',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography'),
  ],
};
