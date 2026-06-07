import { prisma } from '../lib/prisma.js';
import { ListQueryParams } from '../lib/pagination.js';
import { UserCreateInput, UserUpdateInput } from '../types/user.types.js';
import { hashValue } from '../lib/crypto.js';


export class UserRepository {
  // Sensitive fields are excluded from all read responses
  private readonly safeSelect = {
    id: true,
    email: true,
    name: true,
    password: false,
    bio: true,
    createdAt: true,
    updatedAt: true,
  } as const;

  async findMany(
    params: ListQueryParams,
  ): Promise<{ data: any[]; total: number }> {
    const where: any = {};
    if (params.filters['email'] !== undefined) {
      where['email'] = params.filters['email'];
    }
    if (params.filters['name'] !== undefined) {
      where['name'] = params.filters['name'];
    }
    if (params.filters['bio'] !== undefined) {
      where['bio'] = params.filters['bio'];
    }
    const orderBy: any = params.sort
      ? { [params.sort.field]: params.sort.order }
      : { id: 'desc' };
    const [data, total] = await prisma.$transaction([
      prisma.user.findMany({
        where,
        skip: params.skip,
        take: params.limit,
        orderBy,
        select: this.safeSelect,
      }),
      prisma.user.count({ where }),
    ]);

    return { data, total };
  }

  async findById(id: number): Promise<any | null> {
    return prisma.user.findUnique({
      where: { id: id },
      select: this.safeSelect,
    });
  }

  async create(data: UserCreateInput): Promise<any> {
    // Hash sensitive fields before persisting to the database
    const securedData: Record<string, any> = { ...data };
    if (securedData.password) {
      securedData.password = await hashValue(String(securedData.password));
    }
    return prisma.user.create({
      // Cast to any: custom type name clashes with Prisma's checked variant; scalar FKs resolve correctly at runtime.
      data: securedData as any,
      select: this.safeSelect,
    });
  }

  async update(id: number, data: UserUpdateInput): Promise<any | null> {
    try {
      // Hash sensitive fields if included in the update payload
      const securedData: Record<string, any> = { ...data };
      if (securedData.password) {
        securedData.password = await hashValue(String(securedData.password));
      }
      return await prisma.user.update({
        where: { id: id },
        // Cast to any: see create() comment above.
        data: securedData as any,
        select: this.safeSelect,
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
        prisma.post.deleteMany({ where: { authorId: id } }),
        prisma.comment.deleteMany({ where: { authorId: id } }),
        prisma.user.delete({ where: { id: id } }),
      ]);
      return true;
    } catch (err: any) {
      if (err.code === 'P2025') return false;
      throw err;
    }
  }
}
