import { useRef, useState } from "react";
import toast from "react-hot-toast";
import {
  UploadCloud,
  FileText,
  Loader2,
  CheckCircle2,
  Tags,
} from "lucide-react";
import { useDocuments, useUploadDocument } from "../hooks/useDocuments";
import type { UploadResponse } from "../services/types";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { RowSkeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { formatDate } from "../lib/utils";

function docTypeStyle(type: string) {
  const map: Record<string, string> = {
    regulation: "bg-violet-50 text-violet-700",
    work_order: "bg-teal-50 text-teal-700",
    permit: "bg-amber-50 text-amber-700",
    procedure: "bg-slate-100 text-body",
    expert_tacit: "bg-rose-50 text-rose-700",
  };
  return map[type] ?? "bg-slate-100 text-body";
}

export function Documents() {
  const [dragging, setDragging] = useState(false);
  const [lastUpload, setLastUpload] = useState<UploadResponse | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { data, isLoading, isError, refetch } = useDocuments();
  const upload = useUploadDocument();

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    const toastId = toast.loading(`Uploading ${file.name}…`);
    upload.mutate(file, {
      onSuccess: (res) => {
        setLastUpload(res);
        toast.success(
          `Ingested ${res.filename} · ${res.chunk_count} chunks`,
          { id: toastId }
        );
      },
      onError: () => toast.error("Upload failed", { id: toastId }),
    });
  };

  return (
    <PageContainer>
      <PageHeader
        title="Documents"
        subtitle="Ingest regulations, permits, work orders and expert notes into the knowledge base."
      />

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors ${
          dragging
            ? "border-violet-300 bg-violet-50"
            : "border-border bg-card hover:border-violet-200"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-50 text-violet-700">
          {upload.isPending ? (
            <Loader2 size={26} className="animate-spin" />
          ) : (
            <UploadCloud size={26} />
          )}
        </span>
        <p className="mt-4 text-sm font-medium text-body">
          {upload.isPending
            ? "Processing document…"
            : "Drag & drop a document, or click to browse"}
        </p>
        <p className="mt-1 text-xs text-muted">
          PDF, images and text — parsed, embedded and linked automatically
        </p>
      </div>

      {lastUpload && (
        <div className="mt-4 rounded-2xl border border-teal-100 bg-teal-50/60 p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-teal-700">
            <CheckCircle2 size={16} /> {lastUpload.filename} ingested (
            {lastUpload.chunk_count} chunks)
          </div>
          {lastUpload.entities?.equipment_tags?.length > 0 && (
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <Tags size={14} className="text-muted" />
              {lastUpload.entities.equipment_tags.map((t) => (
                <span
                  key={t}
                  className="rounded-lg bg-card px-2 py-0.5 font-mono text-[11px] text-body"
                >
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="mt-8">
        <h2 className="mb-3 text-sm font-semibold text-body">
          Ingested documents
        </h2>
        {isLoading ? (
          <div className="rounded-2xl border border-border bg-card">
            {Array.from({ length: 5 }).map((_, i) => (
              <RowSkeleton key={i} />
            ))}
          </div>
        ) : isError ? (
          <ErrorState
            message="Failed to load documents."
            onRetry={() => refetch()}
          />
        ) : !data || data.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No documents yet"
            message="Upload your first document above to start building the knowledge base."
          />
        ) : (
          <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-background/60">
                <tr className="text-xs font-medium text-muted">
                  <th className="px-4 py-3">Filename</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="hidden px-4 py-3 md:table-cell">Summary</th>
                  <th className="px-4 py-3">Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.map((doc) => (
                  <tr key={doc.id} className="hover:bg-background/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <FileText size={15} className="text-muted" />
                        <span className="font-mono text-xs text-body">
                          {doc.filename}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-lg px-2 py-0.5 font-mono text-[11px] ${docTypeStyle(
                          doc.document_type
                        )}`}
                      >
                        {doc.document_type}
                      </span>
                    </td>
                    <td className="hidden max-w-md px-4 py-3 text-xs text-muted md:table-cell">
                      <span className="line-clamp-2">{doc.summary}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted">
                      {formatDate(doc.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </PageContainer>
  );
}
