"use client";

import { useEffect, useState,type ComponentType, } from "react";
import { createWorker } from "tesseract.js";
import * as pdfjsLib from "pdfjs-dist";
import EngineeringGraphBase from "./components/EngineeringGraph";
type View = "overview" | "pid" | "topology" | "ask" | "evidence";

type EvidenceLocation = {
  tag: string;
  text: string;
  confidence: number;
  x: number;
  y: number;
  width: number;
  height: number;
};
const EngineeringGraph =
  EngineeringGraphBase as ComponentType<{
    selectedComponent: string;
    onSelect: (component: string) => void;
    detectedTags?: string[];
    evidenceLocations?: EvidenceLocation[];
  }>;

export default function Home() {
  const [selectedComponent, setSelectedComponent] = useState("P-101");
  const [activeView, setActiveView] = useState<View>("overview");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState("");
  const [drawingImage, setDrawingImage] = useState("");
  const [zoom, setZoom] = useState(1);

  const [selectedEvidence, setSelectedEvidence] =
    useState<EvidenceLocation | null>(null);

  const [detectedTags, setDetectedTags] = useState<string[]>([]);
  const [evidenceLocations, setEvidenceLocations] = useState<
    EvidenceLocation[]
  >([]);

  const [ocrRunning, setOcrRunning] = useState(false);

  useEffect(() => {
    if (!selectedFile) {
      setFileUrl("");
      setDrawingImage("");
      return;
    }

    const url = URL.createObjectURL(selectedFile);
    setFileUrl(url);

    if (selectedFile.type.startsWith("image/")) {
      setDrawingImage(url);

      return () => {
        URL.revokeObjectURL(url);
      };
    }

    if (selectedFile.type === "application/pdf") {
      let cancelled = false;

      const renderPDF = async () => {
        try {
          const arrayBuffer = await selectedFile.arrayBuffer();

          const pdf = await pdfjsLib.getDocument({
            data: arrayBuffer,
          }).promise;

          const page = await pdf.getPage(1);

          const viewport = page.getViewport({
            scale: 2,
          });

          const canvas = document.createElement("canvas");
          const context = canvas.getContext("2d");

          if (!context) return;

          canvas.width = viewport.width;
          canvas.height = viewport.height;

          await page.render({
  canvas,
  canvasContext: context,
  viewport,
}).promise;
          if (!cancelled) {
            setDrawingImage(canvas.toDataURL("image/png"));
          }
        } catch (error) {
          console.error("PDF rendering failed:", error);
        }
      };

      renderPDF();

      return () => {
        cancelled = true;
        URL.revokeObjectURL(url);
      };
    }

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [selectedFile]);

  const navigation: { id: View; label: string }[] = [
    { id: "overview", label: "OVERVIEW" },
    { id: "pid", label: "P&ID" },
    { id: "topology", label: "TOPOLOGY" },
    { id: "ask", label: "ASK HRIDAY" },
    { id: "evidence", label: "EVIDENCE" },
  ];

  const verifiedCount = evidenceLocations.filter(
    (item) => item.confidence >= 0.75
  ).length;

  const reviewCount = evidenceLocations.filter(
    (item) => item.confidence < 0.75
  ).length;

  const graphRelationCount =
    detectedTags.length > 1 ? detectedTags.length - 1 : 0;

  const averageConfidence =
    evidenceLocations.length > 0
      ? Math.round(
          (evidenceLocations.reduce(
            (sum, item) => sum + item.confidence,
            0
          ) /
            evidenceLocations.length) *
            100
        )
      : 0;

  return (
<main className="min-h-screen bg-[#f5f7fa] text-slate-900">      {/* HEADER */}
     <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-xl">
  <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-3 md:px-6">
    <div className="flex min-w-0 items-center gap-3">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-sky-200 bg-sky-50">
        <span className="font-mono text-sm font-bold text-sky-700">
          H
        </span>
      </div>

      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <h1 className="truncate text-base font-semibold tracking-tight text-slate-900 md:text-lg">
            HRIDAY
          </h1>
          <span className="hidden rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 font-mono text-[9px] tracking-wider text-slate-500 sm:inline">
            GARUD
          </span>
        </div>

        <p className="hidden font-mono text-[9px] tracking-[0.18em] text-slate-400 md:block">
          SOVEREIGN ENGINEERING INTELLIGENCE
        </p>
      </div>
    </div>

    <div className="hidden items-center gap-2 sm:flex">
      <span className="h-2 w-2 rounded-full bg-emerald-500" />
      <span className="font-mono text-[10px] tracking-[0.16em] text-slate-500">
        SYSTEM ONLINE
      </span>
    </div>
  </div>

  <div className="mx-auto max-w-[1600px] overflow-x-auto px-4 pb-3 md:px-6">
    <nav className="flex min-w-max items-center gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1">
      {[
        ["overview", "Overview"],
        ["pid", "P&ID"],
        ["topology", "Topology"],
        ["ask", "Ask HRIDAY"],
        ["evidence", "Evidence"],
      ].map(([view, label]) => (
        <button
          key={view}
          type="button"
          onClick={() => setActiveView(view as View)}
          className={`rounded-lg px-3 py-2 text-xs font-medium transition md:px-4 ${
            activeView === view
              ? "bg-white text-sky-700 shadow-sm ring-1 ring-slate-200"
              : "text-slate-500 hover:bg-white hover:text-slate-800"
          }`}
        >
          {label}
        </button>
      ))}
    </nav>
  </div>
</header>

      <div className="mx-auto max-w-[1600px]">
          {/* OVERVIEW */}
        {activeView === "overview" && (
          <section className="engineering-grid min-h-[calc(100vh-150px)] bg-slate-50 p-4 md:p-6">
            <div className="mx-auto max-w-[1600px]">

              {/* PAGE HEADER */}
              <div className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end">
                <div>
                  <div className="mb-2 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-sky-500" />

                    <p className="font-mono text-[10px] font-semibold tracking-[0.2em] text-sky-600">
                      ENGINEERING INTELLIGENCE
                    </p>
                  </div>

                  <h2 className="text-3xl font-semibold tracking-tight text-slate-900">
                    Analysis Overview
                  </h2>

                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                    Monitor your active engineering document, extracted
                    components, topology relationships, and verification
                    status.
                  </p>
                </div>

                <div className="flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-white px-4 py-2 shadow-sm">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />

                  <span className="font-mono text-[10px] font-semibold tracking-[0.12em] text-emerald-700">
                    ANALYSIS ACTIVE
                  </span>
                </div>
              </div>

              {/* METRICS */}
              <div className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

                {/* COMPONENTS */}
                <div className="command-glass rounded-2xl p-5 transition hover:-translate-y-0.5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-mono text-[10px] font-semibold tracking-[0.14em] text-slate-400">
                        COMPONENTS
                      </p>

                      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                        {detectedTags.length}
                      </p>
                    </div>

                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-50 text-sky-600">
                      ◈
                    </div>
                  </div>

                  <p className="mt-3 text-xs text-slate-400">
                    OCR-detected engineering entities
                  </p>
                </div>

                {/* RELATIONS */}
                <div className="command-glass rounded-2xl p-5 transition hover:-translate-y-0.5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-mono text-[10px] font-semibold tracking-[0.14em] text-slate-400">
                        RELATIONSHIPS
                      </p>

                      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                        {graphRelationCount}
                      </p>
                    </div>

                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                      ⌁
                    </div>
                  </div>

                  <p className="mt-3 text-xs text-slate-400">
                    Provisional topology connections
                  </p>
                </div>

                {/* VERIFIED */}
                <div className="command-glass rounded-2xl p-5 transition hover:-translate-y-0.5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-mono text-[10px] font-semibold tracking-[0.14em] text-slate-400">
                        VERIFIED
                      </p>

                      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                        {verifiedCount}
                      </p>
                    </div>

                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                      ✓
                    </div>
                  </div>

                  <p className="mt-3 text-xs text-slate-400">
                    High-confidence detections
                  </p>
                </div>

                {/* CONFIDENCE */}
                <div className="command-glass rounded-2xl p-5 transition hover:-translate-y-0.5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-mono text-[10px] font-semibold tracking-[0.14em] text-slate-400">
                        CONFIDENCE
                      </p>

                      <p
                        className={`mt-3 text-3xl font-semibold tracking-tight ${
                          averageConfidence >= 75
                            ? "text-emerald-600"
                            : "text-amber-600"
                        }`}
                      >
                        {averageConfidence}%
                      </p>
                    </div>

                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                      ✦
                    </div>
                  </div>

                  <p className="mt-3 text-xs text-slate-400">
                    Average OCR confidence
                  </p>
                </div>
              </div>

              {/* MAIN DASHBOARD */}
              <div className="grid gap-6 xl:grid-cols-12">

                {/* ACTIVE DOCUMENT */}
                <div className="command-glass overflow-hidden rounded-2xl xl:col-span-8">

                  <div className="flex flex-col justify-between gap-4 border-b border-slate-100 px-6 py-5 sm:flex-row sm:items-center">
                    <div>
                      <p className="font-mono text-[10px] font-semibold tracking-[0.16em] text-slate-400">
                        ACTIVE DOCUMENT
                      </p>

                      <h3 className="mt-1 text-lg font-semibold text-slate-900">
                        {selectedFile
                          ? selectedFile.name
                          : "No engineering drawing loaded"}
                      </h3>
                    </div>

                    <button
                      type="button"
                      onClick={() => setActiveView("pid")}
                      className="w-fit rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-600 shadow-sm transition hover:border-sky-200 hover:bg-sky-50 hover:text-sky-700"
                    >
                      Open P&amp;ID →
                    </button>
                  </div>

                  <div className="blueprint-grid relative flex min-h-[360px] items-center justify-center p-8">

                    {drawingImage ? (
                      <img
                        src={drawingImage}
                        alt="Engineering drawing preview"
                        className="max-h-[320px] max-w-full rounded-lg border border-slate-200 bg-white object-contain shadow-lg"
                      />
                    ) : (
                      <div className="text-center">

                        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-sky-200 bg-white text-2xl text-sky-500 shadow-sm">
                          ⌁
                        </div>

                        <p className="mt-4 text-sm font-medium text-slate-700">
                          Engineering drawing workspace
                        </p>

                        <p className="mt-1 text-xs text-slate-400">
                          Upload a P&amp;ID to begin analysis
                        </p>

                        <button
                          type="button"
                          onClick={() => setActiveView("pid")}
                          className="mt-4 rounded-lg bg-sky-600 px-4 py-2 text-xs font-medium text-white shadow-sm transition hover:bg-sky-700"
                        >
                          Upload Drawing →
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* INTELLIGENCE STATUS */}
                <div className="command-glass rounded-2xl xl:col-span-4">

                  <div className="border-b border-slate-100 px-6 py-5">
                    <p className="font-mono text-[10px] font-semibold tracking-[0.16em] text-slate-400">
                      SYSTEM STATUS
                    </p>

                    <h3 className="mt-1 text-lg font-semibold text-slate-900">
                      Intelligence Pipeline
                    </h3>
                  </div>

                  <div className="space-y-1 p-3">

                    {/* DOCUMENT */}
                    <div className="flex items-center justify-between rounded-xl px-4 py-4 hover:bg-slate-50">
                      <div className="flex items-center gap-3">
                        <span
                          className={`h-2 w-2 rounded-full ${
                            selectedFile
                              ? "bg-emerald-500"
                              : "bg-slate-300"
                          }`}
                        />

                        <span className="text-sm text-slate-600">
                          Document ingestion
                        </span>
                      </div>

                      <span
                        className={`font-mono text-[9px] font-semibold ${
                          selectedFile
                            ? "text-emerald-600"
                            : "text-slate-400"
                        }`}
                      >
                        {selectedFile ? "READY" : "WAITING"}
                      </span>
                    </div>

                    {/* OCR */}
                    <div className="flex items-center justify-between rounded-xl px-4 py-4 hover:bg-slate-50">
                      <div className="flex items-center gap-3">
                        <span
                          className={`h-2 w-2 rounded-full ${
                            ocrRunning
                              ? "bg-sky-500"
                              : evidenceLocations.length > 0
                                ? "bg-emerald-500"
                                : "bg-slate-300"
                          }`}
                        />

                        <span className="text-sm text-slate-600">
                          OCR extraction
                        </span>
                      </div>

                      <span
                        className={`font-mono text-[9px] font-semibold ${
                          ocrRunning
                            ? "text-sky-600"
                            : evidenceLocations.length > 0
                              ? "text-emerald-600"
                              : "text-slate-400"
                        }`}
                      >
                        {ocrRunning
                          ? "RUNNING"
                          : evidenceLocations.length > 0
                            ? "READY"
                            : "WAITING"}
                      </span>
                    </div>

                    {/* CLASSIFICATION */}
                    <div className="flex items-center justify-between rounded-xl px-4 py-4 hover:bg-slate-50">
                      <div className="flex items-center gap-3">
                        <span
                          className={`h-2 w-2 rounded-full ${
                            detectedTags.length > 0
                              ? "bg-emerald-500"
                              : "bg-slate-300"
                          }`}
                        />

                        <span className="text-sm text-slate-600">
                          Component classification
                        </span>
                      </div>

                      <span
                        className={`font-mono text-[9px] font-semibold ${
                          detectedTags.length > 0
                            ? "text-emerald-600"
                            : "text-slate-400"
                        }`}
                      >
                        {detectedTags.length > 0
                          ? "READY"
                          : "WAITING"}
                      </span>
                    </div>

                    {/* GRAPH */}
                    <div className="flex items-center justify-between rounded-xl px-4 py-4 hover:bg-slate-50">
                      <div className="flex items-center gap-3">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />

                        <span className="text-sm text-slate-600">
                          Topology engine
                        </span>
                      </div>

                      <span className="font-mono text-[9px] font-semibold text-emerald-600">
                        READY
                      </span>
                    </div>

                    {/* EVIDENCE */}
                    <div className="flex items-center justify-between rounded-xl px-4 py-4 hover:bg-slate-50">
                      <div className="flex items-center gap-3">
                        <span
                          className={`h-2 w-2 rounded-full ${
                            evidenceLocations.length > 0
                              ? "bg-emerald-500"
                              : "bg-slate-300"
                          }`}
                        />

                        <span className="text-sm text-slate-600">
                          Evidence mapping
                        </span>
                      </div>

                      <span
                        className={`font-mono text-[9px] font-semibold ${
                          evidenceLocations.length > 0
                            ? "text-emerald-600"
                            : "text-slate-400"
                        }`}
                      >
                        {evidenceLocations.length > 0
                          ? "READY"
                          : "WAITING"}
                      </span>
                    </div>
                  </div>

                 

                  {/* ASK HRIDAY */}
                  <div className="mx-5 mb-5 rounded-xl border border-sky-100 bg-sky-50/70 p-4">
                    <p className="font-mono text-[9px] font-semibold tracking-[0.14em] text-sky-600">
                      HRIDAY INTELLIGENCE
                    </p>

                    <p className="mt-2 text-xs leading-5 text-slate-600">
                      Ask questions about detected components,
                      relationships, and source evidence.
                    </p>

                    <button
                      type="button"
                      onClick={() => setActiveView("ask")}
                      className="mt-3 text-xs font-semibold text-sky-700 transition hover:text-sky-900"
                    >
                      Ask HRIDAY →
                    </button>
                  </div>
                </div>
              </div>

              {/* QUICK ACTIONS */}
              <div className="mt-6 grid gap-4 md:grid-cols-3">

               <button
  type="button"
  onClick={() => setActiveView("pid")}
  className="group rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-md"
>
  <span className="font-mono text-[10px] font-semibold text-sky-600">
    01
  </span>

  <h3 className="mt-2 font-semibold text-slate-900">
    Inspect P&amp;ID
  </h3>

  <p className="mt-1 text-xs leading-5 text-slate-500">
    Examine the source engineering drawing and run OCR.
  </p>

  <span className="mt-4 block text-xs font-semibold text-sky-600">
    Open workspace →
  </span>
</button>
                <button
                  type="button"
                  onClick={() => setActiveView("topology")}
                  className="group rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md"
                >
                  <span className="font-mono text-[10px] font-semibold text-indigo-600">
                    02
                  </span>

                  <h3 className="mt-2 font-semibold text-slate-900">
                    Explore Topology
                  </h3>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Navigate equipment and process relationships.
                  </p>

                  <span className="mt-4 block text-xs font-semibold text-indigo-600">
                    Open graph →
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveView("ask")}
                  className="group rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-md"
                >
                  <span className="font-mono text-[10px] font-semibold text-emerald-600">
                    03
                  </span>

                  <h3 className="mt-2 font-semibold text-slate-900">
                    Ask HRIDAY
                 </h3>

<p className="mt-1 text-xs leading-5 text-slate-500">                    Ask engineering questions against current drawing data.
                  </p>

                  <span className="mt-4 block text-xs font-semibold text-emerald-600">
                    Query intelligence →
                  </span>
                </button>

              </div>
            </div>
          </section>
        )}
               {/* P&ID */}
        {activeView === "pid" && (
          <section className="engineering-grid p-4 md:p-6">
            <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="font-mono text-[10px] tracking-[0.22em] text-sky-600">
                  SOURCE DOCUMENT
                </p>

                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
                  P&ID Inspection
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Upload, inspect and analyze an engineering drawing.
                </p>
              </div>

              <span
                className={`w-fit rounded-full border px-3 py-1 text-xs font-medium ${
                  selectedFile
                    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                    : "border-amber-200 bg-amber-50 text-amber-700"
                }`}
              >
                {selectedFile ? "DRAWING ACTIVE" : "NO DRAWING"}
              </span>
            </div>

            <div className="mb-4 command-glass rounded-2xl p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
                    DOCUMENT INPUT
                  </p>

                  <p className="mt-2 text-sm font-medium text-slate-800">
                    {selectedFile
                      ? selectedFile.name
                      : "No engineering document selected"}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Supported source: PDF or image
                  </p>
                </div>

                <label className="inline-flex cursor-pointer items-center justify-center rounded-xl border border-sky-200 bg-sky-50 px-5 py-3 text-sm font-medium text-sky-700 transition hover:border-sky-300 hover:bg-sky-100">
                  {selectedFile ? "Replace P&ID" : "Upload P&ID"}

                  <input
                    type="file"
                    accept=".pdf,image/*"
                    className="hidden"
onChange={(event) => {
  const file = event.target.files?.[0] || null;
  setSelectedFile(file);
}}                  />
                </label>
              </div>
            </div>

            <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
              <div className="command-glass hud-corner overflow-hidden rounded-2xl">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
                  <div>
                    <p className="font-mono text-[10px] tracking-[0.16em] text-slate-400">
                      DOCUMENT VIEWER
                    </p>

                    <p className="mt-1 max-w-[420px] truncate text-sm font-medium text-slate-800">
                      {selectedFile?.name || "Awaiting P&ID upload"}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setZoom((value) => Math.max(0.5, value - 0.1))
                      }
                      className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 transition hover:border-sky-300 hover:text-sky-700"
                    >
                      −
                    </button>

                    <span className="min-w-[58px] text-center font-mono text-xs text-slate-500">
                      {Math.round(zoom * 100)}%
                    </span>

                    <button
                      type="button"
                      onClick={() =>
                        setZoom((value) => Math.min(2, value + 0.1))
                      }
                      className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 transition hover:border-sky-300 hover:text-sky-700"
                    >
                      +
                    </button>
                  </div>
                </div>

                <div className="blueprint-grid min-h-[520px] overflow-auto p-4 md:p-6">
                  {drawingImage ? (
                    <div className="flex min-h-[480px] items-center justify-center">
                      <div
                        className="relative origin-center transition-transform duration-200"
                        style={{ transform: `scale(${zoom})` }}
                      >
                        <img
                          src={drawingImage}
                          alt="Uploaded P&ID drawing"
                          className="max-h-[720px] max-w-full rounded-lg border border-slate-300 bg-white shadow-lg"
                        />

                        {evidenceLocations.map((location, index) => (
                          <button
                            key={`${location.tag}-${index}`}
                            type="button"
                            onClick={() => setSelectedEvidence(location)}
                            className={`absolute border-2 transition ${
                              selectedEvidence?.tag === location.tag
                                ? "border-sky-500 bg-sky-400/20"
                                : "border-emerald-400/70 hover:border-sky-500 hover:bg-sky-400/10"
                            }`}
                            style={{
                              left: location.x,
                              top: location.y,
                              width: location.width,
                              height: location.height,
                            }}
                            title={`${location.tag} — ${Math.round(
                              location.confidence * 100
                            )}% confidence`}
                          />
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="flex min-h-[480px] items-center justify-center">
                      <div className="max-w-md text-center">
                        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200 bg-white shadow-sm">
                          <span className="font-mono text-sm font-semibold text-sky-600">
                            P&ID
                          </span>
                        </div>

                        <h3 className="mt-5 text-lg font-semibold text-slate-900">
                          No engineering drawing loaded
                        </h3>

                        <p className="mt-2 text-sm leading-6 text-slate-500">
                          Upload a P&ID above to display the drawing and begin
                          OCR analysis.
                        </p>

                        <label className="mt-5 inline-flex cursor-pointer rounded-xl bg-slate-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-800">
                          Select engineering drawing

                          <input
                            type="file"
                            accept=".pdf,image/*"
                            className="hidden"
onChange={(event) => {
  const file = event.target.files?.[0] || null;
  setSelectedFile(file);
}}                          />
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <aside className="space-y-4">
                <div className="command-glass rounded-2xl p-5">
                  <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
                    DOCUMENT STATUS
                  </p>

                  <div className="mt-4 space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">Source</span>
                      <span className="font-medium text-slate-800">
                        {selectedFile ? "Loaded" : "Waiting"}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">OCR</span>

                      <span
                        className={
                          ocrRunning
                            ? "font-medium text-sky-600"
                            : evidenceLocations.length
                              ? "font-medium text-emerald-600"
                              : "font-medium text-slate-500"
                        }
                      >
                        {ocrRunning
                          ? "Scanning"
                          : evidenceLocations.length
                            ? "Complete"
                            : "Standby"}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">
                        Detected tags
                      </span>

                      <span className="font-mono font-semibold text-slate-900">
                        {detectedTags.length}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="command-glass rounded-2xl p-5">
                  <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
                    SELECTED EVIDENCE
                  </p>

                  {selectedEvidence ? (
                    <div className="mt-4">
                      <p className="font-mono text-lg font-semibold text-sky-700">
                        {selectedEvidence.tag}
                      </p>

                      <p className="mt-2 text-sm text-slate-600">
                        {selectedEvidence.text}
                      </p>

                      <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-3">
                        <span className="text-xs text-slate-500">
                          Confidence
                        </span>

                        <span className="font-mono text-xs font-semibold text-emerald-600">
                          {Math.round(
                            selectedEvidence.confidence * 100
                          )}
                          %
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="mt-4 text-sm leading-6 text-slate-500">
                      Select a detected tag on the drawing to inspect its source
                      evidence.
                    </p>
                  )}
                </div>

                <div className="rounded-2xl border border-sky-100 bg-sky-50 p-5">
                  <p className="font-mono text-[10px] tracking-[0.18em] text-sky-700">
                    INSPECTION NOTE
                  </p>

                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    Highlighted regions represent OCR evidence detected directly
                    from the uploaded engineering source.
                  </p>
                </div>
              </aside>
            </div>
          </section>
        )}

                    {/* TOPOLOGY */}
        {activeView === "topology" && (
          <section className="engineering-grid min-h-[calc(100vh-150px)] p-4 md:p-6">
            <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="font-mono text-[10px] tracking-[0.22em] text-sky-600">
                  ENGINEERING GRAPH
                </p>

                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
                  Process Topology
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Explore detected engineering components and their
                  relationships.
                </p>
              </div>

              <span
                className={`w-fit rounded-full border px-3 py-1 text-xs font-medium ${
                  detectedTags.length > 0
                    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                    : "border-amber-200 bg-amber-50 text-amber-700"
                }`}
              >
                {detectedTags.length > 0
                  ? "GRAPH READY"
                  : "AWAITING DATA"}
              </span>
            </div>

            <div className="grid min-h-[650px] gap-4 xl:grid-cols-[300px_minmax(0,1fr)]">
              <aside className="space-y-4">
                <div className="command-glass rounded-2xl p-5">
                  <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
                    SELECTED COMPONENT
                  </p>

                  <div className="mt-4 rounded-xl border border-sky-100 bg-sky-50 p-4">
                    <p className="font-mono text-lg font-semibold text-sky-700">
                      {selectedComponent}
                    </p>

                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      Engineering component selected from the topology graph.
                    </p>
                  </div>
                </div>

                <div className="command-glass rounded-2xl p-5">
                  <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
                    GRAPH METRICS
                  </p>

                  <div className="mt-4 space-y-4">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                      <span className="text-sm text-slate-500">
                        Nodes
                      </span>

                      <span className="font-mono text-sm font-semibold text-slate-900">
                        {detectedTags.length}
                      </span>
                    </div>

                    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                      <span className="text-sm text-slate-500">
                        Relations
                      </span>

                      <span className="font-mono text-sm font-semibold text-slate-900">
                        {graphRelationCount}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-500">
                        Confidence
                      </span>

                      <span
                        className={`font-mono text-sm font-semibold ${
                          averageConfidence >= 75
                            ? "text-emerald-600"
                            : "text-amber-600"
                        }`}
                      >
                        {averageConfidence}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
                    GRAPH STATE
                  </p>

                  {detectedTags.length > 0 ? (
                    <div className="mt-4">
                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        <span className="text-sm font-medium text-slate-800">
                          Connected engineering data available
                        </span>
                      </div>

                      <p className="mt-3 text-xs leading-5 text-slate-500">
                        The graph is populated from the currently detected
                        drawing tags.
                      </p>
                    </div>
                  ) : (
                    <div className="mt-4">
                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-amber-500" />
                        <span className="text-sm font-medium text-slate-800">
                          Awaiting drawing data
                        </span>
                      </div>

                      <p className="mt-3 text-xs leading-5 text-slate-500">
                        Upload a P&ID and run OCR to populate the engineering
                        graph.
                      </p>
                    </div>
                  )}
                </div>
              </aside>

              <section className="command-glass hud-corner relative min-h-[650px] overflow-hidden rounded-2xl">
                <div className="absolute left-4 top-4 z-10 rounded-lg border border-slate-200 bg-white/90 px-3 py-2 shadow-sm backdrop-blur">
                  <p className="font-mono text-[10px] tracking-[0.16em] text-sky-700">
                    TOPOLOGY ENGINE
                  </p>

                  <p className="mt-1 text-[9px] text-slate-400">
                    LIVE GRAPH VIEW
                  </p>
                </div>

                <div className="absolute right-4 top-4 z-10 rounded-lg border border-slate-200 bg-white/90 px-3 py-2 shadow-sm backdrop-blur">
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-2 w-2 rounded-full ${
                        detectedTags.length > 0
                          ? "bg-emerald-500"
                          : "bg-amber-500"
                      }`}
                    />

                    <span className="font-mono text-[10px] text-slate-600">
                      {detectedTags.length > 0
                        ? "GRAPH VERIFIED"
                        : "GRAPH STANDBY"}
                    </span>
                  </div>
                </div>

                <div className="flex h-full min-h-[650px] items-center justify-center p-6 pt-20">
                  <EngineeringGraph
                    selectedComponent={selectedComponent}
                    onSelect={setSelectedComponent}
                    detectedTags={detectedTags}
                    evidenceLocations={evidenceLocations}
                  />
                </div>
              </section>
            </div>
          </section>
        )}

       {/* ASK HRIDAY */}
{activeView === "ask" && (
  <section className="engineering-grid min-h-[calc(100vh-150px)] p-4 md:p-6">
    <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="font-mono text-[10px] tracking-[0.22em] text-sky-600">
          ENGINEERING INTELLIGENCE
        </p>

        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
          Ask HRIDAY
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Query the current engineering drawing and detected component data.
        </p>
      </div>

      <span className="w-fit rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700">
        AI ENGINE ONLINE
      </span>
    </div>

    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
      {/* CHAT PANEL */}
      <section className="command-glass hud-corner overflow-hidden rounded-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-5 py-4">
          <div>
            <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
              HRIDAY ENGINE
            </p>

            <p className="mt-1 text-sm font-medium text-slate-800">
              Engineering reasoning interface
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-[10px] text-emerald-600">
              READY
            </span>
          </div>
        </div>

        <div className="min-h-[430px] bg-white/60 p-5">
          {!answer ? (
            <div className="flex min-h-[390px] flex-col items-center justify-center text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-sky-200 bg-sky-50">
                <span className="font-mono text-xl font-bold text-sky-600">
                  H
                </span>
              </div>

              <h3 className="mt-5 text-lg font-semibold text-slate-900">
                How can I help with this drawing?
              </h3>

              <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                Ask about detected components, relationships, engineering
                evidence, or the current P&ID.
              </p>

              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {[
                  "What components were detected?",
                  "What is connected to P-101?",
                  "Show the highest-confidence tags",
                ].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setQuestion(prompt)}
                    className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600 shadow-sm transition hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              <div className="ml-auto max-w-xl rounded-2xl rounded-br-md border border-sky-100 bg-sky-50 p-4">
                <p className="font-mono text-[9px] tracking-[0.14em] text-sky-600">
                  QUERY
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-800">
                  {question}
                </p>
              </div>

              <div className="max-w-2xl rounded-2xl rounded-bl-md border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span className="font-mono text-[9px] tracking-[0.14em] text-emerald-600">
                    HRIDAY RESPONSE
                  </span>
                </div>

                <p className="mt-4 text-sm leading-7 text-slate-700">
                  {answer}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-slate-200 bg-white p-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();

                  if (!question.trim()) return;

                  const normalizedQuestion = question.toLowerCase();

                  if (
                    normalizedQuestion.includes("component") ||
                    normalizedQuestion.includes("tag")
                  ) {
                    setAnswer(
                      `The drawing currently contains ${detectedTags.length} detected engineering tag${
                        detectedTags.length === 1 ? "" : "s"
                      }: ${
                        detectedTags.length > 0
                          ? detectedTags.join(", ")
                          : "no tags detected yet"
                      }.`
                    );
                  } else if (
                    normalizedQuestion.includes("connected") ||
                    normalizedQuestion.includes("relation")
                  ) {
                    setAnswer(
                      `The current topology contains ${graphRelationCount} provisional relationship${
                        graphRelationCount === 1 ? "" : "s"
                      } based on the detected drawing tags.`
                    );
                  } else if (
                    normalizedQuestion.includes("confidence")
                  ) {
                    setAnswer(
                      `The current average OCR confidence is ${averageConfidence}%. ${
                        reviewCount > 0
                          ? `${reviewCount} detected item${
                              reviewCount === 1 ? "" : "s"
                            } require review.`
                          : "No detected items currently require review."
                      }`
                    );
                  } else {
                    setAnswer(
                      `I am analyzing the active engineering session. ${
                        detectedTags.length > 0
                          ? `The drawing currently contains ${detectedTags.length} detected tag${
                              detectedTags.length === 1 ? "" : "s"
                            }.`
                          : "No drawing tags have been detected yet."
                      }`
                    );
                  }
                }
              }}
              placeholder="Ask HRIDAY about the engineering drawing..."
              className="min-h-11 flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-sky-400 focus:bg-white focus:ring-2 focus:ring-sky-100"
            />

            <button
              onClick={() => {
                if (!question.trim()) return;

                const normalizedQuestion = question.toLowerCase();

                if (
                  normalizedQuestion.includes("component") ||
                  normalizedQuestion.includes("tag")
                ) {
                  setAnswer(
                    `The drawing currently contains ${detectedTags.length} detected engineering tag${
                      detectedTags.length === 1 ? "" : "s"
                    }: ${
                      detectedTags.length > 0
                        ? detectedTags.join(", ")
                        : "no tags detected yet"
                    }.`
                  );
                } else if (
                  normalizedQuestion.includes("connected") ||
                  normalizedQuestion.includes("relation")
                ) {
                  setAnswer(
                    `The current topology contains ${graphRelationCount} provisional relationship${
                      graphRelationCount === 1 ? "" : "s"
                    } based on the detected drawing tags.`
                  );
                } else if (
                  normalizedQuestion.includes("confidence")
                ) {
                  setAnswer(
                    `The current average OCR confidence is ${averageConfidence}%. ${
                      reviewCount > 0
                        ? `${reviewCount} detected item${
                            reviewCount === 1 ? "" : "s"
                          } require review.`
                        : "No detected items currently require review."
                    }`
                  );
                } else {
                  setAnswer(
                    `I am analyzing the active engineering session. ${
                      detectedTags.length > 0
                        ? `The drawing currently contains ${detectedTags.length} detected tag${
                            detectedTags.length === 1 ? "" : "s"
                          }.`
                        : "No drawing tags have been detected yet."
                    }`
                  );
                }
              }}
              className="rounded-xl bg-sky-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-700"
            >
              Ask HRIDAY
            </button>
          </div>
        </div>
      </section>

      {/* INTELLIGENCE STATUS */}
      <aside className="space-y-4">
        <div className="command-glass rounded-2xl p-5">
          <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
            ENGINEERING CONTEXT
          </p>

          <div className="mt-4 space-y-3">
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-xs text-slate-500">Detected tags</p>
              <p className="mt-1 font-mono text-xl font-semibold text-slate-900">
                {detectedTags.length}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-xs text-slate-500">Relationships</p>
              <p className="mt-1 font-mono text-xl font-semibold text-slate-900">
                {graphRelationCount}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-xs text-slate-500">OCR confidence</p>
              <p className="mt-1 font-mono text-xl font-semibold text-emerald-600">
                {averageConfidence}%
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="font-mono text-[10px] tracking-[0.18em] text-slate-500">
            SYSTEM NOTE
          </p>

          <p className="mt-4 text-sm leading-6 text-slate-600">
            Responses are grounded in the current drawing session and
            detected engineering data.
          </p>
        </div>
      </aside>
    </div>
  </section>
)}
  {/* EVIDENCE */}
        {activeView === "evidence" && (
          <section className="p-4 md:p-6">
            <div className="mb-6">
              <p className="text-xs tracking-[0.25em] text-cyan-400">
                EVIDENCE CHAIN
              </p>

              <h2 className="mt-2 text-2xl font-semibold">
                Engineering Answer Traceability
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Review the source evidence captured from the current
                engineering drawing.
              </p>
            </div>

            <div className="grid gap-4 xl:grid-cols-12">
              <div className="command-glass rounded-xl p-6 xl:col-span-7">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-mono text-xs tracking-[0.2em] text-cyan-400">
                      SOURCE EVIDENCE
                    </p>

                    <p className="mt-2 text-sm text-slate-300">
                      {evidenceLocations.length} evidence location(s)
                      captured.
                    </p>
                  </div>

                  <span className="font-mono text-[10px] text-emerald-300">
                    {verifiedCount} VERIFIED
                  </span>
                </div>

                {evidenceLocations.length > 0 ? (
                  <div className="mt-6 space-y-3">
                    {evidenceLocations.map((item, index) => (
                      <button
                        key={`${item.tag}-${index}`}
                        type="button"
                        onClick={() => {
                          setSelectedComponent(item.tag);
                          setSelectedEvidence(item);
                          setZoom(2);
                          setActiveView("pid");
                        }}
                        className="flex w-full items-center justify-between rounded-lg border border-white/10 bg-black/20 p-4 text-left transition hover:border-cyan-400/30 hover:bg-cyan-400/5"
                      >
                        <div>
                          <span className="font-mono text-sm font-bold text-cyan-300">
                            {item.tag}
                          </span>

                          <p className="mt-1 font-mono text-[10px] text-slate-500">
                            X: {Math.round(item.x)} · Y:{" "}
                            {Math.round(item.y)}
                          </p>
                        </div>

                        <span
                          className={`font-mono text-xs ${
                            item.confidence >= 0.75
                              ? "text-emerald-300"
                              : "text-amber-300"
                          }`}
                        >
                          {Math.round(item.confidence * 100)}%
                        </span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="mt-6 rounded-lg border border-white/5 bg-black/20 p-6 text-center">
                    <p className="font-mono text-xs text-slate-500">
                      NO EVIDENCE AVAILABLE
                    </p>

                    <p className="mt-2 text-xs text-slate-600">
                      Upload a drawing and run OCR to create the evidence
                      chain.
                    </p>
                  </div>
                )}
              </div>

              <div className="agent-terminal rounded-xl p-6 xl:col-span-5">
                <p className="text-xs tracking-[0.2em] text-slate-500">
                  CURRENT ANALYSIS
                </p>

                <div className="mt-5 space-y-4 font-mono text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">
                      DETECTED TAGS
                    </span>

                    <span className="text-cyan-300">
                      {detectedTags.length}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-500">
                      VERIFIED
                    </span>

                    <span className="text-emerald-300">
                      {verifiedCount}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-500">
                      REVIEW
                    </span>

                    <span className="text-amber-300">
                      {reviewCount}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-500">
                      CONFIDENCE
                    </span>

                    <span
                      className={
                        averageConfidence >= 75
                          ? "text-emerald-300"
                          : "text-amber-300"
                      }
                    >
                      {averageConfidence}%
                    </span>
                  </div>
                </div>

                <div className="mt-6 border-t border-white/5 pt-4">
                  <p className="text-xs leading-5 text-slate-500">
                    Evidence remains tied to OCR coordinates captured
                    from the source drawing.
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}