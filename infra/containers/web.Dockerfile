FROM node:24.21.0-alpine3.24 AS builder
WORKDIR /app
ENV COREPACK_HOME=/opt/corepack COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN npm install --global corepack@0.34.0 && corepack prepare pnpm@10.30.2 --activate
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY packages packages
COPY apps/web apps/web
RUN corepack pnpm install --frozen-lockfile
ENV NEXT_TELEMETRY_DISABLED=1 TURBO_TELEMETRY_DISABLED=1
RUN corepack pnpm --filter @kasoma/web build
FROM node:24.21.0-alpine3.24 AS runtime
WORKDIR /app
# Build-only package managers are unnecessary at runtime and carry unrelated CVEs.
RUN rm -rf /usr/local/lib/node_modules /usr/local/bin/npm /usr/local/bin/npx /opt/yarn*
ENV NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
COPY --from=builder --chown=node:node /app/apps/web/.next/standalone ./
COPY --from=builder --chown=node:node /app/apps/web/.next/static ./apps/web/.next/static
USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
