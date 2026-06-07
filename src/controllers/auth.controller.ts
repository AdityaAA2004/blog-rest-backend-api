import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { prisma } from '../lib/prisma.js';
import { hashValue, compareValue } from '../lib/crypto.js';
import { AppError, ValidationError } from '../lib/errors.js';

const registerSchema = z.object({
  email: z.string().email({ message: 'Please provide a valid email address' }),
  password: z.string().min(8, { message: 'Password must be at least 8 characters' }).max(128),
  name: z.string(),
  bio: z.string().optional(),
  createdAt: z.string().optional(),
  updatedAt: z.string().optional(),
});

const loginSchema = z.object({
  email: z.string().email({ message: 'Please provide a valid email address' }),
  password: z.string().min(1),
});

// Safe select: all non-sensitive fields returned from register / embedded in JWT
const safeSelect = {
  id: true,
  email: true,
  name: true,
  bio: true,
  createdAt: true,
  updatedAt: true,
} as const;

export class AuthController {
  async register(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parsed = registerSchema.safeParse(req.body);
      if (!parsed.success) {
        const message = parsed.error.errors.map((e) => e.message).join(', ');
        throw new ValidationError(message);
      }

      const data = parsed.data;
      const hashedCredential = await hashValue(data.password);

      const user = await prisma.user.create({
        data: {
          ...data,
          password: hashedCredential,
        },
        select: safeSelect,
      });

      // Spread entire safe record into JWT; map PK field to 'id' for a stable AuthUser.id
      const { id: pkValue, ...otherFields } = user;
      const token = jwt.sign(
        { id: pkValue, ...otherFields },
        process.env.JWT_SECRET!,
        { expiresIn: '7d' },
      );

      res.status(201).json({ token, user });
    } catch (err: any) {
      if (err?.code === 'P2002') {
        next(new AppError(409, 'An account with this email already exists'));
      } else {
        next(err);
      }
    }
  }

  async login(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const parsed = loginSchema.safeParse(req.body);
      if (!parsed.success) {
        const message = parsed.error.errors.map((e) => e.message).join(', ');
        throw new ValidationError(message);
      }

      const email = parsed.data.email;
      const password = parsed.data.password;

      // Fetch the record including the sensitive credential field for verification
      const user = await prisma.user.findUnique({
        where: { email },
      });

      if (!user) {
        throw new AppError(401, 'Invalid email or password');
      }

      const credentialValid = await compareValue(password, user.password);
      if (!credentialValid) {
        throw new AppError(401, 'Invalid email or password');
      }

      // Build JWT payload: exclude sensitive fields, map PK to 'id' for a stable AuthUser.id
      const { id: pkValue, password: _sf0, ...otherFields } = user;
      const token = jwt.sign(
        { id: pkValue, ...otherFields },
        process.env.JWT_SECRET!,
        { expiresIn: '7d' },
      );

      // Return token only — never expose the credential field in a response
      res.json({ token });
    } catch (err) {
      next(err);
    }
  }
}
