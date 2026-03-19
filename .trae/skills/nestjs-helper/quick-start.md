# NestJS Helper Skill 快速开始指南

欢迎使用 NestJS Helper Skill！本指南将帮助您快速上手，使用该 skill 进行高效的 NestJS 项目开发。

## 目录

- [简介](#简介)
- [前提条件](#前提条件)
- [快速安装](#快速安装)
- [创建第一个项目](#创建第一个项目)
- [核心功能概览](#核心功能概览)
- [常用命令](#常用命令)
- [下一步](#下一步)

## 简介

NestJS Helper Skill 是一个专门为 NestJS 开发者设计的智能辅助工具，提供以下核心功能：

- 🚀 **项目初始化** - 快速创建标准化的 NestJS 项目结构
- 📝 **代码生成** - 自动生成模块、控制器、服务等代码模板
- 💡 **最佳实践指导** - 提供符合 NestJS 规范的开发建议
- 🗄️ **数据库集成** - 支持 TypeORM、Prisma、Mongoose 等
- 🧪 **测试支持** - 单元测试、集成测试和端到端测试
- 🔍 **代码审查** - 自动检测代码质量和潜在问题

## 前提条件

在使用 NestJS Helper Skill 之前，请确保您的开发环境满足以下要求：

### 必需环境

- **Node.js**: 版本 18.x 或更高
- **npm**: 版本 9.x 或更高（或 yarn/pnpm）
- **TypeScript**: 版本 5.x 或更高

### 可选工具

- **Git**: 用于版本控制
- **Docker**: 用于容器化部署
- **PostgreSQL/MySQL/MongoDB**: 根据项目需求选择数据库

### 环境检查

运行以下命令检查您的环境：

```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 检查 TypeScript 版本
tsc --version
```

## 快速安装

### 1. 安装 NestJS CLI

如果您还没有安装 NestJS CLI，请运行：

```bash
npm install -g @nestjs/cli
```

### 2. 创建新项目

使用 NestJS Helper Skill 创建新项目：

```bash
# 使用 NestJS CLI 创建项目
nest new my-nestjs-app

# 进入项目目录
cd my-nestjs-app
```

### 3. 安装常用依赖

```bash
# 安装验证和转换库
npm install class-validator class-transformer

# 安装配置管理
npm install @nestjs/config

# 安装 TypeORM（如果使用 TypeORM）
npm install @nestjs/typeorm typeorm pg
```

## 创建第一个项目

### 步骤 1: 项目初始化

使用 NestJS Helper Skill 进行项目初始化：

```
请帮我创建一个 NestJS 项目，包含以下功能：
- 用户管理模块
- 认证授权模块
- 使用 TypeORM 连接 PostgreSQL 数据库
- 配置环境变量管理
- 添加验证管道
```

NestJS Helper Skill 将自动为您生成标准的项目结构。

### 步骤 2: 配置环境变量

创建 `.env` 文件：

```env
# 应用配置
NODE_ENV=development
PORT=3000
API_PREFIX=api

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_DATABASE=nestjs_app

# JWT 配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=1d
```

创建 `.env.example` 文件作为模板：

```env
NODE_ENV=development
PORT=3000
API_PREFIX=api
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_DATABASE=nestjs_app
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=1d
```

### 步骤 3: 配置主应用

更新 `main.ts` 文件：

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 全局前缀
  app.setGlobalPrefix('api');

  // 全局验证管道
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // 启用 CORS
  // 详细配置请参考 CORS 配置指南
  app.enableCors({
    origin: ['http://localhost:3000', 'http://localhost:4200'],
    credentials: true,
  });

  await app.listen(process.env.PORT || 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
```

### 步骤 4: 启动应用

```bash
# 开发模式
npm run start:dev

# 生产模式
npm run build
npm run start:prod
```

访问 `http://localhost:3000/api` 查看应用是否正常运行。

## 核心功能概览

### 1. 代码生成

使用 NestJS Helper Skill 快速生成代码：

```
生成一个用户模块，包含：
- User 实体（包含 id, username, email, password 字段）
- UsersController（CRUD 操作）
- UsersService（业务逻辑）
- CreateUserDto 和 UpdateUserDto
```

### 2. 数据库集成

```
帮我配置 TypeORM 连接 PostgreSQL 数据库，并创建 User 实体的迁移文件
```

### 3. 认证授权

```
添加 JWT 认证功能，包括：
- AuthService
- JwtStrategy
- JwtAuthGuard
- 登录和注册接口
```

### 4. 测试编写

```
为 UsersService 编写单元测试，覆盖所有方法
```

### 5. 代码审查

```
审查我的 NestJS 项目代码，检查代码质量和潜在问题
```

## 常用命令

### NestJS CLI 命令

```bash
# 生成模块
nest g module users

# 生成控制器
nest g controller users

# 生成服务
nest g service users

# 生成 DTO
nest g class dto/create-user --no-spec

# 生成守卫
nest g guard auth

# 生成拦截器
nest g interceptor logging

# 生成管道
nest g pipe validation

# 生成中间件
nest g middleware logger
```

### 开发命令

```bash
# 启动开发服务器（热重载）
npm run start:dev

# 启动调试模式
npm run start:debug

# 构建项目
npm run build

# 运行生产版本
npm run start:prod

# 运行测试
npm test

# 运行测试并生成覆盖率报告
npm run test:cov

# 运行 ESLint 检查
npm run lint

# 修复 ESLint 问题
npm run lint:fix
```

### 数据库命令（TypeORM）

```bash
# 生成迁移文件
npm run migration:generate -- -n CreateUserTable

# 运行迁移
npm run migration:run

# 回滚迁移
npm run migration:revert

# 显示迁移状态
npm run migration:show
```

## 项目结构示例

NestJS Helper Skill 生成的标准项目结构：

```
my-nestjs-app/
├── src/
│   ├── main.ts                 # 应用入口
│   ├── app.module.ts           # 根模块
│   ├── common/                 # 公共模块
│   │   ├── decorators/         # 自定义装饰器
│   │   ├── filters/            # 异常过滤器
│   │   ├── guards/             # 守卫
│   │   ├── interceptors/       # 拦截器
│   │   ├── middlewares/        # 中间件
│   │   ├── pipes/              # 管道
│   │   └── utils/              # 工具函数
│   ├── config/                 # 配置文件
│   │   └── configuration.ts
│   └── modules/                # 功能模块
│       ├── users/
│       │   ├── users.module.ts
│       │   ├── users.controller.ts
│       │   ├── users.service.ts
│       │   ├── users.entity.ts
│       │   └── dto/
│       └── auth/
│           ├── auth.module.ts
│           ├── auth.controller.ts
│           ├── auth.service.ts
│           └── strategies/
├── test/                       # 测试文件
│   ├── unit/
│   └── e2e/
├── .env                        # 环境变量
├── .env.example                # 环境变量示例
├── nest-cli.json               # NestJS CLI 配置
├── tsconfig.json               # TypeScript 配置
└── package.json                # 项目依赖
```

## 开发工作流

### 1. 需求分析

```
我需要创建一个博客系统，包含文章、评论和用户功能
```

### 2. 设计架构

```
帮我设计博客系统的模块结构，并说明各模块之间的关系
```

### 3. 生成代码

```
生成文章模块，包含完整的 CRUD 功能和评论关联
```

### 4. 编写测试

```
为文章模块编写单元测试和集成测试
```

### 5. 代码审查

```
审查博客系统的代码，提供优化建议
```

### 6. 部署准备

```
帮我准备 Docker 部署文件和 CI/CD 配置
```

## 常见问题快速解决

### 问题 1: 端口被占用

```bash
# 修改 .env 文件中的 PORT
PORT=3001
```

### 问题 2: 数据库连接失败

检查 `.env` 文件中的数据库配置是否正确：

```env
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_DATABASE=nestjs_app
```

### 问题 3: 验证管道不生效

确保在 `main.ts` 中正确配置了全局验证管道：

```typescript
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }),
);
```

## 下一步

恭喜您完成了快速开始！现在您可以：

1. 📖 阅读 [使用示例文档](./usage-examples.md) 了解更多详细用法
2. 📚 查看 [常见问题解答](./faq.md) 解决遇到的问题
3. 🔍 探索项目中的其他文档文件，了解各个功能的详细信息
4. 🚀 开始构建您的 NestJS 应用

## 获取帮助

如果您在使用过程中遇到任何问题，可以：

- 查看项目中的详细文档
- 访问 [NestJS 官方文档](https://docs.nestjs.com/)
- 查看 [NestJS 中文文档](https://docs.nestjs.cn/)
- 参考 [CORS 配置指南](./cors-config.md) 了解详细的跨域配置

---

祝您开发愉快！🎉
