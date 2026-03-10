# NestJS Helper Skill 常见问题解答

本文档回答了用户在使用 NestJS Helper Skill 时可能遇到的常见问题。

## 目录

- [安装和配置问题](#安装和配置问题)
- [项目初始化问题](#项目初始化问题)
- [代码生成问题](#代码生成问题)
- [数据库集成问题](#数据库集成问题)
- [认证授权问题](#认证授权问题)
- [测试相关问题](#测试相关问题)
- [性能优化问题](#性能优化问题)
- [部署相关问题](#部署相关问题)
- [代码审查问题](#代码审查问题)
- [其他问题](#其他问题)

## 安装和配置问题

### Q1: 如何检查我的环境是否满足 NestJS Helper Skill 的要求？

**A:** 运行以下命令检查您的环境：

```bash
# 检查 Node.js 版本（需要 18.x 或更高）
node --version

# 检查 npm 版本（需要 9.x 或更高）
npm --version

# 检查 TypeScript 版本（需要 5.x 或更高）
tsc --version

# 检查 NestJS CLI 是否已安装
nest --version
```

如果任何命令返回错误或版本过低，请先升级相应的工具。

### Q2: NestJS CLI 安装失败怎么办？

**A:** 如果安装 NestJS CLI 时遇到问题，请尝试以下解决方案：

1. **使用 sudo 权限（Linux/Mac）：**
   ```bash
   sudo npm install -g @nestjs/cli
   ```

2. **清除 npm 缓存：**
   ```bash
   npm cache clean --force
   npm install -g @nestjs/cli
   ```

3. **使用 npx 直接运行（无需全局安装）：**
   ```bash
   npx @nestjs/cli new my-project
   ```

4. **切换 npm 镜像源：**
   ```bash
   npm config set registry https://registry.npmmirror.com
   npm install -g @nestjs/cli
   ```

### Q3: 如何配置 TypeScript 路径别名？

**A:** 在 `tsconfig.json` 和 `tsconfig.paths.json` 中配置路径别名：

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@modules/*": ["src/modules/*"],
      "@common/*": ["src/common/*"],
      "@config/*": ["src/config/*"]
    }
  },
  "extends": "./tsconfig.paths.json"
}

// tsconfig.paths.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@modules/*": ["src/modules/*"],
      "@common/*": ["src/common/*"],
      "@config/*": ["src/config/*"]
    }
  }
}
```

### Q4: ESLint 和 Prettier 配置冲突怎么办？

**A:** 确保在 `.eslintrc.js` 中正确配置 Prettier 集成：

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'plugin:@typescript-eslint/recommended',
    'prettier/@typescript-eslint',
    'plugin:prettier/recommended',
  ],
  parserOptions: {
    sourceType: 'module',
  },
  rules: {
    'prettier/prettier': 'error',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
  },
};
```

在 `.prettierrc` 中配置格式化规则：

```json
{
  "singleQuote": true,
  "trailingComma": "all",
  "tabWidth": 2,
  "semi": true,
  "printWidth": 100,
  "arrowParens": "avoid"
}
```

## 项目初始化问题

### Q5: 创建项目时提示端口被占用怎么办？

**A:** 修改 `.env` 文件中的端口配置：

```env
PORT=3001
```

或者在启动时指定端口：

```bash
PORT=3001 npm run start:dev
```

### Q6: 如何配置多个环境变量文件？

**A:** 创建不同环境的配置文件：

```
.env                # 默认配置
.env.development    # 开发环境
.env.production     # 生产环境
.env.test           # 测试环境
```

在 `app.module.ts` 中配置：

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: `.env.${process.env.NODE_ENV || 'development'}`,
    }),
  ],
})
export class AppModule {}
```

### Q7: 如何禁用 TypeORM 的自动同步？

**A:** 在生产环境中，应该禁用自动同步并使用迁移：

```typescript
// app.module.ts
TypeOrmModule.forRoot({
  type: 'postgres',
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT),
  username: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  entities: [__dirname + '/**/*.entity{.ts,.js}'],
  synchronize: process.env.NODE_ENV === 'development', // 仅在开发环境启用
  logging: process.env.NODE_ENV === 'development',
}),
```

### Q8: 如何配置全局前缀和 CORS？

**A:** 在 `main.ts` 中配置：

```typescript
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // 设置全局前缀
  app.setGlobalPrefix('api');

  // 配置 CORS
  app.enableCors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
  });

  // 全局验证管道
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  await app.listen(process.env.PORT || 3000);
}
bootstrap();
```

## 代码生成问题

### Q9: 生成的代码不符合我的项目规范怎么办？

**A:** 您可以自定义代码模板或修改生成的代码。NestJS Helper Skill 生成的代码遵循 NestJS 最佳实践，但您可以根据项目需求进行调整：

1. **修改生成的代码**：直接编辑生成的文件
2. **创建自定义模板**：在项目中创建代码模板
3. **使用 NestJS CLI 的自定义选项**：`nest g module users --no-spec`（不生成测试文件）

### Q10: 如何生成带有关系实体的代码？

**A:** 在请求时明确指定实体关系：

```
生成一个评论模块，Comment 实体与 User 和 Post 实体有多对一关系
```

生成的实体示例：

```typescript
import { Entity, Column, PrimaryGeneratedColumn, ManyToOne, JoinColumn } from 'typeorm';
import { User } from '../users/user.entity';
import { Post } from '../posts/post.entity';

@Entity('comments')
export class Comment {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('text')
  content: string;

  @ManyToOne(() => User)
  @JoinColumn({ name: 'authorId' })
  author: User;

  @Column()
  authorId: string;

  @ManyToOne(() => Post)
  @JoinColumn({ name: 'postId' })
  post: Post;

  @Column()
  postId: string;

  @CreateDateColumn()
  createdAt: Date;
}
```

### Q11: 如何为生成的代码添加 Swagger 文档？

**A:** 安装 Swagger 依赖并配置：

```bash
npm install @nestjs/swagger
```

在 `main.ts` 中配置：

```typescript
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('NestJS API')
    .setDescription('API description')
    .setVersion('1.0')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document);

  await app.listen(3000);
}
bootstrap();
```

在控制器中使用装饰器：

```typescript
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('users')
@Controller('users')
export class UsersController {
  @Get()
  @ApiOperation({ summary: '获取所有用户' })
  @ApiResponse({ status: 200, description: '成功返回用户列表' })
  findAll() {
    return this.usersService.findAll();
  }
}
```

## 数据库集成问题

### Q12: 数据库连接失败怎么办？

**A:** 检查以下几点：

1. **检查数据库服务是否运行：**
   ```bash
   # PostgreSQL
   pg_isready

   # MySQL
   mysqladmin ping

   # MongoDB
   mongosh --eval "db.adminCommand('ping')"
   ```

2. **检查 `.env` 配置：**
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_USERNAME=postgres
   DB_PASSWORD=your_password
   DB_DATABASE=nestjs_app
   ```

3. **检查防火墙设置**

4. **增加连接超时时间：**
   ```typescript
   TypeOrmModule.forRoot({
     // ...其他配置
     connectTimeoutMS: 30000,
     extra: {
       max: 10,
       idleTimeoutMillis: 30000,
       connectionTimeoutMillis: 2000,
     },
   })
   ```

### Q13: 如何处理数据库迁移冲突？

**A:** 当多个开发者同时创建迁移时，可能会出现冲突。解决方法：

1. **回滚本地迁移：**
   ```bash
   npm run migration:revert
   ```

2. **拉取最新的迁移文件**

3. **重新生成迁移：**
   ```bash
   npm run migration:generate -- -n YourMigrationName
   ```

4. **如果迁移文件名冲突，手动重命名并调整时间戳**

### Q14: 如何优化数据库查询性能？

**A:** 使用以下优化策略：

1. **使用索引：**
   ```typescript
   @Entity('users')
   export class User {
     @Column()
     @Index()
     email: string;
   }
   ```

2. **使用查询构建器：**
   ```typescript
   async findActiveUsers(): Promise<User[]> {
     return this.userRepository
       .createQueryBuilder('user')
       .where('user.isActive = :isActive', { isActive: true })
       .select(['user.id', 'user.username', 'user.email'])
       .cache(true)
       .getMany();
   }
   ```

3. **使用分页：**
   ```typescript
   async findAll(page: number = 1, limit: number = 10) {
     const [data, total] = await this.userRepository.findAndCount({
       skip: (page - 1) * limit,
       take: limit,
     });
     return { data, total, page, limit };
   }
   ```

4. **使用缓存：**
   ```typescript
   @CacheTTL(60)
   async findAll(): Promise<User[]> {
     return this.userRepository.find();
   }
   ```

### Q15: 如何处理数据库事务？

**A:** 使用 TypeORM 的事务功能：

```typescript
import { Injectable, Transactional } from '@nestjs/common';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource } from 'typeorm';

@Injectable()
export class UsersService {
  constructor(
    @InjectDataSource()
    private readonly dataSource: DataSource,
  ) {}

  async transferFunds(fromUserId: string, toUserId: string, amount: number) {
    await this.dataSource.transaction(async (manager) => {
      const fromUser = await manager.findOne(User, { where: { id: fromUserId } });
      const toUser = await manager.findOne(User, { where: { id: toUserId } });

      fromUser.balance -= amount;
      toUser.balance += amount;

      await manager.save(fromUser);
      await manager.save(toUser);
    });
  }
}
```

## 认证授权问题

### Q16: JWT Token 过期后如何处理？

**A:** 实现 Token 刷新机制：

```typescript
// auth/auth.service.ts
async refreshToken(refreshToken: string) {
  try {
    const payload = this.jwtService.verify(refreshToken);
    const user = await this.usersService.findOne(payload.sub);

    const newPayload = { email: user.email, sub: user.id };
    const accessToken = this.jwtService.sign(newPayload);
    const newRefreshToken = this.jwtService.sign(newPayload, {
      expiresIn: '7d',
    });

    return { accessToken, refreshToken: newRefreshToken };
  } catch (error) {
    throw new UnauthorizedException('Invalid refresh token');
  }
}
```

### Q17: 如何实现基于角色的访问控制（RBAC）？

**A:** 创建角色守卫和装饰器：

```typescript
// common/decorators/roles.decorator.ts
import { SetMetadata } from '@nestjs/common';

export const ROLES_KEY = 'roles';
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);

// common/guards/roles.guard.ts
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY } from '../decorators/roles.decorator';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles) return true;

    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some((role) => user.roles?.includes(role));
  }
}

// 使用示例
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)
export class AdminController {
  @Get()
  @Roles('admin')
  getAdminData() {
    return 'Admin data';
  }
}
```

### Q18: 如何实现 OAuth2 认证？

**A:** 使用 Passport OAuth2 策略：

```bash
npm install passport-google-oauth20
npm install --save-dev @types/passport-google-oauth20
```

```typescript
// auth/strategies/google.strategy.ts
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, VerifyCallback } from 'passport-google-oauth20';

@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor() {
    super({
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: process.env.GOOGLE_CALLBACK_URL,
      scope: ['email', 'profile'],
    });
  }

  async validate(accessToken: string, refreshToken: string, profile: any, done: VerifyCallback): Promise<any> {
    const { name, emails, photos } = profile;
    const user = {
      email: emails[0].value,
      firstName: name.givenName,
      lastName: name.familyName,
      picture: photos[0].value,
      accessToken,
    };
    done(null, user);
  }
}
```

## 测试相关问题

### Q19: 测试时数据库连接失败怎么办？

**A:** 为测试配置独立的数据库：

```typescript
// test/setup.ts
import { TypeOrmModule } from '@nestjs/typeorm';

export const testDatabaseConfig = {
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  username: 'test',
  password: 'test',
  database: 'test_db',
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  synchronize: true,
  dropSchema: true,
};

// 在测试中使用
beforeAll(async () => {
  const module = await Test.createTestingModule({
    imports: [
      TypeOrmModule.forRoot(testDatabaseConfig),
      // ...其他模块
    ],
  }).compile();

  app = module.createNestApplication();
  await app.init();
});

afterAll(async () => {
  await app.close();
});
```

### Q20: 如何提高测试覆盖率？

**A:** 遵循以下最佳实践：

1. **编写单元测试覆盖所有服务方法**
2. **为每个控制器编写集成测试**
3. **测试边界条件和错误情况**
4. **使用 Mock 隔离依赖**

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let repository: Repository<User>;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: getRepositoryToken(User),
          useClass: Repository,
        },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
    repository = module.get<Repository<User>>(getRepositoryToken(User));
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  it('should create a user', async () => {
    const createUserDto: CreateUserDto = {
      username: 'test',
      email: 'test@example.com',
      password: 'password123',
    };

    const result = await service.create(createUserDto);
    expect(result).toHaveProperty('id');
    expect(result.username).toBe(createUserDto.username);
  });

  it('should throw NotFoundException when user not found', async () => {
    await expect(service.findOne('999')).rejects.toThrow(NotFoundException);
  });
});
```

### Q21: 如何测试异步代码？

**A:** 使用 async/await 和 Jest 的异步测试功能：

```typescript
it('should handle async operations', async () => {
  const promise = service.asyncMethod();
  await expect(promise).resolves.toBe(expectedValue);
});

it('should handle async errors', async () => {
  const promise = service.failingAsyncMethod();
  await expect(promise).rejects.toThrow(Error);
});

it('should handle timeout', async () => {
  jest.useFakeTimers();
  const promise = service.delayedMethod();
  jest.advanceTimersByTime(1000);
  await expect(promise).resolves.toBe(expectedValue);
  jest.useRealTimers();
});
```

## 性能优化问题

### Q22: 应用启动缓慢怎么办？

**A:** 优化启动时间的方法：

1. **延迟加载模块：**
   ```typescript
   @Module({
     imports: [
       // 延迟加载模块
       UsersModule,
       AuthModule,
     ],
   })
   export class AppModule {}
   ```

2. **禁用不必要的中间件**
3. **优化数据库连接池配置**
4. **使用生产模式构建：**
   ```bash
   npm run build
   npm run start:prod
   ```

### Q23: 如何处理大量并发请求？

**A:** 使用以下策略：

1. **启用压缩：**
   ```typescript
   import * as compression from 'compression';

   app.use(compression());
   ```

2. **使用缓存：**
   ```typescript
   @CacheTTL(300)
   async findAll(): Promise<User[]> {
     return this.userRepository.find();
   }
   ```

3. **使用队列处理耗时任务：**
   ```bash
   npm install @nestjs/bull bull
   ```

4. **配置负载均衡**

### Q24: 如何监控应用性能？

**A:** 集成监控工具：

```bash
npm install @nestjs/terminus
```

```typescript
// health/health.controller.ts
import { Controller, Get } from '@nestjs/common';
import { HealthCheck, HealthCheckService, TypeOrmHealthIndicator } from '@nestjs/terminus';

@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private db: TypeOrmHealthIndicator,
  ) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.db.pingCheck('database'),
    ]);
  }
}
```

## 部署相关问题

### Q25: Docker 容器启动失败怎么办？

**A:** 检查以下内容：

1. **检查 Dockerfile 语法**
2. **检查端口映射**
3. **检查环境变量配置**
4. **查看容器日志：**
   ```bash
   docker logs <container_id>
   ```

5. **进入容器调试：**
   ```bash
   docker exec -it <container_id> sh
   ```

### Q26: 如何实现零停机部署？

**A:** 使用以下策略：

1. **使用蓝绿部署**
2. **使用滚动更新**
3. **使用健康检查**

```yaml
# docker-compose.yml
services:
  app:
    image: your-app:latest
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
```

### Q27: 如何配置环境变量管理？

**A:** 使用以下方法：

1. **使用 `.env` 文件（开发环境）**
2. **使用 CI/CD 环境变量（生产环境）**
3. **使用密钥管理服务（AWS Secrets Manager、Azure Key Vault）**

```typescript
// config/configuration.ts
import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  jwtSecret: process.env.JWT_SECRET,
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1d',
}));
```

## 代码审查问题

### Q28: 如何提高代码审查效率？

**A:** 使用 NestJS Helper Skill 的代码审查功能：

```
审查我的用户模块代码，重点关注：
- 安全性问题
- 性能问题
- 代码规范
- 错误处理
```

Skill 会提供详细的审查报告，包括：
- 代码质量评分
- 潜在问题列表
- 改进建议
- 最佳实践推荐

### Q29: 如何处理代码审查中的安全问题？

**A:** 常见安全问题及解决方案：

1. **SQL 注入：** 使用参数化查询
2. **XSS 攻击：** 使用验证和转义
3. **CSRF 攻击：** 使用 CSRF 令牌
4. **敏感信息泄露：** 不要在日志中记录敏感信息

```typescript
// 不安全
const query = `SELECT * FROM users WHERE id = ${userId}`;

// 安全
const user = await this.userRepository.findOne({ where: { id: userId } });
```

### Q30: 如何重构遗留代码？

**A:** 遵循重构原则：

1. **先编写测试**
2. **小步重构**
3. **保持功能不变**
4. **使用工具辅助**

```
帮我重构这个服务类，使其更易于维护和测试
```

## 其他问题

### Q31: 如何处理文件上传？

**A:** 使用 NestJS 文件上传功能：

```typescript
import { Controller, Post, UseInterceptors, UploadedFile } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';

@Controller('upload')
export class UploadController {
  @Post()
  @UseInterceptors(
    FileInterceptor('file', {
      storage: diskStorage({
        destination: './uploads',
        filename: (req, file, cb) => {
          const filename = `${Date.now()}-${file.originalname}`;
          cb(null, filename);
        },
      }),
      limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
    }),
  )
  uploadFile(@UploadedFile() file: Express.Multer.File) {
    return { filename: file.filename };
  }
}
```

### Q32: 如何实现 WebSocket 功能？

**A:** 使用 NestJS WebSocket 网关：

```typescript
import { WebSocketGateway, WebSocketServer, SubscribeMessage, OnGatewayConnection } from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({
  cors: { origin: '*' },
})
export class ChatGateway implements OnGatewayConnection {
  @WebSocketServer()
  server: Server;

  handleConnection(client: Socket) {
    console.log(`Client connected: ${client.id}`);
  }

  @SubscribeMessage('message')
  handleMessage(client: Socket, payload: any): void {
    this.server.emit('message', payload);
  }
}
```

### Q33: 如何实现定时任务？

**A:** 使用 NestJS 调度器：

```bash
npm install @nestjs/schedule
```

```typescript
import { Injectable } from '@nestjs/common';
import { Cron, CronExpression, Timeout, Interval } from '@nestjs/schedule';

@Injectable()
export class TasksService {
  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  handleDailyTask() {
    console.log('Running daily task');
  }

  @Interval(60000) // 每 60 秒
  handleInterval() {
    console.log('Running interval task');
  }

  @Timeout(5000) // 5 秒后执行一次
  handleTimeout() {
    console.log('Running timeout task');
  }
}
```

### Q34: 如何获取更多帮助？

**A:** 如果您的问题没有在这里找到答案，可以：

1. **查看 NestJS 官方文档：** https://docs.nestjs.com/
2. **查看 NestJS 中文文档：** https://docs.nestjs.cn/
3. **搜索 GitHub Issues：** https://github.com/nestjs/nest/issues
4. **加入 NestJS 社区：** Discord、Slack、Stack Overflow
5. **直接向 NestJS Helper Skill 提问：** 描述您的问题，Skill 会尽力帮助您

---

希望这份 FAQ 能够帮助您解决使用 NestJS Helper Skill 时遇到的问题。如果您有其他问题，请随时提问！
