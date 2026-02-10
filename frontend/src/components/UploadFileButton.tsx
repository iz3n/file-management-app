import { Button } from "@mantine/core";
import { useRef, useState } from "react";
import { uploadFile } from "../api/files";
import { IconUpload } from "@tabler/icons-react";

interface Props {
  onSuccess?: () => void;
  onError?: (message: string) => void;
}

export function UploadFileButton({ onSuccess, onError }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      onError?.("Please select a CSV file.");
      e.target.value = "";
      return;
    }
    setUploading(true);
    try {
      await uploadFile(file);
      onSuccess?.();
    } catch (error: any) {
      console.log(error);
      onError?.("Upload failed: " + error.response.data.detail);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        style={{ display: "none" }}
        onChange={handleChange}
      />
      <Button
        leftSection={<IconUpload size={16} />}
        loading={uploading}
        onClick={() => inputRef.current?.click()}
      >
        Upload CSV
      </Button>
    </>
  );
}
