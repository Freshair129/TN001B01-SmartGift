FROM node:22-alpine
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY server ./server
COPY .env.example ./.env.example

ENV NODE_ENV=production
ENV API_PORT=3850
EXPOSE 3850

CMD ["node", "server/index.mjs"]
