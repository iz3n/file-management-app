import {
  MantineReactTable,
  type MRT_ColumnDef,
  type MRT_PaginationState,
} from "mantine-react-table";
import { useState, useEffect } from "react";
import { getFileData } from "../api/files";
import type { FileMetadata } from "../types/file";
import { Center, Loader, Text, Paper } from "@mantine/core";

interface Props {
  /** Selected file; when null, show empty state */
  file: FileMetadata | null;
}

export function FileDataTable({ file }: Props) {
  const [data, setData] = useState<Record<string, string>[]>([]);
  const [loading, setLoading] = useState(false);
  const [rowCount, setRowCount] = useState(0);
  const [pagination, setPagination] = useState<MRT_PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  useEffect(() => {
    if (!file) {
      setData([]);
      setRowCount(0);
      return;
    }
    setLoading(true);
    const page = pagination.pageIndex + 1;
    getFileData(file.id, page, pagination.pageSize)
      .then((res) => {
        setData(res.data);
        setRowCount(res.total);
      })
      .catch(() => {
        setData([]);
        setRowCount(0);
      })
      .finally(() => setLoading(false));
  }, [file?.id, pagination.pageIndex, pagination.pageSize]);

  const pageCount = Math.ceil(rowCount / pagination.pageSize) || 1;
  const columns: MRT_ColumnDef<Record<string, string>>[] =
    data.length > 0
      ? Object.keys(data[0]).map((key) => ({
          accessorKey: key,
          header: key,
        }))
      : [];

  if (!file) {
    return (
      <Paper p="xl" withBorder>
        <Text c="dimmed" ta="center" size="sm">
          Select a file from the list to view its CSV data.
        </Text>
      </Paper>
    );
  }

  if (loading && data.length === 0) {
    return (
      <Center h={200}>
        <Loader />
      </Center>
    );
  }

  if (data.length === 0 && !loading) {
    return (
      <Paper p="xl" withBorder>
        <Text c="dimmed" ta="center" size="sm">
          No rows in this file.
        </Text>
      </Paper>
    );
  }

  return (
    <MantineReactTable
      columns={columns}
      data={data}
      manualPagination
      rowCount={rowCount}
      pageCount={pageCount}
      state={{ pagination, isLoading: loading }}
      onPaginationChange={setPagination}
    />
  );
}
