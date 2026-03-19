# NestJS CORS 配置指南

本文档提供了在 NestJS 项目中配置 CORS（跨域资源共享）的完整指南，包括基本配置、高级选项和最佳实践。

## 目录

- [什么是 CORS](#什么是-cors)
- [NestJS 中的 CORS 支持](#nestjs-中的-cors-支持)
- [基本配置](#基本配置)
- [高级配置选项](#高级配置选项)
- [环境变量集成](#环境变量集成)
- [最佳实践](#最佳实践)
- [常见问题与解决方案](#常见问题与解决方案)

## 什么是 CORS

CORS（Cross-Origin Resource Sharing，跨域资源共享）是一种浏览器安全机制，用于控制从不同域（origin）发起的请求是否被允许访问服务器资源。

当前端应用和后端 API 部署在不同域名下时，浏览器会执行 CORS 预检请求（OPTIONS 请求）来验证是否允许跨域请求。

## NestJS 中的 CORS 支持

NestJS 内置了 CORS 支持，基于 Express 的 CORS 中间件。通过 `app.enableCors()` 方法可以启用 CORS 配置。

## 基本配置

### 最简单的配置

在 `main.ts` 文件中启用基本的 CORS 配置：

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 启用 CORS
  app.enableCors();
  
  await app.listen(3000);
}
bootstrap();
```

这将允许所有跨域请求，使用默认的 CORS 配置。

## 高级配置选项

### 详细配置选项

可以通过传递配置对象来自定义 CORS 行为：

```typescript
app.enableCors({
  origin: ['http://localhost:3000', 'http://localhost:4200'], // 允许的源
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], // 允许的 HTTP 方法
  allowedHeaders: ['Content-Type', 'Authorization'], // 允许的请求头
  credentials: true, // 允许携带凭证（如 cookies）
  maxAge: 86400, // 预检请求的缓存时间（秒）
  preflightContinue: false, // 是否继续处理预检请求
  optionsSuccessStatus: 204, // 预检请求的成功状态码
});
```

### 配置选项说明

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `origin` | `string  string[]  boolean  Function` | `*` | 允许的源，`*` 表示允许所有源 |
| `methods` | `string[]` | `['GET', 'HEAD', 'PUT', 'PATCH', 'POST', 'DELETE']` | 允许的 HTTP 方法 |
| `allowedHeaders` | `string[]` | `['Content-Type', 'Accept', 'Authorization']` | 允许的请求头 |
| `credentials` | `boolean` | `false` | 是否允许携带凭证 |
| `maxAge` | `number` | `86400` | 预检请求的缓存时间（秒） |
| `preflightContinue` | `boolean` | `false` | 是否继续处理预检请求 |
| `optionsSuccessStatus` | `number` | `204` | 预检请求的成功状态码 |

### 动态源配置

可以使用函数来动态决定是否允许请求源：

```typescript
app.enableCors({
  origin: (origin, callback) => {
    // 允许的域名列表
    const allowedOrigins = ['http://localhost:3000', 'http://localhost:4200', 'https://your-production-domain.com'];
    
    // 检查请求源是否在允许列表中
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
});
```

## 环境变量集成

### 配置环境变量

在 `.env` 文件中添加 CORS 相关配置：

```env
# CORS 配置
CORS_ORIGIN=http://localhost:3000,http://localhost:4200
CORS_CREDENTIALS=true
CORS_MAX_AGE=86400
```

### 从环境变量读取配置

在 `main.ts` 中从环境变量读取 CORS 配置：

```typescript
import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);
  
  // 从环境变量读取 CORS 配置
  const corsOrigins = configService.get('CORS_ORIGIN', 'http://localhost:3000').split(',');
  const corsCredentials = configService.get('CORS_CREDENTIALS', 'true') === 'true';
  const corsMaxAge = parseInt(configService.get('CORS_MAX_AGE', '86400'), 10);
  
  app.enableCors({
    origin: corsOrigins,
    credentials: corsCredentials,
    maxAge: corsMaxAge,
  });
  
  await app.listen(configService.get('PORT', 3000));
}
bootstrap();
```

## 最佳实践

### 开发环境

在开发环境中，可以允许所有源：

```typescript
app.enableCors({
  origin: '*',
  credentials: true,
});
```

### 测试环境

在测试环境中，应该限制为特定的测试域名：

```typescript
app.enableCors({
  origin: ['http://test-app.example.com', 'http://localhost:3000'],
  credentials: true,
});
```

### 生产环境

在生产环境中，应该严格限制为实际的前端域名：

```typescript
app.enableCors({
  origin: ['https://app.example.com', 'https://www.example.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400,
});
```

### 安全性考虑

1. **不要在生产环境中使用 `origin: '*'`** - 这会允许任何域名的请求
2. **仅允许必要的 HTTP 方法** - 限制为应用实际需要的方法
3. **仅允许必要的请求头** - 限制为应用实际需要的头
4. **合理设置 `maxAge`** - 过长的缓存时间可能导致配置更新延迟

## 常见问题与解决方案

### 问题 1: CORS 预检请求失败

**症状**：浏览器控制台显示 CORS 错误，提示预检请求失败

**解决方案**：
- 确保服务器正确响应 OPTIONS 请求
- 检查 `allowedHeaders` 配置是否包含所有必要的头
- 确保 `methods` 配置包含 OPTIONS 方法

### 问题 2: 携带凭证的请求被拒绝

**症状**：带有 credentials 的请求被 CORS 策略拒绝

**解决方案**：
- 设置 `credentials: true`
- 确保 `origin` 不是 `*`（当使用 credentials 时不允许使用通配符）

### 问题 3: 自定义请求头被拒绝

**症状**：带有自定义请求头的请求被 CORS 策略拒绝

**解决方案**：
- 在 `allowedHeaders` 中添加自定义头
- 例如：`allowedHeaders: ['Content-Type', 'Authorization', 'X-Custom-Header']`

### 问题 4: 不同环境的 CORS 配置

**解决方案**：
- 使用环境变量来管理不同环境的 CORS 配置
- 为开发、测试和生产环境设置不同的配置

## 完整示例

### 基本配置示例

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 基本 CORS 配置
  app.enableCors({
    origin: ['http://localhost:3000', 'http://localhost:4200'],
    credentials: true,
  });
  
  await app.listen(3000);
}
bootstrap();
```

### 高级配置示例

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);
  
  // 高级 CORS 配置
  app.enableCors({
    origin: configService.get('NODE_ENV') === 'production' 
      ? ['https://app.example.com'] 
      : '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    credentials: true,
    maxAge: 86400,
  });
  
  await app.listen(configService.get('PORT', 3000));
}
bootstrap();
```

### 环境变量配置示例

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);
  
  // 从环境变量读取 CORS 配置
  const corsConfig = {
    origin: configService.get('CORS_ORIGIN', 'http://localhost:3000').split(','),
    credentials: configService.get('CORS_CREDENTIALS', 'true') === 'true',
    maxAge: parseInt(configService.get('CORS_MAX_AGE', '86400'), 10),
    methods: configService.get('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','),
    allowedHeaders: configService.get('CORS_ALLOWED_HEADERS', 'Content-Type,Authorization').split(','),
  };
  
  app.enableCors(corsConfig);
  
  await app.listen(configService.get('PORT', 3000));
}
bootstrap();
```

## 总结

CORS 配置是前后端分离架构中的重要组成部分。通过本文档的指南，您可以：

1. 了解 CORS 的基本概念和工作原理
2. 掌握 NestJS 中 CORS 的配置方法
3. 实现从环境变量读取 CORS 配置
4. 遵循不同环境的 CORS 最佳实践
5. 解决常见的 CORS 问题

正确配置 CORS 可以确保前端应用能够安全地与后端 API 进行通信，同时保持应用的安全性。