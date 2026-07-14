import { useCallback, useEffect, useState } from 'react';
import { Database, Server } from 'lucide-react';
import FileUpload from './FileUpload';
import Chatbox from './Chatbox';
import Sidebar from './Sidebar';
import { deleteSession, listSessions } from '../api';

export default function ChatLayout() {
  const [sessions, setSessions] = useState([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState(null);

  const refreshSessions = useCallback(async () => {
    try {
      const data = await listSessions();
      setSessions(data);
      return data;
    } catch {
      return [];
    }
  }, []);

  useEffect(() => {
    setIsLoadingSessions(true);
    refreshSessions().finally(() => setIsLoadingSessions(false));
  }, [refreshSessions]);

  const handleNewChat = useCallback(() => {
    setActiveSessionId(null);
  }, []);

  const handleSelectSession = useCallback((sessionId) => {
    setActiveSessionId(sessionId);
  }, []);

  // First message of a brand-new chat: the backend just minted a session,
  // so make it active and refresh the sidebar to pick up its title.
  const handleSessionCreated = useCallback(
    async (newSessionId) => {
      setActiveSessionId(newSessionId);
      await refreshSessions();
    },
    [refreshSessions],
  );

  const handleDeleteSession = useCallback(
    async (sessionId) => {
      try {
        await deleteSession(sessionId);
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));
        if (sessionId === activeSessionId) {
          setActiveSessionId(null);
        }
      } catch {
        // Non-fatal — the session simply stays in the list if deletion failed.
      }
    },
    [activeSessionId],
  );

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-50 text-slate-800">
      <aside className="flex w-[22rem] shrink-0 flex-col gap-6 border-r border-indigo-100/70 bg-indigo-50/40 p-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-violet-600 shadow-sm shadow-indigo-200">
            <Database size={17} className="text-white" />
          </div>
          <div>
            <h2 className="text-[15px] font-semibold text-slate-800">Knowledge Base</h2>
            <p className="text-xs text-slate-400">Your documents, searchable</p>
          </div>
        </div>

        <FileUpload />

        <div className="min-h-0 flex-1 border-t border-indigo-100/70 pt-4">
          <Sidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            isLoading={isLoadingSessions}
            onSelectSession={handleSelectSession}
            onNewChat={handleNewChat}
            onDeleteSession={handleDeleteSession}
          />
        </div>

        <div className="flex items-start gap-2.5 rounded-2xl border border-indigo-100 bg-white/70 p-4 text-xs text-slate-500">
          <Server size={14} className="mt-0.5 shrink-0 text-indigo-400" />
          <div className="space-y-0.5">
            <p className="font-medium text-slate-600">Running fully local</p>
            <p>FastAPI · LangChain · ChromaDB · Ollama</p>
          </div>
        </div>
      </aside>

      <main className="flex flex-1 flex-col overflow-hidden">
        <Chatbox sessionId={activeSessionId} onSessionCreated={handleSessionCreated} />
      </main>
    </div>
  );
}
