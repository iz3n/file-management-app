import api from "./provider";
import type { GetFilesResponse, GetFileDataResponse } from "../types/file";

export interface GetFilesFilters {
  filename_contains?: string;
  uploaded_after?: string;  // ISO 8601 date or datetime
  uploaded_before?: string;
}

export async function getFiles(
  page: number = 1,
  pageSize: number = 10,
  filters?: GetFilesFilters
) {
  const params: Record<string, string | number> = {
    page,
    page_size: pageSize,
  };
  if (filters?.filename_contains?.trim()) {
    params.filename_contains = filters.filename_contains.trim();
  }
  if (filters?.uploaded_after) {
    params.uploaded_after = filters.uploaded_after;
  }
  if (filters?.uploaded_before) {
    params.uploaded_before = filters.uploaded_before;
  }
  const res = await api.get<GetFilesResponse>(`/files`, { params });
  return res.data;
}

/** Fetch paginated CSV data. Use file.id (database primary key) for the URL. */
export async function getFileData(
  file_id: number,
  page: number = 1,
  pageSize: number = 10
) {
  const res = await api.get<GetFileDataResponse>(
    `/files/${file_id}/data`,
    { params: { page, page_size: pageSize } }
  );
  return res.data;
}


export async function uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
  
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  
    return response.data;
  }
  