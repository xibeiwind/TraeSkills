# NestJS 拦截器模板

## 基础拦截器模板

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class {{InterceptorName}} implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map(data => {
        return data;
      }),
    );
  }
}
```

## 拦截器实现示例

### 1. 响应转换拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Response<T> {
  success: boolean;
  statusCode: number;
  message: string;
  data: T;
  timestamp: string;
}

@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, Response<T>> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<Response<T>> {
    const response = context.switchToHttp().getResponse();
    const statusCode = response.statusCode;

    return next.handle().pipe(
      map(data => ({
        success: true,
        statusCode,
        message: this.getMessage(statusCode),
        data,
        timestamp: new Date().toISOString(),
      })),
    );
  }

  private getMessage(statusCode: number): string {
    const messages: Record<number, string> = {
      200: 'Success',
      201: 'Created',
      204: 'No Content',
    };
    return messages[statusCode] || 'Success';
  }
}
```

### 2. 日志记录拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const { method, url, body, query, ip } = request;
    const userAgent = request.get('user-agent') || '';
    const now = Date.now();

    this.logger.log(
      `Incoming Request: ${method} ${url} - IP: ${ip} - UserAgent: ${userAgent}`
    );

    return next.handle().pipe(
      tap({
        next: () => {
          const response = context.switchToHttp().getResponse();
          const { statusCode } = response;
          const delay = Date.now() - now;

          this.logger.log(
            `Outgoing Response: ${method} ${url} - Status: ${statusCode} - Delay: ${delay}ms`
          );
        },
        error: (error) => {
          const delay = Date.now() - now;
          this.logger.error(
            `Error Response: ${method} ${url} - Error: ${error.message} - Delay: ${delay}ms`,
            error.stack
          );
        },
      }),
    );
  }
}
```

### 3. 缓存拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Reflector } from '@nestjs/core';

@Injectable()
export class CacheInterceptor implements NestInterceptor {
  private readonly logger = new Logger(CacheInterceptor.name);
  private readonly cache = new Map<string, any>();

  constructor(private readonly reflector: Reflector) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const cacheKey = this.generateCacheKey(context);
    const cachedResponse = this.cache.get(cacheKey);

    if (cachedResponse) {
      this.logger.log(`Cache hit for key: ${cacheKey}`);
      return of(cachedResponse);
    }

    return next.handle().pipe(
      tap(response => {
        const cacheTTL = this.reflector.get<number>('cacheTTL', context.getHandler());
        if (cacheTTL) {
          this.cache.set(cacheKey, response);
          this.logger.log(`Cached response for key: ${cacheKey}, TTL: ${cacheTTL}ms`);

          setTimeout(() => {
            this.cache.delete(cacheKey);
            this.logger.log(`Cache expired for key: ${cacheKey}`);
          }, cacheTTL);
        }
      }),
    );
  }

  private generateCacheKey(context: ExecutionContext): string {
    const request = context.switchToHttp().getRequest();
    const { method, url, query } = request;
    return `${method}:${url}:${JSON.stringify(query)}`;
  }
}
```

### 4. 超时拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, RequestTimeoutException } from '@nestjs/common';
import { Observable, throwError, TimeoutError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

@Injectable()
export class TimeoutInterceptor implements NestInterceptor {
  private readonly defaultTimeout = 5000; // 5秒

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      timeout(this.defaultTimeout),
      catchError(err => {
        if (err instanceof TimeoutError) {
          return throwError(() => new RequestTimeoutException('Request timeout'));
        }
        return throwError(() => err);
      }),
    );
  }
}
```

### 5. 异常处理拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, HttpException, HttpStatus } from '@nestjs/common';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class ExceptionInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      catchError(error => {
        if (error instanceof HttpException) {
          return throwError(() => error);
        }

        const status = error.status || HttpStatus.INTERNAL_SERVER_ERROR;
        const message = error.message || 'Internal server error';

        return throwError(() => new HttpException(
          {
            statusCode: status,
            message,
            timestamp: new Date().toISOString(),
          },
          status,
        ));
      }),
    );
  }
}
```

### 6. 性能监控拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

interface PerformanceData {
  handler: string;
  method: string;
  url: string;
  duration: number;
  timestamp: string;
}

@Injectable()
export class PerformanceInterceptor implements NestInterceptor {
  private readonly logger = new Logger(PerformanceInterceptor.name);
  private readonly performanceData: PerformanceData[] = [];

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const now = Date.now();
    const request = context.switchToHttp().getRequest();
    const handler = context.getHandler().name;

    return next.handle().pipe(
      tap(() => {
        const duration = Date.now() - now;
        const data: PerformanceData = {
          handler,
          method: request.method,
          url: request.url,
          duration,
          timestamp: new Date().toISOString(),
        };

        this.performanceData.push(data);
        this.logger.log(`Performance: ${handler} took ${duration}ms`);

        if (duration > 1000) {
          this.logger.warn(`Slow request detected: ${handler} took ${duration}ms`);
        }
      }),
    );
  }

  getPerformanceData(): PerformanceData[] {
    return this.performanceData;
  }
}
```

### 7. 数据脱敏拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class DataMaskingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(DataMaskingInterceptor.name);
  private readonly sensitiveFields = ['password', 'token', 'creditCard', 'ssn'];

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map(data => this.maskSensitiveData(data)),
    );
  }

  private maskSensitiveData(data: any): any {
    if (!data || typeof data !== 'object') {
      return data;
    }

    if (Array.isArray(data)) {
      return data.map(item => this.maskSensitiveData(item));
    }

    const masked: any = {};
    for (const key in data) {
      if (this.sensitiveFields.some(field => key.toLowerCase().includes(field))) {
        masked[key] = this.maskValue(data[key]);
      } else if (typeof data[key] === 'object' && data[key] !== null) {
        masked[key] = this.maskSensitiveData(data[key]);
      } else {
        masked[key] = data[key];
      }
    }

    return masked;
  }

  private maskValue(value: any): string {
    if (typeof value !== 'string') {
      return '***';
    }
    if (value.length <= 4) {
      return '***';
    }
    return value.substring(0, 2) + '***' + value.substring(value.length - 2);
  }
}
```

### 8. 审计日志拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

interface AuditLog {
  userId?: string;
  action: string;
  resource: string;
  method: string;
  url: string;
  statusCode: number;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
}

@Injectable()
export class AuditLogInterceptor implements NestInterceptor {
  private readonly logger = new Logger(AuditLogInterceptor.name);
  private readonly auditLogs: AuditLog[] = [];

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const response = context.switchToHttp().getResponse();
    const { method, url, ip, user } = request;
    const userAgent = request.get('user-agent') || '';

    return next.handle().pipe(
      tap(() => {
        const auditLog: AuditLog = {
          userId: user?.id,
          action: this.determineAction(method),
          resource: this.extractResource(url),
          method,
          url,
          statusCode: response.statusCode,
          timestamp: new Date().toISOString(),
          ipAddress: ip,
          userAgent,
        };

        this.auditLogs.push(auditLog);
        this.logger.log(`Audit: ${JSON.stringify(auditLog)}`);
      }),
    );
  }

  private determineAction(method: string): string {
    const actions: Record<string, string> = {
      GET: 'READ',
      POST: 'CREATE',
      PUT: 'UPDATE',
      PATCH: 'PARTIAL_UPDATE',
      DELETE: 'DELETE',
    };
    return actions[method] || 'UNKNOWN';
  }

  private extractResource(url: string): string {
    const parts = url.split('/').filter(part => part);
    return parts[0] || 'unknown';
  }

  getAuditLogs(): AuditLog[] {
    return this.auditLogs;
  }
}
```

### 9. 请求计数拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

interface RequestStats {
  total: number;
  successful: number;
  failed: number;
  byMethod: Record<string, number>;
  byPath: Record<string, number>;
}

@Injectable()
export class RequestCountInterceptor implements NestInterceptor {
  private readonly logger = new Logger(RequestCountInterceptor.name);
  private readonly stats: RequestStats = {
    total: 0,
    successful: 0,
    failed: 0,
    byMethod: {},
    byPath: {},
  };

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const { method, url } = request;

    this.stats.total++;
    this.stats.byMethod[method] = (this.stats.byMethod[method] || 0) + 1;
    this.stats.byPath[url] = (this.stats.byPath[url] || 0) + 1;

    return next.handle().pipe(
      tap({
        next: () => {
          this.stats.successful++;
        },
        error: () => {
          this.stats.failed++;
        },
      }),
    );
  }

  getStats(): RequestStats {
    return { ...this.stats };
  }

  resetStats(): void {
    this.stats.total = 0;
    this.stats.successful = 0;
    this.stats.failed = 0;
    this.stats.byMethod = {};
    this.stats.byPath = {};
  }
}
```

### 10. 重试拦截器

```typescript
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable, throwError, timer } from 'rxjs';
import { retryWhen, mergeMap, take } from 'rxjs/operators';

@Injectable()
export class RetryInterceptor implements NestInterceptor {
  private readonly logger = new Logger(RetryInterceptor.name);
  private readonly maxRetries = 3;
  private readonly retryDelay = 1000; // 1秒

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      retryWhen(errors =>
        errors.pipe(
          mergeMap((error, index) => {
            const retryAttempt = index + 1;
            if (retryAttempt > this.maxRetries) {
              this.logger.error(`Retry failed after ${this.maxRetries} attempts`);
              return throwError(() => error);
            }

            this.logger.warn(
              `Retry attempt ${retryAttempt}/${this.maxRetries}. Error: ${error.message}`
            );

            return timer(this.retryDelay * retryAttempt);
          }),
          take(this.maxRetries),
        ),
      ),
    );
  }
}
```

## 拦截器应用

### 全局应用拦截器

```typescript
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { TransformInterceptor } from './interceptors/transform.interceptor';
import { LoggingInterceptor } from './interceptors/logging.interceptor';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: TransformInterceptor,
    },
    {
      provide: APP_INTERCEPTOR,
      useClass: LoggingInterceptor,
    },
  ],
})
export class AppModule {}
```

### 在控制器上应用拦截器

```typescript
import { Controller, UseInterceptors } from '@nestjs/common';
import { TransformInterceptor } from '../interceptors/transform.interceptor';
import { LoggingInterceptor } from '../interceptors/logging.interceptor';

@Controller('users')
@UseInterceptors(TransformInterceptor, LoggingInterceptor)
export class UsersController {
  // 控制器方法
}
```

### 在方法上应用拦截器

```typescript
import { Controller, Get, UseInterceptors } from '@nestjs/common';
import { CacheInterceptor } from '../interceptors/cache.interceptor';

@Controller('users')
export class UsersController {
  @Get()
  @UseInterceptors(CacheInterceptor)
  findAll() {
    // 方法实现
  }
}
```

### 使用自定义提供者

```typescript
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { CacheInterceptor } from './interceptors/cache.interceptor';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useFactory: () => new CacheInterceptor(60000), // 60秒缓存
    },
  ],
})
export class AppModule {}
```

## 拦截器装饰器

### 自定义缓存装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const CACHE_TTL_KEY = 'cacheTTL';

export const Cache = (ttl: number) => SetMetadata(CACHE_TTL_KEY, ttl);
```

### 使用自定义装饰器

```typescript
import { Controller, Get } from '@nestjs/common';
import { Cache } from '../decorators/cache.decorator';

@Controller('users')
export class UsersController {
  @Get()
  @Cache(60000) // 缓存60秒
  findAll() {
    // 方法实现
  }
}
```

## 拦截器最佳实践

1. **单一职责**: 每个拦截器只负责一个功能
2. **性能考虑**: 避免在拦截器中执行耗时操作
3. **错误处理**: 适当处理和传播错误
4. **类型安全**: 使用泛型确保类型安全
5. **日志记录**: 记录重要操作和性能指标
6. **配置灵活**: 通过构造函数或装饰器配置拦截器
7. **测试覆盖**: 为拦截器编写单元测试
8. **文档说明**: 为复杂拦截器添加注释和文档

## 拦截器执行顺序

拦截器按照应用顺序执行：

```typescript
@UseInterceptors(Interceptor1, Interceptor2, Interceptor3)
findAll() {
  // 方法实现
}
```

执行顺序:
- 请求: Interceptor1 → Interceptor2 → Interceptor3 → 方法
- 响应: 方法 → Interceptor3 → Interceptor2 → Interceptor1
