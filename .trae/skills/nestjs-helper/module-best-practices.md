# NestJS 模块组织最佳实践

本文档详细说明了 NestJS 中模块组织的最佳实践，包括按功能划分、共享模块、全局模块等内容。

## 模块基础概念

模块是 NestJS 应用程序的基本构建块，使用 `@Module()` 装饰器定义。每个模块封装了一组相关的功能。

### 模块装饰器选项

```typescript
@Module({
  imports: [],        // 导入其他模块
  controllers: [],    // 声明控制器
  providers: [],      // 声明服务提供者
  exports: [],        // 导出服务供其他模块使用
})
export class MyModule {}
```

## 按功能划分模块

### 原则

将应用程序按业务功能划分为独立的模块，每个模块负责特定的业务领域。

### 示例：用户模块

```typescript
// users.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { User } from './users.entity';
import { EmailModule } from '../email/email.module';

@Module({
  imports: [
    TypeOrmModule.forFeature([User]),
    EmailModule,
  ],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

### 模块目录结构

```
modules/
├── users/
│   ├── users.module.ts
│   ├── users.controller.ts
│   ├── users.service.ts
│   ├── users.entity.ts
│   ├── dto/
│   │   ├── create-user.dto.ts
│   │   ├── update-user.dto.ts
│   │   └── user-response.dto.ts
│   ├── interfaces/
│   │   └── user.interface.ts
│   └── tests/
│       └── users.service.spec.ts
├── products/
│   ├── products.module.ts
│   ├── products.controller.ts
│   ├── products.service.ts
│   ├── products.entity.ts
│   └── dto/
│       ├── create-product.dto.ts
│       └── update-product.dto.ts
└── orders/
    ├── orders.module.ts
    ├── orders.controller.ts
    ├── orders.service.ts
    ├── orders.entity.ts
    └── dto/
        ├── create-order.dto.ts
        └── update-order.dto.ts
```

### 模块间通信

模块之间通过依赖注入进行通信：

```typescript
// orders.service.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order } from './orders.entity';
import { UsersService } from '../users/users.service';

@Injectable()
export class OrdersService {
  constructor(
    @InjectRepository(Order)
    private readonly orderRepository: Repository<Order>,
    private readonly usersService: UsersService,
  ) {}

  async createOrder(userId: string, orderData: any) {
    const user = await this.usersService.findOne(userId);
    const order = this.orderRepository.create({
      ...orderData,
      user,
    });
    return this.orderRepository.save(order);
  }
}
```

## 共享模块

### 概念

共享模块是可以在多个模块中重用的模块。通过 `exports` 数组导出服务，其他模块可以导入并使用这些服务。

### 创建共享模块

```typescript
// logger.module.ts
import { Module, Global } from '@nestjs/common';
import { LoggerService } from './logger.service';

@Module({
  providers: [LoggerService],
  exports: [LoggerService],
})
export class LoggerModule {}
```

### 使用共享模块

```typescript
// users.module.ts
import { Module } from '@nestjs/common';
import { LoggerModule } from '../logger/logger.module';
import { UsersService } from './users.service';

@Module({
  imports: [LoggerModule],
  providers: [UsersService],
})
export class UsersModule {
  constructor(private readonly loggerService: LoggerService) {}
}
```

### 共享模块最佳实践

1. **单一职责**：每个共享模块只负责一个特定功能
2. **明确导出**：只导出需要被其他模块使用的服务
3. **配置灵活**：使用 `forRoot()` 和 `forRootAsync()` 提供配置选项

### 动态模块配置

```typescript
// database.module.ts
import { Module, DynamicModule } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Module({})
export class DatabaseModule {
  static forRoot(options: DatabaseOptions): DynamicModule {
    return {
      module: DatabaseModule,
      providers: [
        {
          provide: 'DATABASE_OPTIONS',
          useValue: options,
        },
        DatabaseService,
      ],
      exports: [DatabaseService],
      global: true,
    };
  }

  static forRootAsync(options: DatabaseAsyncOptions): DynamicModule {
    return {
      module: DatabaseModule,
      imports: options.imports || [],
      providers: [
        {
          provide: 'DATABASE_OPTIONS',
          useFactory: options.useFactory,
          inject: options.inject || [],
        },
        DatabaseService,
      ],
      exports: [DatabaseService],
      global: true,
    };
  }
}

// 使用
@Module({
  imports: [
    DatabaseModule.forRoot({
      host: 'localhost',
      port: 5432,
    }),
  ],
})
export class AppModule {}

// 或异步配置
@Module({
  imports: [
    DatabaseModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        host: configService.get('DATABASE_HOST'),
        port: configService.get('DATABASE_PORT'),
      }),
      inject: [ConfigService],
    }),
  ],
})
export class AppModule {}
```

## 全局模块

### 概念

全局模块在整个应用程序中可用，无需在每个模块中导入。使用 `@Global()` 装饰器标记。

### 创建全局模块

```typescript
// logger.module.ts
import { Module, Global } from '@nestjs/common';
import { LoggerService } from './logger.service';

@Global()
@Module({
  providers: [LoggerService],
  exports: [LoggerService],
})
export class LoggerModule {}
```

### 全局模块使用

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { LoggerModule } from './logger/logger.module';

@Module({
  imports: [LoggerModule],
})
export class AppModule {}

// users.service.ts
import { Injectable } from '@nestjs/common';
import { LoggerService } from '../logger/logger.service';

@Injectable()
export class UsersService {
  constructor(private readonly logger: LoggerService) {}

  async findAll() {
    this.logger.log('Fetching all users');
    return [];
  }
}
```

### 全局模块注意事项

1. **谨慎使用**：全局模块会增加隐式依赖，降低代码可维护性
2. **基础设施服务**：适合日志、配置、缓存等基础设施服务
3. **避免业务逻辑**：不要将业务逻辑模块设为全局

## 模块组织模式

### 1. 功能模块模式

按业务功能组织模块，每个模块包含完整的 CRUD 操作。

```typescript
// users.module.ts
@Module({
  imports: [
    TypeOrmModule.forFeature([User]),
    EmailModule,
  ],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

### 2. 共享核心模块模式

将核心功能提取为共享模块。

```typescript
// core.module.ts
@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    LoggerModule,
    DatabaseModule.forRoot({ ... }),
  ],
  exports: [ConfigModule, LoggerModule, DatabaseModule],
})
export class CoreModule {}
```

### 3. 特性模块模式

将相关功能组合成特性模块。

```typescript
// auth.module.ts
@Module({
  imports: [
    UsersModule,
    JwtModule.registerAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        secret: configService.get('JWT_SECRET'),
        signOptions: { expiresIn: '7d' },
      }),
      inject: [ConfigService],
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, LocalStrategy, JwtStrategy],
  exports: [AuthService, JwtModule],
})
export class AuthModule {}
```

### 4. 领域驱动设计模式

按领域边界组织模块，每个模块代表一个限界上下文。

```
modules/
├── user/
│   ├── domain/
│   │   ├── user.entity.ts
│   │   ├── user.value-object.ts
│   │   └── user.repository.interface.ts
│   ├── application/
│   │   ├── user.service.ts
│   │   └── user.use-cases.ts
│   ├── infrastructure/
│   │   ├── user.repository.impl.ts
│   │   └── user.mapper.ts
│   └── presentation/
│       ├── users.controller.ts
│       └── dto/
├── order/
│   └── ...
└── payment/
    └── ...
```

## 模块依赖管理

### 循环依赖解决

```typescript
// 方法1：使用 forwardRef()
@Module({
  imports: [forwardRef(() => OrdersModule)],
})
export class UsersModule {}

@Module({
  imports: [forwardRef(() => UsersModule)],
})
export class OrdersModule {}

// 方法2：提取共享服务
// 创建 shared.service.ts
@Injectable()
export class SharedService {
  // 共享逻辑
}

// 在两个模块中导入
@Module({
  imports: [SharedModule],
})
export class UsersModule {}

@Module({
  imports: [SharedModule],
})
export class OrdersModule {}
```

### 依赖注入最佳实践

```typescript
// 使用接口而非具体实现
export interface IUserRepository {
  findById(id: string): Promise<User>;
  save(user: User): Promise<User>;
}

@Injectable()
export class UsersService {
  constructor(
    @Inject('IUserRepository')
    private readonly userRepository: IUserRepository,
  ) {}
}

// 在模块中提供实现
@Module({
  providers: [
    {
      provide: 'IUserRepository',
      useClass: UserRepository,
    },
    UsersService,
  ],
})
export class UsersModule {}
```

## 模块测试策略

### 单元测试

```typescript
// users.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from './users.service';
import { getRepositoryToken } from '@nestjs/typeorm';
import { User } from './users.entity';

describe('UsersService', () => {
  let service: UsersService;

  const mockUserRepository = {
    find: jest.fn(),
    findOne: jest.fn(),
    create: jest.fn(),
    save: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: getRepositoryToken(User),
          useValue: mockUserRepository,
        },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('findAll', () => {
    it('should return an array of users', async () => {
      const expectedUsers = [{ id: '1', name: 'John' }];
      mockUserRepository.find.mockResolvedValue(expectedUsers);

      const result = await service.findAll();
      expect(result).toEqual(expectedUsers);
    });
  });
});
```

### 集成测试

```typescript
// users.module.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { UsersModule } from './users.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './users.entity';

describe('UsersModule (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [
        UsersModule,
        TypeOrmModule.forRoot({
          type: 'sqlite',
          database: ':memory:',
          entities: [User],
          synchronize: true,
        }),
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('/users (GET)', () => {
    return request(app.getHttpServer())
      .get('/users')
      .expect(200)
      .expect([]);
  });
});
```

## 模块性能优化

### 延迟加载模块

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { RouterModule } from '@nestjs/core';

@Module({
  imports: [
    RouterModule.register([
      {
        path: 'users',
        module: UsersModule,
      },
      {
        path: 'orders',
        module: OrdersModule,
      },
    ]),
  ],
})
export class AppModule {}
```

### 模块缓存

```typescript
// 使用 CACHE_MANAGER 缓存模块
@Module({
  imports: [
    CacheModule.register({
      ttl: 60,
      max: 100,
    }),
  ],
  providers: [UsersService],
})
export class UsersModule {}

@Injectable()
export class UsersService {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async findAll() {
    const cached = await this.cacheManager.get('users');
    if (cached) return cached;

    const users = await this.userRepository.find();
    await this.cacheManager.set('users', users);
    return users;
  }
}
```

## 模块安全最佳实践

### 模块级守卫

```typescript
// users.module.ts
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { RolesGuard } from '../common/guards/roles.guard';

@Module({
  providers: [
    {
      provide: APP_GUARD,
      useClass: RolesGuard,
    },
  ],
})
export class UsersModule {}
```

### 模块级拦截器

```typescript
// users.module.ts
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { LoggingInterceptor } from '../common/interceptors/logging.interceptor';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: LoggingInterceptor,
    },
  ],
})
export class UsersModule {}
```

## 总结

NestJS 模块组织的最佳实践包括：

1. **按功能划分**：将应用程序按业务功能划分为独立的模块
2. **共享模块**：创建可重用的共享模块，通过 `exports` 导出服务
3. **全局模块**：谨慎使用全局模块，适合基础设施服务
4. **依赖管理**：避免循环依赖，使用接口进行依赖注入
5. **测试策略**：为每个模块编写单元测试和集成测试
6. **性能优化**：使用延迟加载和缓存提高性能
7. **安全考虑**：在模块级别应用守卫和拦截器

遵循这些最佳实践可以创建易于维护、可扩展和高性能的 NestJS 应用程序。
