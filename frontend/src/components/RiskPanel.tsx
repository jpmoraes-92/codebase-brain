import { useGraphStore } from '../store/graphStore';
import { AlertTriangle, Activity } from 'lucide-react';

export function RiskPanel() {
  const { summary, selectedNodeId, setSelectedNode } = useGraphStore();

  if (!summary) return null;

  return (
    <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col h-full overflow-y-auto">
      <div className="p-4 border-b border-gray-800 sticky top-0 bg-gray-900 z-10">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <AlertTriangle className="text-yellow-500" size={20} />
          High Risk Nodes
        </h2>
        <p className="text-xs text-gray-400 mt-1">Baseado em Complexidade e Gargalos</p>
      </div>

      <div className="flex-1 p-2 space-y-2">
        {summary.top_10_risks.map((risk, index) => {
          const isSelected = selectedNodeId === risk.component;
          // Pega apenas o nome final da função/arquivo para ficar limpo na UI
          const shortName = risk.component.split('/').pop();

          return (
            <div 
              key={risk.component}
              onClick={() => setSelectedNode(risk.component)}
              className={`p-3 rounded cursor-pointer transition-colors border ${
                isSelected 
                  ? 'bg-blue-900/30 border-blue-500' 
                  : 'bg-gray-800/50 border-gray-700 hover:bg-gray-800'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="font-mono text-sm text-blue-300 break-all" title={risk.component}>
                  {index + 1}. {shortName}
                </span>
              </div>
              
              <div className="flex items-center gap-4 text-xs text-gray-400">
                <span className="flex items-center gap-1" title="Risco Global">
                  <Activity size={12} className="text-red-400" />
                  {risk.risk_score.toFixed(1)}
                </span>
                <span title="Fan-in (Dependências de entrada)">
                  📥 {risk.metrics.fan_in}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}