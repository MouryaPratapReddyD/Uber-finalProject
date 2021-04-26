# BUILDER 
FROM node:15.2.0-alpine as builder
WORKDIR /usr/src/app
ENV PATH /usr/src/app/node_modules/.bin:$PATH
COPY package.json .
COPY package-lock.json .
RUN npm ci
ARG NODE_ENV
ENV NODE_ENV $NODE_ENV
COPY . .
RUN npm run build

# FINAL 
FROM nginx
COPY --from=builder /usr/src/app/build /usr/share/nginx/html
EXPOSE 80
