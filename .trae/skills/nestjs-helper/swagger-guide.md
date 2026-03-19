# NestJS Swagger 配置指南

本指南将帮助您在 NestJS 项目中快速配置和使用 Swagger API 文档。

## 目录

- [简介](#简介)
- [安装依赖](#安装依赖)
- [基本配置](#基本配置)
- [高级配置](#高级配置)
- [使用装饰器](#使用装饰器)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 简介

Swagger 是一个强大的 API 文档工具，它可以自动生成交互式 API 文档，使开发者和API使用者能够更方便地理解和测试 API。NestJS 提供了官方的 Swagger 集成，通过 `@nestjs/swagger` 包实现。

## 安装依赖

### 步骤 1: 安装 Swagger 相关依赖

```bash
# 安装 @nestjs/swagger 和 swagger-ui-express
npm install @nestjs/swagger swagger-ui-express
```

### 步骤 2: 验证安装

检查 `package.json` 文件，确保依赖已正确安装：

```json
"dependencies": {
  "@nestjs/swagger": "^7.0.0",
  "swagger-ui-express": "^5.0.0"
  // 其他依赖...
}
```

## 基本配置

### 步骤 1: 更新 main.ts 文件

在 `src/main.ts` 文件中添加 Swagger 配置：

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
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

  // Swagger 配置
  const config = new DocumentBuilder()
    .setTitle('API 文档')
    .setDescription('应用程序 API 文档')
    .setVersion('1.0')
    .addTag('api')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document);

  // 启用 CORS
  app.enableCors();

  await app.listen(process.env.PORT || 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
  console.log(`Swagger documentation is available at: ${await app.getUrl()}/api/docs`);
}
bootstrap();
```

### 步骤 2: 启动应用

```bash
# 开发模式
npm run start:dev
```

### 步骤 3: 访问 Swagger UI

打开浏览器，访问 `http://localhost:3000/api/docs` 查看生成的 API 文档。

## 高级配置

### 自定义 Swagger 配置

您可以根据需要自定义 Swagger 配置：

```typescript
const config = new DocumentBuilder()
  .setTitle('API 文档')
  .setDescription('应用程序 API 文档')
  .setVersion('1.0')
  .addTag('api')
  .addBearerAuth() // 添加 Bearer 认证
  .addSecurityRequirements('bearer') // 添加安全要求
  .setTermsOfService('https://example.com/terms')
  .setContact({
    name: 'API 支持',
    url: 'https://example.com/support',
    email: 'support@example.com',
  })
  .setLicense('MIT', 'https://opensource.org/licenses/MIT')
  .build();
```

### 配置 Swagger UI 选项

您可以自定义 Swagger UI 的选项：

```typescript
const options = {
  swaggerOptions: {
    persistAuthorization: true,
    defaultModelsExpandDepth: 2,
    defaultModelExpandDepth: 2,
    defaultModelRendering: 'model',
    displayRequestDuration: true,
    docExpansion: 'none',
    filter: true,
    showExtensions: true,
  },
};

SwaggerModule.setup('api/docs', app, document, options);
```

### 环境特定配置

您可以根据环境配置 Swagger：

```typescript
if (process.env.NODE_ENV !== 'production') {
  const config = new DocumentBuilder()
    .setTitle('API 文档')
    .setDescription('应用程序 API 文档')
    .setVersion('1.0')
    .addTag('api')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document);
}
```

## 使用装饰器

### 控制器装饰器

使用 `@ApiTags`、`@ApiOperation` 等装饰器为控制器和路由添加文档信息：

```typescript
import { Controller, Get, Post, Body } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { User } from './users.entity';

@ApiTags('users')
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @ApiOperation({ summary: '创建用户' })
  @ApiResponse({ status: 201, description: '用户创建成功', type: User })
  @ApiResponse({ status: 400, description: '请求参数错误' })
  create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto);
  }

  @Get()
  @ApiOperation({ summary: '获取所有用户' })
  @ApiResponse({ status: 200, description: '获取成功', type: [User] })
  findAll() {
    return this.usersService.findAll();
  }
}
```

### DTO 装饰器

使用 `@ApiProperty` 装饰器为 DTO 添加属性描述：

```typescript
import { ApiProperty } from '@nestjs/swagger';

export class CreateUserDto {
  @ApiProperty({
    description: '用户名',
    example: 'john_doe',
    required: true,
  })
  username: string;

  @ApiProperty({
    description: '邮箱',
    example: 'john@example.com',
    required: true,
  })
  email: string;

  @ApiProperty({
    description: '密码',
    example: 'password123',
    required: true,
  })
  password: string;
}
```

### 实体装饰器

使用 `@ApiProperty` 装饰器为实体添加属性描述：

```typescript
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  @ApiProperty({
    description: '用户 ID',
    example: 1,
  })
  id: number;

  @Column()
  @ApiProperty({
    description: '用户名',
    example: 'john_doe',
  })
  username: string;

  @Column()
  @ApiProperty({
    description: '邮箱',
    example: 'john@example.com',
  })
  email: string;

  @Column()
  password: string; // 密码不显示在文档中
}
```

## 最佳实践

### 1. 保持 API 文档与代码同步

- 使用装饰器为所有控制器、路由、DTO 和实体添加文档信息
- 定期更新文档描述，确保与代码实现一致

### 2. 合理组织 API 文档

- 使用 `@ApiTags` 对 API 进行分类
- 为每个操作添加清晰的 `@ApiOperation` 描述
- 为每个响应添加 `@ApiResponse` 说明

### 3. 安全考虑

- 在生产环境中禁用 Swagger 文档或限制访问
- 敏感信息（如密码）不应在文档中显示
- 使用 `@ApiHideProperty` 装饰器隐藏敏感属性

### 4. 性能优化

- 对于大型项目，考虑使用多个 Swagger 文档
- 合理使用 `@ApiExtraModels` 减少文档大小

## 常见问题

### 问题 1: Swagger 文档不显示

**解决方案**：
- 检查 `main.ts` 中的 Swagger 配置是否正确
- 确保应用已启动，访问正确的 URL
- 检查控制台是否有相关错误

### 问题 2: 装饰器不生效

**解决方案**：
- 确保正确导入装饰器：`import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';`
- 检查装饰器使用是否正确
- 重新启动应用

### 问题 3: 生产环境中 Swagger 文档仍然可用

**解决方案**：
- 在 `main.ts` 中添加环境检查：
  ```typescript
  if (process.env.NODE_ENV !== 'production') {
    // Swagger 配置
  }
  ```

### 问题 4: 认证令牌不持久

**解决方案**：
- 在 Swagger UI 选项中启用 `persistAuthorization`：
  ```typescript
  const options = {
    swaggerOptions: {
      persistAuthorization: true,
    },
  };
  ```

## 示例代码

### 完整的 main.ts 配置

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
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

  // 仅在非生产环境启用 Swagger
  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle('API 文档')
      .setDescription('应用程序 API 文档')
      .setVersion('1.0')
      .addTag('api')
      .addBearerAuth()
      .build();

    const document = SwaggerModule.createDocument(app, config);
    
    const options = {
      swaggerOptions: {
        persistAuthorization: true,
      },
    };

    SwaggerModule.setup('api/docs', app, document, options);
    console.log(`Swagger documentation is available at: http://localhost:3000/api/docs`);
  }

  // 启用 CORS
  app.enableCors();

  await app.listen(process.env.PORT || 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
```

### 带认证的控制器示例

```typescript
import { Controller, Get, Post, Body, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { User } from './users.entity';

@ApiTags('users')
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @ApiOperation({ summary: '创建用户' })
  @ApiResponse({ status: 201, description: '用户创建成功', type: User })
  @ApiResponse({ status: 400, description: '请求参数错误' })
  create(@Body() createUserDto: CreateUserDto) {
    return this.usersService.create(createUserDto);
  }

  @Get()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取所有用户' })
  @ApiResponse({ status: 200, description: '获取成功', type: [User] })
  @ApiResponse({ status: 401, description: '未授权' })
  findAll() {
    return this.usersService.findAll();
  }
}
```

## 总结

Swagger 是 NestJS 项目中非常重要的工具，它可以帮助开发者和API使用者更好地理解和测试 API。通过本指南，您应该能够：

- 安装和配置 Swagger
- 自定义 Swagger 选项
- 使用装饰器为 API 添加文档信息
- 遵循 Swagger 配置的最佳实践

如果您有任何问题或需要进一步的帮助，请参考 [NestJS 官方文档](https://docs.nestjs.com/openapi/introduction) 或 [Swagger 官方文档](https://swagger.io/docs/)。