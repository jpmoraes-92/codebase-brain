import { create } from 'zustand';

// 1. Definimos as Tipagens Exatas do nosso Backend
export interface RiskMetrics {
  fan_in: number;
  bottleneck: number;
  complexity: number;
}

export interface RiskComponent {
  component: string;
  type: string;
  risk_score: number;
  metrics: RiskMetrics;
}

export interface GraphSummary {
  metrics: {
    total_nodes: number;
    total_edges: number;
    node_types: Record<string, number>;
    functions_without_tests: number;
  };
  top_10_risks: RiskComponent[];
}

// 2. Atualizamos o Estado para usar as tipagens em vez de 'any'
interface GraphState {
  isAnalyzing: boolean;
  repoPath: string;
  summary: GraphSummary | null;
  selectedNodeId: string | null;
  setAnalyzing: (status: boolean) => void;
  setRepoPath: (path: string) => void;
  setSummary: (summary: GraphSummary) => void;
  setSelectedNode: (id: string | null) => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  isAnalyzing: false,
  repoPath: '',
  summary: null,
  selectedNodeId: null,
  setAnalyzing: (status) => set({ isAnalyzing: status }),
  setRepoPath: (path) => set({ repoPath: path }),
  setSummary: (summary) => set({ summary }),
  setSelectedNode: (id) => set({ selectedNodeId: id }),
}));