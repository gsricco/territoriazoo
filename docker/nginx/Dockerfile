FROM node:16-alpine as builder
WORKDIR /react
COPY ../../itec_project/package.json ./
RUN yarn install
COPY . .
RUN yarn build

FROM nginx:1.23-alpine
COPY nginx-setup.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /react/build .