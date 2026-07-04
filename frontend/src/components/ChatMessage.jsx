import { useEffect, useRef, useState } from 'react';
import { Check, Copy, RotateCcw, Volume2, VolumeX } from 'lucide-react';

function ThinkingDots() {
  return (
    <span className="flex items-center gap-1 py-1">
      <span className="h-1.5 w-1.5 animate-bounceDot rounded-full bg-slate-400 [animation-delay:-0.32s]" />
      <span className="h-1.5 w-1.5 animate-bounceDot rounded-full bg-slate-400 [animation-delay:-0.16s]" />
      <span className="h-1.5 w-1.5 animate-bounceDot rounded-full bg-slate-400" />
    </span>
  );
}

/**
 * Small ghost icon button used in the AI message action bar. Kept as a
 * local component so copy/listen/restart all share identical sizing,
 * hover, and focus treatment.
 */
function ActionButton({ onClick, label, active, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className={`inline-flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
        active
          ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white shadow-sm shadow-indigo-200'
          : 'text-slate-400 hover:bg-indigo-50 hover:text-indigo-600'
      }`}
    >
      {children}
    </button>
  );
}

export default function ChatMessage({
  content,
  sources,
  isError,
  isRegenerating,
  onRestart,
  role,
}) {
  const isUser = role === 'user';
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const utteranceRef = useRef(null);

  // If the browser navigates away or the message unmounts mid-speech, make
  // sure we don't leave a dangling utterance talking over a new one.
  useEffect(() => {
    return () => {
      if (isSpeaking) {
        window.speechSynthesis?.cancel();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard permission denied or unavailable — fail silently, no UI needed.
    }
  };

  const handleListen = () => {
    if (!('speechSynthesis' in window)) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(content);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  if (isUser) {
    return (
      <div className="flex w-full animate-fadeInUp justify-end">
        <div className="max-w-[75%] rounded-3xl rounded-tr-lg bg-gradient-to-r from-blue-600 to-violet-600 px-5 py-3 text-[15px] leading-relaxed text-white shadow-md">
          <p className="whitespace-pre-wrap break-words">{content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full animate-fadeInUp justify-start">
      <div className="flex max-w-[80%] flex-col gap-1.5">
        <div
          className={`rounded-3xl rounded-tl-lg border px-5 py-3 text-[15px] leading-relaxed ${
            isError
              ? 'border-red-100 bg-red-50 text-red-700 shadow-sm'
              : 'border-slate-100 bg-white text-slate-800 shadow-sm shadow-indigo-100'
          }`}
        >
          {isRegenerating ? (
            <ThinkingDots />
          ) : (
            <p className="whitespace-pre-wrap break-words">{content}</p>
          )}

          {!isRegenerating && sources && sources.length > 0 && (
            <div className="mt-3 border-t border-slate-100 pt-2.5">
              <p className="mb-1 text-xs font-medium text-slate-400">Sources</p>
              <ul className="space-y-0.5 text-xs text-slate-500">
                {sources.map((src, idx) => (
                  <li key={idx} className="truncate">
                    📄 {src}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {!isRegenerating && (
          <div className="flex items-center gap-0.5 pl-1">
            <ActionButton onClick={handleCopy} label={copied ? 'Copied' : 'Copy'} active={copied}>
              {copied ? <Check size={16} /> : <Copy size={16} />}
            </ActionButton>

            <ActionButton
              onClick={handleListen}
              label={isSpeaking ? 'Stop reading' : 'Read aloud'}
              active={isSpeaking}
            >
              {isSpeaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
            </ActionButton>

            {onRestart && (
              <ActionButton onClick={onRestart} label="Regenerate response">
                <RotateCcw size={16} />
              </ActionButton>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
