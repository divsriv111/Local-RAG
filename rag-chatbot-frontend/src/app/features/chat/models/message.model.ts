export interface MessageReference {
  pdf: string;
  page: number;
  pdfId?: string;
}

export interface Message {
  id: string;
  chatHistoryId: string;
  content: string;
  isUserMessage: boolean;
  timestamp: Date;
  references?: MessageReference[];
  isStreaming?: boolean;
}

export interface StreamingChunk {
  type: 'token' | 'source' | 'done' | 'error';
  content?: string;
  pdf?: string;
  page?: number;
  pdfId?: string;
  answer?: string;
  references?: MessageReference[];
  message?: string;
}

export interface StreamingResponse {
  chunks: StreamingChunk[];
  complete: boolean;
}

export interface SendMessageRequest {
  query: string;
  selectedPdfIds: string[];
  workspaceId: string;
  chatHistoryId: string;
  llmModel: string;
  chatHistory?: { role: string; content: string }[];
}

export interface LlmModel {
  label: string;
  value: string;
  description?: string;
}

export const LLM_MODELS: LlmModel[] = [
  {
    label: 'GPT-4 Turbo',
    value: 'gpt-4-turbo',
    description: 'Most capable model, best for complex queries',
  },
  {
    label: 'GPT-4.1 Mini',
    value: 'gpt-4o-mini',
    description: 'Fast and efficient for most queries',
  },
  {
    label: 'Local LLaMA-3',
    value: 'local-llama-3',
    description: 'Privacy-focused local model',
  },
];
