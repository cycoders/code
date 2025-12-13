FROM node:18-alpine

# Install deps
RUN npm install -g pnpm
RUN pnpm install

# Build
RUN pnpm build

# Copy source
COPY . /app

EXPOSE 3000
CMD ["pnpm", "start"]
