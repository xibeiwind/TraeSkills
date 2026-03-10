# NestJS 部署指南

## 目录
1. [构建配置](#构建配置)
2. [环境变量管理](#环境变量管理)
3. [Docker 化部署](#docker-化部署)
4. [云平台部署](#云平台部署)
5. [监控与日志](#监控与日志)
6. [最佳实践](#最佳实践)

---

## 构建配置

### 1. 基础构建配置

#### package.json 脚本

```json
{
  "scripts": {
    "build": "nest build",
    "build:prod": "nest build --webpack",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:debug": "nest start --debug --watch",
    "start:prod": "node dist/main",
    "prebuild": "rimraf dist",
    "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:cov": "jest --coverage",
    "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
    "test:e2e": "jest --config ./test/jest-e2e.json"
  }
}
```

### 2. TypeScript 配置

#### tsconfig.json

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "skipLibCheck": true,
    "strictNullChecks": false,
    "noImplicitAny": false,
    "strictBindCallApply": false,
    "forceConsistentCasingInFileNames": false,
    "noFallthroughCasesInSwitch": false,
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

#### tsconfig.build.json

```json
{
  "extends": "./tsconfig.json",
  "exclude": ["node_modules", "test", "dist", "**/*spec.ts"]
}
```

### 3. Nest CLI 配置

#### nest-cli.json

```json
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true,
    "webpack": true,
    "webpackConfigPath": "webpack-hmr.config.js"
  }
}
```

### 4. Webpack 配置（生产环境）

#### webpack.config.js

```javascript
const path = require('path');

module.exports = (options, webpack) => {
  const lazyImports = [
    '@nestjs/microservices',
    '@nestjs/microservices/microservices-module',
    '@nestjs/websockets/socket-module',
    'cache-manager',
    'class-validator',
    'class-transformer',
  ];

  return {
    ...options,
    entry: './src/main.ts',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'main.js',
      clean: true,
    },
    externals: [
      ({ request }, callback) => {
        if (!lazyImports.includes(request)) {
          return callback();
        }
        try {
          webpack.nodeModulePath(request);
          return callback(null, `commonjs ${request}`);
        } catch (error) {
          return callback();
        }
      },
    ],
    optimization: {
      minimize: true,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: true,
              drop_debugger: true,
            },
          },
        }),
      ],
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      },
    },
    plugins: [
      new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production'),
      }),
    ],
  };
};
```

### 5. 环境特定配置

#### src/config/configuration.ts

```typescript
import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  apiUrl: process.env.API_URL || 'http://localhost:3000',
  cors: {
    origin: process.env.CORS_ORIGIN?.split(',') || '*',
    credentials: true,
  },
}));
```

#### src/config/database.config.ts

```typescript
import { registerAs } from '@nestjs/config';

export default registerAs('database', () => ({
  type: (process.env.DATABASE_TYPE as any) || 'postgres',
  host: process.env.DATABASE_HOST || 'localhost',
  port: parseInt(process.env.DATABASE_PORT, 10) || 5432,
  username: process.env.DATABASE_USERNAME || 'postgres',
  password: process.env.DATABASE_PASSWORD || 'postgres',
  database: process.env.DATABASE_NAME || 'nestjs',
  synchronize: process.env.NODE_ENV === 'development',
  logging: process.env.NODE_ENV === 'development',
  ssl: process.env.DATABASE_SSL === 'true',
}));
```

#### src/config/jwt.config.ts

```typescript
import { registerAs } from '@nestjs/config';

export default registerAs('jwt', () => ({
  secret: process.env.JWT_SECRET || 'your-secret-key',
  expiresIn: process.env.JWT_EXPIRES_IN || '1d',
  refreshSecret: process.env.JWT_REFRESH_SECRET || 'your-refresh-secret',
  refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d',
}));
```

### 6. 构建脚本

#### scripts/build.sh

```bash
#!/bin/bash

set -e

echo "🚀 Starting build process..."

# 清理旧的构建
echo "🧹 Cleaning previous build..."
npm run prebuild

# 运行测试
echo "🧪 Running tests..."
npm run test:cov

# 运行代码检查
echo "🔍 Running linter..."
npm run lint

# 构建项目
echo "📦 Building project..."
npm run build

echo "✅ Build completed successfully!"

# 显示构建信息
echo "📊 Build information:"
ls -lh dist/
```

#### scripts/build-prod.sh

```bash
#!/bin/bash

set -e

echo "🚀 Starting production build..."

# 设置生产环境
export NODE_ENV=production

# 清理旧的构建
echo "🧹 Cleaning previous build..."
rm -rf dist

# 构建生产版本
echo "📦 Building production version..."
npm run build:prod

# 压缩构建产物
echo "🗜️ Compressing build artifacts..."
tar -czf dist.tar.gz dist/

echo "✅ Production build completed!"
echo "📦 Build artifact: dist.tar.gz"
```

---

## 环境变量管理

### 1. 环境变量文件

#### .env.example

```env
# 应用配置
NODE_ENV=development
PORT=3000
API_URL=http://localhost:3000

# 数据库配置
DATABASE_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=nestjs
DATABASE_SSL=false

# JWT 配置
JWT_SECRET=your-secret-key-change-this-in-production
JWT_EXPIRES_IN=1d
JWT_REFRESH_SECRET=your-refresh-secret-change-this-in-production
JWT_REFRESH_EXPIRES_IN=7d

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 外部服务配置
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_KEY=your-api-key

# 日志配置
LOG_LEVEL=debug
LOG_FORMAT=json

# CORS 配置
CORS_ORIGIN=http://localhost:3000,http://localhost:4200

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM=noreply@example.com
```

#### .env.development

```env
NODE_ENV=development
PORT=3000
DATABASE_HOST=localhost
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=nestjs_dev
LOG_LEVEL=debug
LOG_FORMAT=pretty
```

#### .env.production

```env
NODE_ENV=production
PORT=3000
DATABASE_HOST=your-production-db-host
DATABASE_USERNAME=prod_user
DATABASE_PASSWORD=your-secure-password
DATABASE_NAME=nestjs_prod
LOG_LEVEL=info
LOG_FORMAT=json
```

#### .env.test

```env
NODE_ENV=test
PORT=3001
DATABASE_TYPE=sqlite
DATABASE_PATH=./test.db
LOG_LEVEL=error
```

### 2. 环境变量验证

#### src/config/env.validation.ts

```typescript
import * as Joi from 'joi';

export const envValidationSchema = Joi.object({
  NODE_ENV: Joi.string()
    .valid('development', 'production', 'test')
    .default('development'),
  PORT: Joi.number().default(3000),
  API_URL: Joi.string().uri().required(),

  // 数据库配置
  DATABASE_TYPE: Joi.string()
    .valid('postgres', 'mysql', 'sqlite', 'mongodb')
    .default('postgres'),
  DATABASE_HOST: Joi.string().when('DATABASE_TYPE', {
    is: 'sqlite',
    then: Joi.optional(),
    otherwise: Joi.required(),
  }),
  DATABASE_PORT: Joi.number().default(5432),
  DATABASE_USERNAME: Joi.string().required(),
  DATABASE_PASSWORD: Joi.string().required(),
  DATABASE_NAME: Joi.string().required(),
  DATABASE_SSL: Joi.boolean().default(false),

  // JWT 配置
  JWT_SECRET: Joi.string().min(32).required(),
  JWT_EXPIRES_IN: Joi.string().default('1d'),
  JWT_REFRESH_SECRET: Joi.string().min(32).required(),
  JWT_REFRESH_EXPIRES_IN: Joi.string().default('7d'),

  // Redis 配置
  REDIS_HOST: Joi.string().required(),
  REDIS_PORT: Joi.number().default(6379),
  REDIS_PASSWORD: Joi.string().allow('').default(''),
  REDIS_DB: Joi.number().default(0),

  // 外部服务配置
  EXTERNAL_API_URL: Joi.string().uri().required(),
  EXTERNAL_API_KEY: Joi.string().required(),

  // 日志配置
  LOG_LEVEL: Joi.string()
    .valid('error', 'warn', 'info', 'debug', 'verbose')
    .default('info'),
  LOG_FORMAT: Joi.string().valid('json', 'pretty').default('json'),

  // CORS 配置
  CORS_ORIGIN: Joi.string().default('*'),

  // 文件上传配置
  UPLOAD_DIR: Joi.string().default('./uploads'),
  MAX_FILE_SIZE: Joi.number().default(10485760),

  // 邮件配置
  SMTP_HOST: Joi.string().required(),
  SMTP_PORT: Joi.number().default(587),
  SMTP_USER: Joi.string().required(),
  SMTP_PASSWORD: Joi.string().required(),
  SMTP_FROM: Joi.string().email().required(),
});
```

### 3. 配置模块设置

#### src/config/config.module.ts

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { envValidationSchema } from './env.validation';
import appConfig from './configuration';
import databaseConfig from './database.config';
import jwtConfig from './jwt.config';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: [
        `.env.${process.env.NODE_ENV}`,
        '.env',
      ],
      validationSchema: envValidationSchema,
      validationOptions: {
        allowUnknown: true,
        abortEarly: true,
      },
      load: [appConfig, databaseConfig, jwtConfig],
    }),
  ],
})
export class AppConfigModule {}
```

### 4. 环境变量管理最佳实践

#### scripts/generate-env.sh

```bash
#!/bin/bash

# 生成随机密钥
generate_secret() {
  openssl rand -base64 32
}

# 创建 .env 文件
create_env_file() {
  local env_file=$1
  local env_type=$2

  if [ -f "$env_file" ]; then
    echo "⚠️  $env_file already exists. Skipping."
    return
  fi

  echo "📝 Creating $env_file..."

  cat > "$env_file" << EOF
NODE_ENV=$env_type
PORT=3000

# 数据库配置
DATABASE_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=nestjs_$env_type

# JWT 配置
JWT_SECRET=$(generate_secret)
JWT_EXPIRES_IN=1d
JWT_REFRESH_SECRET=$(generate_secret)
JWT_REFRESH_EXPIRES_IN=7d

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 外部服务配置
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_KEY=$(generate_secret)

# 日志配置
LOG_LEVEL=debug
LOG_FORMAT=pretty

# CORS 配置
CORS_ORIGIN=http://localhost:3000

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM=noreply@example.com
EOF

  echo "✅ Created $env_file"
}

# 创建所有环境文件
create_env_file ".env.development" "development"
create_env_file ".env.production" "production"
create_env_file ".env.test" "test"

echo "🎉 Environment files created successfully!"
echo "⚠️  Please update the values in the generated files."
```

---

## Docker 化部署

### 1. 基础 Dockerfile

#### Dockerfile

```dockerfile
# 多阶段构建 - 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM node:18-alpine AS production

# 安装 dumb-init 用于正确的信号处理
RUN apk add --no-cache dumb-init

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nestjs -u 1001

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 只安装生产依赖
RUN npm ci --only=production && \
    npm cache clean --force

# 从构建阶段复制构建产物
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist

# 切换到非 root 用户
USER nestjs

# 暴露端口
EXPOSE 3000

# 使用 dumb-init 启动应用
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/main"]
```

### 2. 优化的 Dockerfile

#### Dockerfile.optimized

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

# 安装构建依赖
RUN apk add --no-cache python3 make g++

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装所有依赖（包括 devDependencies）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build && \
    npm prune --production

# 生产阶段
FROM node:18-alpine AS production

# 安装运行时依赖
RUN apk add --no-cache dumb-init curl

# 创建应用目录和用户
RUN mkdir -p /app && \
    addgroup -g 1001 -S nodejs && \
    adduser -S nestjs -u 1001

# 设置工作目录
WORKDIR /app

# 从构建阶段复制 node_modules 和 dist
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nestjs:nodejs /app/package.json ./package.json

# 创建上传目录
RUN mkdir -p uploads && \
    chown -R nestjs:nodejs uploads

# 切换到非 root 用户
USER nestjs

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# 暴露端口
EXPOSE 3000

# 使用 dumb-init 启动应用
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/main"]
```

### 3. Docker Compose 配置

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # NestJS 应用
  app:
    build:
      context: .
      dockerfile: Dockerfile.optimized
    container_name: nestjs-app
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_USERNAME=postgres
      - DATABASE_PASSWORD=postgres
      - DATABASE_NAME=nestjs
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
    networks:
      - nestjs-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: nestjs-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=nestjs
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - nestjs-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: nestjs-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - nestjs-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: nestjs-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - nestjs-network
    restart: unless-stopped

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local

networks:
  nestjs-network:
    driver: bridge
```

### 4. 开发环境 Docker Compose

#### docker-compose.dev.yml

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder
    container_name: nestjs-app-dev
    ports:
      - "3000:3000"
      - "9229:9229"  # 调试端口
    environment:
      - NODE_ENV=development
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_USERNAME=postgres
      - DATABASE_PASSWORD=postgres
      - DATABASE_NAME=nestjs_dev
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - .:/app
      - /app/node_modules
      - ./uploads:/app/uploads
    command: npm run start:debug
    depends_on:
      - postgres
      - redis
    networks:
      - nestjs-network

  postgres:
    image: postgres:15-alpine
    container_name: nestjs-postgres-dev
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=nestjs_dev
    volumes:
      - postgres-dev-data:/var/lib/postgresql/data
    networks:
      - nestjs-network

  redis:
    image: redis:7-alpine
    container_name: nestjs-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis-dev-data:/data
    networks:
      - nestjs-network

  # pgAdmin 数据库管理工具
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: nestjs-pgadmin
    ports:
      - "5050:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    depends_on:
      - postgres
    networks:
      - nestjs-network

volumes:
  postgres-dev-data:
  redis-dev-data:

networks:
  nestjs-network:
```

### 5. Nginx 配置

#### nginx/nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream nestjs_app {
        server app:3000;
    }

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    server {
        listen 80;
        server_name localhost;

        # 客户端最大上传大小
        client_max_body_size 10M;

        # 静态文件缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            proxy_pass http://nestjs_app;
        }

        # API 路由
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://nestjs_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # WebSocket 支持
        location /socket.io/ {
            proxy_pass http://nestjs_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 健康检查端点
        location /health {
            proxy_pass http://nestjs_app;
            access_log off;
        }

        # 默认路由
        location / {
            proxy_pass http://nestjs_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }

    # HTTPS 配置（可选）
    server {
        listen 443 ssl http2;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 其他配置与 HTTP 相同
        # ...
    }
}
```

### 6. Docker 部署脚本

#### scripts/deploy.sh

```bash
#!/bin/bash

set -e

# 配置变量
IMAGE_NAME="nestjs-app"
CONTAINER_NAME="nestjs-app"
REGISTRY="your-registry.com"
VERSION=${1:-latest}

echo "🚀 Starting deployment..."

# 构建镜像
echo "📦 Building Docker image..."
docker build -f Dockerfile.optimized -t ${IMAGE_NAME}:${VERSION} .

# 标记镜像
echo "🏷️  Tagging image..."
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}

# 推送镜像（如果配置了 registry）
if [ -n "$REGISTRY" ]; then
    echo "📤 Pushing image to registry..."
    docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
fi

# 停止旧容器
echo "🛑 Stopping old container..."
if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
fi

# 启动新容器
echo "🚀 Starting new container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --restart unless-stopped \
    -p 3000:3000 \
    --env-file .env.production \
    ${IMAGE_NAME}:${VERSION}

# 等待应用启动
echo "⏳ Waiting for application to start..."
sleep 10

# 健康检查
echo "🏥 Performing health check..."
if curl -f http://localhost:3000/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    exit 1
fi
```

#### scripts/docker-compose-deploy.sh

```bash
#!/bin/bash

set -e

# 配置变量
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.production"

echo "🚀 Starting Docker Compose deployment..."

# 检查环境文件
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file $ENV_FILE not found!"
    exit 1
fi

# 拉取最新镜像
echo "📥 Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

# 构建镜像
echo "📦 Building images..."
docker-compose -f $COMPOSE_FILE build

# 停止旧容器
echo "🛑 Stopping old containers..."
docker-compose -f $COMPOSE_FILE down

# 启动新容器
echo "🚀 Starting new containers..."
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo "⏳ Waiting for services to start..."
sleep 15

# 健康检查
echo "🏥 Performing health checks..."
if curl -f http://localhost:3000/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

# 显示运行状态
echo "📊 Container status:"
docker-compose -f $COMPOSE_FILE ps
```

---

## 云平台部署

### 1. AWS 部署

#### AWS ECS 任务定义

```json
{
  "family": "nestjs-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "nestjs-app",
      "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/nestjs-app:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "PORT",
          "value": "3000"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:nestjs/db-password"
        },
        {
          "name": "JWT_SECRET",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:nestjs/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nestjs-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### AWS Lambda 部署（Serverless）

#### serverless.yml

```yaml
service: nestjs-app

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  environment:
    NODE_ENV: ${self:provider.stage}
    DATABASE_HOST: ${env:DATABASE_HOST}
    DATABASE_PASSWORD: ${env:DATABASE_PASSWORD}

plugins:
  - serverless-offline
  - serverless-dotenv-plugin

functions:
  api:
    handler: dist/lambda.handler
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY

custom:
  serverless-offline:
    httpPort: 3000
    lambdaPort: 3002
```

#### src/lambda.ts

```typescript
import { NestFactory } from '@nestjs/core';
import { Server } from 'http';
import { ExpressAdapter } from '@nestjs/platform-express';
import { Context, Handler } from 'aws-lambda';
import { createServer, proxy } from 'aws-serverless-express';
import { eventContext } from 'aws-serverless-express/middleware';
import express from 'express';
import { AppModule } from './app.module';

let cachedServer: Server;

async function bootstrapServer(): Promise<Server> {
  if (!cachedServer) {
    const expressApp = express();
    const nestApp = await NestFactory.create(
      AppModule,
      new ExpressAdapter(expressApp),
    );
    
    nestApp.use(eventContext());
    nestApp.enableCors();
    await nestApp.init();
    
    cachedServer = createServer(expressApp);
  }
  
  return cachedServer;
}

export const handler: Handler = async (event: any, context: Context) => {
  const server = await bootstrapServer();
  return proxy(server, event, context, 'PROMISE').promise;
};
```

### 2. Google Cloud Platform 部署

#### Cloud Run 配置

#### cloudbuild.yaml

```yaml
steps:
  # 构建镜像
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/nestjs-app:$COMMIT_SHA', '-f', 'Dockerfile.optimized', '.']
  
  # 推送镜像
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/nestjs-app:$COMMIT_SHA']
  
  # 部署到 Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'nestjs-app'
      - '--image'
      - 'gcr.io/$PROJECT_ID/nestjs-app:$COMMIT_SHA'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'NODE_ENV=production'
      - '--set-secrets'
      - 'DATABASE_PASSWORD=nestjs-db-password:latest,JWT_SECRET=nestjs-jwt-secret:latest'

timeout: '1800s'
```

### 3. Azure 部署

#### Azure Web App 配置

#### azure-pipelines.yml

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  dockerRegistryServiceConnection: 'my-registry-connection'
  imageRepository: 'nestjs-app'
  containerRegistry: 'myregistry.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile.optimized'
  tag: '$(Build.BuildId)'

stages:
- stage: Build
  displayName: Build and push stage
  jobs:
  - job: Build
    displayName: Build job
    steps:
    - task: Docker@2
      displayName: Build and push an image to container registry
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: Deploy
    displayName: Deploy job
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebAppContainer@1
            displayName: 'Azure Web App for Container'
            inputs:
              azureSubscription: 'my-azure-subscription'
              appName: 'nestjs-app'
              containers: $(containerRegistry)/$(imageRepository):$(tag)
```

### 4. Kubernetes 部署

#### k8s/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nestjs-app
  labels:
    app: nestjs-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nestjs-app
  template:
    metadata:
      labels:
        app: nestjs-app
    spec:
      containers:
      - name: nestjs-app
        image: your-registry.com/nestjs-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "3000"
        envFrom:
        - secretRef:
            name: nestjs-secrets
        - configMapRef:
            name: nestjs-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### k8s/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nestjs-service
spec:
  selector:
    app: nestjs-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

#### k8s/configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nestjs-config
data:
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "nestjs"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
```

#### k8s/secret.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: nestjs-secrets
type: Opaque
stringData:
  DATABASE_USERNAME: "postgres"
  DATABASE_PASSWORD: "your-password"
  JWT_SECRET: "your-jwt-secret"
  JWT_REFRESH_SECRET: "your-refresh-secret"
```

#### k8s/hpa.yaml

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nestjs-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nestjs-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 监控与日志

### 1. 日志配置

#### src/logger/logger.service.ts

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const { method, url, ip } = request;
    const userAgent = request.get('user-agent') || '';
    const now = Date.now();

    this.logger.log(`${method} ${url} - ${ip} - ${userAgent}`);

    return next.handle().pipe(
      tap(() => {
        const response = context.switchToHttp().getResponse();
        const { statusCode } = response;
        const delay = Date.now() - now;

        this.logger.log(
          `${method} ${url} - ${statusCode} - ${delay}ms - ${ip}`,
        );
      }),
    );
  }
}
```

#### src/logger/winston.config.ts

```typescript
import * as winston from 'winston';
import * as DailyRotateFile from 'winston-daily-rotate-file';

const logDir = 'logs';

export const winstonConfig = {
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json(),
  ),
  transports: [
    // 控制台输出
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ timestamp, level, message, ...metadata }) => {
          let msg = `${timestamp} [${level}]: ${message}`;
          if (Object.keys(metadata).length > 0) {
            msg += ` ${JSON.stringify(metadata)}`;
          }
          return msg;
        }),
      ),
    }),

    // 错误日志
    new DailyRotateFile({
      filename: `${logDir}/error-%DATE%.log`,
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxSize: '20m',
      maxFiles: '14d',
    }),

    // 组合日志
    new DailyRotateFile({
      filename: `${logDir}/combined-%DATE%.log`,
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d',
    }),
  ],
};
```

### 2. 监控配置

#### src/monitoring/health.controller.ts

```typescript
import { Controller, Get } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckService,
  TypeOrmHealthIndicator,
  MemoryHealthIndicator,
  DiskHealthIndicator,
} from '@nestjs/terminus';

@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private db: TypeOrmHealthIndicator,
    private memory: MemoryHealthIndicator,
    private disk: DiskHealthIndicator,
  ) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.db.pingCheck('database'),
      () => this.memory.checkHeap('memory_heap', 150 * 1024 * 1024),
      () => this.memory.checkRSS('memory_rss', 150 * 1024 * 1024),
      () => this.disk.checkStorage('storage', { path: '/', thresholdPercent: 0.9 }),
    ]);
  }
}
```

#### src/monitoring/metrics.service.ts

```typescript
import { Injectable } from '@nestjs/common';
import { Counter, Histogram, Registry } from 'prom-client';

@Injectable()
export class MetricsService {
  private registry: Registry;
  private httpRequestsTotal: Counter;
  private httpRequestDuration: Histogram;

  constructor() {
    this.registry = new Registry();

    this.httpRequestsTotal = new Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code'],
      registers: [this.registry],
    });

    this.httpRequestDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status_code'],
      buckets: [0.1, 0.5, 1, 2, 5],
      registers: [this.registry],
    });
  }

  incrementHttpRequests(method: string, route: string, statusCode: number) {
    this.httpRequestsTotal.inc({ method, route, status_code: statusCode });
  }

  observeHttpRequestDuration(method: string, route: string, statusCode: number, duration: number) {
    this.httpRequestDuration.observe({ method, route, status_code: statusCode }, duration);
  }

  getMetrics() {
    return this.registry.metrics();
  }
}
```

### 3. Prometheus 集成

#### docker-compose.monitoring.yml

```yaml
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - monitoring

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
```

#### monitoring/prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'nestjs-app'
    static_configs:
      - targets: ['app:3000']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

---

## 最佳实践

### 1. 安全最佳实践

```dockerfile
# 使用非 root 用户运行
USER node

# 最小化镜像层
RUN npm ci --only=production && npm cache clean --force

# 扫描漏洞
# 使用 trivy 或其他安全扫描工具
# trivy image nestjs-app:latest
```

### 2. 性能优化

```dockerfile
# 使用多阶段构建减少镜像大小
# 使用 .dockerignore 排除不必要的文件
# 优化依赖安装
```

#### .dockerignore

```
node_modules
npm-debug.log
dist
.git
.env
.env.*
coverage
.vscode
.idea
*.md
test
```

### 3. 持续集成/持续部署

#### .github/workflows/deploy.yml

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test:cov
      - name: Run linter
        run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t nestjs-app:${{ github.sha }} .
      - name: Login to registry
        run: echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
      - name: Push image
        run: docker push nestjs-app:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # 部署命令
          echo "Deploying to production..."
```

### 4. 备份与恢复

#### scripts/backup.sh

```bash
#!/bin/bash

# 数据库备份
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.sql"

mkdir -p $BACKUP_DIR

# 备份数据库
docker exec nestjs-postgres pg_dump -U postgres nestjs > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 删除 7 天前的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_FILE}.gz"
```

#### scripts/restore.sh

```bash
#!/bin/bash

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 解压备份
gunzip -c $BACKUP_FILE | docker exec -i nestjs-postgres psql -U postgres nestjs

echo "✅ Restore completed from: $BACKUP_FILE"
```

### 5. 监控告警

#### monitoring/alerts.yml

```yaml
groups:
  - name: nestjs_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 500
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value }}MB"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"
```

---

## 总结

本指南涵盖了 NestJS 部署的各个方面，包括：

1. **构建配置**: 完整的构建流程和优化配置
2. **环境变量管理**: 安全的环境变量处理和验证
3. **Docker 化部署**: 容器化部署的完整方案
4. **云平台部署**: AWS、GCP、Azure、Kubernetes 部署配置
5. **监控与日志**: 完善的监控和日志系统
6. **最佳实践**: 安全、性能、CI/CD 等最佳实践

遵循这些指南可以帮助您构建可靠、可扩展的 NestJS 应用部署方案。
