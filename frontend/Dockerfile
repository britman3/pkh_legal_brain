
FROM node:20-alpine as build
WORKDIR /app
COPY package.json package-lock.json* yarn.lock* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

FROM caddy:2-alpine
COPY --from=build /app/dist /usr/share/caddy
