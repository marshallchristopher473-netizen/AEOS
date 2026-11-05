import { NextResponse } from 'next/server';
import { ZodError } from 'zod';

/** An error with an intended HTTP status. Thrown by helpers, caught by `handle`. */
export class ApiError extends Error {
  readonly status: number;
  readonly details?: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

export function badRequest(message: string, details?: unknown): ApiError {
  return new ApiError(400, message, details);
}

export function notFound(message: string): ApiError {
  return new ApiError(404, message);
}

export function conflict(message: string): ApiError {
  return new ApiError(409, message);
}

/**
 * Wrap a route handler so every failure returns a predictable JSON envelope
 * instead of an HTML error page, and so internal messages are not leaked.
 */
export async function handle<T>(fn: () => Promise<T> | T): Promise<NextResponse> {
  try {
    return NextResponse.json(await fn());
  } catch (err) {
    if (err instanceof ApiError) {
      return NextResponse.json(
        { error: err.message, ...(err.details ? { details: err.details } : {}) },
        { status: err.status },
      );
    }
    if (err instanceof ZodError) {
      return NextResponse.json({ error: 'invalid request body', details: err.issues }, { status: 400 });
    }
    // Unexpected: log server-side, return a generic message to the client.
    console.error('[api] unhandled error', err);
    return NextResponse.json({ error: 'internal error' }, { status: 500 });
  }
}

/** Parse a JSON request body, turning malformed JSON into a 400 rather than a 500. */
export async function readJson(req: Request): Promise<unknown> {
  try {
    return await req.json();
  } catch {
    throw badRequest('request body must be valid JSON');
  }
}
