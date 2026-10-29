export type CaseStatus = 'queued' | 'running' | 'cancelling' | 'complete' | 'failed' | 'cancelled';
export type Mode = 'diagnostic' | 'chat';
export type Options = Record<'A' | 'B' | 'C' | 'D', string>;
export type RecordValue = Record<string, unknown>;
export interface CaseInput {
  kind: Mode;
  case_text?: string;
  text?: string;
  question?: string;
  options?: Options;
  title?: string;
  parent_id?: string;
  source_id?: string;
}
export interface EvidenceSpan { id: string; text: string; start?: number; end?: number }
export interface Omission extends RecordValue { span_id: string; label?: string; changed?: boolean; valid?: boolean }
export interface Analysis extends RecordValue {
  evidence: RecordValue & {
    decision?: { label?: string; name?: string };
    spans?: EvidenceSpan[];
    omissions?: Omission[];
    selected?: unknown;
    recheck?: unknown;
    target?: unknown;
  };
  views?: { novice?: Record<string, string>; expert?: Record<string, string> };
  release_status?: string;
  automated_release_passed?: boolean;
  checker?: RecordValue;
  time?: RecordValue;
}
export interface Source extends RecordValue { id?: string; title: string; url?: string; content?: string; category?: string; content_type?: string; citation_number?: number; verification?: unknown }
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  kind: 'case' | 'analysis' | 'answer' | string;
  payload: CaseInput & { text?: string; citations?: Source[]; grounding_status?: string };
  created_at: string;
}
export interface CaseSummary { id: string; title: string; status: CaseStatus; created_at: string; updated_at: string }
export interface ClinicalCase extends CaseSummary {
  input: CaseInput;
  progress?: { stage?: string; detail?: string; percent?: number };
  result?: Analysis | null;
  messages: Message[];
  error?: string | { message?: string; [key: string]: unknown } | null;
}
export interface Runtime extends RecordValue {
  ready: boolean;
  phase?: string;
  device?: string;
  target?: RecordValue;
  communicator?: RecordValue;
  assets?: unknown;
}
export interface Example extends CaseInput { id: string; title: string; synthetic: boolean }
