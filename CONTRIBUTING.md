# Contributing to Stadium Sync

Thank you for your interest in contributing to Stadium Sync! This document provides guidelines for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Redis (optional)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Code Standards

### Backend (Python)

- **Framework**: FastAPI with async/await
- **Type Hints**: All functions must have complete type annotations
- **Docstrings**: Every module, class, and public function must have a docstring
- **Testing**: New features must include test coverage (pytest-asyncio)
- **Formatting**: Follow PEP 8 conventions

### Frontend (TypeScript/React)

- **Components**: Functional components with hooks
- **File Docs**: Every `.tsx`/`.ts` file must have a JSDoc header comment
- **Accessibility**: All interactive elements must have `aria-label` attributes
- **Testing**: Component tests with Vitest + Testing Library

## Pull Request Process

1. Create a feature branch from `develop`
2. Write tests for new functionality
3. Ensure all tests pass: `pytest tests/ -v` and `npm run test`
4. Update documentation if needed
5. Submit a PR with a clear description

## Commit Messages

Use conventional commit format:

```
feat: add eco-vision waste classification
fix: resolve WebSocket reconnection loop
docs: update API documentation
test: add crowd service unit tests
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
