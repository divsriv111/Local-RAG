export interface ChatHistory {
  id: string;
  workspaceId: string;
  name: string;
  firstQuery: string;
  createdAt: Date;
  isArchived: boolean;
  messageCount?: number;
  updatedAt?: Date;
}

export interface CreateChatHistoryRequest {
  workspaceId: string;
}

export interface ChatHistoryResponse {
  id: string;
  workspaceId: string;
  name: string;
  firstQuery: string;
  createdAt: string;
  isArchived: boolean;
  messageCount?: number;
  updatedAt?: string;
}
