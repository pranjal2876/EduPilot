import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, ChevronDown, ChevronUp, Database, FileText, CheckCircle2 } from 'lucide-react';
import { fetchApi, ChatResponse } from '../lib/api';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  intent?: string;
  tools_used?: string[];
  sources?: string[];
  data_trace?: any;
}

interface AssistantTabProps {
  studentId: string;
}

export const AssistantTab: React.FC<AssistantTabProps> = ({ studentId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      content:
        'Hello! I am your AI College Learning Assistant. I can analyze your enrolled courses, diagnose your weak topics from actual assessment data, check your eligibility for hackathons using deterministic rules, and explain concepts grounded in course curriculum notes.',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedTraceId, setExpandedTraceId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    'What are my weak topics?',
    'Explain the first one',
    'Give me 5 questions on it',
    'Can I take assessment 341?',
    'Explain normalization from my DBMS course.',
    'What should I study next?',
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: text,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setLoading(true);

    try {
      const res = await fetchApi<ChatResponse>(
        '/assistant/chat',
        studentId,
        {
          method: 'POST',
          body: JSON.stringify({ message: text }),
        }
      );

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: res.reply,
        intent: res.intent,
        tools_used: res.tools_used,
        sources: res.sources,
        data_trace: res.data_trace,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          content: `Error: ${err.message || 'Failed to process message'}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleTrace = (id: string) => {
    setExpandedTraceId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="flex flex-col h-[750px] bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-sky-600 text-white flex items-center justify-center shadow-sm">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              AI Academic Assistant
              <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">
                Connected
              </span>
            </h2>
            <p className="text-xs text-slate-500">Separation of Data, RAG, Rules & Orchestration</p>
          </div>
        </div>

        <div className="text-xs text-slate-400 hidden sm:block">
          Student ID: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">{studentId.slice(0, 8)}...</code>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-5 bg-slate-50/30">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          const hasTrace = m.tools_used && m.tools_used.length > 0;
          const isTraceOpen = expandedTraceId === m.id;

          return (
            <div key={m.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
              <div className="flex items-start space-x-2 max-w-3xl">
                {!isUser && (
                  <div className="h-8 w-8 rounded-lg bg-sky-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    isUser
                      ? 'bg-sky-600 text-white rounded-br-none shadow-sm'
                      : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none shadow-sm'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{m.content}</div>

                  {/* Sources Pills */}
                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                        <FileText className="h-3 w-3" /> Sources Cited:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {m.sources.map((s, idx) => (
                          <span
                            key={idx}
                            className="inline-block text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md border border-slate-200"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="h-8 w-8 rounded-lg bg-slate-700 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>

              {/* Execution Trace (Phase 15 Transparency) */}
              {!isUser && hasTrace && (
                <div className="ml-10 mt-1.5 max-w-2xl">
                  <button
                    onClick={() => toggleTrace(m.id)}
                    className="flex items-center gap-1.5 text-[11px] font-semibold text-sky-700 hover:text-sky-800 bg-sky-50 px-2.5 py-1 rounded-md border border-sky-200 transition"
                  >
                    <Sparkles className="h-3 w-3" />
                    AI Execution Provenance ({m.tools_used?.length} tools invoked)
                    {isTraceOpen ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                  </button>

                  {isTraceOpen && (
                    <div className="mt-2 p-3.5 bg-slate-900 text-slate-200 rounded-xl text-xs space-y-2.5 font-mono shadow-inner border border-slate-800">
                      <div>
                        <span className="text-sky-400 font-bold">Intent Classified:</span> {m.intent}
                      </div>
                      <div>
                        <span className="text-emerald-400 font-bold">Tools Executed:</span>
                        <ul className="list-disc list-inside mt-0.5 space-y-0.5 text-slate-300">
                          {m.tools_used?.map((tool, i) => (
                            <li key={i}>{tool}</li>
                          ))}
                        </ul>
                      </div>
                      {m.sources && m.sources.length > 0 && (
                        <div>
                          <span className="text-amber-400 font-bold">RAG Chunks Retrieved:</span> {m.sources.length} document references
                        </div>
                      )}
                      <div className="text-[10px] text-slate-500 border-t border-slate-800 pt-1.5">
                        Deterministic backend execution • Zero direct raw SQL generated
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-start space-x-2">
            <div className="h-8 w-8 rounded-lg bg-sky-600 text-white flex items-center justify-center shadow-sm">
              <Bot className="h-4 w-4 animate-spin" />
            </div>
            <div className="p-3.5 bg-white rounded-2xl border border-slate-200 text-xs text-slate-500 shadow-sm flex items-center gap-2">
              <span>Orchestrating tools, evaluating business rules & RAG...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div className="px-6 py-2.5 border-t border-slate-100 bg-white">
        <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Suggested Queries:</p>
        <div className="flex flex-wrap gap-1.5 overflow-x-auto">
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(p)}
              disabled={loading}
              className="text-xs bg-slate-100 hover:bg-sky-50 hover:text-sky-700 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 transition whitespace-nowrap"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage(inputValue);
        }}
        className="p-4 border-t border-slate-200 bg-white flex items-center space-x-3"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question (e.g. 'What are my weak topics?', 'Explain ACID properties')..."
          disabled={loading}
          className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition"
        />
        <button
          type="submit"
          disabled={loading || !inputValue.trim()}
          className="px-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-medium text-sm flex items-center gap-1.5 transition disabled:opacity-50 shadow-sm"
        >
          <Send className="h-4 w-4" />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>
    </div>
  );
};
