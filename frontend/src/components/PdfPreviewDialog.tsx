import { useCallback, useEffect, useState } from "react";
import { fetchAuthenticatedFile, saveBlob } from "../api";

type PreviewState = {
  title: string;
  url: string;
  filename: string;
  blob: Blob;
};

export function usePdfPreview() {
  const [preview, setPreview] = useState<PreviewState | null>(null);

  const close = useCallback(() => {
    setPreview((current) => {
      if (current?.url) URL.revokeObjectURL(current.url);
      return null;
    });
  }, []);

  useEffect(() => () => {
    if (preview?.url) URL.revokeObjectURL(preview.url);
  }, [preview?.url]);

  async function show(title: string, path: string, filename: string) {
    const blob = await fetchAuthenticatedFile(path);
    const pdf = blob.type.includes("pdf") ? blob : new Blob([blob], { type: "application/pdf" });
    const url = URL.createObjectURL(pdf);
    setPreview((current) => {
      if (current?.url) URL.revokeObjectURL(current.url);
      return { title, url, filename, blob: pdf };
    });
  }

  function download() {
    if (!preview) return;
    saveBlob(preview.blob, preview.filename);
  }

  return { preview, show, close, download };
}

type DialogProps = {
  preview: PreviewState | null;
  onClose: () => void;
  onDownload: () => void;
};

export default function PdfPreviewDialog({ preview, onClose, onDownload }: DialogProps) {
  useEffect(() => {
    if (!preview) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = previous;
    };
  }, [preview, onClose]);

  if (!preview) return null;

  return (
    <div className="pdf-preview" role="dialog" aria-modal="true" aria-labelledby="pdf-preview-title">
      <button type="button" className="pdf-preview__backdrop" aria-label="Đóng xem trước" onClick={onClose} />
      <div className="pdf-preview__panel">
        <header className="pdf-preview__head">
          <h2 id="pdf-preview-title">{preview.title}</h2>
          <div className="pdf-preview__actions">
            <button type="button" onClick={onDownload}>
              Tải xuống
            </button>
            <button type="button" className="secondary" onClick={onClose}>
              Đóng
            </button>
          </div>
        </header>
        <iframe className="pdf-preview__frame" title={preview.title} src={preview.url} />
      </div>
    </div>
  );
}
