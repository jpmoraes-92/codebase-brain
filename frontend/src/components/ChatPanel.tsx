import { useState, useRef, useEffect } from 'react';
import { brainApi } from '../api/brainApi';
import { useGraphStore } from '../store/graphStore';
import { Send, Bot, User, Loader2, Code } from 'lucide-react';

interface Message {
  role: 'user' | 'bot';
  content: string;
  sources?: string[];
}

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', content: 'Olá! Sou o seu Codebase Brain. O que quer descobrir sobre a arquitetura deste projeto?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { summary } = useGraphStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || !summary) return;

    const userQuestion = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userQuestion }]);
    setIsTyping(true);

    try {
      const response = await brainApi.askQuestion(userQuestion);
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: response.answer,
        sources: response.sources
      }]);
    } catch (error) {
      // Agora usamos a variável 'error' registando-a na consola para debug!
      console.error("Erro de comunicação com o Cérebro:", error);
      setMessages(prev => [...prev, { role: 'bot', content: 'Desculpe, ocorreu um erro ao consultar o cérebro vetorial.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="w-96 bg-gray-950 border-l border-gray-800 flex flex-col h-full">
      <div className="p-4 border-b border-gray-800 bg-gray-900 flex items-center gap-2">
        <Bot className="text-blue-400" size={20} />
        <h2 className="font-semibold text-white">Cognitive QA Chat</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`flex items-start gap-2 max-w-[90%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              {/* Avatares Modernos utilizando o Bot e o User */}
              <div className={`p-1.5 rounded-full mt-0.5 flex-shrink-0 ${
                msg.role === 'user' ? 'bg-blue-900/50 border border-blue-800' : 'bg-gray-800 border border-gray-700'
              }`}>
                {msg.role === 'user' ? <User size={14} className="text-blue-400" /> : <Bot size={14} className="text-gray-300" />}
              </div>

              <div className={`p-2 rounded-lg text-sm whitespace-pre-wrap ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-200 border border-gray-700'
              }`}>
                {msg.content}
              </div>
            </div>
            
            {/* Renderiza as fontes de código se o bot as enviar */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-2 ml-8 flex flex-wrap gap-1">
                {msg.sources.map(src => (
                  <span key={src} className="flex items-center gap-1 text-[10px] bg-gray-900 border border-gray-700 text-gray-400 px-2 py-1 rounded">
                    <Code size={10} />
                    {src.split('/').pop()}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex items-center gap-2 text-gray-500 text-sm p-2 ml-8">
            <Loader2 className="animate-spin" size={14} /> Analisando arquitetura...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-gray-900 border-t border-gray-800">
        <div className="flex items-center gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={summary ? "Pergunte algo ao código..." : "Ingira um repositório primeiro"}
            disabled={!summary || isTyping}
            className="flex-1 bg-gray-800 text-white text-sm rounded px-3 py-2 border border-gray-700 focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || !summary || isTyping}
            className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50 disabled:bg-gray-700 transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}