# Frontend

React + TypeScript + Vite frontend for the file management app. Lists uploaded CSV files, supports filters and pagination, and displays paginated CSV data in a table.

## Features

- **File list**: Paginated table of uploaded files (filename, size, rows, columns, upload date)
- **Filters**: Filename substring (debounced), date range (uploaded after/before)
- **File data view**: Select a file to see its CSV data in a second table with pagination
- **Upload**: Button to upload a new CSV file; list refreshes on success, errors shown in an alert
- **UI**: Mantine components and Mantine React Table

## Tech stack

- **React 19** with **TypeScript**
- **Vite 7** for build and dev server
- **Mantine 7** (core + hooks) for UI
- **Mantine React Table** for file list and data tables
- **Axios** for API calls
- **Tabler Icons** (optional)

## Requirements

- Node.js 18+ (recommended: 20+)
- Backend API running (see `../backend/README.md`) or use Docker Compose from repo root

## Project structure

```
frontend/
├── src/
│   ├── api/           # Axios instance and file API (getFiles, getFileData, uploadFile)
│   ├── components/    # FilesTable, FileDataTable, UploadFileButton
│   ├── pages/         # FilesPage (main screen)
│   ├── types/         # TypeScript types (file metadata, API responses)
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── Dockerfile
```

## Setup (local development)

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Environment**

   Create a `.env` file (or `.env.local`) in `frontend/` with the API base URL the browser will use:

   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

   For Docker, this is usually set as a build arg (e.g. `http://localhost:8000` so the host machine can call the backend).

3. **Run the dev server**

   ```bash
   npm run dev
   ```

   App runs at http://localhost:5173 (or the port Vite prints). Ensure the backend is reachable at the URL set in `VITE_API_BASE_URL` and that CORS allows that origin.

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | TypeScript check + production build (`dist/`) |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |

## API integration

The frontend talks to the backend under `/files`:

- **GET /files** – List files (params: `page`, `page_size`, `filename_contains`, `uploaded_after`, `uploaded_before`)
- **GET /files/:id/metadata** – File metadata by ID
- **GET /files/:id/data** – Paginated CSV data (params: `page`, `page_size`)
- **POST /files/upload** – Upload CSV (multipart form with `file`)

The base URL is taken from `import.meta.env.VITE_API_BASE_URL`. Errors from the API (e.g. 400, 404, 502) are surfaced in the UI (e.g. upload error alert, table empty or error state).

## Docker

The frontend Dockerfile builds a static bundle and serves it with nginx. The API base URL is set at build time via `VITE_API_BASE_URL` (e.g. in `docker-compose.yml` as `http://localhost:8000` for the host). See the project root `README.docker.md` and `docker-compose.yml` for full stack usage.

## Linting and type checking

- **ESLint**: `npm run lint` (see `eslint.config.js`)
- **TypeScript**: run as part of `npm run build` (`tsc -b`)

To tighten type-aware ESLint rules, you can switch to `tseslint.configs.recommendedTypeChecked` (and add `parserOptions.project`) as in the original Vite+React+TS template.
