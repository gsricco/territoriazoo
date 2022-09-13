FROM node:16-alpine
WORKDIR /react
COPY package.json .
RUN yarn install
COPY . .
RUN yarn build

#FROM nginx:1.23-alpine
#WORKDIR /usr/share/nginx/html
#RUN rm -rf ./*
#COPY --from=builder /react/build .
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]