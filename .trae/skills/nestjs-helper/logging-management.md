# NestJS 日志管理指南

本文档介绍 NestJS 应用程序中的日志管理最佳实践，包括日志配置、日志级别管理和结构化日志方案。

## 目录

1. [日志基础配置](#日志基础配置)
2. [日志级别管理](#日志级别管理)
3. [结构化日志](#结构化日志)
4. [日志存储和归档](#日志存储和归档)
5. [日志监控和分析](#日志监控和分析)
6. [日志性能优化](#日志性能优化)

---

## 日志基础配置

### 1. 使用 NestJS 内置 Logger

NestJS 提供了内置的 Logger 类，可以直接使用：

```typescript
import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class UserService {
  private readonly logger = new Logger(UserService.name);

  async createUser(userData: any) {
    this.logger.log('Creating new user');
    
    try {
      const user = await this.saveUser(userData);
      this.logger.log(`User created successfully with ID: ${user.id}`);
      return user;
    } catch (error) {
      this.logger.error('Failed to create user', error.stack);
      throw error;
    }
  }

  async getUserById(id: string) {
    this.logger.debug(`Fetching user with ID: ${id}`);
    
    const user = await this.findUserById(id);
    
    if (!user) {
      this.logger.warn(`User not found with ID: ${id}`);
    }
    
    return user;
  }
}
```

### 2. 全局日志配置

在 main.ts 中配置全局日志：

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: ['error', 'warn', 'log', 'debug', 'verbose'],
  });

  app.useGlobalPipes(new ValidationPipe());

  const logger = new Logger('Bootstrap');
  logger.log('Application is starting...');
  
  await app.listen(3000);
  logger.log('Application is running on: http://localhost:3000');
}

bootstrap();
```

### 3. 自定义 Logger 服务

创建自定义的 Logger 服务：

```typescript
import { Injectable, LoggerService, Scope } from '@nestjs/common';

@Injectable({ scope: Scope.TRANSIENT })
export class CustomLogger implements LoggerService {
  private context?: string;

  setContext(context: string) {
    this.context = context;
  }

  log(message: any, context?: string) {
    this.printMessage(message, 'LOG', context);
  }

  error(message: any, trace?: string, context?: string) {
    this.printMessage(message, 'ERROR', context);
    if (trace) {
      this.printMessage(trace, 'ERROR', context);
    }
  }

  warn(message: any, context?: string) {
    this.printMessage(message, 'WARN', context);
  }

  debug(message: any, context?: string) {
    this.printMessage(message, 'DEBUG', context);
  }

  verbose(message: any, context?: string) {
    this.printMessage(message, 'VERBOSE', context);
  }

  private printMessage(message: any, level: string, context?: string) {
    const timestamp = new Date().toISOString();
    const ctx = context || this.context || 'Application';
    
    const colorMap: Record<string, string> = {
      LOG: '\x1b[32m',
      ERROR: '\x1b[31m',
      WARN: '\x1b[33m',
      DEBUG: '\x1b[36m',
      VERBOSE: '\x1b[35m',
    };
    
    const color = colorMap[level] || '\x1b[0m';
    const reset = '\x1b[0m';
    
    console.log(`${color}[${timestamp}] [${ctx}] [${level}]${reset} ${message}`);
  }
}
```

### 4. 使用自定义 Logger

```typescript
import { Module } from '@nestjs/common';
import { APP_LOGGER } from './constants';
import { CustomLogger } from './logger/custom-logger';

@Module({
  providers: [
    {
      provide: APP_LOGGER,
      useClass: CustomLogger,
    },
  ],
  exports: [APP_LOGGER],
})
export class LoggerModule {}
```

---

## 日志级别管理

### 1. 日志级别定义

NestJS 支持以下日志级别：

```typescript
enum LogLevel {
  ERROR = 0,
  WARN = 1,
  LOG = 2,
  DEBUG = 3,
  VERBOSE = 4,
}
```

### 2. 环境变量配置日志级别

```typescript
import { NestFactory } from '@nestjs/core';
import { Logger } from '@nestjs/common';
import { AppModule } from './app.module';

function getLogLevels(): string[] {
  const env = process.env.NODE_ENV || 'development';
  
  if (env === 'production') {
    return ['error', 'warn', 'log'];
  }
  
  if (env === 'test') {
    return ['error'];
  }
  
  return ['error', 'warn', 'log', 'debug', 'verbose'];
}

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: getLogLevels(),
  });

  await app.listen(3000);
}

bootstrap();
```

### 3. 动态日志级别控制

创建动态日志级别管理服务：

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class LogLevelService {
  private readonly logger = new Logger(LogLevelService.name);
  private currentLogLevel: number = 2;

  constructor(private configService: ConfigService) {
    this.initializeLogLevel();
  }

  private initializeLogLevel() {
    const level = this.configService.get<string>('LOG_LEVEL', 'LOG');
    this.currentLogLevel = this.getLevelValue(level);
    this.logger.log(`Log level initialized to: ${level}`);
  }

  private getLevelValue(level: string): number {
    const levels: Record<string, number> = {
      ERROR: 0,
      WARN: 1,
      LOG: 2,
      DEBUG: 3,
      VERBOSE: 4,
    };
    return levels[level.toUpperCase()] || 2;
  }

  setLogLevel(level: string) {
    this.currentLogLevel = this.getLevelValue(level);
    this.logger.log(`Log level changed to: ${level}`);
  }

  shouldLog(level: string): boolean {
    return this.getLevelValue(level) <= this.currentLogLevel;
  }

  getCurrentLogLevel(): string {
    const levels = ['ERROR', 'WARN', 'LOG', 'DEBUG', 'VERBOSE'];
    return levels[this.currentLogLevel];
  }
}
```

### 4. 条件日志记录

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { LogLevelService } from './log-level.service';

@Injectable()
export class ConditionalLogger {
  private readonly logger = new Logger(ConditionalLogger.name);

  constructor(private logLevelService: LogLevelService) {}

  log(message: string) {
    if (this.logLevelService.shouldLog('LOG')) {
      this.logger.log(message);
    }
  }

  debug(message: string) {
    if (this.logLevelService.shouldLog('DEBUG')) {
      this.logger.debug(message);
    }
  }

  verbose(message: string) {
    if (this.logLevelService.shouldLog('VERBOSE')) {
      this.logger.verbose(message);
    }
  }

  warn(message: string) {
    if (this.logLevelService.shouldLog('WARN')) {
      this.logger.warn(message);
    }
  }

  error(message: string, trace?: string) {
    if (this.logLevelService.shouldLog('ERROR')) {
      this.logger.error(message, trace);
    }
  }
}
```

---

## 结构化日志

### 1. 使用 Winston 结构化日志

#### 安装依赖

```bash
npm install winston nest-winston
npm install -D @types/winston
```

#### 配置 Winston 格式

```typescript
import { Module } from '@nestjs/common';
import { WinstonModule } from 'nest-winston';
import * as winston from 'winston';

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json(),
);

@Module({
  imports: [
    WinstonModule.forRoot({
      level: process.env.LOG_LEVEL || 'info',
      format: logFormat,
      defaultMeta: { service: 'nestjs-app' },
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.printf(({ timestamp, level, message, context, ...meta }) => {
              return `${timestamp} [${context || 'Application'}] ${level}: ${message} ${Object.keys(meta).length ? JSON.stringify(meta) : ''}`;
            }),
          ),
        }),
      ],
    }),
  ],
})
export class AppModule {}
```

### 2. 结构化日志格式

定义统一的结构化日志格式：

```typescript
export interface StructuredLogData {
  timestamp: string;
  level: string;
  message: string;
  context?: string;
  userId?: string;
  requestId?: string;
  action?: string;
  duration?: number;
  metadata?: Record<string, any>;
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
}

export class StructuredLogger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  private createLogData(
    level: string,
    message: string,
    metadata?: Record<string, any>,
  ): StructuredLogData {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: this.context,
      ...metadata,
    };
  }

  log(message: string, metadata?: Record<string, any>) {
    const logData = this.createLogData('info', message, metadata);
    console.log(JSON.stringify(logData));
  }

  error(message: string, error?: Error, metadata?: Record<string, any>) {
    const logData = this.createLogData('error', message, {
      ...metadata,
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : undefined,
    });
    console.error(JSON.stringify(logData));
  }

  warn(message: string, metadata?: Record<string, any>) {
    const logData = this.createLogData('warn', message, metadata);
    console.warn(JSON.stringify(logData));
  }

  debug(message: string, metadata?: Record<string, any>) {
    const logData = this.createLogData('debug', message, metadata);
    console.debug(JSON.stringify(logData));
  }
}
```

### 3. 请求日志记录器

创建专门用于记录请求的日志记录器：

```typescript
import { Injectable, Logger, Scope } from '@nestjs/common';
import { Request } from 'express';

@Injectable({ scope: Scope.TRANSIENT })
export class RequestLogger {
  private logger: Logger;

  constructor() {
    this.logger = new Logger();
  }

  setContext(context: string) {
    this.logger.setContext(context);
  }

  logRequest(request: Request) {
    const logData = {
      timestamp: new Date().toISOString(),
      type: 'request',
      method: request.method,
      url: request.url,
      ip: request.ip,
      userAgent: request.headers['user-agent'],
      requestId: request['requestId'],
      userId: request['userId'],
    };

    this.logger.log(JSON.stringify(logData));
  }

  logResponse(request: Request, statusCode: number, duration: number) {
    const logData = {
      timestamp: new Date().toISOString(),
      type: 'response',
      method: request.method,
      url: request.url,
      statusCode,
      duration,
      requestId: request['requestId'],
      userId: request['userId'],
    };

    this.logger.log(JSON.stringify(logData));
  }

  logError(request: Request, error: Error, statusCode: number) {
    const logData = {
      timestamp: new Date().toISOString(),
      type: 'error',
      method: request.method,
      url: request.url,
      statusCode,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      requestId: request['requestId'],
      userId: request['userId'],
    };

    this.logger.error(JSON.stringify(logData));
  }
}
```

### 4. 业务事件日志记录器

```typescript
import { Injectable, Logger } from '@nestjs/common';

export enum BusinessEventType {
  USER_CREATED = 'USER_CREATED',
  USER_UPDATED = 'USER_UPDATED',
  USER_DELETED = 'USER_DELETED',
  ORDER_CREATED = 'ORDER_CREATED',
  ORDER_CANCELLED = 'ORDER_CANCELLED',
  PAYMENT_RECEIVED = 'PAYMENT_RECEIVED',
  PAYMENT_FAILED = 'PAYMENT_FAILED',
}

export interface BusinessEventLog {
  timestamp: string;
  eventType: BusinessEventType;
  userId?: string;
  entityId?: string;
  entityType?: string;
  data?: Record<string, any>;
  metadata?: Record<string, any>;
}

@Injectable()
export class BusinessEventLogger {
  private readonly logger = new Logger(BusinessEventLogger.name);

  logEvent(event: BusinessEventLog) {
    const logData = {
      ...event,
      timestamp: event.timestamp || new Date().toISOString(),
    };

    this.logger.log(JSON.stringify(logData));
  }

  logUserCreated(userId: string, userData: any) {
    this.logEvent({
      eventType: BusinessEventType.USER_CREATED,
      userId,
      entityId: userId,
      entityType: 'User',
      data: {
        email: userData.email,
        name: userData.name,
      },
    });
  }

  logOrderCreated(userId: string, orderId: string, orderData: any) {
    this.logEvent({
      eventType: BusinessEventType.ORDER_CREATED,
      userId,
      entityId: orderId,
      entityType: 'Order',
      data: {
        totalAmount: orderData.totalAmount,
        items: orderData.items.length,
      },
    });
  }

  logPaymentReceived(userId: string, orderId: string, paymentData: any) {
    this.logEvent({
      eventType: BusinessEventType.PAYMENT_RECEIVED,
      userId,
      entityId: orderId,
      entityType: 'Order',
      data: {
        amount: paymentData.amount,
        paymentMethod: paymentData.paymentMethod,
      },
    });
  }
}
```

---

## 日志存储和归档

### 1. 文件日志存储

使用 Winston 的文件传输：

```typescript
import { Module } from '@nestjs/common';
import { WinstonModule } from 'nest-winston';
import * as winston from 'winston';
import 'winston-daily-rotate-file';

@Module({
  imports: [
    WinstonModule.forRoot({
      transports: [
        new winston.transports.DailyRotateFile({
          filename: 'logs/application-%DATE%.log',
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '14d',
          level: 'info',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json(),
          ),
        }),
        new winston.transports.DailyRotateFile({
          filename: 'logs/error-%DATE%.log',
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '30d',
          level: 'error',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json(),
          ),
        }),
        new winston.transports.DailyRotateFile({
          filename: 'logs/debug-%DATE%.log',
          datePattern: 'YYYY-MM-DD',
          zippedArchive: true,
          maxSize: '20m',
          maxFiles: '7d',
          level: 'debug',
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

### 2. 数据库日志存储

创建日志实体：

```typescript
import { Entity, PrimaryGeneratedColumn, Column, CreateIndex, Index } from 'typeorm';

@Entity('logs')
@Index(['level', 'createdAt'])
@Index(['context', 'createdAt'])
export class Log {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 20 })
  level: string;

  @Column({ type: 'text' })
  message: string;

  @Column({ type: 'varchar', length: 100, nullable: true })
  context: string;

  @Column({ type: 'json', nullable: true })
  metadata: Record<string, any>;

  @Column({ type: 'text', nullable: true })
  stack: string;

  @Column({ type: 'varchar', length: 100, nullable: true })
  requestId: string;

  @Column({ type: 'varchar', length: 100, nullable: true })
  userId: string;

  @Column({ type: 'timestamp' })
  createdAt: Date;
}
```

创建日志存储服务：

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Log } from './entities/log.entity';

@Injectable()
export class LogStorageService {
  constructor(
    @InjectRepository(Log)
    private logRepository: Repository<Log>,
  ) {}

  async saveLog(logData: Partial<Log>) {
    const log = this.logRepository.create({
      ...logData,
      createdAt: new Date(),
    });
    return this.logRepository.save(log);
  }

  async getLogsByLevel(level: string, limit: number = 100) {
    return this.logRepository.find({
      where: { level },
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }

  async getLogsByContext(context: string, limit: number = 100) {
    return this.logRepository.find({
      where: { context },
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }

  async getLogsByRequestId(requestId: string) {
    return this.logRepository.find({
      where: { requestId },
      order: { createdAt: 'ASC' },
    });
  }

  async getLogsByDateRange(startDate: Date, endDate: Date) {
    return this.logRepository
      .createQueryBuilder('log')
      .where('log.createdAt BETWEEN :startDate AND :endDate', {
        startDate,
        endDate,
      })
      .orderBy('log.createdAt', 'DESC')
      .getMany();
  }

  async getLogStats() {
    return this.logRepository
      .createQueryBuilder('log')
      .select('log.level', 'level')
      .addSelect('COUNT(*)', 'count')
      .groupBy('log.level')
      .getRawMany();
  }

  async deleteOldLogs(days: number = 30) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const result = await this.logRepository
      .createQueryBuilder()
      .delete()
      .where('createdAt < :cutoffDate', { cutoffDate })
      .execute();

    return result.affected;
  }
}
```

### 3. Elasticsearch 日志存储

```typescript
import { Injectable } from '@nestjs/common';
import { Client } from '@elastic/elasticsearch';

@Injectable()
export class ElasticsearchLogService {
  private readonly client: Client;

  constructor() {
    this.client = new Client({
      node: process.env.ELASTICSEARCH_URL || 'http://localhost:9200',
    });
  }

  async indexLog(logData: any) {
    const indexName = `logs-${new Date().toISOString().split('T')[0]}`;
    
    return this.client.index({
      index: indexName,
      body: {
        ...logData,
        '@timestamp': new Date().toISOString(),
      },
    });
  }

  async searchLogs(query: any, size: number = 100) {
    return this.client.search({
      index: 'logs-*',
      body: {
        query,
        size,
        sort: [
          { '@timestamp': { order: 'desc' } },
        ],
      },
    });
  }

  async getLogsByLevel(level: string, size: number = 100) {
    return this.searchLogs({
      term: { level },
    }, size);
  }

  async getLogsByContext(context: string, size: number = 100) {
    return this.searchLogs({
      term: { context },
    }, size);
  }

  async getLogsByDateRange(startDate: Date, endDate: Date, size: number = 100) {
    return this.searchLogs({
      range: {
        '@timestamp': {
          gte: startDate.toISOString(),
          lte: endDate.toISOString(),
        },
      },
    }, size);
  }
}
```

---

## 日志监控和分析

### 1. 日志统计服务

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Log } from './entities/log.entity';

export interface LogStats {
  totalLogs: number;
  logsByLevel: Record<string, number>;
  logsByContext: Record<string, number>;
  errorRate: number;
  averageLogsPerDay: number;
}

@Injectable()
export class LogStatsService {
  constructor(
    @InjectRepository(Log)
    private logRepository: Repository<Log>,
  ) {}

  async getStats(days: number = 7): Promise<LogStats> {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const logs = await this.logRepository
      .createQueryBuilder('log')
      .where('log.createdAt >= :startDate', { startDate })
      .getMany();

    const logsByLevel: Record<string, number> = {};
    const logsByContext: Record<string, number> = {};

    logs.forEach(log => {
      logsByLevel[log.level] = (logsByLevel[log.level] || 0) + 1;
      
      if (log.context) {
        logsByContext[log.context] = (logsByContext[log.context] || 0) + 1;
      }
    });

    const totalLogs = logs.length;
    const errorCount = logsByLevel['error'] || 0;
    const errorRate = totalLogs > 0 ? (errorCount / totalLogs) * 100 : 0;

    return {
      totalLogs,
      logsByLevel,
      logsByContext,
      errorRate,
      averageLogsPerDay: Math.round(totalLogs / days),
    };
  }

  async getErrorTrends(days: number = 30) {
    const trends: Array<{ date: string; count: number }> = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const startDate = new Date(date.setHours(0, 0, 0, 0));
      const endDate = new Date(date.setHours(23, 59, 59, 999));

      const count = await this.logRepository
        .createQueryBuilder('log')
        .where('log.level = :level', { level: 'error' })
        .andWhere('log.createdAt BETWEEN :startDate AND :endDate', {
          startDate,
          endDate,
        })
        .getCount();

      trends.push({
        date: startDate.toISOString().split('T')[0],
        count,
      });
    }

    return trends;
  }

  async getTopErrors(limit: number = 10) {
    return this.logRepository
      .createQueryBuilder('log')
      .select('log.message', 'message')
      .addSelect('COUNT(*)', 'count')
      .where('log.level = :level', { level: 'error' })
      .groupBy('log.message')
      .orderBy('count', 'DESC')
      .limit(limit)
      .getRawMany();
  }
}
```

### 2. 日志告警服务

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { LogStatsService } from './log-stats.service';

@Injectable()
export class LogAlertService {
  private readonly logger = new Logger(LogAlertService.name);
  private readonly errorRateThreshold = 5;
  private readonly errorCountThreshold = 100;

  constructor(private logStatsService: LogStatsService) {}

  @Cron(CronExpression.EVERY_HOUR)
  async checkErrorRate() {
    const stats = await this.logStatsService.getStats(1);

    if (stats.errorRate > this.errorRateThreshold) {
      this.logger.warn(
        `High error rate detected: ${stats.errorRate.toFixed(2)}%`,
      );
      await this.sendAlert({
        type: 'HIGH_ERROR_RATE',
        message: `Error rate is ${stats.errorRate.toFixed(2)}%`,
        threshold: this.errorRateThreshold,
        current: stats.errorRate,
      });
    }
  }

  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  async checkErrorCount() {
    const stats = await this.logStatsService.getStats(1);

    if (stats.logsByLevel['error'] > this.errorCountThreshold) {
      this.logger.warn(
        `High error count detected: ${stats.logsByLevel['error']} errors`,
      );
      await this.sendAlert({
        type: 'HIGH_ERROR_COUNT',
        message: `Error count is ${stats.logsByLevel['error']}`,
        threshold: this.errorCountThreshold,
        current: stats.logsByLevel['error'],
      });
    }
  }

  private async sendAlert(alertData: any) {
    this.logger.log(`Sending alert: ${JSON.stringify(alertData)}`);
    
    const webhookUrl = process.env.SLACK_WEBHOOK_URL;
    
    if (webhookUrl) {
      await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `Log Alert: ${alertData.type}`,
          attachments: [
            {
              color: 'danger',
              title: alertData.message,
              fields: [
                { title: 'Threshold', value: alertData.threshold.toString() },
                { title: 'Current', value: alertData.current.toString() },
              ],
            },
          ],
        }),
      });
    }
  }
}
```

### 3. 日志查询 API

```typescript
import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { LogStorageService } from './log-storage.service';

@Controller('logs')
@UseGuards(JwtAuthGuard)
export class LogsController {
  constructor(private logStorageService: LogStorageService) {}

  @Get()
  async getLogs(
    @Query('level') level?: string,
    @Query('context') context?: string,
    @Query('requestId') requestId?: string,
    @Query('limit') limit: number = 100,
  ) {
    if (level) {
      return this.logStorageService.getLogsByLevel(level, limit);
    }

    if (context) {
      return this.logStorageService.getLogsByContext(context, limit);
    }

    if (requestId) {
      return this.logStorageService.getLogsByRequestId(requestId);
    }

    return this.logStorageService.getRecentLogs(limit);
  }

  @Get('stats')
  async getStats(@Query('days') days: number = 7) {
    return this.logStorageService.getStats(days);
  }

  @Get('errors')
  async getErrors(@Query('limit') limit: number = 100) {
    return this.logStorageService.getLogsByLevel('error', limit);
  }
}
```

---

## 日志性能优化

### 1. 异步日志记录

使用异步方式记录日志以提高性能：

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { Queue } from 'bull';
import { InjectQueue } from '@nestjs/bull';

@Injectable()
export class AsyncLogger {
  private readonly logger = new Logger(AsyncLogger.name);

  constructor(@InjectQueue('logs') private logQueue: Queue) {}

  async log(message: string, metadata?: any) {
    await this.logQueue.add('log', {
      level: 'info',
      message,
      metadata,
    });
  }

  async error(message: string, error?: Error, metadata?: any) {
    await this.logQueue.add('log', {
      level: 'error',
      message,
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : undefined,
      metadata,
    });
  }

  async warn(message: string, metadata?: any) {
    await this.logQueue.add('log', {
      level: 'warn',
      message,
      metadata,
    });
  }

  async debug(message: string, metadata?: any) {
    await this.logQueue.add('log', {
      level: 'debug',
      message,
      metadata,
    });
  }
}
```

### 2. 日志批量写入

```typescript
import { Injectable, Logger, OnModuleDestroy } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Log } from './entities/log.entity';

@Injectable()
export class BatchLogService implements OnModuleDestroy {
  private readonly logger = new Logger(BatchLogService.name);
  private logBuffer: Partial<Log>[] = [];
  private readonly bufferSize = 100;
  private readonly flushInterval = 5000;
  private flushTimer?: NodeJS.Timeout;

  constructor(
    @InjectRepository(Log)
    private logRepository: Repository<Log>,
  ) {
    this.startFlushTimer();
  }

  addLog(logData: Partial<Log>) {
    this.logBuffer.push(logData);

    if (this.logBuffer.length >= this.bufferSize) {
      this.flushLogs();
    }
  }

  private async flushLogs() {
    if (this.logBuffer.length === 0) {
      return;
    }

    const logsToSave = [...this.logBuffer];
    this.logBuffer = [];

    try {
      await this.logRepository.save(logsToSave);
      this.logger.debug(`Flushed ${logsToSave.length} logs`);
    } catch (error) {
      this.logger.error('Failed to flush logs', error);
      this.logBuffer.unshift(...logsToSave);
    }
  }

  private startFlushTimer() {
    this.flushTimer = setInterval(() => {
      this.flushLogs();
    }, this.flushInterval);
  }

  async onModuleDestroy() {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    await this.flushLogs();
  }
}
```

### 3. 日志采样

在高负载情况下对日志进行采样：

```typescript
import { Injectable } from '@nestjs/common';

@Injectable()
export class LogSampler {
  private sampleRates: Record<string, number> = {
    debug: 0.1,
    info: 0.5,
    warn: 1.0,
    error: 1.0,
  };

  setSampleRate(level: string, rate: number) {
    this.sampleRates[level] = Math.max(0, Math.min(1, rate));
  }

  shouldSample(level: string): boolean {
    const rate = this.sampleRates[level] || 1.0;
    return Math.random() < rate;
  }

  getSampleRate(level: string): number {
    return this.sampleRates[level] || 1.0;
  }
}
```

---

## 最佳实践总结

1. **日志配置**
   - 根据环境配置不同的日志级别
   - 使用结构化日志格式
   - 避免在生产环境中记录敏感信息

2. **日志级别管理**
   - 合理设置日志级别
   - 使用环境变量动态控制日志级别
   - 实现条件日志记录

3. **结构化日志**
   - 使用 JSON 格式记录日志
   - 包含必要的上下文信息
   - 为不同类型的日志创建专用记录器

4. **日志存储**
   - 使用文件轮转避免日志文件过大
   - 考虑使用数据库或 Elasticsearch 存储日志
   - 定期清理旧日志

5. **日志监控**
   - 监控错误率和错误数量
   - 设置告警机制
   - 分析日志趋势

6. **性能优化**
   - 使用异步日志记录
   - 实现批量写入
   - 在高负载情况下使用日志采样

通过以上日志管理技巧，可以构建一个高效、可维护的日志系统，帮助开发者更好地监控和调试应用程序。