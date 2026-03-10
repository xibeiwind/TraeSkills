# NestJS 中间件模板

## 基础中间件模板

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class {{MiddlewareName}} implements NestMiddleware {
  private readonly logger = new Logger({{MiddlewareName}}.name);

  use(req: Request, res: Response, next: NextFunction): void {
    // 中间件逻辑
    next();
  }
}
```

## 中间件实现示例

### 1. 日志中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  private readonly logger = new Logger(LoggerMiddleware.name);

  use(req: Request, res: Response, next: NextFunction): void {
    const { method, originalUrl, ip } = req;
    const userAgent = req.get('user-agent') || '';

    const startTime = Date.now();

    res.on('finish', () => {
      const { statusCode } = res;
      const contentLength = res.get('content-length');
      const responseTime = Date.now() - startTime;

      this.logger.log(
        `${method} ${originalUrl} ${statusCode} ${contentLength} - ${responseTime}ms - ${ip} - ${userAgent}`
      );
    });

    next();
  }
}
```

### 2. 认证中间件

```typescript
import { Injectable, NestMiddleware, UnauthorizedException, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthMiddleware implements NestMiddleware {
  private readonly logger = new Logger(AuthMiddleware.name);

  constructor(private readonly jwtService: JwtService) {}

  use(req: Request, res: Response, next: NextFunction): void {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      throw new UnauthorizedException('Authorization header missing');
    }

    const [type, token] = authHeader.split(' ');

    if (type !== 'Bearer' || !token) {
      throw new UnauthorizedException('Invalid authorization header format');
    }

    try {
      const payload = this.jwtService.verify(token);
      req['user'] = payload;
      next();
    } catch (error) {
      this.logger.error(`Authentication failed: ${error.message}`);
      throw new UnauthorizedException('Invalid or expired token');
    }
  }
}
```

### 3. 请求限流中间件

```typescript
import { Injectable, NestMiddleware, HttpException, HttpStatus, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

interface RateLimitStore {
  count: number;
  resetTime: number;
}

@Injectable()
export class RateLimitMiddleware implements NestMiddleware {
  private readonly logger = new Logger(RateLimitMiddleware.name);
  private readonly store = new Map<string, RateLimitStore>();
  private readonly windowMs = 60 * 1000; // 1分钟
  private readonly maxRequests = 100;

  use(req: Request, res: Response, next: NextFunction): void {
    const ip = req.ip;
    const now = Date.now();

    let record = this.store.get(ip);

    if (!record || now > record.resetTime) {
      record = {
        count: 1,
        resetTime: now + this.windowMs,
      };
      this.store.set(ip, record);
    } else {
      record.count++;
    }

    const remaining = this.maxRequests - record.count;
    const resetTime = Math.ceil(record.resetTime / 1000);

    res.setHeader('X-RateLimit-Limit', this.maxRequests);
    res.setHeader('X-RateLimit-Remaining', Math.max(0, remaining));
    res.setHeader('X-RateLimit-Reset', resetTime);

    if (record.count > this.maxRequests) {
      this.logger.warn(`Rate limit exceeded for IP: ${ip}`);
      throw new HttpException(
        'Too many requests, please try again later',
        HttpStatus.TOO_MANY_REQUESTS
      );
    }

    next();
  }
}
```

### 4. CORS 中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class CorsMiddleware implements NestMiddleware {
  private readonly logger = new Logger(CorsMiddleware.name);

  private readonly allowedOrigins = [
    'http://localhost:3000',
    'https://example.com',
  ];

  private readonly allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'];

  private readonly allowedHeaders = [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
  ];

  use(req: Request, res: Response, next: NextFunction): void {
    const origin = req.headers.origin;

    if (origin && this.allowedOrigins.includes(origin)) {
      res.setHeader('Access-Control-Allow-Origin', origin);
    }

    res.setHeader('Access-Control-Allow-Methods', this.allowedMethods.join(', '));
    res.setHeader('Access-Control-Allow-Headers', this.allowedHeaders.join(', '));
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Access-Control-Max-Age', '86400');

    if (req.method === 'OPTIONS') {
      res.sendStatus(204);
      return;
    }

    next();
  }
}
```

### 5. 请求体大小限制中间件

```typescript
import { Injectable, NestMiddleware, PayloadTooLargeException, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class BodySizeLimitMiddleware implements NestMiddleware {
  private readonly logger = new Logger(BodySizeLimitMiddleware.name);
  private readonly maxBodySize = 10 * 1024 * 1024; // 10MB

  use(req: Request, res: Response, next: NextFunction): void {
    const contentLength = parseInt(req.headers['content-length'] || '0', 10);

    if (contentLength > this.maxBodySize) {
      this.logger.warn(`Request body too large: ${contentLength} bytes`);
      throw new PayloadTooLargeException(
        `Request body too large. Maximum size is ${this.maxBodySize} bytes`
      );
    }

    next();
  }
}
```

### 6. 压缩中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import * as compression from 'compression';

@Injectable()
export class CompressionMiddleware implements NestMiddleware {
  private readonly logger = new Logger(CompressionMiddleware.name);
  private readonly compression = compression({
    filter: (req: Request, res: Response) => {
      if (req.headers['x-no-compression']) {
        return false;
      }
      return compression.filter(req, res);
    },
    threshold: 1024,
    level: 6,
  });

  use(req: Request, res: Response, next: NextFunction): void {
    this.compression(req, res, next);
  }
}
```

### 7. 请求 ID 中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

declare global {
  namespace Express {
    interface Request {
      id?: string;
    }
  }
}

@Injectable()
export class RequestIdMiddleware implements NestMiddleware {
  private readonly logger = new Logger(RequestIdMiddleware.name);

  use(req: Request, res: Response, next: NextFunction): void {
    const requestId = req.headers['x-request-id'] as string || uuidv4();
    req.id = requestId;

    res.setHeader('X-Request-ID', requestId);

    next();
  }
}
```

### 8. 健康检查中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class HealthCheckMiddleware implements NestMiddleware {
  private readonly logger = new Logger(HealthCheckMiddleware.name);

  use(req: Request, res: Response, next: NextFunction): void {
    if (req.path === '/health') {
      res.status(200).json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
      });
      return;
    }
    next();
  }
}
```

### 9. 错误处理中间件

```typescript
import { Injectable, NestMiddleware, HttpException, HttpStatus, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class ErrorHandlerMiddleware implements NestMiddleware {
  private readonly logger = new Logger(ErrorHandlerMiddleware.name);

  use(req: Request, res: Response, next: NextFunction): void {
    res.on('error', (error) => {
      this.logger.error(`Response error: ${error.message}`);
      if (!res.headersSent) {
        res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
          statusCode: HttpStatus.INTERNAL_SERVER_ERROR,
          message: 'Internal server error',
        });
      }
    });

    next();
  }
}
```

### 10. 安全头中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class SecurityHeadersMiddleware implements NestMiddleware {
  private readonly logger = new Logger(SecurityHeadersMiddleware.name);

  use(req: Request, res: Response, next: NextFunction): void {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');

    next();
  }
}
```

## 函数式中间件

### 1. 简单日志中间件

```typescript
import { Request, Response, NextFunction } from 'express';

export function loggerMiddleware(req: Request, res: Response, next: NextFunction): void {
  console.log(`${req.method} ${req.url}`);
  next();
}
```

### 2. 认证中间件

```typescript
import { Request, Response, NextFunction } from 'express';
import { UnauthorizedException } from '@nestjs/common';

export function authMiddleware(req: Request, res: Response, next: NextFunction): void {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    throw new UnauthorizedException('Token not provided');
  }

  // 验证 token 逻辑
  next();
}
```

## 中间件配置

### 在模块中应用中间件

```typescript
import { Module, MiddlewareConsumer, NestModule, RequestMethod } from '@nestjs/common';
import { LoggerMiddleware } from './middlewares/logger.middleware';
import { AuthMiddleware } from './middlewares/auth.middleware';
import { UserController } from './user.controller';
import { AdminController } from './admin.controller';

@Module({
  imports: [],
  controllers: [UserController, AdminController],
  providers: [],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer
      .apply(LoggerMiddleware)
      .forRoutes('*');

    consumer
      .apply(AuthMiddleware)
      .exclude(
        { path: 'auth/login', method: RequestMethod.POST },
        { path: 'auth/register', method: RequestMethod.POST },
      )
      .forRoutes(UserController);

    consumer
      .apply(AuthMiddleware, LoggerMiddleware)
      .forRoutes(AdminController);
  }
}
```

### 使用函数式中间件

```typescript
import { Module, MiddlewareConsumer, NestModule } from '@nestjs/common';
import { loggerMiddleware } from './middlewares/logger.middleware';

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer
      .apply(loggerMiddleware)
      .forRoutes('*');
  }
}
```

## 中间件最佳实践

1. **单一职责**: 每个中间件只负责一个功能
2. **错误处理**: 适当处理和记录错误
3. **性能考虑**: 避免在中间件中执行耗时操作
4. **类型安全**: 使用 TypeScript 类型定义
5. **日志记录**: 记录重要操作和错误
6. **配置灵活**: 通过构造函数或环境变量配置中间件
7. **测试覆盖**: 为中间件编写单元测试
8. **文档说明**: 为复杂中间件添加注释和文档

## 中间件执行顺序

中间件按照配置的顺序执行：

```typescript
configure(consumer: MiddlewareConsumer): void {
  consumer
    .apply(Middleware1, Middleware2, Middleware3)
    .forRoutes('*');
}
```

执行顺序: Middleware1 → Middleware2 → Middleware3 → 路由处理器

## 类型定义扩展

### 扩展 Express Request 接口

```typescript
// src/common/interfaces/request.interface.ts
import { Request } from 'express';

declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email: string;
        role: string;
      };
      id?: string;
      tenantId?: string;
    }
  }
}

export {};
```

### 在中间件中使用扩展类型

```typescript
import { Injectable, NestMiddleware } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class CustomMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction): void {
    // 现在可以安全地访问 req.user 和 req.id
    console.log(req.user?.id);
    console.log(req.id);
    next();
  }
}
```
