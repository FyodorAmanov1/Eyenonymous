/**
 * Simple in-memory rate limiter for API endpoints
 * For production, consider using Redis or a dedicated rate limiting service
 */

type RateLimitEntry = {
  count: number;
  resetAt: number;
};

const rateLimitStore = new Map<string, RateLimitEntry>();

const DEFAULT_RATE_LIMIT_WINDOW_MS = 60 * 1000; // 1 minute
const DEFAULT_RATE_LIMIT_MAX_REQUESTS = 60; // 60 requests per minute

/**
 * Get rate limit configuration from environment variables
 */
export function getRateLimitConfig() {
  const windowMs = Number(process.env.RATE_LIMIT_WINDOW_MS) || DEFAULT_RATE_LIMIT_WINDOW_MS;
  const maxRequests = Number(process.env.RATE_LIMIT_MAX_REQUESTS) || DEFAULT_RATE_LIMIT_MAX_REQUESTS;
  return { windowMs, maxRequests };
}

export function checkRateLimit(identifier: string): {
  allowed: boolean;
  remaining: number;
  resetAt: number;
} {
  const { windowMs, maxRequests } = getRateLimitConfig();
  const now = Date.now();
  const entry = rateLimitStore.get(identifier);

  // Clean up expired entries periodically (simple cleanup)
  if (rateLimitStore.size > 1000) {
    for (const [key, value] of rateLimitStore.entries()) {
      if (value.resetAt < now) {
        rateLimitStore.delete(key);
      }
    }
  }

  if (!entry || entry.resetAt < now) {
    // New or expired entry
    const resetAt = now + windowMs;
    rateLimitStore.set(identifier, { count: 1, resetAt });
    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetAt,
    };
  }

  // Existing entry within window
  if (entry.count >= maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: entry.resetAt,
    };
  }

  entry.count += 1;
  return {
    allowed: true,
    remaining: maxRequests - entry.count,
    resetAt: entry.resetAt,
  };
}

