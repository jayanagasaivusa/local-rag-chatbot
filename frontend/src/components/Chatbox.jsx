import { useEffect, useRef, useState } from 'react';
import { ArrowUp, Sparkles } from 'lucide-react';
import ChatMessage from './ChatMessage';
import { sendChatMessage } from '../api';

let nextId = 1;
const makeId = () => nextId++;

const WELCOME_MESSAGE = {
  id: makeId(),
  role: 'assistant',
  content:
    "Hi! I'm your local RAG assistant. Upload a document on the left, then ask me anything about it.",
};

function ThinkingBubble() {
  return (
    <div className="flex w-full animate-fadeInUp justify-start">
      <div className="flex items-center gap-1 rounded-3xl rounded-tl-lg border border-slate-100 bg-white px-5 py-3.5 shadow-sm shadow-indigo-100">
        <span className="mr-1 text-sm text-slate-400">Thinking</span>
        <span className="h-1.5 w-1.5 animate-bounceDot rounded-full bg-slate-400 [animation-delay:-0.32s]" />
        <span className="h-1.5 w-1.5 animate-bounceDot rounded-full bg-slate-400 [animation-delay:-0.16s]" />
        <span className="h-1.5 w-1.5 animate-bounceDot rounded-full bg-slate-400" />
      </div>
    </div>
  );
}

export default function Chatbox() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const scrollAnchorRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  async function runPrompt(prompt) {
    try {
      const data = await sendChatMessage(prompt);
      return {
        role: 'assistant',
        content: data.response,
        sources: data.sources,
        prompt,
      };
    } catch (err) {
      return {
        role: 'assistant',
        content: `Something went wrong: ${err.message}`,
        isError: true,
        prompt,
      };
    }
  }

  async function handleSend(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isThinking) return;

    setMessages((prev) => [...prev, { id: makeId(), role: 'user', content: trimmed }]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsThinking(true);

    const result = await runPrompt(trimmed);
    setMessages((prev) => [...prev, { id: makeId(), ...result }]);
    setIsThinking(false);
  }

  async function handleRestart(messageId) {
    const target = messages.find((m) => m.id === messageId);
    if (!target?.prompt || isThinking) return;

    setMessages((prev) =>
      prev.map((m) => (m.id === messageId ? { ...m, isRegenerating: true } : m)),
    );

    const result = await runPrompt(target.prompt);
    setMessages((prev) =>
      prev.map((m) => (m.id === messageId ? { ...result, id: messageId } : m)),
    );
  }

  function handleInputChange(e) {
    setInput(e.target.value);
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }

  return (
    <div className="flex h-full flex-col bg-slate-50">
      <header className="flex items-center gap-2.5 border-b border-indigo-100/70 bg-white/80 px-8 py-4 backdrop-blur">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-violet-600 shadow-sm shadow-indigo-200">
          <Sparkles size={16} className="text-white" />
        </div>
        <div>
          <h1 className="text-[15px] font-semibold text-slate-800">Local RAG Chatbot</h1>
          <p className="text-xs text-slate-400">LangChain · ChromaDB · Ollama</p>
        </div>
      </header>

      <div className="scrollbar-thin flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-3xl flex-col gap-5 px-6 py-8">
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              {...msg}
              onRestart={
                msg.role === 'assistant' && msg.prompt ? () => handleRestart(msg.id) : undefined
              }
            />
          ))}
          {isThinking && <ThinkingBubble />}
          <div ref={scrollAnchorRef} />
        </div>
      </div>

      <div className="border-t border-indigo-100/70 bg-white/80 px-6 py-5 backdrop-blur">
        <form onSubmit={handleSend} className="mx-auto max-w-3xl">
          <div className="flex items-end gap-2 rounded-3xl border border-slate-200 bg-white px-4 py-2.5 shadow-sm transition-all focus-within:border-transparent focus-within:shadow-md focus-within:ring-2 focus-within:ring-violet-500">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  handleSend(e);
                }
              }}
              placeholder="Ask a question about your documents..."
              rows={1}
              className="max-h-40 flex-1 resize-none bg-transparent py-1.5 text-[15px] text-slate-800 placeholder:text-slate-400 outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim() || isThinking}
              aria-label="Send message"
              className="mb-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white transition disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none enabled:bg-gradient-to-r enabled:from-blue-600 enabled:to-violet-600 enabled:shadow-md enabled:shadow-indigo-200 enabled:hover:opacity-90"
            >
              <ArrowUp size={18} />
            </button>
          </div>
          <p className="mt-2 text-center text-xs text-slate-400">
            Responses are generated locally and may be inaccurate.
          </p>
        </form>
      </div>
    </div>
  );
}
