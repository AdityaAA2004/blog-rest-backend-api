export interface PostCreateInput {
  title: string;
  content: string;
  published?: boolean;
  authorId: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export type PostUpdateInput = Partial<PostCreateInput>;
