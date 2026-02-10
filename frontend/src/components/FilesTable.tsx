import {
  MantineReactTable,
  type MRT_ColumnDef,
  type MRT_PaginationState,
} from "mantine-react-table";
import type { FileMetadata } from "../types/file";
import { Button, TextInput, Group, Stack, Text } from "@mantine/core";
import { useState, useEffect, useCallback, useRef } from "react";
import { getFiles } from "../api/files";
import { Loader, Center } from "@mantine/core";

const FILENAME_DEBOUNCE_MS = 400;

interface Props {
  /** Currently selected file id (for row highlight) */
  selectedFileId?: number | null;
  /** Called when user chooses to view a file's data */
  onSelectFile?: (file: FileMetadata) => void;
  /** Increment to refetch the list (e.g. after upload) */
  refreshKey?: number;
}

export function FilesTable({
  selectedFileId = null,
  onSelectFile,
  refreshKey = 0,
}: Props) {
  const [data, setData] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [rowCount, setRowCount] = useState(0);
  const [pagination, setPagination] = useState<MRT_PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [filenameFilter, setFilenameFilter] = useState("");
  const [debouncedFilename, setDebouncedFilename] = useState("");
  const [uploadedAfter, setUploadedAfter] = useState("");
  const [uploadedBefore, setUploadedBefore] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedFilename(filenameFilter);
      debounceRef.current = null;
    }, FILENAME_DEBOUNCE_MS);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [filenameFilter]);

  const fetchFiles = useCallback(() => {
    setLoading(true);
    const page = pagination.pageIndex + 1;
    const filters = {
      ...(debouncedFilename.trim() && {
        filename_contains: debouncedFilename.trim(),
      }),
      ...(uploadedAfter && { uploaded_after: `${uploadedAfter}T00:00:00` }),
      ...(uploadedBefore && { uploaded_before: `${uploadedBefore}T23:59:59` }),
    };
    getFiles(
      page,
      pagination.pageSize,
      Object.keys(filters).length ? filters : undefined,
    )
      .then((res) => {
        setData(res.data);
        setRowCount(res.total);
      })
      .finally(() => setLoading(false));
  }, [
    pagination.pageIndex,
    pagination.pageSize,
    debouncedFilename,
    uploadedAfter,
    uploadedBefore,
  ]);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles, refreshKey]);

  const clearFilters = useCallback(() => {
    setFilenameFilter("");
    setDebouncedFilename("");
    setUploadedAfter("");
    setUploadedBefore("");
    setPagination((p) => ({ ...p, pageIndex: 0 }));
  }, []);

  const pageCount = Math.ceil(rowCount / pagination.pageSize) || 1;

  const formatSize = (bytes: number | undefined) => {
    if (bytes == null) return "—";
    // Decimal (SI): 1 KB = 1000 B, 1 MB = 1_000_000 B (matches OS/file manager display)
    const mb = bytes / 1_000_000;
    if (mb >= 1) return `${mb.toFixed(2)} MB`;
    const kb = bytes / 1000;
    if (kb >= 1) return `${kb.toFixed(2)} KB`;
    return `${bytes} B`;
  };

  const columns: MRT_ColumnDef<FileMetadata>[] = [
    { accessorKey: "filename", header: "Filename" },
    { accessorKey: "rows", header: "Rows" },
    { accessorKey: "columns", header: "Columns" },
    {
      accessorKey: "size",
      header: "Size",
      Cell: ({ row }) => formatSize(row.original.size),
    },
    {
      accessorKey: "uploaded_at",
      header: "Uploaded At",
      Cell: ({ row }) => {
        const d = row.original.uploaded_at;
        return new Date(d).toISOString().slice(0, 10);
      },
    },
    {
      accessorKey: "actions",
      header: "Actions",
      Cell: ({ row }) => (
        <Button
          variant="light"
          size="xs"
          onClick={() => onSelectFile?.(row.original)}
        >
          View Data
        </Button>
      ),
      size: 120,
    },
  ];

  const hasFilters = Boolean(
    debouncedFilename.trim() || uploadedAfter || uploadedBefore,
  );

  return (
    <Stack gap="sm">
      <Group wrap="nowrap" align="flex-end" gap="xs">
        <TextInput
          placeholder="Filter by filename"
          value={filenameFilter}
          onChange={(e) => setFilenameFilter(e.currentTarget.value)}
          size="xs"
          style={{ minWidth: 140 }}
        />
        <TextInput
          type="date"
          placeholder="From date"
          value={uploadedAfter}
          onChange={(e) => setUploadedAfter(e.currentTarget.value)}
          size="xs"
          style={{ minWidth: 130 }}
        />
        <TextInput
          type="date"
          placeholder="To date"
          value={uploadedBefore}
          onChange={(e) => setUploadedBefore(e.currentTarget.value)}
          size="xs"
          style={{ minWidth: 130 }}
        />
        {hasFilters && (
          <Button variant="subtle" size="xs" onClick={clearFilters}>
            Clear filters
          </Button>
        )}
      </Group>
      {loading && data.length === 0 && (
        <Center h={200}>
          <Loader />
        </Center>
      )}
      {!loading && data.length === 0 && !hasFilters && (
        <Text size="sm" c="dimmed">
          No files yet. Upload a CSV to get started.
        </Text>
      )}
      {!loading && data.length === 0 && hasFilters && (
        <Text size="sm" c="dimmed">
          No files match the current filters.
        </Text>
      )}
      {data.length > 0 && (
        <MantineReactTable
          columns={columns}
          data={data}
          manualPagination
          rowCount={rowCount}
          pageCount={pageCount}
          state={{ pagination, isLoading: loading }}
          onPaginationChange={setPagination}
          mantineTableBodyRowProps={({ row }) => ({
            onClick: () => onSelectFile?.(row.original),
            style: {
              cursor: onSelectFile ? "pointer" : undefined,
              backgroundColor:
                row.original.id === selectedFileId
                  ? "var(--mantine-color-blue-light)"
                  : undefined,
            },
          })}
        />
      )}
    </Stack>
  );
}
