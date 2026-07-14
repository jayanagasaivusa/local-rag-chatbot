import { LogOut, MessageSquarePlus, MessageSquareText, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

function formatDate(isoString) {
  try {
    return new Date(isoString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return '';
  }
}

/**
 * ChatGPT-style list of past chat sessions. Purely presentational — all
 * fetching/state lives in App so both the sidebar and the chat window stay
 * in sync on the active session.
 */
export default function Sidebar({
  sessions,
  activeSessionId,
  isLoading,
  onSelectSession,
  onNewChat,
  onDeleteSession,
}) {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-full flex-col gap-3">
      <button
        type="button"
        onClick={onNewChat}
        className="flex items-center justify-center gap-2 rounded-xl border border-indigo-200 bg-white/70 px-3.5 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition hover:border-violet-300 hover:bg-indigo-50/70"
      >
        <MessageSquarePlus size={16} className="text-indigo-500" />
        New chat
      </button>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <p className="mb-1.5 px-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Chats
        </p>

        {isLoading && (
          <p className="px-1 py-2 text-xs text-slate-400">Loading chats...</p>
        )}

        {!isLoading && sessions.length === 0 && (
          <p className="px-1 py-2 text-xs text-slate-400">No chats yet. Start one above.</p>
        )}

        <ul className="space-y-1">
          {sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <li key={session.id}>
                <button
                  type="button"
                  onClick={() => onSelectSession(session.id)}
                  className={`group flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-sm transition ${
                    isActive
                      ? 'bg-white shadow-sm shadow-indigo-100 ring-1 ring-indigo-100'
                      : 'hover:bg-white/60'
                  }`}
                >
                  <MessageSquareText
                    size={15}
                    className={`shrink-0 ${isActive ? 'text-indigo-500' : 'text-slate-400'}`}
                  />
                  <span className="min-w-0 flex-1 truncate text-slate-700">{session.title}</span>
                  <span className="shrink-0 text-[11px] text-slate-300">
                    {formatDate(session.created_at)}
                  </span>
                  <span
                    role="button"
                    tabIndex={-1}
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    className="shrink-0 rounded-md p-1 text-slate-300 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                    aria-label="Delete chat"
                  >
                    <Trash2 size={13} />
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="flex items-center justify-between gap-2 rounded-2xl border border-indigo-100 bg-white/70 p-3 text-xs">
        <span className="min-w-0 truncate font-medium text-slate-600">{user?.id ? 'Signed in' : ''}</span>
        <button
          type="button"
          onClick={logout}
          className="flex shrink-0 items-center gap-1.5 rounded-lg px-2 py-1.5 font-medium text-slate-500 transition hover:bg-red-50 hover:text-red-600"
        >
          <LogOut size={13} />
          Log out
        </button>
      </div>
    </div>
  );
}
