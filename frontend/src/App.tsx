import { useState } from 'react';
import { IngestionBar } from './components/IngestionBar';
import { RiskPanel } from './components/RiskPanel';
import { GraphView } from './components/GraphView';
import { ChatPanel } from './components/ChatPanel';
import { ArchitectureSandbox } from './components/ArchitectureSandbox';
import type { DiffResult } from './types/diff';

function App() {
  const [simulationResult, setSimulationResult] = useState<DiffResult | null>(null);

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-950 text-gray-300 overflow-hidden font-sans">
      <IngestionBar />
      
      <div className="flex-1 flex overflow-hidden relative">
        <RiskPanel />
        
        <div className="flex-1 relative">
          
          <ArchitectureSandbox onSimulationResult={(result) => {
            console.log("Resultado da Simulação:", result);
            setSimulationResult(result);
          }} />
          
          {/* Card de Risco Estratégico */}
          {simulationResult && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50 bg-gray-900 border border-gray-700 p-5 rounded-xl shadow-2xl min-w-[350px] animate-in fade-in slide-in-from-bottom-8">
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-bold text-white flex items-center gap-2 text-lg">
                  🛡️ Veredito de Arquitetura
                </h3>
                <button onClick={() => setSimulationResult(null)} className="text-gray-500 hover:text-white">✕</button>
              </div>
              
              <div className="bg-gray-950 p-3 rounded-lg border border-gray-800 mb-3">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-gray-400 uppercase tracking-wider">Risk Score Predito</span>
                  <span className={`font-bold text-lg ${
                    simulationResult.risk.level === 'CRITICAL' ? 'text-red-500' : 
                    simulationResult.risk.level === 'HIGH' ? 'text-orange-500' : 
                    simulationResult.risk.level === 'MEDIUM' ? 'text-yellow-500' : 'text-green-500'
                  }`}>
                    {simulationResult.risk.score}/100 ({simulationResult.risk.level})
                  </span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
                  <div 
                    className={`h-1.5 rounded-full ${simulationResult.risk.level === 'CRITICAL' ? 'bg-red-500' : simulationResult.risk.level === 'HIGH' ? 'bg-orange-500' : simulationResult.risk.level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'}`} 
                    style={{ width: `${simulationResult.risk.score}%` }}
                  ></div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-800/50 p-2 rounded border border-gray-700/50">
                  <span className="block text-xs text-gray-400">Nós Impactados</span>
                  <span className="text-white font-mono text-lg">{simulationResult.metrics.nodes_impacted}</span>
                </div>
                <div className="bg-gray-800/50 p-2 rounded border border-gray-700/50">
                  <span className="block text-xs text-gray-400">Nós Sem Testes</span>
                  <span className="text-white font-mono text-lg">{simulationResult.metrics.untested_nodes}</span>
                </div>
              </div>
            </div>
          )}
          
          <GraphView />
        </div>

        <ChatPanel />
      </div>
    </div>
  );
}

export default App;