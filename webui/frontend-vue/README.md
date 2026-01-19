# Kometa Web UI - Vue 3 Frontend

Modern Vue 3 + TypeScript + Vite frontend for the Kometa Web UI.

## Tech Stack

- **Vue 3** - Composition API
- **TypeScript** - Type safety
- **Vite** - Build tool with HMR
- **Pinia** - State management
- **TanStack Query** - Server state & caching
- **Tailwind CSS** - Utility-first styling
- **Vitest** - Unit testing

## Development

### Prerequisites

- Node.js 20+
- npm 10+

### Setup

```bash
# Install dependencies
npm install

# Start development server (with API proxy)
npm run dev

# The dev server runs on http://localhost:5173
# API requests are proxied to http://localhost:8000
```

### Backend

Make sure the FastAPI backend is running:

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run test` | Run unit tests |
| `npm run test:coverage` | Run tests with coverage |
| `npm run lint` | Lint code |
| `npm run lint:fix` | Fix lint errors |
| `npm run format` | Format code with Prettier |
| `npm run type-check` | Check TypeScript types |

## Project Structure

```
src/
├── api/                 # API client & TanStack Query hooks
├── assets/
│   └── styles/          # Global styles & Tailwind config
├── components/
│   ├── common/          # Reusable UI components
│   ├── layout/          # Layout components (Header, Sidebar)
│   └── tabs/            # Tab content components
├── composables/         # Vue composables (hooks)
├── stores/              # Pinia stores
├── types/               # TypeScript type definitions
├── App.vue              # Root component
└── main.ts              # Application entry point
```

## Building for Production

```bash
npm run build
```

Output is in `dist/` directory. The Dockerfile will copy this to the final image.

## Docker

Use the Vue-specific Dockerfile:

```bash
# From webui directory
docker build -f Dockerfile.vue -t kometa-webui:vue .

# Or use docker-compose
docker-compose -f docker-compose.vue.yml up -d --build
```
