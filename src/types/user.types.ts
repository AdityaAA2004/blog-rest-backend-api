export interface UserCreateInput {
  email: string;
  name: string;
  password: string;
  bio?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export type UserUpdateInput = Partial<UserCreateInput>;
