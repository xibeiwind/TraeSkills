# NestJS 错误处理指南

本文档介绍 NestJS 应用程序中的错误处理最佳实践，包括全局异常过滤器、自定义错误类和错误日志记录方案。

## 目录

1. [全局异常过滤器](#全局异常过滤器)
2. [自定义错误类](#自定义错误类)
3. [错误日志记录](#错误日志记录)
4. [错误响应格式](#错误响应格式)
5. [错误处理中间件](#错误处理中间件)
6. [错误监控和告警](#错误监控和告警)

---

## 全局异常过滤器

### 1. 基础全局异常过滤器

创建全局异常过滤器来统一处理所有异常：

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    const message =
      exception instanceof HttpException
        ? exception.message
        : 'Internal server error';

    const errorResponse = {
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
      message,
    };

    this.logger.error(
      `${request.method} ${request.url}`,
      exception instanceof Error ? exception.stack : '',
    );

    response.status(status).json(errorResponse);
  }
}
```

### 2. 在应用中注册全局过滤器

```typescript
import { Module } from '@nestjs/common';
import { APP_FILTER } from '@nestjs/core';
import { AllExceptionsFilter } from './filters/all-exceptions.filter';

@Module({
  providers: [
    {
      provide: APP_FILTER,
      useClass: AllExceptionsFilter,
    },
  ],
})
export class AppModule {}
```

### 3. 高级全局异常过滤器

支持更多功能的异常过滤器：

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { QueryFailedError } from 'typeorm';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Internal server error';
    let errors: any[] = [];

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();
      
      if (typeof exceptionResponse === 'string') {
        message = exceptionResponse;
      } else if (typeof exceptionResponse === 'object') {
        const responseObj = exceptionResponse as any;
        message = responseObj.message || message;
        errors = responseObj.errors || [];
      }
    } else if (exception instanceof QueryFailedError) {
      status = HttpStatus.BAD_REQUEST;
      message = 'Database query failed';
      errors = [
        {
          field: 'database',
          message: exception.message,
        },
      ];
    } else if (exception instanceof Error) {
      message = exception.message;
    }

    const errorResponse = {
      success: false,
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
      message,
      errors: errors.length > 0 ? errors : undefined,
      correlationId: request.headers['x-correlation-id'] || this.generateCorrelationId(),
    };

    this.logError(request, exception, errorResponse);

    response.status(status).json(errorResponse);
  }

  private logError(request: Request, exception: unknown, errorResponse: any) {
    const { method, url, ip } = request;
    const { statusCode, message, correlationId } = errorResponse;

    this.logger.error(
      `${method} ${url} - ${statusCode} - ${message}`,
      exception instanceof Error ? exception.stack : '',
    );

    if (statusCode >= 500) {
      this.logger.error(
        `Correlation ID: ${correlationId}`,
        exception instanceof Error ? exception.stack : '',
      );
    }
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

---

## 自定义错误类

### 1. 基础自定义错误类

创建自定义错误类来处理特定业务场景：

```typescript
import { HttpException, HttpStatus } from '@nestjs/common';

export class BusinessException extends HttpException {
  constructor(
    message: string,
    statusCode: HttpStatus = HttpStatus.BAD_REQUEST,
    errors?: any[],
  ) {
    super(
      {
        success: false,
        statusCode,
        message,
        errors,
        timestamp: new Date().toISOString(),
      },
      statusCode,
    );
  }
}

export class NotFoundException extends BusinessException {
  constructor(resource: string = 'Resource') {
    super(`${resource} not found`, HttpStatus.NOT_FOUND);
  }
}

export class UnauthorizedException extends BusinessException {
  constructor(message: string = 'Unauthorized access') {
    super(message, HttpStatus.UNAUTHORIZED);
  }
}

export class ForbiddenException extends BusinessException {
  constructor(message: string = 'Access forbidden') {
    super(message, HttpStatus.FORBIDDEN);
  }
}

export class ValidationException extends BusinessException {
  constructor(errors: any[]) {
    super('Validation failed', HttpStatus.BAD_REQUEST, errors);
  }
}

export class ConflictException extends BusinessException {
  constructor(message: string = 'Resource conflict') {
    super(message, HttpStatus.CONFLICT);
  }
}

export class RateLimitException extends BusinessException {
  constructor(message: string = 'Rate limit exceeded') {
    super(message, HttpStatus.TOO_MANY_REQUESTS);
  }
}
```

### 2. 使用自定义错误类

在服务中使用自定义错误类：

```typescript
import { Injectable } from '@nestjs/common';
import { NotFoundException, ConflictException, ValidationException } from './exceptions';

@Injectable()
export class UserService {
  async getUserById(id: string) {
    const user = await this.findUserById(id);
    
    if (!user) {
      throw new NotFoundException('User');
    }
    
    return user;
  }

  async createUser(userData: any) {
    const existingUser = await this.findUserByEmail(userData.email);
    
    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }

    const validationErrors = this.validateUserData(userData);
    if (validationErrors.length > 0) {
      throw new ValidationException(validationErrors);
    }

    return this.saveUser(userData);
  }

  private validateUserData(userData: any): any[] {
    const errors: any[] = [];
    
    if (!userData.email || !this.isValidEmail(userData.email)) {
      errors.push({
        field: 'email',
        message: 'Invalid email format',
      });
    }
    
    if (!userData.password || userData.password.length < 8) {
      errors.push({
        field: 'password',
        message: 'Password must be at least 8 characters',
      });
    }
    
    return errors;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
```

### 3. 领域特定错误类

为特定领域创建错误类：

```typescript
import { HttpException, HttpStatus } from '@nestjs/common';

export class PaymentException extends HttpException {
  constructor(
    message: string,
    code: string,
    details?: any,
  ) {
    super(
      {
        success: false,
        statusCode: HttpStatus.BAD_REQUEST,
        message,
        code,
        details,
        timestamp: new Date().toISOString(),
      },
      HttpStatus.BAD_REQUEST,
    );
  }
}

export class PaymentFailedException extends PaymentException {
  constructor(details?: any) {
    super('Payment processing failed', 'PAYMENT_FAILED', details);
  }
}

export class InsufficientFundsException extends PaymentException {
  constructor(details?: any) {
    super('Insufficient funds', 'INSUFFICIENT_FUNDS', details);
  }
}

export class PaymentTimeoutException extends PaymentException {
  constructor(details?: any) {
    super('Payment processing timeout', 'PAYMENT_TIMEOUT', details);
  }
}

export class InvalidPaymentMethodException extends PaymentException {
  constructor(details?: any) {
    super('Invalid payment method', 'INVALID_PAYMENT_METHOD', details);
  }
}
```

### 4. 错误代码枚举

定义统一的错误代码：

```typescript
export enum ErrorCode {
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  CONFLICT = 'CONFLICT',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  PAYMENT_FAILED = 'PAYMENT_FAILED',
  INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS',
  PAYMENT_TIMEOUT = 'PAYMENT_TIMEOUT',
  INVALID_PAYMENT_METHOD = 'INVALID_PAYMENT_METHOD',
}

export class AppError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public statusCode: number = 500,
    public details?: any,
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      code: this.code,
      message: this.message,
      statusCode: this.statusCode,
      details: this.details,
      timestamp: new Date().toISOString(),
    };
  }
}
```

---

## 错误日志记录

### 1. 使用 NestJS Logger

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { AppError } from './errors';

@Injectable()
export class ErrorLoggingService {
  private readonly logger = new Logger(ErrorLoggingService.name);

  logError(error: Error | AppError, context?: string) {
    if (error instanceof AppError) {
      this.logger.error(
        `[${error.code}] ${error.message}`,
        error.stack,
        context,
      );
      
      if (error.details) {
        this.logger.debug(`Error details: ${JSON.stringify(error.details)}`, context);
      }
    } else {
      this.logger.error(
        error.message,
        error.stack,
        context,
      );
    }
  }

  logWarning(message: string, context?: string) {
    this.logger.warn(message, context);
  }

  logInfo(message: string, context?: string) {
    this.logger.log(message, context);
  }
}
```

### 2. 使用 Winston 日志库

#### 安装依赖

```bash
npm install winston nest-winston
npm install -D @types/winston
```

#### 配置 Winston

```typescript
import { Module } from '@nestjs/common';
import { WinstonModule } from 'nest-winston';
import * as winston from 'winston';
import 'winston-daily-rotate-file';

@Module({
  imports: [
    WinstonModule.forRoot({
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.colorize(),
            winston.format.printf(({ timestamp, level, message, context, trace }) => {
              return `${timestamp} [${context || 'Application'}] ${level}: ${message}${trace ? '\n' + trace : ''}`;
            }),
          ),
        }),
        new winston.transports.DailyRotateFile({
          filename: 'logs/application-%DATE%.log',
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '14d',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json(),
          ),
        }),
        new winston.transports.DailyRotateFile({
          level: 'error',
          filename: 'logs/error-%DATE%.log',
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json(),
          ),
        }),
      ],
    }),
  ],
})
export class AppModule {}
```

### 3. 结构化错误日志

创建结构化日志服务：

```typescript
import { Injectable, Logger, Scope } from '@nestjs/common';
import { Request } from 'express';

@Injectable({ scope: Scope.TRANSIENT })
export class StructuredLogger {
  private logger: Logger;

  constructor() {
    this.logger = new Logger();
  }

  setContext(context: string) {
    this.logger.setContext(context);
  }

  logInfo(message: string, meta?: any) {
    this.logger.log({
      message,
      level: 'info',
      timestamp: new Date().toISOString(),
      ...meta,
    });
  }

  logError(message: string, error?: Error, meta?: any) {
    this.logger.error({
      message,
      level: 'error',
      timestamp: new Date().toISOString(),
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : undefined,
      ...meta,
    });
  }

  logWarning(message: string, meta?: any) {
    this.logger.warn({
      message,
      level: 'warning',
      timestamp: new Date().toISOString(),
      ...meta,
    });
  }

  logDebug(message: string, meta?: any) {
    this.logger.debug({
      message,
      level: 'debug',
      timestamp: new Date().toISOString(),
      ...meta,
    });
  }

  logRequest(request: Request, responseTime?: number) {
    this.logInfo('HTTP Request', {
      method: request.method,
      url: request.url,
      ip: request.ip,
      userAgent: request.headers['user-agent'],
      responseTime,
    });
  }

  logErrorWithContext(error: Error, request: Request) {
    this.logError('Request Error', error, {
      method: request.method,
      url: request.url,
      ip: request.ip,
      userAgent: request.headers['user-agent'],
      body: request.body,
      query: request.query,
      params: request.params,
    });
  }
}
```

### 4. 错误日志存储到数据库

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ErrorLog } from './entities/error-log.entity';

@Injectable()
export class ErrorLogService {
  constructor(
    @InjectRepository(ErrorLog)
    private errorLogRepository: Repository<ErrorLog>,
  ) {}

  async logError(error: Error, context?: string, metadata?: any) {
    const errorLog = this.errorLogRepository.create({
      message: error.message,
      stack: error.stack,
      name: error.name,
      context,
      metadata,
      timestamp: new Date(),
    });

    return this.errorLogRepository.save(errorLog);
  }

  async getRecentErrors(limit: number = 100) {
    return this.errorLogRepository.find({
      order: { timestamp: 'DESC' },
      take: limit,
    });
  }

  async getErrorStats() {
    return this.errorLogRepository
      .createQueryBuilder('errorLog')
      .select('errorLog.name', 'errorName')
      .addSelect('COUNT(*)', 'count')
      .groupBy('errorLog.name')
      .orderBy('count', 'DESC')
      .getRawMany();
  }
}
```

---

## 错误响应格式

### 1. 统一错误响应格式

定义统一的错误响应格式：

```typescript
export interface ErrorResponse {
  success: false;
  statusCode: number;
  message: string;
  errors?: ValidationError[];
  code?: string;
  timestamp: string;
  path?: string;
  method?: string;
  correlationId?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface SuccessResponse<T = any> {
  success: true;
  data: T;
  message?: string;
  timestamp: string;
}
```

### 2. 响应拦截器

创建响应拦截器来统一响应格式：

```typescript
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class ResponseInterceptor<T>
  implements NestInterceptor<T, SuccessResponse<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<SuccessResponse<T>> {
    return next.handle().pipe(
      map((data) => ({
        success: true,
        data,
        timestamp: new Date().toISOString(),
      })),
    );
  }
}
```

### 3. 注册响应拦截器

```typescript
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { ResponseInterceptor } from './interceptors/response.interceptor';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: ResponseInterceptor,
    },
  ],
})
export class AppModule {}
```

---

## 错误处理中间件

### 1. 请求 ID 中间件

为每个请求生成唯一 ID 用于追踪：

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class RequestIdMiddleware implements NestMiddleware {
  private readonly logger = new Logger(RequestIdMiddleware.name);

  use(req: Request, res: Response, next: NextFunction) {
    const requestId = req.headers['x-request-id'] as string || uuidv4();
    req['requestId'] = requestId;
    res.setHeader('x-request-id', requestId);

    this.logger.debug(`Request ID: ${requestId}`);

    next();
  }
}
```

### 2. 错误追踪中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class ErrorTrackingMiddleware implements NestMiddleware {
  private readonly logger = new Logger(ErrorTrackingMiddleware.name);

  use(req: Request, res: Response, next: NextFunction) {
    const startTime = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - startTime;
      const { method, url, ip } = req;
      const { statusCode } = res;

      if (statusCode >= 400) {
        this.logger.warn(
          `${method} ${url} - ${statusCode} - ${duration}ms - ${ip}`,
        );
      }
    });

    next();
  }
}
```

### 3. 注册中间件

```typescript
import { Module, MiddlewareConsumer, NestModule } from '@nestjs/common';
import { RequestIdMiddleware } from './middlewares/request-id.middleware';
import { ErrorTrackingMiddleware } from './middlewares/error-tracking.middleware';

@Module({})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(RequestIdMiddleware, ErrorTrackingMiddleware)
      .forRoutes('*');
  }
}
```

---

## 错误监控和告警

### 1. Sentry 集成

#### 安装依赖

```bash
npm install @sentry/node
```

#### 配置 Sentry

```typescript
import * as Sentry from '@sentry/node';

export function initSentry() {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1.0,
    beforeSend(event, hint) {
      if (event.request) {
        event.request.headers = {
          'user-agent': event.request.headers['user-agent'],
        };
      }
      return event;
    },
  });
}
```

### 2. 在异常过滤器中使用 Sentry

```typescript
import { ExceptionFilter, Catch, ArgumentsHost } from '@nestjs/common';
import { Sentry } from '@sentry/node';
import { HttpExceptionFilter } from './http-exception.filter';

@Catch()
export class SentryExceptionFilter extends HttpExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    Sentry.captureException(exception);
    return super.catch(exception, host);
  }
}
```

### 3. 自定义告警服务

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { AppError } from './errors';

@Injectable()
export class AlertService {
  private readonly logger = new Logger(AlertService.name);

  async sendAlert(error: AppError) {
    if (error.statusCode >= 500) {
      await this.sendCriticalAlert(error);
    } else if (error.statusCode >= 400) {
      await this.sendWarningAlert(error);
    }
  }

  private async sendCriticalAlert(error: AppError) {
    this.logger.error(`CRITICAL ALERT: ${error.code} - ${error.message}`);
    
    await this.sendSlackAlert({
      color: 'danger',
      title: 'Critical Error',
      text: error.message,
      fields: [
        { title: 'Code', value: error.code },
        { title: 'Status', value: error.statusCode.toString() },
      ],
    });

    await this.sendEmailAlert({
      subject: `Critical Error: ${error.code}`,
      body: error.message,
    });
  }

  private async sendWarningAlert(error: AppError) {
    this.logger.warn(`WARNING ALERT: ${error.code} - ${error.message}`);
    
    await this.sendSlackAlert({
      color: 'warning',
      title: 'Warning',
      text: error.message,
      fields: [
        { title: 'Code', value: error.code },
        { title: 'Status', value: error.statusCode.toString() },
      ],
    });
  }

  private async sendSlackAlert(payload: any) {
    const webhookUrl = process.env.SLACK_WEBHOOK_URL;
    
    try {
      await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (error) {
      this.logger.error('Failed to send Slack alert', error);
    }
  }

  private async sendEmailAlert(payload: any) {
    const emailService = process.env.EMAIL_SERVICE_URL;
    
    try {
      await fetch(emailService, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (error) {
      this.logger.error('Failed to send email alert', error);
    }
  }
}
```

---

## 最佳实践总结

1. **全局异常处理**
   - 使用全局异常过滤器统一处理所有异常
   - 提供清晰的错误信息和状态码
   - 记录详细的错误日志

2. **自定义错误类**
   - 为不同的业务场景创建专用错误类
   - 使用错误代码枚举统一错误标识
   - 提供详细的错误信息和建议

3. **错误日志记录**
   - 使用结构化日志记录错误
   - 区分不同级别的日志
   - 保存错误日志到数据库以便分析

4. **错误响应格式**
   - 统一错误响应格式
   - 包含必要的调试信息
   - 避免泄露敏感信息

5. **错误监控**
   - 集成第三方监控工具（如 Sentry）
   - 设置告警机制
   - 定期分析错误日志

6. **错误追踪**
   - 为每个请求生成唯一 ID
   - 记录完整的请求上下文
   - 便于问题排查和调试

通过以上错误处理技巧，可以构建一个健壮、可维护的 NestJS 应用程序，提供良好的用户体验和便于问题排查的能力。