# Frontend Documentation

## Overview
Minimalist Angular frontend for the LangGraph Evol Instruct MVP.

## Setup

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation
```bash
cd frontend/
npm install
```

## Development

### Start development server
```bash
npm start
```

The application will be available at `http://localhost:4200`

### Build for production
```bash
npm run build
```

## Features

### File Upload
- Drag and drop or click to select PDF files
- Multiple file selection support
- Real-time upload progress

### Results Display
- Processing metrics and statistics
- Evolution type distribution
- Questions, answers, and contexts
- Quality scores and validation status

## Architecture

### Components
- `AppComponent` - Main application component
- `AppService` - API communication service

### Styling
- Minimalist CSS design
- Responsive layout
- Clean, modern interface

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- `POST /upload` - Upload PDF documents
- `GET /results/{id}` - Get processing results
- `GET /health` - Health check

## File Structure

```
src/
├── app/
│   ├── app.component.ts
│   ├── app.component.html
│   ├── app.component.css
│   ├── app.service.ts
│   └── app.module.ts
├── styles.css
├── main.ts
└── index.html
``` 