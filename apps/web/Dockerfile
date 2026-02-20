FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json next.config.ts ./
COPY app ./app
COPY globals.css ./globals.css
COPY lib ./lib
COPY stores ./stores
RUN npm install
EXPOSE 3000
CMD ["npm", "run", "dev"]
