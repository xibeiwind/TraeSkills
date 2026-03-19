# NestJS 配置文件示例

本文档提供了 NestJS 项目中常用配置文件的完整示例和详细说明。

## tsconfig.json

TypeScript 编译器配置文件：

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
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["src/*"],
      "@modules/*": ["src/modules/*"],
      "@common/*": ["src/common/*"],
      "@config/*": ["src/config/*"],
      "@database/*": ["src/database/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "test"]
}
```

**配置说明：**
- `module`: 模块系统，NestJS 使用 CommonJS
- `experimentalDecorators`: 启用装饰器支持（必需）
- `emitDecoratorMetadata`: 启用装饰器元数据（必需）
- `paths`: 路径别名，简化导入路径
- `outDir`: 编译输出目录

## tsconfig.build.json

构建专用的 TypeScript 配置：

```json
{
  "extends": "./tsconfig.json",
  "exclude": ["node_modules", "test", "dist", "**/*spec.ts"]
}
```

## nest-cli.json

NestJS CLI 配置文件：

```json
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true,
    "webpack": true,
    "tsConfigPath": "tsconfig.build.json",
    "plugins": [
      {
        "name": "@nestjs/swagger",
        "options": {
          "classValidatorShim": true,
          "introspectComments": true,
          "controller": {
            "path": "swagger",
            "fileName": "swagger.json"
          }
        }
      }
    ]
  },
  "generateOptions": {
    "spec": true,
    "flat": false,
    "specFileSuffix": ".spec"
  },
  "projects": {
    "app": {
      "type": "application",
      "root": ".",
      "entryFile": "main",
      "sourceRoot": "src",
      "compilerOptions": {
        "tsConfigPath": "tsconfig.build.json"
      }
    }
  }
}
```

**配置说明：**
- `deleteOutDir`: 构建前删除输出目录
- `webpack`: 启用 webpack 打包
- `spec`: 自动生成测试文件
- `flat`: 不使用扁平目录结构

## .env.example

环境变量示例文件：

```bash
# 应用配置
NODE_ENV=development
PORT=3000
API_PREFIX=api
APP_NAME=My NestJS App
APP_URL=http://localhost:3000

# 数据库配置
DATABASE_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=myapp_db
DATABASE_SYNCHRONIZE=false
DATABASE_LOGGING=true

# JWT 配置
JWT_SECRET=your-secret-key-change-this-in-production
JWT_EXPIRATION=7d
JWT_REFRESH_SECRET=your-refresh-secret-key
JWT_REFRESH_EXPIRATION=30d

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 邮件配置
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=noreply@myapp.com

# AWS S3 配置（可选）
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=myapp-bucket

# 日志配置
LOG_LEVEL=debug
LOG_FORMAT=json

# CORS 配置
CORS_ORIGIN=http://localhost:3000,http://localhost:4200
CORS_CREDENTIALS=true
CORS_MAX_AGE=86400
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOWED_HEADERS=Content-Type,Authorization

# 限流配置
THROTTLE_TTL=60
THROTTLE_LIMIT=10

# 文件上传配置
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=image/jpeg,image/png,application/pdf
```

## .env

实际环境变量文件（不提交到版本控制）：

```bash
NODE_ENV=development
PORT=3000
API_PREFIX=api
APP_NAME=My NestJS App
APP_URL=http://localhost:3000

DATABASE_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_password_here
DATABASE_NAME=myapp_db
DATABASE_SYNCHRONIZE=false
DATABASE_LOGGING=true

JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRATION=7d
JWT_REFRESH_SECRET=your-super-secret-refresh-key
JWT_REFRESH_EXPIRATION=30d
```

## .gitignore

Git 忽略文件配置：

```gitignore
# 编译输出
dist
build
*.tsbuildinfo

# 依赖
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# 环境变量
.env
.env.local
.env.*.local

# IDE
.vscode
.idea
*.swp
*.swo
*~

# 操作系统
.DS_Store
Thumbs.db

# 测试覆盖率
coverage
.nyc_output

# 日志
logs
*.log

# 临时文件
tmp
temp
*.tmp

# 数据库
*.sqlite
*.db

# 上传文件
uploads
public/uploads
```

## .prettierrc

代码格式化配置：

```json
{
  "singleQuote": true,
  "trailingComma": "all",
  "semi": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

## .eslintrc.js

ESLint 代码检查配置：

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    project: 'tsconfig.json',
    tsconfigRootDir: __dirname,
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint/eslint-plugin'],
  extends: [
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
  ],
  root: true,
  env: {
    node: true,
    jest: true,
  },
  ignorePatterns: ['.eslintrc.js'],
  rules: {
    '@typescript-eslint/interface-name-prefix': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'prettier/prettier': 'error',
  },
};
```

## .prettierrc.js

Prettier 格式化配置（JavaScript 版本）：

```javascript
module.exports = {
  singleQuote: true,
  trailingComma: 'all',
  semi: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  arrowParens: 'always',
  endOfLine: 'lf',
};
```

## package.json

项目依赖配置：

```json
{
  "name": "my-nestjs-app",
  "version": "1.0.0",
  "description": "A NestJS application",
  "author": "Your Name",
  "private": true,
  "license": "MIT",
  "scripts": {
    "build": "nest build",
    "format": "prettier --write \"src/**/*.ts\" \"test/**/*.ts\"",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:debug": "nest start --debug --watch",
    "start:prod": "node dist/main",
    "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:cov": "jest --coverage",
    "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
    "test:e2e": "jest --config ./test/jest-e2e.json",
    "typeorm": "ts-node -r tsconfig-paths/register ./node_modules/typeorm/cli.js",
    "migration:generate": "npm run typeorm -- migration:generate -d src/database/data-source.ts",
    "migration:run": "npm run typeorm -- migration:run -d src/database/data-source.ts",
    "migration:revert": "npm run typeorm -- migration:revert -d src/database/data-source.ts",
    "seed": "ts-node -r tsconfig-paths/register src/database/seeds/run-seed.ts"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/config": "^3.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/jwt": "^10.1.0",
    "@nestjs/passport": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/swagger": "^7.1.0",
    "@nestjs/typeorm": "^10.0.0",
    "bcrypt": "^5.1.0",
    "class-transformer": "^0.5.1",
    "class-validator": "^0.14.0",
    "passport": "^0.6.0",
    "passport-jwt": "^4.0.1",
    "passport-local": "^1.0.0",
    "pg": "^8.11.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1",
    "typeorm": "^0.3.17"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/bcrypt": "^5.0.0",
    "@types/express": "^4.17.17",
    "@types/jest": "^29.5.2",
    "@types/node": "^20.3.1",
    "@types/passport-jwt": "^3.0.9",
    "@types/passport-local": "^1.0.35",
    "@types/supertest": "^2.0.12",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.42.0",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-prettier": "^5.0.0",
    "jest": "^29.5.0",
    "prettier": "^3.0.0",
    "source-map-support": "^0.5.21",
    "supertest": "^6.3.3",
    "ts-jest": "^29.1.0",
    "ts-loader": "^9.4.3",
    "ts-node": "^10.9.1",
    "tsconfig-paths": "^4.2.0",
    "typescript": "^5.1.3"
  },
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\.spec\\.ts$",
    "transform": {
      "^.+\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
```

## jest.config.js

Jest 测试配置：

```javascript
module.exports = {
  moduleFileExtensions: ['js', 'json', 'ts'],
  rootDir: '.',
  testRegex: '.*\\.spec\\.ts$',
  transform: {
    '^.+\\.(t|j)s$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.(t|j)s',
    '!src/main.ts',
    '!src/**/*.module.ts',
    '!src/**/*.dto.ts',
    '!src/**/*.interface.ts',
  ],
  coverageDirectory: './coverage',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/test'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@modules/(.*)$': '<rootDir>/src/modules/$1',
    '^@common/(.*)$': '<rootDir>/src/common/$1',
    '^@config/(.*)$': '<rootDir>/src/config/$1',
  },
};
```

## .dockerignore

Docker 构建忽略文件：

```dockerfile
node_modules
npm-debug.log
dist
.git
.gitignore
.env
.env.local
.vscode
.idea
coverage
*.md
```

## Dockerfile

Docker 容器配置：

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM node:18-alpine AS production

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/main"]
```

## docker-compose.yml

Docker Compose 配置：

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: myapp_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 配置文件使用建议

### 1. 环境变量管理
- 使用 `.env.example` 作为模板
- 永远不要将 `.env` 文件提交到版本控制
- 为不同环境创建不同的配置文件（`.env.development`, `.env.production`）

### 2. TypeScript 配置
- 使用路径别名简化导入
- 保持 `tsconfig.json` 和 `tsconfig.build.json` 同步
- 定期更新 TypeScript 版本

### 3. 代码质量
- 配置 ESLint 和 Prettier 保持代码风格一致
- 在 CI/CD 流程中运行 lint 和测试
- 使用 Husky 添加 pre-commit 钩子

### 4. 测试配置
- 配置适当的覆盖率阈值
- 使用测试环境变量
- 分离单元测试和端到端测试

### 5. Docker 配置
- 使用多阶段构建减小镜像大小
- 优化依赖安装
- 使用健康检查确保容器正常运行

这些配置文件为 NestJS 项目提供了完整的开发和部署环境配置，可以根据项目需求进行调整。
