import { showPageAgentPanel } from "../PageAgentInit";

export function PageAgentFab() {
  return (
    <button
      className="page-agent-fab"
      onClick={showPageAgentPanel}
      title="唤起 AI 助手"
    >
      <svg
        width="26"
        height="26"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M12 2a2 2 0 0 1 2 2c-.11.66-.45 1.25-1 1.71-.56.45-1.25.71-2 .71s-1.44-.26-2-.71A2.99 2.99 0 0 1 8 4a2 2 0 0 1 2-2h2z"></path>
        <path d="M14.29 8.6A5.99 5.99 0 0 1 18 14c0 3.31-2.69 6-6 6s-6-2.69-6-6c0-2.67 1.75-4.99 4.29-5.73"></path>
        <line x1="12" y1="10" x2="12" y2="14"></line>
        <line x1="10" y1="12" x2="14" y2="12"></line>
      </svg>
    </button>
  );
}