"use client";

import { useRef, useState } from "react";

type PIDUploaderProps = {
onFileSelected?: (file: File) => void;
};

export default function PIDUploader({
onFileSelected,
}: PIDUploaderProps) {
const inputRef = useRef<HTMLInputElement>(null);
const [fileName, setFileName] = useState("");
const [dragging, setDragging] = useState(false);

const handleFile = (file?: File) => {
if (!file) return;

const isPDF = file.type === "application/pdf";
const isImage = file.type.startsWith("image/");

if (!isPDF && !isImage) {
  alert("Please upload a PDF or engineering drawing image.");
  return;
}

setFileName(file.name);
onFileSelected?.(file);

};

return (
<div>
<input
ref={inputRef}
type="file"
accept=".pdf,image/*"
className="hidden"
onChange={(event) => {
handleFile(event.target.files?.[0]);
}}
/>

  <button
    type="button"
    onClick={() => inputRef.current?.click()}
    onDragOver={(event) => {
      event.preventDefault();
      setDragging(true);
    }}
    onDragLeave={() => setDragging(false)}
    onDrop={(event) => {
      event.preventDefault();
      setDragging(false);
      handleFile(event.dataTransfer.files?.[0]);
    }}
    className={`w-full rounded-xl border border-dashed p-10 text-center transition ${
      dragging
        ? "border-cyan-300 bg-cyan-400/10"
        : "border-cyan-400/20 bg-cyan-400/5 hover:border-cyan-400/40 hover:bg-cyan-400/10"
    }`}
  >
    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/10">
      <span className="text-xl text-cyan-300">↑</span>
    </div>

    <p className="mt-4 text-sm font-medium text-slate-200">
      Upload P&amp;ID drawing
    </p>

    <p className="mt-2 text-xs text-slate-500">
      Drop a PDF or engineering drawing here, or click to browse
    </p>

    <p className="mt-4 font-mono text-[10px] tracking-wider text-slate-600">
      SUPPORTED: PDF / PNG / JPG / JPEG
    </p>
  </button>

  {fileName && (
    <div className="mt-3 flex items-center justify-between rounded-lg border border-emerald-400/20 bg-emerald-400/5 px-4 py-3">
      <div>
        <p className="text-xs text-emerald-300">
          DRAWING SELECTED
        </p>

        <p className="mt-1 truncate font-mono text-xs text-slate-300">
          {fileName}
        </p>
      </div>

      <span className="text-xs text-emerald-300">
        READY
      </span>
    </div>
  )}
</div>

);
}