export interface FileMetadata {
  id: number;
  filename: string;
  file_path?: string;
  rows: number;
  columns: number;
  uploaded_at: string;
  size?: number;
}

export interface GetFilesResponse {
  data: FileMetadata[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GetFileDataResponse {
  data: Record<string, string>[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

  