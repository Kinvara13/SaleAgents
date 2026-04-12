import { useState, useEffect } from "react";

interface LLMProvider {
  id: string;
  name: string;
  base_url: string;
  api_key_masked: string;
  model: string;
}

interface LLMConfig {
  providers: LLMProvider[];
  active_provider_id: string | null;
}

interface NewProvider {
  name: string;
  base_url: string;
  api_key: string;
  model: string;
}

const API_BASE = "http://localhost:8000/api/v1";

export function LLMConfigPage() {
  const [config, setConfig] = useState<LLMConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewProvider>({
    name: "",
    base_url: "",
    api_key: "",
    model: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  async function fetchConfig() {
    try {
      const res = await fetch(`${API_BASE}/llm-config`);
      if (!res.ok) throw new Error("Failed to fetch");
      const data = await res.json();
      setConfig(data);
      setError(null);
    } catch (e) {
      setError("加载配置失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/llm-config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error("Failed to add");
      await fetchConfig();
      setShowForm(false);
      setForm({ name: "", base_url: "", api_key: "", model: "" });
    } catch (e) {
      setError("添加失败");
    } finally {
      setSaving(false);
    }
  }

  async function handleActivate(id: string) {
    try {
      await fetch(`${API_BASE}/llm-config/activate/${id}`, { method: "POST" });
      await fetchConfig();
    } catch (e) {
      setError("切换失败");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("确定要删除这个模型配置吗？")) return;
    try {
      await fetch(`${API_BASE}/llm-config/${id}`, { method: "DELETE" });
      await fetchConfig();
    } catch (e) {
      setError("删除失败");
    }
  }

  if (loading) return <div className="page-loading">加载中...</div>;

  return (
    <div className="llm-config-page">
      <div className="page-header">
        <h2>大模型配置</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "取消" : "+ 添加模型"}
        </button>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {showForm && (
        <form className="config-form" onSubmit={handleAdd}>
          <div className="form-group">
            <label>配置名称</label>
            <input
              type="text"
              placeholder="例如：小米 Mimo"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>API Base URL</label>
            <input
              type="text"
              placeholder="https://api.example.com/v1"
              value={form.base_url}
              onChange={(e) => setForm({ ...form, base_url: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>API Key</label>
            <input
              type="password"
              placeholder="sk-..."
              value={form.api_key}
              onChange={(e) => setForm({ ...form, api_key: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>模型名称</label>
            <input
              type="text"
              placeholder="例如：gpt-4o、mimo-v2-pro"
              value={form.model}
              onChange={(e) => setForm({ ...form, model: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? "保存中..." : "保存"}
          </button>
        </form>
      )}

      <div className="provider-list">
        {config?.providers.length === 0 && (
          <div className="empty-state">暂无模型配置，请添加</div>
        )}
        {config?.providers.map((provider) => (
          <div
            key={provider.id}
            className={`provider-card ${
              config.active_provider_id === provider.id ? "active" : ""
            }`}
          >
            <div className="provider-info">
              <div className="provider-header">
                <h3>{provider.name}</h3>
                {config.active_provider_id === provider.id && (
                  <span className="badge-active">使用中</span>
                )}
              </div>
              <div className="provider-detail">
                <span className="label">模型：</span>
                <span className="value">{provider.model}</span>
              </div>
              <div className="provider-detail">
                <span className="label">API：</span>
                <span className="value">{provider.base_url}</span>
              </div>
              <div className="provider-detail">
                <span className="label">Key：</span>
                <span className="value masked">{provider.api_key_masked}</span>
              </div>
            </div>
            <div className="provider-actions">
              {config.active_provider_id !== provider.id && (
                <button
                  className="btn-activate"
                  onClick={() => handleActivate(provider.id)}
                >
                  激活
                </button>
              )}
              <button
                className="btn-delete"
                onClick={() => handleDelete(provider.id)}
              >
                删除
              </button>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .llm-config-page {
          padding: 24px;
          max-width: 800px;
        }
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }
        .page-header h2 {
          margin: 0;
          font-size: 20px;
          color: var(--text-primary);
        }
        .btn-primary {
          background: var(--accent);
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        }
        .btn-primary:hover {
          opacity: 0.9;
        }
        .btn-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .config-form {
          background: var(--bg-secondary);
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 24px;
        }
        .form-group {
          margin-bottom: 16px;
        }
        .form-group label {
          display: block;
          margin-bottom: 6px;
          font-size: 13px;
          color: var(--text-secondary);
        }
        .form-group input {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid var(--border);
          border-radius: 6px;
          font-size: 14px;
          background: var(--bg-primary);
          color: var(--text-primary);
        }
        .provider-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .provider-card {
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }
        .provider-card.active {
          border-color: var(--accent);
          background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, transparent 60%);
        }
        .provider-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 8px;
        }
        .provider-header h3 {
          margin: 0;
          font-size: 16px;
          color: var(--text-primary);
        }
        .badge-active {
          background: var(--accent);
          color: white;
          font-size: 11px;
          padding: 2px 8px;
          border-radius: 10px;
        }
        .provider-detail {
          font-size: 13px;
          margin-bottom: 4px;
          color: var(--text-secondary);
        }
        .provider-detail .label {
          color: var(--text-tertiary);
        }
        .provider-detail .value {
          color: var(--text-primary);
        }
        .provider-detail .masked {
          font-family: monospace;
        }
        .provider-actions {
          display: flex;
          gap: 8px;
        }
        .btn-activate {
          background: var(--accent);
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }
        .btn-delete {
          background: transparent;
          color: #ef4444;
          border: 1px solid #ef4444;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }
        .alert-error {
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #dc2626;
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 16px;
        }
        .empty-state {
          text-align: center;
          padding: 40px;
          color: var(--text-tertiary);
        }
        .page-loading {
          padding: 40px;
          text-align: center;
          color: var(--text-tertiary);
        }
      `}</style>
    </div>
  );
}
