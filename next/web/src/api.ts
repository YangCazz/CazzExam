export interface ConceptSummary { id: string; slug: string; title: string; summary: string; aliases: string[]; match_reason?: string | null }
export interface Concept extends ConceptSummary { content_version: string; source_label: string; sections: { heading: string; body: string }[]; relations: { slug: string; title: string; kind: string; reason: string }[]; mappings: { qualification: string; label: string; evidence_status: string; source_url: string | null }[] }
export interface Qualification { id: string; name: string; has_content: boolean }
export interface Collection<T> { items: T[]; content_version: string }
export class ApiError extends Error { constructor(public status: number) { super(status === 404 ? '这个概念暂未收录。' : status === 422 ? '搜索条件无效，请重新选择。' : '知识库暂时无法读取，请稍后重试。') } }
export async function get<T>(path: string, signal?: AbortSignal): Promise<T> { const response = await fetch('/api/v1/' + path, {signal}); if (!response.ok) throw new ApiError(response.status); const result = await response.json(); signal?.throwIfAborted(); return result }
