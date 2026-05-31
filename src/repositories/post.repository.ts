import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { PostCreateInput, PostUpdateInput } from '../types/post.types.js';


export class PostRepository {
  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['title'] !== undefined) {
      where['title'] = params.filters['title'];
    }
    if (params.filters['content'] !== undefined) {
      where['content'] = params.filters['content'];
    }
    if (params.filters['published'] !== undefined) {
      where['published'] = params.filters['published'] === 'true';
    }
    if (params.filters['authorId'] !== undefined) {
      const _v4 = Number(params.filters['authorId']);
      if (!isNaN(_v4)) where['authorId'] = _v4;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.post.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.post.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.post.findUnique({
      where: { id: id },
    });
  }

  async create(data: PostCreateInput): Promise<any> {
    return prisma.post.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: data as any,
    });
  }

  async update(id: number, data: PostUpdateInput): Promise<any | null> {
    try {
      return await prisma.post.update({
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
      // Delete child records first to avoid FK constraint violations, then delete this entity.
      await prisma.$transaction([
        prisma.comment.deleteMany({ where: { postId: id } }),
        prisma.post.delete({ where: { id: id } }),
      ]);
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
  // Find all posts belonging to a parent via authorId
  async findManyByAuthorId(
    parentId: number,
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = { authorId: parentId };
    if (params.filters['title'] !== undefined) {
      where['title'] = params.filters['title'];
    }
    if (params.filters['content'] !== undefined) {
      where['content'] = params.filters['content'];
    }
    if (params.filters['published'] !== undefined) {
      where['published'] = params.filters['published'] === 'true';
    }
    if (params.filters['authorId'] !== undefined) {
      const _v4 = Number(params.filters['authorId']);
      if (!isNaN(_v4)) where['authorId'] = _v4;
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.post.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
      }),
      prisma.post.count({ where }),
    ]);

    return { data, total };
  }
}
