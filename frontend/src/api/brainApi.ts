import axios from 'axios';

// 1. Definição rigorosa dos contratos
export interface ChangedFilePayload {
  path: string;
  changed_lines: number[];
}

export interface AnalyzeDiffPayload {
  repo: string;
  base_commit?: string;
  head_commit?: string;
  changed_files: ChangedFilePayload[];
}

// 2. Configuração da API
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

// 3. Exportação dos métodos
export const brainApi = {
  analyzeRepo: async (path: string) => {
    const response = await api.post('/analyze', { repo_url_or_path: path });
    return response.data;
  },
  
  getSummary: async () => {
    const response = await api.get('/graph/summary');
    return response.data;
  },
  
  getNodeDetails: async (nodeId: string) => {
    const response = await api.get(`/graph/node/${encodeURIComponent(nodeId)}`);
    return response.data;
  },
  
  getImpact: async (nodeId: string) => {
    const response = await api.get(`/graph/impact/${encodeURIComponent(nodeId)}`);
    return response.data;
  },
  
  analyzeDiff: async (payload: AnalyzeDiffPayload) => {
    const response = await api.post('/analyze/diff', payload);
    return response.data;
  },
  
  askQuestion: async (question: string) => {
    const response = await api.post('/ask', { question });
    return response.data;
  }
};