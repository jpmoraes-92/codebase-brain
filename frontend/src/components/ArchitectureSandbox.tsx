import { useState } from 'react';
import { brainApi } from '../api/brainApi';
import { useGraphStore } from '../store/graphStore';
import { Beaker, Loader2, AlertTriangle, Lightbulb } from 'lucide-react';
import type { DiffResult } from '../types/diff';

interface ArchitectureSandboxProps {
  onSimulationResult: (data: DiffResult) => void;
}

export function ArchitectureSandbox({ onSimulationResult }: ArchitectureSandboxProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filePath, setFilePath] = useState('app/services/mongo_service.py');
  const [lines, setLines] = useState('30,31,32');
  const [isLoading, setIsLoading] = useState(false);
  const { summary } = useGraphStore();

  const handleSimulate = async () => {
    if (!summary) return alert("Analise um repositório primeiro.");
    setIsLoading(true);
    try {
      const payload = {
        repo: summary.top_10_risks[0]?.component.split('/')[0] || 'repo',
        changed_files: [
          {
            path: filePath,
            changed_lines: lines.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n))
          }
        ]
      };
      
      const result = await brainApi.analyzeDiff(payload);
      onSimulationResult(result);
      setIsOpen(false);
    } catch (error) {
      console.error(error);
      alert("Erro ao simular impacto.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="absolute top-4 right-4 z-50">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium shadow-lg transition-all border border-indigo-500/50"
      >
        <Beaker size={18} />
        Architecture Sandbox
      </button>

      {isOpen && (
        <div className="absolute top-12 right-0 w-96 bg-gray-900 border border-gray-700 rounded-lg shadow-2xl p-5 mt-2 animate-in fade-in slide-in-from-top-2">
          <div className="flex items-center gap-2 mb-1">
            <Lightbulb size={18} className="text-yellow-500" />
            <h3 className="font-semibold text-white">What-If Analysis</h3>
          </div>
          <p className="text-xs text-gray-400 mb-4">
            Simule alterações no código antes de pedir à equipa para implementar. Descubra o raio de explosão instantaneamente.
          </p>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-gray-300 block mb-1">Target Component (Caminho do Ficheiro)</label>
              <input 
                type="text" 
                value={filePath}
                onChange={e => setFilePath(e.target.value)}
                placeholder="ex: app/services/pagamentos.py"
                className="w-full bg-gray-950 border border-gray-700 rounded-md p-2 text-sm text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-300 block mb-1">Linhas a Refatorar (separadas por vírgula)</label>
              <input 
                type="text" 
                value={lines}
                onChange={e => setLines(e.target.value)}
                placeholder="ex: 10,11,12"
                className="w-full bg-gray-950 border border-gray-700 rounded-md p-2 text-sm text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all"
              />
            </div>
            
            <button 
              onClick={handleSimulate}
              disabled={isLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-700 text-white py-2 rounded-md flex items-center justify-center gap-2 mt-2 font-medium transition-colors"
            >
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <AlertTriangle size={16} />}
              {isLoading ? 'A calcular topologia...' : 'Simular Raio de Explosão'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}