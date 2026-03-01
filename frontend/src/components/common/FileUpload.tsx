import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accept?: Record<string, string[]>;
  label?: string;
  selectedFile?: File | null;
}

export default function FileUpload({
  onFileSelect,
  accept = {
    'text/csv': ['.csv'],
    'text/plain': ['.txt'],
    'application/octet-stream': ['.s2p', '.s1p'],
  },
  label = 'Drop file here or click to browse',
  selectedFile,
}: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
        ${isDragActive
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-surface-300 dark:border-surface-600 hover:border-primary-400'
        }`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto mb-2 text-surface-400" size={24} />
      {selectedFile ? (
        <p className="text-sm text-primary-600 dark:text-primary-400 font-medium">
          {selectedFile.name}
        </p>
      ) : (
        <p className="text-sm text-surface-500">{label}</p>
      )}
      <p className="text-xs text-surface-400 mt-1">CSV, TXT, S2P files</p>
    </div>
  );
}
