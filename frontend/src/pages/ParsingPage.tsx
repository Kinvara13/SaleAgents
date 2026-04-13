import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { Select } from "../components/Select";
import {
  getProjectParsingContext,
  rerunProjectParsing,
  updateProjectParsingField,
  uploadProjectTenderDocument,
} from "../services/workspace";
import type { ExtractedField, ParseSection, ProjectParsingContext, WorkspaceData } from "../types";

type ParsingPageProps = {
  data: WorkspaceData;
};

export function ParsingPage({ data }: ParsingPageProps) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const projectId = searchParams.get("projectId");

  const [selectedProjectId, setSelectedProjectId] = useState<string | undefined>(
    projectId || (data.projectRows.length > 0 ? data.projectRows[0].id : undefined)
  );

  useEffect(() => {
    if (selectedProjectId) {
      setSearchParams({ projectId: selectedProjectId });
    }
  }, [selectedProjectId, setSearchParams]);

  const [context, setContext] = useState<ProjectParsingContext | null>(null);
  const [selectedSectionTitle, setSelectedSectionTitle] = useState("");
  const [activeFileName, setActiveFileName] = useState<string | null>(null);
  const [sectionSourceText, setSectionSourceText] = useState("");
  const [editingFieldLabel, setEditingFieldLabel] = useState("");
  const [editingFieldValue, setEditingFieldValue] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [isSavingField, setIsSavingField] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const getFileIcon = (fileType: string) => {
    const icons: Record<string, string> = {
      pdf: '📄',
      docx: '📝',
      doc: '📝',
      xlsx: '📊',
      xls: '📊',
      txt: '📃',
      zip: '📦',
    };
    return icons[fileType.toLowerCase()] || '📄';
  };

  const handleFileSelect = (fileName: string) => {
    setActiveFileName(fileName === activeFileName ? null : fileName);
    const fileSections = context?.parse_sections?.filter(s => s.source_file === fileName);
    if (fileSections && fileSections.length > 0) {
      setSelectedSectionTitle(fileSections[0].title);
    }
  };

  useEffect(() => {
    if (!selectedProjectId) {
      setContext(null);
      return;
    }
    void loadProjectContext(selectedProjectId);
  }, [selectedProjectId]);

  const parseSections: ParseSection[] = selectedProjectId ? (context?.parse_sections || []) : data.parseSections;
  const extractedFields: ExtractedField[] = selectedProjectId ? (context?.extracted_fields || []) : data.extractedFields;

  useEffect(() => {
    if (!parseSections.some((item) => item.title === selectedSectionTitle)) {
      setSelectedSectionTitle(parseSections[0]?.title ?? "");
    }
  }, [parseSections, selectedSectionTitle]);

  const activeSection = useMemo(
    () => parseSections.find((item) => item.title === selectedSectionTitle && (item.source_file === activeFileName || !activeFileName || !item.source_file)) ?? parseSections[0] ?? null,
    [parseSections, selectedSectionTitle, activeFileName],
  );

  const groupedSections = useMemo(() => {
    const groups: Record<string, ParseSection[]> = {};
    parseSections.forEach(sec => {
      const file = sec.source_file || context?.documents?.[0]?.file_name || "主文件/未分组";
      if (!groups[file]) groups[file] = [];
      groups[file].push(sec);
    });
    return groups;
  }, [parseSections, context?.documents]);

  useEffect(() => {
    if (activeSection?.source_text) {
      setSectionSourceText(activeSection.source_text);
    } else if (activeFileName) {
      const fileSections = context?.parse_sections?.filter(s => s.source_file === activeFileName);
      if (fileSections && fileSections.length > 0) {
        setSectionSourceText(fileSections.map(s => s.source_text || '').join('\n\n'));
      }
    } else {
      setSectionSourceText(context?.source_excerpt || "");
    }
  }, [activeSection, activeFileName, context?.source_excerpt, context?.parse_sections]);

  async function loadProjectContext(nextProjectId: string) {
    try {
      const nextContext = await getProjectParsingContext(nextProjectId);
      const sections = nextContext.parse_sections;
      const firstSectionWithText = sections.find(s => s.source_text);
      const initialSectionText = firstSectionWithText?.source_text || nextContext.source_excerpt || "";
      setContext(nextContext);
      setSectionSourceText(initialSectionText);
      if (firstSectionWithText) {
        setSelectedSectionTitle(firstSectionWithText.title);
        setActiveFileName(firstSectionWithText.source_file || null);
      }
      setStatusMessage(`已加载项目提取上下文：${nextProjectId}`);
      setErrorMessage("");
    } catch {
      setErrorMessage("加载项目解析结果失败。");
    }
  }

  async function handleFileUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !selectedProjectId) {
      return;
    }
    setIsUploading(true);
    setErrorMessage("");
    setStatusMessage("");
    try {
      const nextContext = await uploadProjectTenderDocument({
        projectId: selectedProjectId,
        file,
        documentType: "招标文件",
      });
      const fullContext = await getProjectParsingContext(selectedProjectId);
      const updatedSections = fullContext.parse_sections;
      const firstSectionWithText = updatedSections.find(s => s.source_text);
      const initialSectionText = firstSectionWithText?.source_text || nextContext.source_excerpt || "";
      setContext({
        ...fullContext,
        parse_sections: updatedSections,
        source_excerpt: nextContext.source_excerpt,
      });
      setSectionSourceText(initialSectionText);
      if (firstSectionWithText) {
        setSelectedSectionTitle(firstSectionWithText.title);
      }
      setStatusMessage(`已上传并解析：${file.name}`);
    } catch {
      setErrorMessage("上传或解析招标文件失败。");
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  async function handleRerun() {
    if (!selectedProjectId) {
      return;
    }
    setIsRunning(true);
    setErrorMessage("");
    setStatusMessage("");
    try {
      const nextContext = await rerunProjectParsing(selectedProjectId);
      const sections = nextContext.parse_sections;
      const firstSectionWithText = sections.find(s => s.source_text);
      const initialSectionText = firstSectionWithText?.source_text || nextContext.source_excerpt || "";
      setContext(nextContext);
      setSectionSourceText(initialSectionText);
      if (firstSectionWithText) {
        setSelectedSectionTitle(firstSectionWithText.title);
      }
      setStatusMessage("已重新抽取项目招标要求。");
    } catch {
      setErrorMessage("重新抽取失败。");
    } finally {
      setIsRunning(false);
    }
  }

  function startEditField(field: ExtractedField) {
    setEditingFieldLabel(field.label);
    setEditingFieldValue(field.value);
  }

  async function handleSaveField() {
    if (!selectedProjectId || !editingFieldLabel || !editingFieldValue.trim()) {
      return;
    }
    setIsSavingField(true);
    setErrorMessage("");
    setStatusMessage("");
    try {
      const updated = await updateProjectParsingField(selectedProjectId, editingFieldLabel, editingFieldValue.trim());
      setContext((current) =>
        current
          ? {
              ...current,
              extracted_fields: current.extracted_fields.map((item) =>
                item.label === updated.label ? updated : item,
              ),
            }
          : current,
      );
      setStatusMessage(`已保存字段：${updated.label}`);
      setEditingFieldLabel("");
      setEditingFieldValue("");
    } catch {
      setErrorMessage("保存字段失败。");
    } finally {
      setIsSavingField(false);
    }
  }

  // Helper to render text with highlighting
  const renderHighlightedText = (text: string, highlight?: string) => {
    if (!highlight) return text;
    
    // Simple substring match
    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return (
      <>
        {parts.map((part, i) => 
          part.toLowerCase() === highlight.toLowerCase() ? (
            <mark key={i} id={`highlight-${highlight}`} style={{ backgroundColor: 'rgba(59, 130, 246, 0.4)', color: '#fff', borderRadius: '2px', padding: '0 2px' }}>
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </>
    );
  };

  // Helper to clean garbled file paths from zip extraction
  const cleanSourceText = (text: string) => {
    if (!text) return text;
    // Match lines like === some/path/to/file.ext === or === zip -> file ===
    return text.replace(/^===\s*(.+?)\s*===$/gm, (match, path) => {
      const parts = path.split(' -> ');
      const lastPart = parts[parts.length - 1];
      const fileName = lastPart.split('/').pop()?.split('\\').pop() || lastPart;
      return `=== ${fileName} ===`;
    });
  };

  useEffect(() => {
    if (activeSection?.title) {
      // Find the mark element and scroll it into view
      setTimeout(() => {
        const markEl = document.getElementById(`highlight-${activeSection.title}`);
        if (markEl) {
          markEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
    }
  }, [activeSection]);

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Requirement Extraction"
        title="招标要求提取"
        description="按项目上传招标文件，抽取资格、评分、格式和关键商务要求，再直接流向回标生成。"
        actions={
          <>
            <label className="primary-button" style={{ display: "inline-flex", alignItems: "center", cursor: isUploading ? "wait" : "pointer" }}>
              {isUploading ? (
                <>
                  <svg className="animate-spin" style={{ marginRight: '8px', height: '16px', width: '16px' }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  文件解析中...
                </>
              ) : "上传招标文件"}
              <input
                type="file"
                accept=".txt,.docx,.pdf,.xlsx,.xls,.zip"
                onChange={handleFileUpload}
                hidden
                disabled={!selectedProjectId || isUploading}
              />
            </label>
            <button className="ghost-button" type="button" onClick={handleRerun} disabled={!selectedProjectId || isRunning}>
              {isRunning ? (
                <>
                  <svg className="animate-spin" style={{ marginRight: '8px', height: '16px', width: '16px' }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  大模型解析中...
                </>
              ) : "重新抽取"}
            </button>
            <button
              className="ghost-button"
              type="button"
              onClick={() => selectedProjectId && navigate(`/generation?projectId=${selectedProjectId}`)}
              disabled={!selectedProjectId}
            >
              去生成回标
            </button>
          </>
        }
      />

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: -12 }}>
        <span style={{ fontSize: "13px", color: "rgba(139, 200, 255, 0.72)", letterSpacing: "0.06em" }}>当前项目</span>
        <Select
          className="workspace-select"
          value={selectedProjectId || ""}
          onChange={(val) => setSelectedProjectId(val)}
          options={
            data.projectRows.length === 0
              ? [{ label: "暂无项目", value: "" }]
              : data.projectRows.map((p) => ({ label: p.name, value: p.id || "" }))
          }
        />
      </div>

      {statusMessage ? <p className="form-success">{statusMessage}</p> : null}
      {errorMessage ? <p className="form-error">{errorMessage}</p> : null}

      <section className="parse-layout" style={{ display: "grid", gridTemplateColumns: "22% 1fr 22%", gap: 20 }}>
        <aside className="workspace-card" style={{ padding: "1rem", overflowY: "auto", maxHeight: "calc(100vh - 200px)" }}>
          <div className="section-card-head" style={{ marginBottom: "12px" }}>
            <div>
              <p className="eyebrow">File Tree</p>
              <h3>文件解析清单</h3>
            </div>
            <span className="badge">{Object.keys(groupedSections).length} 个文件</span>
          </div>
          
          {context?.debug_info && (
            <div style={{ fontSize: '11px', color: '#a0aec0', padding: '6px 10px', background: 'rgba(255, 255, 255, 0.05)', marginBottom: '8px', borderRadius: '6px' }}>
              ZIP内共 {context.debug_info.total_files_in_zip} 个文件，成功解析 {context.debug_info.parsed_count} 个
              {context.debug_info.skipped_count > 0 && <span>，跳过 {context.debug_info.skipped_count} 个</span>}
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {Object.keys(groupedSections).length > 0 ? (
              Object.entries(groupedSections).map(([fileName, sections]) => {
                const parsedFileInfo = context?.parsed_files?.find(f => f.file_name === fileName);
                const isSkipped = !!parsedFileInfo?.skip_reason;
                const isUnsupported = parsedFileInfo?.parse_status === '不支持';
                
                return (
                  <div key={fileName} className={`tree-file-group ${activeFileName === fileName ? 'active' : ''}`} style={{ 
                    background: 'rgba(10, 29, 50, 0.4)', 
                    borderRadius: '8px', 
                    overflow: 'hidden', 
                    border: activeFileName === fileName ? '1px solid rgba(59, 130, 246, 0.5)' : '1px solid rgba(119, 180, 255, 0.1)',
                    opacity: (isSkipped || isUnsupported) ? 0.6 : 1
                  }}>
                    <div 
                      className="tree-file-header" 
                      onClick={() => !isSkipped && !isUnsupported && handleFileSelect(fileName)}
                      style={{ 
                        padding: '8px 10px', 
                        fontSize: '12px', 
                        fontWeight: 600, 
                        color: '#dce9ff', 
                        borderBottom: sections.length > 0 && !isSkipped && !isUnsupported ? '1px solid rgba(119, 180, 255, 0.1)' : 'none', 
                        background: activeFileName === fileName ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)', 
                        wordBreak: 'break-all',
                        cursor: (isSkipped || isUnsupported) ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      <span>{getFileIcon(parsedFileInfo?.file_type || fileName.split('.').pop() || '')}</span>
                      <span style={{ flex: 1 }}>{fileName.split('/').pop() || fileName}</span>
                      {isUnsupported && <span style={{ color: '#ef4444', fontSize: '11px', fontWeight: 'normal' }}>不支持</span>}
                      {isSkipped && !isUnsupported && <span style={{ color: '#eab308', fontSize: '11px', fontWeight: 'normal' }}>跳过</span>}
                    </div>
                    
                    {(!isSkipped && !isUnsupported) && (
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        {sections.map(section => (
                          <button
                            key={section.title}
                            type="button"
                            className={`section-item ${activeSection?.title === section.title && activeFileName === fileName ? "section-item-active" : ""}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedSectionTitle(section.title);
                              setActiveFileName(fileName);
                            }}
                            style={{ 
                              border: 'none', 
                              borderBottom: '1px solid rgba(119, 180, 255, 0.05)', 
                              borderRadius: 0, 
                              margin: 0,
                              padding: '6px 10px 6px 20px',
                              background: activeSection?.title === section.title && activeFileName === fileName ? 'rgba(59, 130, 246, 0.15)' : 'transparent'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                              <strong style={{ fontSize: '12px' }}>{section.title}</strong>
                              <em style={{ fontSize: '10px', color: section.state === '待确认' ? '#f59e0b' : '#10b981' }}>
                                {section.state}
                              </em>
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <p className="muted-caption" style={{ padding: '12px', fontSize: '13px' }}>暂无解析结果，请上传招标文件。</p>
            )}
          </div>
        </aside>

        <main style={{ minWidth: 0 }}>
          <article className="workspace-card" style={{ padding: "1rem", minHeight: "calc(100vh - 200px)" }}>
            <div className="section-card-head" style={{ flexWrap: 'nowrap', marginBottom: '12px' }}>
              <div>
                <p className="eyebrow">Document Preview</p>
                <h3 style={{ margin: 0 }}>招标原文预览</h3>
              </div>
              <span className="muted-caption" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', textAlign: 'right' }}>
                {activeSection ? `${activeSection.title} ${activeSection.page ? `/ ${activeSection.page}` : ''}` : "暂无章节"}
              </span>
            </div>
            <div style={{ 
              padding: '16px', 
              borderRadius: '14px', 
              background: 'rgba(6, 20, 35, 0.74)', 
              border: '1px solid rgba(120, 184, 255, 0.08)',
              overflowY: 'auto',
              overflowX: 'auto',
              maxHeight: 'calc(100vh - 320px)'
            }}>
              <div style={{ 
                padding: '12px 14px', 
                borderRadius: '12px', 
                background: 'rgba(17, 54, 92, 0.54)', 
                border: '1px solid rgba(124, 189, 255, 0.14)',
                marginBottom: '14px'
              }}>
                <strong style={{ fontSize: '12px', color: '#83c7ff', letterSpacing: '0.12em', textTransform: 'uppercase' }}>解析状态</strong>
                <p style={{ margin: '8px 0 0', color: 'rgba(217, 232, 255, 0.76)', lineHeight: '1.6', fontSize: '13px' }}>
                  {context?.parsed_files && context.parsed_files.length > 0
                    ? `共 ${context.parsed_files.length} 个文件，已解析 ${context.parsed_files.filter(f => f.parse_status === '已解析').length} 个`
                    : context?.documents && context.documents.length > 0
                      ? `${context.documents[0].file_name} · ${context.documents[0].parse_status}`
                      : "当前项目还没有上传招标文件，先从台账页进入项目，再上传文件。"}
                </p>
              </div>
              
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '14px', lineHeight: '1.8', color: 'rgba(216, 231, 255, 0.85)' }}>
                <strong style={{ display: 'block', fontSize: '12px', color: '#83c7ff', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '8px' }}>
                  {activeSection ? `${activeSection.title} 原文` : '关键段落'}
                </strong>
                <p style={{ margin: 0 }}>
                  {sectionSourceText 
                    ? cleanSourceText(sectionSourceText)
                    : context?.source_excerpt 
                      ? renderHighlightedText(cleanSourceText(context.source_excerpt), activeSection?.title) 
                      : "选择左侧章节查看对应原文，或上传招标文件开始解析。"}
                </p>
              </div>
            </div>
          </article>
        </main>

        <aside className="workspace-card" style={{ padding: "1rem", overflowY: "auto", maxHeight: "calc(100vh - 200px)" }}>
          <div className="section-card-head" style={{ flexWrap: 'nowrap', marginBottom: '12px' }}>
            <div>
              <p className="eyebrow">Extracted Fields</p>
              <h3 style={{ margin: 0 }}>结构化要求</h3>
            </div>
          </div>
          <p className="muted-caption" style={{ fontSize: '12px', marginBottom: '12px' }}>
            项目级字段可直接校正，随后流向回标生成
          </p>
          <div className="field-list">
            {extractedFields.map((field) => {
              const isEditing = editingFieldLabel === field.label;
              return (
                <div key={field.label} className="field-item">
                  <div className="field-head">
                    <span>{field.label}</span>
                    <span
                      className={`confidence-badge ${
                        field.confidence.includes("人工") || Number.parseInt(field.confidence, 10) < 85
                          ? "confidence-low"
                          : ""
                      }`}
                    >
                      {field.confidence}
                    </span>
                  </div>
                  {isEditing ? (
                    <>
                      <textarea
                        value={editingFieldValue}
                        onChange={(event) => setEditingFieldValue(event.target.value)}
                        rows={3}
                      />
                      <div className="review-action-row" style={{ display: "flex", gap: 8 }}>
                        <button className="primary-button" type="button" onClick={handleSaveField} disabled={isSavingField} style={{ padding: '8px 12px', fontSize: '13px' }}>
                          {isSavingField ? "保存中..." : "保存"}
                        </button>
                        <button className="ghost-button" type="button" onClick={() => setEditingFieldLabel("")} style={{ padding: '8px 12px', fontSize: '13px' }}>
                          取消
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <strong>{field.value}</strong>
                      <button className="link-button" type="button" onClick={() => startEditField(field)} style={{ fontSize: '12px' }}>
                        校正字段
                      </button>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </aside>
      </section>
    </div>
  );
}
