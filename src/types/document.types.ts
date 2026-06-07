export interface DocumentCreateInput {
  title: string;
  content: string;
  createdAt?: Date;
}

export type DocumentUpdateInput = Partial<DocumentCreateInput>;
