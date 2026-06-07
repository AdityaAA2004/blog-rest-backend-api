import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { CommentCreateInput, CommentUpdateInput } from '../types/comment.types.js';


export class CommentRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['body'] !== undefined) {
      where['body'] = params.filters['body'];
    }
    if (params.filters['authorId'] !== undefined) {
      const _v2 = Number(params.filters['authorId']);
      if (!isNaN(_v2)) where['authorId'] = _v2;
    }
    if (params.filters['postId'] !== undefined) {
      const _v3 = Number(params.filters['postId']);
      if (!isNaN(_v3)) where['postId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.comment.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.comment.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.comment.findUnique({
      where: { id: id },
    });
  }

  async create(data: CommentCreateInput): Promise<any> {
    return prisma.comment.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: CommentUpdateInput): Promise<any | null> {
    try {
      return await prisma.comment.update({
        where: { id: id },
        // Cast to any: see create() comment above.
        data: data as any,
      });
    } catch (err: any) {
      if (err.code === 'P2025') return null;
      throw err;
    }
  }

  async delete(id: number): Promise<boolean> {
    try {
      await prisma.comment.delete({
        where: { id: id },
      });
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
  // Find all comments belonging to a parent via authorId
  async findManyByAuthorId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { authorId: parentId };
    if (params.filters['body'] !== undefined) {
      where['body'] = params.filters['body'];
    }
    if (params.filters['authorId'] !== undefined) {
      const _v2 = Number(params.filters['authorId']);
      if (!isNaN(_v2)) where['authorId'] = _v2;
    }
    if (params.filters['postId'] !== undefined) {
      const _v3 = Number(params.filters['postId']);
      if (!isNaN(_v3)) where['postId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.comment.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.comment.count({ where }),
    ]);

    return { data, total };
  }
  // Find all comments belonging to a parent via postId
  async findManyByPostId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { postId: parentId };
    if (params.filters['body'] !== undefined) {
      where['body'] = params.filters['body'];
    }
    if (params.filters['authorId'] !== undefined) {
      const _v2 = Number(params.filters['authorId']);
      if (!isNaN(_v2)) where['authorId'] = _v2;
    }
    if (params.filters['postId'] !== undefined) {
      const _v3 = Number(params.filters['postId']);
      if (!isNaN(_v3)) where['postId'] = _v3;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.comment.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.comment.count({ where }),
    ]);

    return { data, total };
  }
}
