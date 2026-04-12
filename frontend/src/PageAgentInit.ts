import { PageAgent } from 'page-agent';

let agentInstance: PageAgent | null = null;

export function initPageAgent() {
  if (agentInstance) return agentInstance;

  const baseURL = import.meta.env.VITE_LLM_BASE_URL || 'https://token-plan-cn.xiaomimimo.com/v1';
  const apiKey = import.meta.env.VITE_LLM_API_KEY || 'tp-c3m5bswivfv8s6fua13o6elcxhikfwc8p5xt4fs9okjdjqw1';
  const model = import.meta.env.VITE_LLM_MODEL || 'mimo-v2-pro';

  console.log('[PageAgent] Initializing with model:', model);
  
  agentInstance = new PageAgent({
    baseURL,
    apiKey,
    model,
    language: 'zh-CN',
  });

  // 如果 panel 被 disposed 或者由于某些原因不可用，我们拦截默认的 close 行为
  // 在某些版本的 PageAgent 中，点击 X 会直接 dispose 掉整个 panel
  if (agentInstance.panel && agentInstance.panel.wrapper) {
    const closeBtn = agentInstance.panel.wrapper.querySelector('.page-agent-close-btn') || 
                     agentInstance.panel.wrapper.querySelector('[title="Close"]') ||
                     agentInstance.panel.wrapper.querySelector('button:last-child'); // heuristic
    
    if (closeBtn) {
      // 移除原有的事件监听（如果能）或者拦截点击
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        agentInstance!.panel.hide(); // 强制覆盖为 hide
      }, true);
    }
  }
  
  return agentInstance;
}

export function showPageAgentPanel() {
  if (!agentInstance) {
    initPageAgent();
  }
  
  if (agentInstance && agentInstance.panel) {
    try {
      // 如果 wrapper 存在但被移除了，放回去
      if (agentInstance.panel.wrapper && !document.body.contains(agentInstance.panel.wrapper)) {
        document.body.appendChild(agentInstance.panel.wrapper);
      }
      // 强制修改 CSS 样式展示
      agentInstance.panel.wrapper.style.display = "block";
      agentInstance.panel.wrapper.style.opacity = "1";
      agentInstance.panel.wrapper.style.transform = "translateX(-50%) translateY(0)";
      agentInstance.panel.show();
    } catch (e) {
      console.warn('Panel show failed, trying to re-init', e);
      agentInstance = null;
      initPageAgent();
      agentInstance!.panel.show();
    }
  }
}
