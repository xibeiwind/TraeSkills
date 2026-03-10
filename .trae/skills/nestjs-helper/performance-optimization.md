# NestJS 性能优化指南

本文档介绍 NestJS 应用程序的性能优化技巧和最佳实践。

## 目录

1. [缓存策略](#缓存策略)
2. [数据库查询优化](#数据库查询优化)
3. [异步处理](#异步处理)
4. [连接池管理](#连接池管理)
5. [响应压缩](#响应压缩)
6. [懒加载模块](#懒加载模块)

---

## 缓存策略

### 1. 使用 NestJS 内置缓存模块

NestJS 提供了强大的缓存模块，可以轻松集成到应用程序中。

#### 安装依赖

```bash
npm install @nestjs/cache-manager cache-manager
npm install @nestjs/platform-socket.io
```

#### 配置缓存模块

```typescript
import { Module, CacheModule } from '@nestjs/common';
import * as redisStore from 'cache-manager-redis-store';

@Module({
  imports: [
    CacheModule.register({
      store: redisStore,
      host: 'localhost',
      port: 6379,
      ttl: 60,
      max: 100,
    }),
  ],
  providers: [AppService],
  controllers: [AppController],
})
export class AppModule {}
```

#### 在服务中使用缓存

```typescript
import { Injectable, Inject } from '@nestjs/common';
import { CACHE_MANAGER } from '@nestjs/common';
import { Cache } from 'cache-manager';

@Injectable()
export class UserService {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async getUser(id: string) {
    const cacheKey = `user_${id}`;
    
    const cachedUser = await this.cacheManager.get(cacheKey);
    if (cachedUser) {
      return cachedUser;
    }

    const user = await this.findUserById(id);
    await this.cacheManager.set(cacheKey, user, { ttl: 3600 });
    
    return user;
  }

  async updateUser(id: string, userData: any) {
    const user = await this.findUserById(id);
    const updatedUser = await this.saveUser(user, userData);
    
    const cacheKey = `user_${id}`;
    await this.cacheManager.del(cacheKey);
    
    return updatedUser;
  }
}
```

### 2. 使用装饰器缓存

创建自定义缓存装饰器：

```typescript
import { Cache } from 'cache-manager';
import { CACHE_MANAGER, Inject, Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

export function Cacheable(ttl: number = 300) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const cacheManager: Cache = this.cacheManager;
      const cacheKey = `${target.constructor.name}_${propertyKey}_${JSON.stringify(args)}`;

      const cachedResult = await cacheManager.get(cacheKey);
      if (cachedResult) {
        return cachedResult;
      }

      const result = await originalMethod.apply(this, args);
      await cacheManager.set(cacheKey, result, { ttl });
      
      return result;
    };

    return descriptor;
  };
}

@Injectable()
export class ProductService {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  @Cacheable(600)
  async getProduct(id: string) {
    return this.findProductById(id);
  }
}
```

### 3. Redis 缓存集群配置

```typescript
import { Module } from '@nestjs/common';
import { CacheModule } from '@nestjs/cache-manager';
import { redisStore } from 'cache-manager-redis-store';

@Module({
  imports: [
    CacheModule.register({
      store: redisStore,
      host: 'localhost',
      port: 6379,
      password: 'your_password',
      db: 0,
      ttl: 300,
      max: 10000,
      isCacheableValue: (val) => val !== undefined && val !== null,
    }),
  ],
})
export class AppModule {}
```

---

## 数据库查询优化

### 1. 使用 TypeORM 查询优化

#### 选择性字段查询

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async getUserProfile(id: string) {
    return this.userRepository
      .createQueryBuilder('user')
      .select([
        'user.id',
        'user.name',
        'user.email',
        'user.createdAt',
      ])
      .where('user.id = :id', { id })
      .getOne();
  }

  async getUserWithPosts(id: string) {
    return this.userRepository
      .createQueryBuilder('user')
      .leftJoinAndSelect('user.posts', 'posts')
      .where('user.id = :id', { id })
      .orderBy('posts.createdAt', 'DESC')
      .getOne();
  }
}
```

#### 批量查询优化

```typescript
async getUsersByIds(ids: string[]) {
  return this.userRepository
    .createQueryBuilder('user')
    .where('user.id IN (:...ids)', { ids })
    .getMany();
}

async getUserCountByStatus(status: string) {
  return this.userRepository
    .createQueryBuilder('user')
    .select('COUNT(user.id)', 'count')
    .where('user.status = :status', { status })
    .getRawOne();
}
```

### 2. 使用 Mongoose 查询优化

```typescript
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { User, UserDocument } from './schemas/user.schema';

@Injectable()
export class UserService {
  constructor(@InjectModel(User.name) private userModel: Model<UserDocument>) {}

  async getUserById(id: string) {
    return this.userModel
      .findById(id)
      .select('name email createdAt')
      .lean()
      .exec();
  }

  async getUsersWithPagination(page: number, limit: number) {
    const skip = (page - 1) * limit;
    
    const [users, total] = await Promise.all([
      this.userModel
        .find()
        .select('-password')
        .skip(skip)
        .limit(limit)
        .lean()
        .exec(),
      this.userModel.countDocuments().exec(),
    ]);

    return {
      data: users,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async getUserStats() {
    return this.userModel
      .aggregate([
        {
          $group: {
            _id: '$status',
            count: { $sum: 1 },
          },
        },
      ])
      .exec();
  }
}
```

### 3. 数据库连接池配置

```typescript
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'myapp',
      entities: [__dirname + '/**/*.entity{.ts,.js}'],
      synchronize: false,
      logging: false,
      poolSize: 10,
      extra: {
        max: 20,
        min: 5,
        idleTimeoutMillis: 30000,
      },
    }),
  ],
})
export class AppModule {}
```

---

## 异步处理

### 1. 使用队列处理耗时任务

#### 安装 Bull 队列

```bash
npm install @nestjs/bull bull
npm install -D @types/bull
```

#### 配置队列模块

```typescript
import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bull';
import { EmailProcessor } from './email.processor';

@Module({
  imports: [
    BullModule.forRoot({
      redis: {
        host: 'localhost',
        port: 6379,
      },
    }),
    BullModule.registerQueue({
      name: 'email',
      defaultJobOptions: {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 2000,
        },
      },
    }),
  ],
  providers: [EmailProcessor],
})
export class AppModule {}
```

#### 创建队列处理器

```typescript
import { Processor, Process, OnQueueActive, OnQueueCompleted, OnQueueFailed } from '@nestjs/bull';
import { Job } from 'bull';
import { Logger } from '@nestjs/common';

@Processor('email')
export class EmailProcessor {
  private readonly logger = new Logger(EmailProcessor.name);

  @Process('send')
  async handleSendEmail(job: Job) {
    this.logger.log(`Processing email job ${job.id}`);
    
    const { to, subject, content } = job.data;
    
    await this.sendEmail(to, subject, content);
    
    return { success: true };
  }

  @OnQueueActive()
  onActive(job: Job) {
    this.logger.debug(`Processing job ${job.id} of type ${job.name}`);
  }

  @OnQueueCompleted()
  onCompleted(job: Job, result: any) {
    this.logger.debug(`Completed job ${job.id} with result: ${JSON.stringify(result)}`);
  }

  @OnQueueFailed()
  onFailed(job: Job, error: Error) {
    this.logger.error(`Failed job ${job.id}: ${error.message}`);
  }

  private async sendEmail(to: string, subject: string, content: string) {
    this.logger.log(`Sending email to ${to}`);
    await new Promise(resolve => setTimeout(resolve, 1000));
    this.logger.log(`Email sent to ${to}`);
  }
}
```

#### 在服务中使用队列

```typescript
import { Injectable, Inject } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bull';
import { Queue } from 'bull';

@Injectable()
export class UserService {
  constructor(@InjectQueue('email') private emailQueue: Queue) {}

  async registerUser(userData: any) {
    const user = await this.createUser(userData);
    
    await this.emailQueue.add('send', {
      to: user.email,
      subject: 'Welcome to our platform',
      content: 'Thank you for registering!',
    });

    return user;
  }
}
```

### 2. 使用 Promise.all 并行处理

```typescript
async getUserDashboard(userId: string) {
  const [user, posts, notifications, stats] = await Promise.all([
    this.getUserById(userId),
    this.getUserPosts(userId),
    this.getUserNotifications(userId),
    this.getUserStats(userId),
  ]);

  return {
    user,
    posts,
    notifications,
    stats,
  };
}
```

### 3. 使用 RxJS 处理流式数据

```typescript
import { Observable } from 'rxjs';
import { map, filter, debounceTime, distinctUntilChanged } from 'rxjs/operators';

async searchUsers(query: string): Observable<User[]> {
  return from(this.userRepository.find()).pipe(
    debounceTime(300),
    distinctUntilChanged(),
    map(users => 
      users.filter(user => 
        user.name.toLowerCase().includes(query.toLowerCase())
      )
    ),
  );
}
```

---

## 连接池管理

### 1. HTTP 连接池配置

```typescript
import { HttpModule } from '@nestjs/axios';

@Module({
  imports: [
    HttpModule.register({
      timeout: 5000,
      maxRedirects: 5,
      maxSockets: 100,
      maxFreeSockets: 10,
      keepAlive: true,
      keepAliveMsecs: 1000,
    }),
  ],
})
export class AppModule {}
```

### 2. 数据库连接池监控

```typescript
import { Injectable, OnModuleDestroy } from '@nestjs/common';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource } from 'typeorm';

@Injectable()
export class DatabaseMonitorService implements OnModuleDestroy {
  constructor(
    @InjectDataSource()
    private dataSource: DataSource,
  ) {}

  getConnectionStats() {
    const driver = this.dataSource.driver;
    return {
      connected: driver.isConnected,
      poolSize: driver.pool?.size || 0,
      poolMax: driver.pool?.max || 0,
      poolMin: driver.pool?.min || 0,
    };
  }

  onModuleDestroy() {
    this.dataSource.destroy();
  }
}
```

---

## 响应压缩

### 1. 启用 Gzip 压缩

```typescript
import { Module } from '@nestjs/common';
import { CompressionModule } from '@nestjs/compression';

@Module({
  imports: [
    CompressionModule.register({
      threshold: 1024,
      level: 6,
      memLevel: 8,
    }),
  ],
})
export class AppModule {}
```

### 2. 自定义压缩配置

```typescript
import { Module } from '@nestjs/common';
import { CompressionModule } from '@nestjs/compression';
import * as compression from 'compression';

@Module({
  imports: [
    CompressionModule.register({
      filter: (req, res) => {
        if (req.headers['x-no-compression']) {
          return false;
        }
        return compression.filter(req, res);
      },
      threshold: 1024,
      chunkSize: 16 * 1024,
      windowBits: 15,
      level: 6,
      memLevel: 8,
      strategy: compression.constants.Z_DEFAULT_STRATEGY,
    }),
  ],
})
export class AppModule {}
```

---

## 懒加载模块

### 1. 配置懒加载

```typescript
import { Module } from '@nestjs/common';
import { RouterModule, Routes } from 'nest-router';

const routes: Routes = [
  {
    path: '/users',
    module: import('./users/users.module'),
    children: [
      {
        path: '/profile',
        module: import('./users/profile/profile.module'),
      },
    ],
  },
];

@Module({
  imports: [
    RouterModule.forRoutes(routes),
  ],
})
export class AppModule {}
```

### 2. 动态模块加载

```typescript
import { Injectable, OnModuleInit } from '@nestjs/common';

@Injectable()
export class ModuleLoaderService implements OnModuleInit {
  async onModuleInit() {
    const module = await import('./dynamic/dynamic.module');
    const DynamicModule = module.DynamicModule;
    
    this.moduleRef.register(DynamicModule);
  }
}
```

---

## 性能监控

### 1. 使用 APM 工具

```typescript
import { Injectable } from '@nestjs/common';
import { InjectMetric } from '@willsoto/nestjs-prometheus';
import { Counter, Histogram, Gauge } from 'prom-client';

@Injectable()
export class MetricsService {
  constructor(
    @InjectMetric('http_requests_total')
    private httpRequestCounter: Counter<string>,
    
    @InjectMetric('http_request_duration_seconds')
    private httpRequestDuration: Histogram<string>,
    
    @InjectMetric('active_connections')
    private activeConnections: Gauge<string>,
  ) {}

  recordRequest(method: string, path: string, statusCode: number) {
    this.httpRequestCounter.inc({
      method,
      path,
      status_code: statusCode,
    });
  }

  recordRequestDuration(method: string, path: string, duration: number) {
    this.httpRequestDuration.observe(
      {
        method,
        path,
      },
      duration / 1000,
    );
  }

  setActiveConnections(count: number) {
    this.activeConnections.set(count);
  }
}
```

### 2. 性能分析中间件

```typescript
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class PerformanceMiddleware implements NestMiddleware {
  private readonly logger = new Logger(PerformanceMiddleware.name);

  use(req: Request, res: Response, next: NextFunction) {
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;
      const { method, url, ip } = req;
      const { statusCode } = res;

      this.logger.log(
        `${method} ${url} ${statusCode} ${duration}ms - ${ip}`,
      );

      if (duration > 1000) {
        this.logger.warn(
          `Slow request detected: ${method} ${url} took ${duration}ms`,
        );
      }
    });

    next();
  }
}
```

---

## 最佳实践总结

1. **缓存策略**
   - 使用 Redis 作为缓存存储
   - 为频繁访问的数据设置合理的 TTL
   - 实现缓存失效机制

2. **数据库优化**
   - 使用索引提高查询性能
   - 避免使用 SELECT *
   - 使用批量查询减少数据库往返

3. **异步处理**
   - 使用队列处理耗时任务
   - 利用 Promise.all 并行处理
   - 合理使用 RxJS 处理流式数据

4. **连接管理**
   - 配置合理的连接池大小
   - 监控连接池状态
   - 及时释放不再使用的连接

5. **响应优化**
   - 启用响应压缩
   - 使用懒加载模块
   - 实现分页查询

6. **监控和分析**
   - 使用 APM 工具监控性能
   - 记录关键指标
   - 定期分析慢查询

通过以上优化技巧，可以显著提高 NestJS 应用程序的性能和响应速度。