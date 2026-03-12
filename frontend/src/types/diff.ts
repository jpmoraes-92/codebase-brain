export interface DiffResult {
  epicenters: string[];
  impact: {
    upstream: string[];
    downstream: string[];
  };
  risk: {
    score: number;
    level: string;
  };
  suggested_tests: string[];
  metrics: {
    nodes_impacted: number;
    modules_impacted: number;
    untested_nodes: number;
    impact_depth: number;
  };
}