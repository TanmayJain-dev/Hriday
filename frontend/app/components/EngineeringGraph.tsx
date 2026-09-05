"use client";

import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

type EngineeringGraphProps = {
  selectedComponent: string;
  onSelect: (component: string) => void;
};

type EquipmentNodeData = {
  tag: string;
  name: string;
  type: string;
  confidence: string;
  status: "VERIFIED" | "REVIEW";
};

function EquipmentNode({
  data,
  selected,
}: {
  data: EquipmentNodeData;
  selected?: boolean;
}) {
  const isReview = data.status === "REVIEW";

  return (
    <div
      className={`relative min-w-[190px] rounded-xl border px-4 py-3 transition-all ${
        selected
          ? "border-cyan-300 bg-cyan-400/10 shadow-[0_0_28px_rgba(34,211,238,0.25)]"
          : "border-white/10 bg-[#0b1722]/95 hover:border-cyan-400/40"
      }`}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2.5 !w-2.5 !border-2 !border-[#071018] !bg-cyan-300"
      />

      <Handle
        type="source"
        position={Position.Right}
        className="!h-2.5 !w-2.5 !border-2 !border-[#071018] !bg-cyan-300"
      />

      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="font-mono text-sm font-bold tracking-wide text-cyan-200">
            {data.tag}
          </div>

          <div className="mt-1 text-sm font-semibold text-slate-100">
            {data.name}
          </div>

          <div className="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-slate-500">
            {data.type}
          </div>
        </div>

        <div
          className={`mt-1 h-2 w-2 rounded-full ${
            isReview ? "bg-amber-400" : "bg-emerald-400"
          }`}
        />
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-white/6 pt-2">
        <span
          className={`font-mono text-[10px] uppercase tracking-wider ${
            isReview ? "text-amber-300" : "text-emerald-300"
          }`}
        >
          {data.status}
        </span>

        <span className="font-mono text-[10px] text-slate-400">
          {data.confidence}
        </span>
      </div>
    </div>
  );
}

const nodeTypes = {
  equipment: EquipmentNode,
};

const initialNodes: Node<EquipmentNodeData>[] = [
  {
    id: "P-101",
    type: "equipment",
    position: { x: 80, y: 180 },
    data: {
      tag: "P-101",
      name: "Crude Feed Pump",
      type: "CENTRIFUGAL PUMP",
      confidence: "96%",
      status: "VERIFIED",
    },
  },
  {
    id: "V-204",
    type: "equipment",
    position: { x: 390, y: 80 },
    data: {
      tag: "V-204",
      name: "Process Isolation Valve",
      type: "PROCESS VALVE",
      confidence: "91%",
      status: "VERIFIED",
    },
  },
  {
    id: "T-301",
    type: "equipment",
    position: { x: 700, y: 180 },
    data: {
      tag: "T-301",
      name: "Feed Surge Drum",
      type: "VESSEL",
      confidence: "94%",
      status: "VERIFIED",
    },
  },
  {
    id: "E-110",
    type: "equipment",
    position: { x: 390, y: 330 },
    data: {
      tag: "E-110",
      name: "Feed Heat Exchanger",
      type: "HEAT EXCHANGER",
      confidence: "88%",
      status: "REVIEW",
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: "P-101-V-204",
    source: "P-101",
    target: "V-204",
    type: "smoothstep",
    animated: true,
    style: {
      stroke: "#22d3ee",
      strokeWidth: 2,
    },
  },
  {
    id: "V-204-T-301",
    source: "V-204",
    target: "T-301",
    type: "smoothstep",
    animated: true,
    style: {
      stroke: "#34d399",
      strokeWidth: 2,
    },
  },
  {
    id: "P-101-E-110",
    source: "P-101",
    target: "E-110",
    type: "smoothstep",
    style: {
      stroke: "#f59e0b",
      strokeWidth: 2,
      strokeDasharray: "6 5",
    },
  },
];

export default function EngineeringGraph({
  selectedComponent,
  onSelect,
}: EngineeringGraphProps) {
  return (
    <div className="relative h-[560px] w-full overflow-hidden rounded-xl border border-cyan-400/10 bg-[#071018]">
      <ReactFlow
        nodes={initialNodes.map((node) => ({
          ...node,
          selected: node.id === selectedComponent,
        }))}
        edges={initialEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelect(node.id)}
        fitView
        fitViewOptions={{
          padding: 0.25,
        }}
        minZoom={0.5}
        maxZoom={1.8}
        panOnScroll
        zoomOnScroll
        proOptions={{
          hideAttribution: true,
        }}
      >
        <Background
          gap={32}
          size={1}
          color="rgba(148, 163, 184, 0.12)"
        />

        <Controls
          position="bottom-left"
          className="!overflow-hidden !rounded-lg !border !border-white/10 !bg-[#0b1722]/95 !shadow-2xl"
        />

        <MiniMap
          position="bottom-right"
          pannable
          zoomable
          nodeColor={(node) =>
            node.id === selectedComponent ? "#22d3ee" : "#334155"
          }
          nodeStrokeColor="#22d3ee"
          nodeStrokeWidth={1}
          className="!overflow-hidden !rounded-lg !border !border-white/10 !bg-[#0b1722]/95"
        />
      </ReactFlow>

      <div className="pointer-events-none absolute left-4 top-4 z-10 rounded-lg border border-cyan-400/15 bg-[#071018]/80 px-3 py-2 backdrop-blur-md">
        <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-cyan-300">
          Topology Engine // Live
        </div>

        <div className="mt-1 flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />

          <span className="font-mono text-[10px] text-slate-400">
            GRAPH VERIFIED
          </span>
        </div>
      </div>

      <div className="pointer-events-none absolute right-4 top-4 z-10 rounded-lg border border-white/8 bg-[#071018]/75 px-3 py-2 backdrop-blur-md">
        <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-slate-500">
          Relations
        </div>

        <div className="mt-1 font-mono text-sm text-slate-200">
          126
        </div>
      </div>
    </div>
  );
}