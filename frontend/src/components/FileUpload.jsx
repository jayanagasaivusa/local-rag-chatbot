import { useCallback, useRef, useState } from 'react';
import { AlertCircle, CheckCircle2, FileText, Loader2, UploadCloud } from 'lucide-react';
import { uploadFile } from '../api';

const ACCEPTED_EXTENSIONS = ['.pdf', '.xlsx', '.xls', '.html', '.htm'];

/**
 * Drag-and-drop (or click-to-browse) upload zone. Tracks per-upload status
 * so the user gets clear feedback while a document is being processed and
 * embedded into the vector store.
 */
export default function FileUpload({ onUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState('idle'); // idle | uploading | success | error
  const [statusMessage, setStatusMessage] = useState('');
  const [history, setHistory] = useState([]);
  const inputRef = useRef(null);

  const isValidFile = (file) =>
    ACCEPTED_EXTENSIONS.some((ext) => file.name.toLowerCase().endsWith(ext));

  const processFile = useCallback(
    async (file) => {
      if (!file) return;

      if (!isValidFile(file)) {
        setStatus('error');
        setStatusMessage(`Unsupported file type. Allowed: ${ACCEPTED_EXTENSIONS.join(', ')}`);
        return;
      }

      setStatus('uploading');
      setStatusMessage(`Processing "${file.name}"...`);

      try {
        const result = await uploadFile(file);
        setStatus('success');
        setStatusMessage(`Added ${result.chunks_added} chunks from "${result.filename}"`);
        setHistory((prev) => [{ name: result.filename, chunks: result.chunks_added }, ...prev]);
        onUploaded?.(result);
      } catch (err) {
        setStatus('error');
        setStatusMessage(err.message || 'Upload failed.');
      }
    },
    [onUploaded],
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      processFile(file);
    },
    [processFile],
  );

  const handleBrowse = (e) => {
    const file = e.target.files?.[0];
    processFile(file);
    e.target.value = '';
  };

  return (
    <div className="flex flex-col gap-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`group flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-4 py-9 text-center transition-all ${
          isDragging
            ? 'border-violet-400 bg-indigo-50'
            : 'border-indigo-200 bg-white/60 hover:border-violet-300 hover:bg-indigo-50/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          onChange={handleBrowse}
        />

        <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-indigo-100 transition-transform group-hover:scale-105">
          <UploadCloud
            size={20}
            className="text-indigo-500 transition-colors group-hover:text-violet-600"
            strokeWidth={1.75}
          />
        </div>
        <p className="text-sm font-medium text-slate-700">
          Drag & drop a file, or <span className="text-indigo-600 underline">browse</span>
        </p>
        <p className="mt-1 text-xs text-slate-400">PDF, Excel (.xlsx/.xls), or HTML</p>
      </div>

      {status !== 'idle' && (
        <div
          className={`flex items-center gap-2 rounded-xl px-3.5 py-2.5 text-xs font-medium ${
            status === 'uploading'
              ? 'bg-blue-50 text-blue-700'
              : status === 'success'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700'
          }`}
        >
          {status === 'uploading' && <Loader2 size={14} className="shrink-0 animate-spin" />}
          {status === 'success' && <CheckCircle2 size={14} className="shrink-0" />}
          {status === 'error' && <AlertCircle size={14} className="shrink-0" />}
          <span className="leading-snug">{statusMessage}</span>
        </div>
      )}

      {history.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Ingested documents
          </p>
          <ul className="scrollbar-thin max-h-52 space-y-1.5 overflow-y-auto">
            {history.map((doc, idx) => (
              <li
                key={idx}
                className="flex items-center justify-between gap-2 rounded-xl border border-slate-100 bg-white px-3.5 py-2.5 text-sm shadow-sm"
              >
                <span className="flex min-w-0 items-center gap-2 truncate text-slate-600">
                  <FileText size={14} className="shrink-0 text-slate-400" />
                  <span className="truncate">{doc.name}</span>
                </span>
                <span className="shrink-0 rounded-full bg-indigo-50 px-2 py-0.5 text-[11px] font-medium text-indigo-600">
                  {doc.chunks} chunks
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
