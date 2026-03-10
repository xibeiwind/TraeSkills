# NestJS 控制器模板

## 基础控制器模板

```typescript
import { Controller, Get, Post, Put, Delete, Body, Param, Query, HttpStatus } from '@nestjs/common';
import { {{ServiceName}} } from './{{serviceFileName}}';
import { Create{{EntityName}}Dto } from './dto/create-{{entityFileName}}.dto';
import { Update{{EntityName}}Dto } from './dto/update-{{entityFileName}}.dto';

@Controller('{{routePath}}')
export class {{ControllerName}} {
  constructor(private readonly {{serviceName}}: {{ServiceName}}) {}

  @Get()
  async findAll(@Query() query: any): Promise<any> {
    return await this.{{serviceName}}.findAll(query);
  }

  @Get(':id')
  async findOne(@Param('id') id: string): Promise<any> {
    return await this.{{serviceName}}.findOne(id);
  }

  @Post()
  async create(@Body() create{{EntityName}}Dto: Create{{EntityName}}Dto): Promise<any> {
    return await this.{{serviceName}}.create(create{{EntityName}}Dto);
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() update{{EntityName}}Dto: Update{{EntityName}}Dto
  ): Promise<any> {
    return await this.{{serviceName}}.update(id, update{{EntityName}}Dto);
  }

  @Delete(':id')
  async remove(@Param('id') id: string): Promise<void> {
    await this.{{serviceName}}.remove(id);
  }
}
```

## 装饰器使用示例

### 1. 请求方法装饰器

```typescript
@Controller('users')
export class UsersController {
  
  @Get()
  findAll(): string {
    return 'This action returns all users';
  }

  @Get(':id')
  findOne(@Param('id') id: string): string {
    return `This action returns a #${id} user`;
  }

  @Post()
  create(@Body() createUserDto: CreateUserDto): string {
    return 'This action adds a new user';
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto): string {
    return `This action updates a #${id} user`;
  }

  @Patch(':id')
  partialUpdate(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto): string {
    return `This action partially updates a #${id} user`;
  }

  @Delete(':id')
  remove(@Param('id') id: string): string {
    return `This action removes a #${id} user`;
  }

  @Options()
  options(): string {
    return 'This action returns options';
  }

  @Head()
  head(): string {
    return 'This action returns head';
  }

  @All()
  all(): string {
    return 'This action handles all requests';
  }
}
```

### 2. 请求参数装饰器

```typescript
@Controller('users')
export class UsersController {
  
  @Get()
  getUsers(
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 10,
    @Query('sort') sort: string = 'createdAt'
  ): string {
    return `Get users page: ${page}, limit: ${limit}, sort: ${sort}`;
  }

  @Get(':id')
  getUserById(
    @Param('id') id: string,
    @Param('name') name: string
  ): string {
    return `Get user id: ${id}, name: ${name}`;
  }

  @Post()
  createUser(
    @Body() createUserDto: CreateUserDto,
    @Body('email') email: string
  ): string {
    return `Create user with email: ${email}`;
  }

  @Get('profile')
  getProfile(
    @Headers('authorization') auth: string,
    @Headers('user-agent') userAgent: string
  ): string {
    return `Auth: ${auth}, UserAgent: ${userAgent}`;
  }

  @Get('ip')
  getIp(@Ip() ip: string): string {
    return `Client IP: ${ip}`;
  }

  @Get('session')
  getSession(@Session() session: Record<string, any>): string {
    return `Session ID: ${session.id}`;
  }

  @Get('host')
  getHost(@Host() host: string): string {
    return `Host: ${host}`;
  }
}
```

### 3. 响应状态码装饰器

```typescript
@Controller('users')
export class UsersController {
  
  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() createUserDto: CreateUserDto): string {
    return 'This action adds a new user';
  }

  @Post('login')
  @HttpCode(HttpStatus.OK)
  login(): string {
    return 'Login successful';
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string): void {
    // 删除操作
  }

  @Get('not-found')
  @HttpCode(HttpStatus.NOT_FOUND)
  notFound(): string {
    return 'Resource not found';
  }
}
```

### 4. 响应头装饰器

```typescript
@Controller('users')
export class UsersController {
  
  @Get()
  @Header('Cache-Control', 'no-cache')
  @Header('X-Custom-Header', 'CustomValue')
  findAll(): string {
    return 'This action returns all users';
  }

  @Post()
  @Header('Location', '/users/123')
  create(@Body() createUserDto: CreateUserDto): string {
    return 'User created';
  }
}
```

### 5. 重定向装饰器

```typescript
@Controller('users')
export class UsersController {
  
  @Get('redirect')
  @Redirect('https://nestjs.com', 301)
  redirect(): string {
    return 'Redirecting...';
  }

  @Get('docs')
  @Redirect('https://docs.nestjs.com', 302)
  getDocs(@Query('version') version: string) {
    if (version && version === '5') {
      return { url: 'https://docs.nestjs.com/v5/' };
    }
    return {};
  }
}
```

### 6. 路由参数装饰器

```typescript
@Controller('users')
export class UsersController {
  
  @Get(':userId/posts/:postId')
  getUserPost(
    @Param('userId') userId: string,
    @Param('postId') postId: string
  ): string {
    return `User: ${userId}, Post: ${postId}`;
  }

  @Get('wildcard/*')
  wildcard(@Param('0') path: string): string {
    return `Wildcard path: ${path}`;
  }
}
```

### 7. 作用域装饰器

```typescript
@Controller('users')
@UseGuards(AuthGuard)
@UseInterceptors(LoggingInterceptor)
@UsePipes(ValidationPipe)
export class UsersController {
  
  @Get()
  @UseGuards(RolesGuard)
  @UseInterceptors(TransformInterceptor)
  @SetMetadata('roles', ['admin'])
  findAll(): string {
    return 'This action returns all users';
  }

  @Post()
  @UsePipes(new ValidationPipe({ whitelist: true }))
  create(@Body() createUserDto: CreateUserDto): string {
    return 'This action adds a new user';
  }
}
```

### 8. 完整示例控制器

```typescript
import { 
  Controller, 
  Get, 
  Post, 
  Put, 
  Delete, 
  Body, 
  Param, 
  Query, 
  HttpCode, 
  HttpStatus,
  Header,
  UseGuards,
  UseInterceptors,
  UsePipes,
  ValidationPipe,
  ParseIntPipe,
  DefaultValuePipe
} from '@nestjs/common';
import { UserService } from './user.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { AuthGuard } from '../guards/auth.guard';
import { RolesGuard } from '../guards/roles.guard';
import { LoggingInterceptor } from '../interceptors/logging.interceptor';
import { TransformInterceptor } from '../interceptors/transform.interceptor';

@Controller('users')
@UseGuards(AuthGuard)
@UseInterceptors(LoggingInterceptor)
export class UsersController {
  constructor(private readonly userService: UserService) {}

  @Get()
  @UseInterceptors(TransformInterceptor)
  async findAll(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number,
    @Query('search') search?: string
  ): Promise<any> {
    return await this.userService.findAll({
      page,
      limit,
      search
    });
  }

  @Get(':id')
  async findOne(@Param('id', ParseIntPipe) id: number): Promise<any> {
    return await this.userService.findOne(id);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @Header('Cache-Control', 'no-cache')
  @UsePipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true }))
  async create(@Body() createUserDto: CreateUserDto): Promise<any> {
    return await this.userService.create(createUserDto);
  }

  @Put(':id')
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateUserDto: UpdateUserDto
  ): Promise<any> {
    return await this.userService.update(id, updateUserDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async remove(@Param('id', ParseIntPipe) id: number): Promise<void> {
    await this.userService.remove(id);
  }

  @Post('batch')
  @UseGuards(RolesGuard)
  async createBatch(@Body() createUserDtos: CreateUserDto[]): Promise<any> {
    return await this.userService.createBatch(createUserDtos);
  }
}
```

## 装饰器说明

### 控制器装饰器
- `@Controller('path')`: 声明控制器，指定路由前缀
- `@Get('path')`: 处理 GET 请求
- `@Post('path')`: 处理 POST 请求
- `@Put('path')`: 处理 PUT 请求
- `@Patch('path')`: 处理 PATCH 请求
- `@Delete('path')`: 处理 DELETE 请求

### 参数装饰器
- `@Req()`, `@Request()`: 请求对象
- `@Res()`, `@Response()`: 响应对象
- `@Next()`: Next 函数
- `@Session()`: 会话对象
- `@Param(key?: string)`: 路由参数
- `@Body(key?: string)`: 请求体
- `@Query(key?: string)`: 查询参数
- `@Headers(key?: string)`: 请求头
- `@Ip()`: 客户端 IP
- `@Host()`: 主机名

### 其他装饰器
- `@HttpCode(statusCode)`: 设置响应状态码
- `@Header(name, value)`: 设置响应头
- `@Redirect(url?, statusCode?)`: 重定向
- `@UseGuards(guard)`: 应用守卫
- `@UseInterceptors(interceptor)`: 应用拦截器
- `@UsePipes(pipe)`: 应用管道
- `@SetMetadata(key, value)`: 设置元数据

## 类型安全最佳实践

1. **使用 DTO 类型**: 所有请求体应使用 DTO 类型
2. **参数类型转换**: 使用 `ParseIntPipe` 等管道进行类型转换
3. **返回类型注解**: 明确指定方法返回类型
4. **可选参数**: 使用 `?` 标记可选参数
5. **默认值**: 使用 `DefaultValuePipe` 设置默认值
