# pricing--2-router Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm ci
COPY handler.ts .
RUN npx tsc handler.ts

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/*.js .
EXPOSE 8080
CMD ["node", "handler.js"]
