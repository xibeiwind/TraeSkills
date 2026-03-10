# NestJS 项目结构指南

## 目录概述

NestJS 采用模块化架构，整个应用程序由多个模块组成。以下是标准的 NestJS 项目结构：

```
my-nestjs-app/
├── src/
│   ├── main.ts                 # 应用程序入口文件
│   ├── app.module.ts           # 根模块
│   ├── app.controller.ts       # 根控制器（可选）
│   ├── app.service.ts          # 根服务（可选）
│   ├── common/                 # 公共模块和工具
│   │   ├── decorators/         # 自定义装饰器
│   │   ├── filters/            # 异常过滤器
│   │   ├── guards/             # 守卫
│   │   ├── interceptors/       # 拦截器
│   │   ├── middlewares/        # 中间件
│   │   ├── pipes/              # 管道
│   │   └── utils/              # 工具函数
│   ├── config/                 # 配置文件
│   │   ├── configuration.ts    # 配置类
│   │   └── database.config.ts  # 数据库配置
│   ├── modules/                # 功能模块
│   │   ├── users/              # 用户模块
│   │   │   ├── users.module.ts
│   │   │   ├── users.controller.ts
│   │   │   ├── users.service.ts
│   │   │   ├── users.entity.ts
│   │   │   ├── dto/            # 数据传输对象
│   │   │   │   ├── create-user.dto.ts
│   │   │   │   └── update-user.dto.ts
│   │   │   └── interfaces/     # TypeScript 接口
│   │   └── auth/               # 认证模块
│   │       ├── auth.module.ts
│   │       ├── auth.controller.ts
│   │       ├── auth.service.ts
│   │       ├── strategies/     # 认证策略
│   │       │   └── jwt.strategy.ts
│   │       └── guards/
│   │           └── jwt-auth.guard.ts
│   ├── database/               # 数据库相关
│   │   ├── migrations/         # 数据库迁移
│   │   └── seeds/              # 种子数据
│   └── shared/                 # 共享模块
│       └── logger/
│           ├── logger.module.ts
│           └── logger.service.ts
├── test/                       # 测试文件
│   ├── unit/
│   └── e2e/
├── public/                     # 静态资源
├── .env                        # 环境变量
├── .env.example                # 环境变量示例
├── nest-cli.json               # NestJS CLI 配置
├── tsconfig.json               # TypeScript 配置
├── tsconfig.build.json         # 构建配置
├── package.json                # 项目依赖
├── tsconfig.paths.json         # 路径别名配置
└── README.md                   # 项目说明
```

## 核心文件说明

### main.ts - 应用程序入口

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 全局验证管道
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );
  
  // 启用 CORS
  app.enableCors();
  
  // 全局前缀
  app.setGlobalPrefix('api');
  
  await app.listen(3000);
}
bootstrap();
```

### app.module.ts - 根模块

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UsersModule } from './modules/users/users.module';
import { AuthModule } from './modules/auth/auth.module';
import { DatabaseModule } from './database/database.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    UsersModule,
    AuthModule,
    DatabaseModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
```

## 模块结构详解

### 模块 (Module)

模块是 NestJS 应用程序的基本构建块，使用 `@Module()` 装饰器定义：

```typescript
import { Module } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './users.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

**模块装饰器选项：**
- `imports`: 导入其他模块
- `controllers`: 声明控制器
- `providers`: 声明服务提供者
- `exports`: 导出服务供其他模块使用

### 控制器 (Controller)

控制器负责处理传入的请求并返回响应：

```typescript
import { Controller, Get, Post, Body, Param, Put, Delete } from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll() {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(id);
  }

  @Post()
  create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto) {
    return this.usersService.update(id, updateUserDto);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.usersService.remove(id);
  }
}
```

### 服务 (Service)

服务包含业务逻辑，使用 `@Injectable()` 装饰器标记：

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './users.entity';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async findAll(): Promise<User[]> {
    return this.userRepository.find();
  }

  async findOne(id: string): Promise<User> {
    const user = await this.userRepository.findOne(id);
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  }

  async create(createUserDto: CreateUserDto): Promise<User> {
    const user = this.userRepository.create(createUserDto);
    return this.userRepository.save(user);
  }

  async update(id: string, updateUserDto: UpdateUserDto): Promise<User> {
    const user = await this.findOne(id);
    this.userRepository.merge(user, updateUserDto);
    return this.userRepository.save(user);
  }

  async remove(id: string): Promise<void> {
    await this.userRepository.delete(id);
  }
}
```

### DTO (Data Transfer Object)

DTO 用于定义数据传输的结构和验证规则：

```typescript
// create-user.dto.ts
import { IsEmail, IsNotEmpty, IsString, MinLength } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @IsNotEmpty()
  username: string;

  @IsEmail()
  @IsNotEmpty()
  email: string;

  @IsString()
  @MinLength(6)
  password: string;
}

// update-user.dto.ts
import { PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';

export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

### 实体 (Entity)

实体定义数据库表结构：

```typescript
import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  username: string;

  @Column({ unique: true })
  email: string;

  @Column()
  password: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

## 目录组织最佳实践

### 按功能划分

将相关的控制器、服务、DTO 和实体组织在同一目录下：

```
modules/
├── users/
│   ├── users.module.ts
│   ├── users.controller.ts
│   ├── users.service.ts
│   ├── users.entity.ts
│   ├── dto/
│   │   ├── create-user.dto.ts
│   │   └── update-user.dto.ts
│   └── interfaces/
│       └── user.interface.ts
```

### 公共模块

将可复用的代码放在 `common` 目录：

```
common/
├── decorators/
│   └── roles.decorator.ts
├── filters/
│   └── http-exception.filter.ts
├── guards/
│   └── roles.guard.ts
├── interceptors/
│   └── logging.interceptor.ts
├── pipes/
│   └── validation.pipe.ts
└── utils/
    └── date.util.ts
```

### 配置管理

将所有配置集中在 `config` 目录：

```
config/
├── configuration.ts
├── database.config.ts
├── jwt.config.ts
└── app.config.ts
```

## 文件命名约定

- **模块**: `*.module.ts`
- **控制器**: `*.controller.ts`
- **服务**: `*.service.ts`
- **DTO**: `*.dto.ts`
- **实体**: `*.entity.ts`
- **接口**: `*.interface.ts`
- **守卫**: `*.guard.ts`
- **拦截器**: `*.interceptor.ts`
- **过滤器**: `*.filter.ts`
- **管道**: `*.pipe.ts`
- **中间件**: `*.middleware.ts`

## 总结

NestJS 的项目结构强调模块化和关注点分离。通过遵循标准的目录结构和命名约定，可以创建易于维护和扩展的应用程序。每个模块都应该保持独立，并通过依赖注入进行通信。
