import { useState, useCallback } from "react";
import { FilesTable } from "../components/FilesTable";
import { FileDataTable } from "../components/FileDataTable";
import { UploadFileButton } from "../components/UploadFileButton";
import type { FileMetadata } from "../types/file";
import {
  Container,
  Title,
  Flex,
  Paper,
  Text,
  Stack,
  Alert,
} from "@mantine/core";

export function FilesPage() {
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [uploadMessage, setUploadMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleUploadSuccess = useCallback(() => {
    setRefreshKey((k) => k + 1);
    setUploadMessage({ type: "success", text: "File uploaded. The list will update." });
  }, []);

  const handleUploadError = useCallback((message: string) => {
    setUploadMessage({ type: "error", text: message });
  }, []);

  return (
    <Container fluid py="md">
      <Stack gap="lg">
        <Flex justify="space-between" align="center" wrap="wrap" gap="md">
          <Title order={2}>CSV Files</Title>
          <UploadFileButton
            onSuccess={handleUploadSuccess}
            onError={handleUploadError}
          />
        </Flex>
        {uploadMessage && (
          <Alert
            color={uploadMessage.type === "success" ? "green" : "red"}
            title={uploadMessage.type === "success" ? "Upload complete" : "Upload failed"}
            onClose={() => setUploadMessage(null)}
            withCloseButton
          >
            {uploadMessage.text}
          </Alert>
        )}

        <Flex
          direction={{ base: "column", md: "row" }}
          gap="lg"
          align="stretch"
          style={{ minHeight: 400 }}
        >
          <Paper
            withBorder
            p="md"
            style={{ flex: "0 0 min(100%, 420px)" }}
            radius="md"
          >
            <Text size="sm" fw={600} mb="xs" c="dimmed">
              File list
            </Text>
            <FilesTable
              selectedFileId={selectedFile?.id ?? null}
              onSelectFile={setSelectedFile}
              refreshKey={refreshKey}
            />
          </Paper>

          <Paper withBorder p="md" style={{ flex: 1 }} radius="md">
            <Text size="sm" fw={600} mb="xs" c="dimmed">
              {selectedFile ? `Data: ${selectedFile.filename}` : "CSV data"}
            </Text>
            <FileDataTable file={selectedFile} />
          </Paper>
        </Flex>
      </Stack>
    </Container>
  );
}
