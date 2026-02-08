# Multi-stage build for Next.js frontend
FROM node:20-alpine AS deps

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Builder stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY . .

# Set build-time environment variables
ENV NEXT_PUBLIC_API_URL=http://localhost:8001
ENV NEXT_PUBLIC_ENVIRONMENT=development

# Build Next.js application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set correct permissions
RUN chown -R nextjs:nodejs /app

USER nextjs

# Expose port
EXPOSE 3001

# Set port environment variable
ENV PORT=3001
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3001/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run the application
CMD ["node", "server.js"]
