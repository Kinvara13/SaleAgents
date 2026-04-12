import { useEffect, useState, type FormEvent } from "react";

import { PageHeader } from "../components/PageHeader";
import { Modal } from "../components/Modal";
import { Select } from "../components/Select";
import {
  deleteRuleConfig,
  getRuleConfigs,
  getRuleStatistics,
  createRuleConfig,
  updateRuleConfig,
  initializeDefaultRules,
} from "../services/workspace";
import type { RuleConfig, RuleStatistics } from "../types";

const CATEGORIES = ["全部", "付款风险", "责任风险", "知识产权", "合规风险", "交付风险", "验收风险"];
const LEVELS = ["P0", "P1", "P2"];

export function RulesPage() {
  const [rules, setRules] = useState<RuleConfig[]>([]);
  const [stats, setStats] = useState<RuleStatistics[]>([]);
  const [activeCategory, setActiveCategory] = useState("全部");
  const [isCreating, setIsCreating] = useState(false);
  const [actionMessage, setActionMessage] = useState("");
  const [actionError, setActionError] = useState("");

  // create form state
  const [formName, setFormName] = useState("");
  const [formTitle, setFormTitle] = useState("");
  const [formIssueType, setFormIssueType] = useState("合同条款");
  const [formLevel, setFormLevel] = useState("P1");
  const [formCategory, setFormCategory] = useState("付款风险");
  const [formDetail, setFormDetail] = useState("");
  const [formSuggestion, setFormSuggestion] = useState("");
  const [formPatterns, setFormPatterns] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    void loadData();
  }, []);

  async function loadData() {
    try {
      const [rulesData, statsData] = await Promise.all([
        getRuleConfigs(),
        getRuleStatistics(),
      ]);
      setRules(rulesData);
      setStats(statsData);
    } catch {
      setActionError("加载规则数据失败，请确认后端服务已启动。");
    }
  }

  const filteredRules =
    activeCategory === "全部"
      ? rules
      : rules.filter((r) => r.category === activeCategory);

  function getStatsForRule(ruleName: string): RuleStatistics | undefined {
    return stats.find((s) => s.rule_name === ruleName);
  }

  async function handleToggleEnabled(rule: RuleConfig) {
    setActionMessage("");
    setActionError("");
    try {
      await updateRuleConfig(rule.id, { is_enabled: !rule.is_enabled });
      setActionMessage(`已${rule.is_enabled ? "禁用" : "启用"}规则：${rule.title}`);
      await loadData();
    } catch {
      setActionError("更新规则状态失败。");
    }
  }

  async function handleDelete(rule: RuleConfig) {
    setActionMessage("");
    setActionError("");
    try {
      await deleteRuleConfig(rule.id);
      setActionMessage(`已删除规则：${rule.title}`);
      await loadData();
    } catch {
      setActionError("删除规则失败。");
    }
  }

  async function handleInitialize() {
    setActionMessage("");
    setActionError("");
    try {
      const result = await initializeDefaultRules();
      setActionMessage(result.message);
      await loadData();
    } catch {
      setActionError("初始化默认规则失败。");
    }
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setActionMessage("");
    setActionError("");
    try {
      await createRuleConfig({
        name: formName.trim(),
        title: formTitle.trim(),
        issue_type: formIssueType,
        level: formLevel,
        category: formCategory,
        detail: formDetail.trim(),
        suggestion: formSuggestion.trim(),
        patterns: formPatterns.trim(),
      });
      setActionMessage(`已创建规则：${formTitle}`);
      setIsCreating(false);
      resetForm();
      await loadData();
    } catch {
      setActionError("创建规则失败，请检查必填字段。");
    } finally {
      setIsSubmitting(false);
    }
  }

  function resetForm() {
    setFormName("");
    setFormTitle("");
    setFormIssueType("合同条款");
    setFormLevel("P1");
    setFormCategory("付款风险");
    setFormDetail("");
    setFormSuggestion("");
    setFormPatterns("");
  }

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Rule Center"
        title="规则中心"
        description="管理合同审查规则库，查看规则命中统计，支持新增、编辑、启停用和删除规则。"
        actions={
          <>
            <button className="primary-button" type="button" onClick={() => setIsCreating(true)}>
              新增规则
            </button>
            <button className="ghost-button" type="button" onClick={handleInitialize}>
              初始化默认规则
            </button>
          </>
        }
      />

      {actionMessage ? <p className="form-success">{actionMessage}</p> : null}
      {actionError ? <p className="form-error">{actionError}</p> : null}

      {/* Statistics Overview */}
      <section className="mini-metric-grid">
        <article className="mini-metric mini-metric-blue">
          <span>已配置规则</span>
          <strong>{rules.length}</strong>
          <p>当前规则库总数</p>
        </article>
        <article className="mini-metric mini-metric-cyan">
          <span>已启用</span>
          <strong>{rules.filter((r) => r.is_enabled).length}</strong>
          <p>参与审查的活跃规则</p>
        </article>
        <article className="mini-metric mini-metric-amber">
          <span>总命中数</span>
          <strong>{stats.reduce((sum, s) => sum + s.hit_count, 0)}</strong>
          <p>所有规则的历史命中总数</p>
        </article>
        <article className="mini-metric mini-metric-violet">
          <span>平均准确率</span>
          <strong>
            {stats.length > 0
              ? `${(stats.reduce((sum, s) => sum + s.accuracy_rate, 0) / stats.length * 100).toFixed(0)}%`
              : "—"}
          </strong>
          <p>基于法务反馈的综合准确率</p>
        </article>
      </section>

      {/* Category Filters */}
      <section className="workspace-card">
        <div className="toolbar-row">
          <div className="filter-chips">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                className={`chip ${activeCategory === cat ? "chip-active" : ""}`}
                type="button"
                onClick={() => setActiveCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Rules Table */}
        <div className="data-table">
          <div className="table-row table-head-row">
            <span>规则名称</span>
            <span>类型</span>
            <span>等级</span>
            <span>分类</span>
            <span>命中 / 确认 / 误报</span>
            <span>准确率</span>
            <span>状态</span>
            <span>操作</span>
          </div>
          {filteredRules.length === 0 ? (
            <div className="table-row">
              <span style={{ gridColumn: "1 / -1", textAlign: "center", opacity: 0.5 }}>
                {rules.length === 0 ? "暂无规则，请点击「初始化默认规则」" : "当前分类下无规则"}
              </span>
            </div>
          ) : null}
          {filteredRules.map((rule) => {
            const ruleStat = getStatsForRule(rule.name);
            return (
              <div key={rule.id} className="table-row">
                <div className="table-title-cell">
                  <strong>{rule.title}</strong>
                  <span>{rule.detail.slice(0, 40)}{rule.detail.length > 40 ? "…" : ""}</span>
                </div>
                <span>{rule.issue_type}</span>
                <span className={`risk-pill risk-${rule.level.toLowerCase()}`}>{rule.level}</span>
                <span className="status-tag">{rule.category}</span>
                <span>
                  {ruleStat
                    ? `${ruleStat.hit_count} / ${ruleStat.confirmed_count} / ${ruleStat.dismissed_count}`
                    : "0 / 0 / 0"}
                </span>
                <span>
                  {ruleStat ? `${(ruleStat.accuracy_rate * 100).toFixed(0)}%` : "—"}
                </span>
                <span>
                  <button
                    className={rule.is_enabled ? "chip chip-active" : "chip"}
                    type="button"
                    onClick={() => handleToggleEnabled(rule)}
                    style={{ fontSize: "0.75rem", padding: "2px 8px" }}
                  >
                    {rule.is_enabled ? "已启用" : "已禁用"}
                  </button>
                </span>
                <span>
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() => handleDelete(rule)}
                    style={{ fontSize: "0.75rem", padding: "2px 8px", color: "#f87171" }}
                  >
                    删除
                  </button>
                </span>
              </div>
            );
          })}
        </div>
      </section>

      {/* Create Rule Form */}
      {isCreating ? (
        <section className="workspace-card project-form-card">
          <div className="section-card-head">
            <div>
              <p className="eyebrow">Create Rule</p>
              <h3>新增审查规则</h3>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={() => {
                setIsCreating(false);
                resetForm();
              }}
            >
              取消
            </button>
          </div>
          <form className="project-form-grid" onSubmit={handleCreate}>
            <label className="form-field">
              <span>规则标识</span>
              <input
                required
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="例如：payment_tail_risk"
              />
            </label>
            <label className="form-field">
              <span>规则名称</span>
              <input
                required
                value={formTitle}
                onChange={(e) => setFormTitle(e.target.value)}
                placeholder="例如：付款尾款比例风险"
              />
            </label>
            <label className="form-field">
              <span>问题类型</span>
              <input
                value={formIssueType}
                onChange={(e) => setFormIssueType(e.target.value)}
                placeholder="例如：合同条款"
              />
            </label>
            <label className="form-field">
              <span>风险等级</span>
              <Select 
                value={formLevel} 
                onChange={(val) => setFormLevel(val)}
                options={LEVELS.map((l) => ({ value: l, label: l }))}
              />
            </label>
            <label className="form-field">
              <span>规则分类</span>
              <Select 
                value={formCategory} 
                onChange={(val) => setFormCategory(val)}
                options={CATEGORIES.filter((c) => c !== "全部").map((c) => ({ value: c, label: c }))}
              />
            </label>
            <label className="form-field">
              <span>匹配模式（关键词，逗号分隔）</span>
              <input
                value={formPatterns}
                onChange={(e) => setFormPatterns(e.target.value)}
                placeholder="例如：尾款,终验,10%"
              />
            </label>
            <label className="form-field form-field-full">
              <span>风险说明</span>
              <input
                required
                value={formDetail}
                onChange={(e) => setFormDetail(e.target.value)}
                placeholder="描述该规则识别的风险场景"
              />
            </label>
            <label className="form-field form-field-full">
              <span>修订建议</span>
              <input
                required
                value={formSuggestion}
                onChange={(e) => setFormSuggestion(e.target.value)}
                placeholder="建议如何修改合同条款"
              />
            </label>
            <div className="form-submit-row">
              <p className="muted-caption">创建后规则将立即参与后续审查任务。</p>
              <button className="primary-button" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "创建中..." : "创建规则"}
              </button>
            </div>
          </form>
        </section>
      ) : null}
    </div>
  );
}
