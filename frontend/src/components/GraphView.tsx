import { useEffect, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { brainApi } from '../api/brainApi';
import { useGraphStore } from '../store/graphStore';
import { Loader2 } from 'lucide-react';

// 1. Tipagens rigorosas para removermos os 'any'
interface CytoData {
  id?: string;
  label?: string;
  type?: string;
  source?: string;
  target?: string;
}

interface CytoElement {
  data: CytoData;
  classes?: string;
}

interface ApiEdge {
  source: string;
  target: string;
  relation: string;
}

export function GraphView() {
  const { selectedNodeId } = useGraphStore();
  const [elements, setElements] = useState<CytoElement[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function fetchImpactGraph() {
      if (!selectedNodeId) return;
      
      setIsLoading(true);
      try {
        const data = await brainApi.getImpact(selectedNodeId);
        const newElements: CytoElement[] = [];
        
        // Nó Central
        newElements.push({
          data: { id: selectedNodeId, label: selectedNodeId.split('/').pop() },
          classes: 'target-node'
        });

        // Nós Afetados
        Object.entries(data.blast_radius.nodes).forEach(([type, nodesArray]) => {
          (nodesArray as string[]).forEach((nodeId) => {
            if (nodeId !== selectedNodeId) {
              newElements.push({
                data: { id: nodeId, label: nodeId.split('/').pop(), type },
                classes: type.toLowerCase()
              });
            }
          });
        });

        // Arestas
        data.blast_radius.edges.forEach((edge: ApiEdge) => {
          newElements.push({
            data: { 
              source: edge.source, 
              target: edge.target, 
              label: edge.relation 
            }
          });
        });

        setElements(newElements);
      } catch (error) {
        console.error("Erro ao carregar o grafo de impacto:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchImpactGraph();
  }, [selectedNodeId]);

  const cyStylesheet = [
    {
      selector: 'node',
      style: {
        'background-color': '#374151',
        'label': 'data(label)',
        'color': '#D1D5DB',
        'font-size': '10px',
        'text-valign': 'bottom',
        'text-margin-y': 5,
      }
    },
    {
      selector: '.target-node',
      style: {
        'background-color': '#EF4444',
        'border-width': 2,
        'border-color': '#FCA5A5',
        'width': 40,
        'height': 40,
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#4B5563',
        'target-arrow-color': '#4B5563',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '8px',
        'color': '#9CA3AF',
        'text-rotation': 'autorotate'
      }
    }
  ];

  if (!selectedNodeId) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 flex-col gap-4">
        <div className="text-4xl">🕸️</div>
        <p>Selecione um nó no painel lateral para visualizar a sua teia de impacto arquitetural.</p>
      </div>
    );
  }

  return (
    <div className="h-full w-full relative bg-gray-950">
      {isLoading && (
        <div className="absolute inset-0 bg-gray-950/80 z-10 flex items-center justify-center">
          <Loader2 className="animate-spin text-blue-500" size={32} />
        </div>
      )}
      
      {/* O componente Cytoscape agora renderiza os nossos CytoElements tipados */}
      <CytoscapeComponent 
        elements={elements} 
        stylesheet={cyStylesheet}
        style={{ width: '100%', height: '100%' }}
        layout={{ name: 'cose', padding: 50, animate: true }}
        wheelSensitivity={0.1}
      />
    </div>
  );
}