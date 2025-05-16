FROM node:20

WORKDIR /app

# 先に依存関係ファイルだけコピーしてキャッシュを効かせる
COPY package*.json ./
#COPY vite.config.js ./

RUN npm install 

# 残りのファイルをコピー
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
