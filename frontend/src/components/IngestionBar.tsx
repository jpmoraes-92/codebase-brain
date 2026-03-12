import { useState } from 'react';
import { brainApi } from '../api/brainApi';
import { useGraphStore } from '../store/graphStore';
import { Play, Loader2 } from 'lucide-react';

export function IngestionBar() {
  const [inputPath, setInputPath] = useState('');
  const { setAnalyzing, isAnalyzing, setSummary, setRepoPath } = useGraphStore();

  const handleAnalyze = async () => {
    if (!inputPath) return;
    
    setAnalyzing(true);
    try {
      // 1. Inicia a ingestão
      await brainApi.analyzeRepo(inputPath);
      setRepoPath(inputPath);
      
      // 2. Busca o resumo e o grafo inicial
      const summaryData = await brainApi.getSummary();
      setSummary(summaryData);
      
    } catch (error) {
      console.error("Erro na análise:", error);
      alert("Falha ao analisar o repositório. Verifique se o backend está a correr.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="flex items-center gap-4 p-4 bg-gray-900 border-b border-gray-800 text-white">
      <div className="font-bold text-xl text-blue-400 mr-4">🧠 Codebase Brain</div>
      <input 
        type="text" 
        placeholder="Cole o caminho local ou URL do GitHub..." 
        className="flex-1 bg-gray-800 border border-gray-700 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
        value={inputPath}
        onChange={(e) => setInputPath(e.target.value)}
        disabled={isAnalyzing}
      />
      <button 
        onClick={handleAnalyze}
        disabled={isAnalyzing}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded flex items-center gap-2 font-medium disabled:opacity-50"
      >
        {isAnalyzing ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
        {isAnalyzing ? 'Ingerindo Código...' : 'Analisar'}
      </button>
    </div>
  );
}