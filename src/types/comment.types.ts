export interface CommentCreateInput {
  body: string;
  authorId: number;
  postId: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export type CommentUpdateInput = Partial<CommentCreateInput>;
