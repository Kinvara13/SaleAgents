import { useState, useEffect } from "react";
import { Modal } from "../components/Modal";
import { Select } from "../components/Select";

interface LLMProvider {
  id: string;
  name: string;
  base_url: string;
  api_key_masked: string;
  model: string;
  protocol: string;
}

interface LLMConfig {
  providers: LLMProvider[];
  active_provider_id: string | null;
}

interface NewProvider {
  id?: string;
  name: string;
  base_url: string;
  api_key: string;
  model: string;
  protocol: string;
}

const API_BASE = "/api/v1";

export function LLMConfigPage() {
  const [config, setConfig] = useState<LLMConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addForm, setAddForm] = useState<NewProvider>({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" });
  const [addSaving, setAddSaving] = useState(false);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingProvider, setEditingProvider] = useState<LLMProvider | null>(null);
  const [editForm, setEditForm] = useState<NewProvider>({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" });
  const [editSaving, setEditSaving] = useState(false);

  const [testModal, setTestModal] = useState<{ open: boolean; provider?: LLMProvider }>({ open: false });
  const [testForm, setTestForm] = useState<NewProvider>({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; response_time_ms?: number } | null>(null);

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
    } catch {
      setError("加载配置失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setAddSaving(true);
    try {
      const res = await fetch(`${API_BASE}/llm-config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(addForm),
      });
      if (!res.ok) throw new Error("Failed to add");
      await fetchConfig();
      setIsAddModalOpen(false);
      setAddForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" });
    } catch {
      setError("添加失败");
    } finally {
      setAddSaving(false);
    }
  }

  async function handleActivate(id: string) {
    try {
      await fetch(`${API_BASE}/llm-config/activate/${id}`, { method: "POST" });
      await fetchConfig();
    } catch {
      setError("切换失败");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("确定要删除这个模型配置吗？")) return;
    try {
      await fetch(`${API_BASE}/llm-config/${id}`, { method: "DELETE" });
      await fetchConfig();
    } catch {
      setError("删除失败");
    }
  }

  function openEditModal(provider: LLMProvider) {
    setEditingProvider(provider);
    setEditForm({
      name: provider.name,
      base_url: provider.base_url,
      api_key: "",
      model: provider.model,
      protocol: provider.protocol || "openai",
    });
    setIsEditModalOpen(true);
  }

  async function handleEdit(e: React.FormEvent) {
    e.preventDefault();
    if (!editingProvider) return;
    setEditSaving(true);
    try {
      const payload: Record<string, string> = {
        name: editForm.name,
        base_url: editForm.base_url,
        model: editForm.model,
        protocol: editForm.protocol,
        api_key: editForm.api_key.trim(),
      };
      const res = await fetch(`${API_BASE}/llm-config/${editingProvider.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to update");
      await fetchConfig();
      setIsEditModalOpen(false);
      setEditingProvider(null);
      setEditForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" });
    } catch {
      setError("修改失败");
    } finally {
      setEditSaving(false);
    }
  }

  function openTestModal(provider?: LLMProvider) {
    if (provider) {
      setTestForm({ id: provider.id, name: provider.name, base_url: provider.base_url, api_key: "", model: provider.model, protocol: provider.protocol || "openai" });
    } else {
      setTestForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" });
    }
    setTestResult(null);
    setTestModal({ open: true, provider });
  }

  async function handleTest(e: React.FormEvent) {
    e.preventDefault();
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`${API_BASE}/llm-config/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(testForm),
      });
      const data = await res.json();
      setTestResult(data);
    } catch {
      setTestResult({ success: false, message: "测试请求失败，请检查网络" });
    } finally {
      setTesting(false);
    }
  }

  if (loading) return <div className="page-loading">加载中...</div>;

  return (
    <div className="workspace-page">
      <div className="section-card-head" style={{ marginBottom: "24px" }}>
        <div>
          <p className="eyebrow" style={{ fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", color: "#8cc7ff", margin: "0 0 4px" }}>LLM Configuration</p>
          <h3 style={{ margin: 0, fontSize: "1.3rem", color: "#f4f8ff" }}>大模型配置</h3>
          <p className="muted-caption" style={{ margin: "6px 0 0", fontSize: "0.85rem" }}>管理 AI 模型供应商，激活其中一个作为全系统默认引擎。</p>
        </div>
        <button className="primary-button" onClick={() => setIsAddModalOpen(true)}>
          + 添加模型
        </button>
      </div>

      {error && (
        <div style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)", color: "#ef4444", padding: "12px 16px", borderRadius: "8px", marginBottom: "16px", fontSize: "0.9rem" }}>
          {error}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {config?.providers.length === 0 && (
          <div className="workspace-card" style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>
            暂无模型配置，请点击右上角"添加模型"进行配置。
          </div>
        )}
        {config?.providers.map((provider) => (
          <div
            key={provider.id}
            className="workspace-card"
            style={{
              padding: "20px 24px",
              border: config.active_provider_id === provider.id ? "1px solid rgba(59, 130, 246, 0.4)" : "1px solid rgba(129, 186, 255, 0.1)",
              background: config.active_provider_id === provider.id ? "rgba(59, 130, 246, 0.08)" : "rgba(255,255,255,0.02)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "12px" }}>
                  <h4 style={{ margin: 0, fontSize: "1.1rem", color: "#f4f8ff" }}>{provider.name}</h4>
                  {config.active_provider_id === provider.id && (
                    <span style={{ background: "rgba(59, 130, 246, 0.2)", color: "#60a5fa", fontSize: "0.75rem", padding: "2px 10px", borderRadius: "10px", border: "1px solid rgba(59, 130, 246, 0.3)" }}>
                      使用中
                    </span>
                  )}
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "8px" }}>
                  <div style={{ fontSize: "0.85rem" }}>
                    <span style={{ color: "#64748b" }}>协议：</span>
                    <span style={{ color: "#dce9ff", fontFamily: "monospace" }}>{provider.protocol === "anthropic" ? "Anthropic" : "OpenAI"}</span>
                  </div>
                  <div style={{ fontSize: "0.85rem" }}>
                    <span style={{ color: "#64748b" }}>模型：</span>
                    <span style={{ color: "#dce9ff", fontFamily: "monospace" }}>{provider.model}</span>
                  </div>
                  <div style={{ fontSize: "0.85rem" }}>
                    <span style={{ color: "#64748b" }}>API：</span>
                    <span style={{ color: "#94a3b8", fontFamily: "monospace" }}>{provider.base_url}</span>
                  </div>
                  <div style={{ fontSize: "0.85rem" }}>
                    <span style={{ color: "#64748b" }}>Key：</span>
                    <span style={{ color: "#94a3b8", fontFamily: "monospace" }}>{provider.api_key_masked}</span>
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", gap: "8px", marginLeft: "16px" }}>
                <button className="primary-button" style={{ padding: "6px 14px", fontSize: "0.8rem", background: "rgba(16, 185, 129, 0.15)", border: "1px solid rgba(16, 185, 129, 0.3)", color: "#34d399" }} onClick={() => openTestModal(provider)}>
                  测试
                </button>
                {config.active_provider_id !== provider.id && (
                  <button className="primary-button" style={{ padding: "6px 14px", fontSize: "0.8rem" }} onClick={() => handleActivate(provider.id)}>
                    激活
                  </button>
                )}
                <button className="ghost-button" style={{ padding: "6px 14px", fontSize: "0.8rem" }} onClick={() => openEditModal(provider)}>
                  编辑
                </button>
                <button className="ghost-button" style={{ padding: "6px 14px", fontSize: "0.8rem", color: "#ef4444", borderColor: "rgba(239, 68, 68, 0.3)" }} onClick={() => handleDelete(provider.id)}>
                  删除
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 新增模型弹窗 */}
      <Modal
        isOpen={isAddModalOpen}
        title="添加模型"
        maxWidth="520px"
        onClose={() => { setIsAddModalOpen(false); setAddForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" }); }}
        footer={
          <>
            <button className="ghost-button" onClick={() => { setIsAddModalOpen(false); setAddForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" }); }}>
              取消
            </button>
            <button className="primary-button" form="add-model-form" type="submit" disabled={addSaving}>
              {addSaving ? "保存中..." : "保存"}
            </button>
          </>
        }
      >
        <form id="add-model-form" onSubmit={handleAdd} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <label className="form-field">
            <span>配置名称</span>
            <input type="text" placeholder="例如：小米 Mimo" value={addForm.name} onChange={(e) => setAddForm({ ...addForm, name: e.target.value })} required />
          </label>
          <label className="form-field">
            <span>协议类型</span>
            <Select 
              value={addForm.protocol} 
              onChange={(val) => setAddForm({ ...addForm, protocol: val })}
              options={[
                { value: "openai", label: "OpenAI 兼容协议" },
                { value: "anthropic", label: "Anthropic (Messages) 协议" }
              ]}
            />
          </label>
          <label className="form-field">
            <span>API Base URL</span>
            <input type="text" placeholder={addForm.protocol === "anthropic" ? "https://api.anthropic.com/v1" : "https://api.example.com/v1"} value={addForm.base_url} onChange={(e) => setAddForm({ ...addForm, base_url: e.target.value })} required />
          </label>
          <label className="form-field">
            <span>API Key</span>
            <input type="password" placeholder="sk-..." value={addForm.api_key} onChange={(e) => setAddForm({ ...addForm, api_key: e.target.value })} required />
          </label>
          <label className="form-field">
            <span>模型名称</span>
            <input type="text" placeholder="例如：gpt-4o、claude-3-5-sonnet" value={addForm.model} onChange={(e) => setAddForm({ ...addForm, model: e.target.value })} required />
          </label>
        </form>
      </Modal>

      {/* 编辑模型弹窗 */}
      <Modal
        isOpen={isEditModalOpen}
        title={`编辑模型：${editingProvider?.name || ""}`}
        maxWidth="520px"
        onClose={() => { setIsEditModalOpen(false); setEditingProvider(null); setEditForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" }); }}
        footer={
          <>
            <button className="ghost-button" onClick={() => { setIsEditModalOpen(false); setEditingProvider(null); setEditForm({ name: "", base_url: "", api_key: "", model: "", protocol: "openai" }); }}>
              取消
            </button>
            <button className="primary-button" form="edit-model-form" type="submit" disabled={editSaving}>
              {editSaving ? "保存中..." : "保存"}
            </button>
          </>
        }
      >
        <form id="edit-model-form" onSubmit={handleEdit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <label className="form-field">
            <span>配置名称</span>
            <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} required />
          </label>
          <label className="form-field">
            <span>协议类型</span>
            <Select 
              value={editForm.protocol} 
              onChange={(val) => setEditForm({ ...editForm, protocol: val })}
              options={[
                { value: "openai", label: "OpenAI 兼容协议" },
                { value: "anthropic", label: "Anthropic (Messages) 协议" }
              ]}
            />
          </label>
          <label className="form-field">
            <span>API Base URL</span>
            <input type="text" value={editForm.base_url} onChange={(e) => setEditForm({ ...editForm, base_url: e.target.value })} required />
          </label>
          <label className="form-field">
            <span>API Key <em style={{ fontSize: "0.8em", color: "#64748b" }}>（留空则保持不变）</em></span>
            <input type="password" placeholder="sk-..." value={editForm.api_key} onChange={(e) => setEditForm({ ...editForm, api_key: e.target.value })} />
          </label>
          <label className="form-field">
            <span>模型名称</span>
            <input type="text" value={editForm.model} onChange={(e) => setEditForm({ ...editForm, model: e.target.value })} required />
          </label>
        </form>
      </Modal>

      {/* 测试模型弹窗 */}
      <Modal
        isOpen={testModal.open}
        title="测试模型连接"
        maxWidth="520px"
        onClose={() => { setTestModal({ open: false }); setTestResult(null); }}
        footer={
          <>
            <button className="ghost-button" onClick={() => { setTestModal({ open: false }); setTestResult(null); }}>
              关闭
            </button>
            <button className="primary-button" form="test-model-form" type="submit" disabled={testing} style={{ background: testing ? "rgba(16,185,129,0.5)" : "rgba(16,185,129,0.8)", borderColor: "rgba(16,185,129,0.4)" }}>
              {testing ? "测试中..." : "开始测试"}
            </button>
          </>
        }
      >
        <form id="test-model-form" onSubmit={handleTest} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <label className="form-field">
            <span>协议类型</span>
            <Select 
              value={testForm.protocol} 
              onChange={(val) => setTestForm({ ...testForm, protocol: val })}
              options={[
                { value: "openai", label: "OpenAI 兼容协议" },
                { value: "anthropic", label: "Anthropic (Messages) 协议" }
              ]}
            />
          </label>
          <label className="form-field">
            <span>API Base URL</span>
            <input type="text" placeholder={testForm.protocol === "anthropic" ? "https://api.anthropic.com/v1" : "https://api.example.com/v1"} value={testForm.base_url} onChange={(e) => setTestForm({ ...testForm, base_url: e.target.value })} required />
          </label>
          <label className="form-field">
            <span>API Key {testModal.provider && <em style={{ fontSize: "0.8em", color: "#64748b" }}>（留空则使用已保存的密钥）</em>}</span>
            <input type="password" placeholder="sk-..." value={testForm.api_key} onChange={(e) => setTestForm({ ...testForm, api_key: e.target.value })} required={!testModal.provider} />
          </label>
          <label className="form-field">
            <span>模型名称</span>
            <input type="text" placeholder="例如：gpt-4o、mimo-v2-pro" value={testForm.model} onChange={(e) => setTestForm({ ...testForm, model: e.target.value })} required />
          </label>
        </form>

        {testResult && (
          <div style={{
            marginTop: "12px",
            padding: "14px 16px",
            borderRadius: "8px",
            background: testResult.success ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)",
            border: `1px solid ${testResult.success ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
            color: testResult.success ? "#34d399" : "#ef4444",
            fontSize: "0.9rem",
            lineHeight: "1.5",
          }}>
            <div style={{ fontWeight: 600, marginBottom: "6px" }}>
              {testResult.success ? "✅ 测试成功" : "❌ 测试失败"}
            </div>
            <div style={{ color: testResult.success ? "#a7f3d0" : "#fca5a5", wordBreak: "break-all" }}>
              {testResult.message}
            </div>
            {testResult.response_time_ms && (
              <div style={{ marginTop: "6px", fontSize: "0.8rem", opacity: 0.7 }}>
                响应耗时：{testResult.response_time_ms}ms
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
