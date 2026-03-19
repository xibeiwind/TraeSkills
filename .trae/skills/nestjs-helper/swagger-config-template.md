# NestJS Swagger 配置模板

## 基本配置模板

### 1. 安装依赖

```bash
# 安装 Swagger 相关依赖
npm install @nestjs/swagger swagger-ui-express
```

### 2. 基本 Swagger 配置

```typescript
// src/main.ts
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

  // Swagger 基本配置
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

## 高级配置模板

### 1. 带认证的 Swagger 配置

```typescript
// src/main.ts
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

  // Swagger 配置（带认证）
  const config = new DocumentBuilder()
    .setTitle('API 文档')
    .setDescription('应用程序 API 文档')
    .setVersion('1.0')
    .addTag('api')
    .addBearerAuth({
      type: 'http',
      scheme: 'bearer',
      bearerFormat: 'JWT',
      name: 'JWT',
      description: 'Enter JWT token',
      in: 'header',
    }, 'access-token')
    .addSecurityRequirements('access-token')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  
  // Swagger UI 选项
  const options = {
    swaggerOptions: {
      persistAuthorization: true,
      defaultModelsExpandDepth: 2,
      defaultModelExpandDepth: 2,
      displayRequestDuration: true,
    },
  };

  SwaggerModule.setup('api/docs', app, document, options);

  // 启用 CORS
  app.enableCors();

  await app.listen(process.env.PORT || 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
  console.log(`Swagger documentation is available at: ${await app.getUrl()}/api/docs`);
}
bootstrap();
```

### 2. 环境特定配置

```typescript
// src/main.ts
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
    SwaggerModule.setup('api/docs', app, document);
    console.log(`Swagger documentation is available at: http://localhost:3000/api/docs`);
  }

  // 启用 CORS
  app.enableCors();

  await app.listen(process.env.PORT || 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
```

## 装饰器使用模板

### 1. 控制器装饰器

```typescript
// src/users/users.controller.ts
import { Controller, Get, Post, Body, Param, Delete, Put } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { UseGuards } from '@nestjs/common';

@ApiTags('users')
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

  @Get(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取单个用户' })
  @ApiResponse({ status: 200, description: '获取成功', type: User })
  @ApiResponse({ status: 401, description: '未授权' })
  @ApiResponse({ status: 404, description: '用户不存在' })
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(+id);
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '更新用户' })
  @ApiResponse({ status: 200, description: '更新成功', type: User })
  @ApiResponse({ status: 401, description: '未授权' })
  @ApiResponse({ status: 404, description: '用户不存在' })
  update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto) {
    return this.usersService.update(+id, updateUserDto);
  }

  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '删除用户' })
  @ApiResponse({ status: 200, description: '删除成功' })
  @ApiResponse({ status: 401, description: '未授权' })
  @ApiResponse({ status: 404, description: '用户不存在' })
  remove(@Param('id') id: string) {
    return this.usersService.remove(+id);
  }
}
```

### 2. DTO 装饰器

```typescript
// src/users/dto/create-user.dto.ts
import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsNotEmpty, IsString, MinLength } from 'class-validator';

export class CreateUserDto {
  @ApiProperty({
    description: '用户名',
    example: 'john_doe',
    required: true,
    minLength: 3,
  })
  @IsString()
  @IsNotEmpty()
  @MinLength(3)
  username: string;

  @ApiProperty({
    description: '邮箱地址',
    example: 'john@example.com',
    required: true,
  })
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @ApiProperty({
    description: '密码',
    example: 'password123',
    required: true,
    minLength: 6,
  })
  @IsString()
  @IsNotEmpty()
  @MinLength(6)
  password: string;

  @ApiProperty({
    description: '角色',
    example: 'user',
    required: false,
    default: 'user',
  })
  @IsString()
  role?: string;
}
```

### 3. 实体装饰器

```typescript
// src/users/entities/user.entity.ts
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';
import { ApiProperty, ApiHideProperty } from '@nestjs/swagger';

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
    description: '邮箱地址',
    example: 'john@example.com',
  })
  email: string;

  @Column()
  @ApiHideProperty() // 隐藏敏感信息
  password: string;

  @Column({
    default: 'user',
  })
  @ApiProperty({
    description: '用户角色',
    example: 'user',
    default: 'user',
  })
  role: string;

  @Column({
    default: () => 'CURRENT_TIMESTAMP',
  })
  @ApiProperty({
    description: '创建时间',
    example: '2023-01-01T00:00:00.000Z',
  })
  createdAt: Date;

  @Column({
    default: () => 'CURRENT_TIMESTAMP',
    onUpdate: 'CURRENT_TIMESTAMP',
  })
  @ApiProperty({
    description: '更新时间',
    example: '2023-01-01T00:00:00.000Z',
  })
  updatedAt: Date;
}
```

### 4. 响应装饰器

```typescript
// src/common/decorators/api-response.decorator.ts
import { applyDecorators, HttpStatus } from '@nestjs/common';
import { ApiResponse, ApiOperation } from '@nestjs/swagger';

export function ApiSuccessResponse(description: string, type?: any) {
  return applyDecorators(
    ApiResponse({
      status: HttpStatus.OK,
      description,
      type,
    }),
  );
}

export function ApiCreatedResponse(description: string, type?: any) {
  return applyDecorators(
    ApiResponse({
      status: HttpStatus.CREATED,
      description,
      type,
    }),
  );
}

export function ApiErrorResponse(description: string, status: HttpStatus = HttpStatus.BAD_REQUEST) {
  return applyDecorators(
    ApiResponse({
      status,
      description,
    }),
  );
}
```

## 完整配置示例

### 1. 企业级 Swagger 配置

```typescript
// src/main.ts
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
      .setTitle('企业级 API 文档')
      .setDescription('企业应用程序 API 文档，包含用户管理、认证授权、业务逻辑等功能')
      .setVersion('1.0')
      .addTag('认证', '用户登录、注册、刷新令牌等功能')
      .addTag('用户', '用户管理相关功能')
      .addTag('产品', '产品管理相关功能')
      .addTag('订单', '订单管理相关功能')
      .addBearerAuth({
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        name: 'JWT',
        description: '输入您的 JWT 令牌',
        in: 'header',
      }, 'access-token')
      .addSecurityRequirements('access-token')
      .setTermsOfService('https://example.com/terms')
      .setContact({
        name: 'API 支持团队',
        url: 'https://example.com/support',
        email: 'support@example.com',
      })
      .setLicense('MIT', 'https://opensource.org/licenses/MIT')
      .build();

    const document = SwaggerModule.createDocument(app, config);
    
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
        showCommonExtensions: true,
      },
      customCss: `.swagger-ui .topbar { background-color: #f0f0f0; }`,
      customTitle: '企业级 API 文档',
    };

    SwaggerModule.setup('api/docs', app, document, options);
    console.log(`Swagger documentation is available at: http://localhost:3000/api/docs`);
  }

  // 启用 CORS
  app.enableCors({
    origin: process.env.CORS_ORIGIN || '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
    credentials: true,
  });

  await app.listen(process.env.PORT || 3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
```

### 2. 微服务 Swagger 配置

```typescript
// src/main.ts
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 全局前缀
  app.setGlobalPrefix('api/v1');

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
    .setTitle('用户服务 API')
    .setDescription('用户管理微服务 API 文档')
    .setVersion('1.0')
    .addTag('用户服务')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  
  // 导出 Swagger 文档为 JSON
  const fs = require('fs');
  const path = require('path');
  fs.writeFileSync(
    path.join(__dirname, 'swagger.json'),
    JSON.stringify(document, null, 2),
  );

  SwaggerModule.setup('api/docs', app, document);

  // 启用 CORS
  app.enableCors();

  await app.listen(process.env.PORT || 3000);
  console.log(`User Service is running on: ${await app.getUrl()}`);
  console.log(`Swagger documentation is available at: ${await app.getUrl()}/api/docs`);
}
bootstrap();
```

## 配置选项说明

### DocumentBuilder 选项

| 方法 | 描述 | 参数 |
|------|------|------|
| `setTitle` | 设置文档标题 | `title: string` |
| `setDescription` | 设置文档描述 | `description: string` |
| `setVersion` | 设置文档版本 | `version: string` |
| `addTag` | 添加标签 | `name: string, description?: string` |
| `addBearerAuth` | 添加 Bearer 认证 | `options?: SecuritySchemeObject, name?: string` |
| `addApiKey` | 添加 API Key 认证 | `options?: SecuritySchemeObject, name?: string` |
| `addBasicAuth` | 添加 Basic 认证 | `options?: SecuritySchemeObject, name?: string` |
| `addOAuth2` | 添加 OAuth2 认证 | `options?: SecuritySchemeObject, name?: string` |
| `addSecurityRequirements` | 添加安全要求 | `name: string, requirements?: SecurityRequirementObject` |
| `setTermsOfService` | 设置服务条款 URL | `url: string` |
| `setContact` | 设置联系人信息 | `contact: ContactObject` |
| `setLicense` | 设置许可证信息 | `name: string, url: string` |
| `addServer` | 添加服务器信息 | `url: string, description?: string` |
| `build` | 构建配置 | - |

### SwaggerModule.setup 选项

| 选项 | 描述 | 类型 |
|------|------|------|
| `swaggerOptions` | Swagger UI 选项 | `object` |
| `customCss` | 自定义 CSS | `string` |
| `customCssUrl` | 自定义 CSS URL | `string` |
| `customJs` | 自定义 JavaScript | `string` |
| `customJsUrl` | 自定义 JavaScript URL | `string` |
| `customfavIcon` | 自定义 favicon | `string` |
| `customSiteTitle` | 自定义站点标题 | `string` |
| `validatorUrl` | 验证器 URL | `string` |
| `url` | 文档 URL | `string` |
| `urls` | 多个文档 URL | `Array<{url: string, name: string}>` |

### 常用 Swagger UI 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `persistAuthorization` | 持久化授权信息 | `false` |
| `defaultModelsExpandDepth` | 默认模型展开深度 | `1` |
| `defaultModelExpandDepth` | 默认模型展开深度 | `1` |
| `defaultModelRendering` | 默认模型渲染方式 | `'example'` |
| `displayRequestDuration` | 显示请求持续时间 | `false` |
| `docExpansion` | 文档展开方式 | `'list'` |
| `filter` | 启用过滤器 | `false` |
| `showExtensions` | 显示扩展 | `false` |
| `showCommonExtensions` | 显示通用扩展 | `false` |

## 最佳实践

1. **保持配置简洁**：只包含必要的配置选项
2. **环境分离**：在生产环境中禁用 Swagger
3. **认证安全**：正确配置认证方式，保护敏感 API
4. **文档组织**：使用标签对 API 进行分类
5. **装饰器使用**：为所有 API 添加适当的装饰器
6. **版本控制**：在文档中明确版本信息
7. **响应规范**：为所有响应添加适当的描述
8. **示例数据**：为 API 参数和响应提供示例数据