# NestJS 集成测试指南

## 目录
1. [测试环境配置](#测试环境配置)
2. [端到端测试示例](#端到端测试示例)
3. [数据库集成测试](#数据库集成测试)
4. [外部服务集成测试](#外部服务集成测试)
5. [性能测试](#性能测试)
6. [最佳实践](#最佳实践)

---

## 测试环境配置

### 1. 安装依赖

```bash
npm install --save-dev supertest @types/supertest
npm install --save-dev sqlite3
npm install --save-dev @nestjs/testing
```

### 2. E2E 测试配置文件

创建 `test/jest-e2e.json`：

```json
{
  "moduleFileExtensions": ["js", "json", "ts"],
  "rootDir": ".",
  "testEnvironment": "node",
  "testRegex": ".e2e-spec.ts$",
  "transform": {
    "^.+\\.(t|j)s$": "ts-jest"
  },
  "moduleNameMapper": {
    "^@/(.*)$": "<rootDir>/../src/$1"
  }
}
```

### 3. 测试环境配置

创建 `test/test.env`：

```env
# 测试数据库配置
DATABASE_TYPE=sqlite
DATABASE_PATH=./test.db

# 测试服务器配置
PORT=3001
NODE_ENV=test

# 外部服务 Mock
EXTERNAL_API_URL=http://localhost:4000
EXTERNAL_API_KEY=test-api-key

# Redis 配置（如果需要）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# JWT 配置
JWT_SECRET=test-secret-key
JWT_EXPIRES_IN=1h
```

### 4. 测试辅助工具

创建 `test/test-utils.ts`：

```typescript
import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import { AppModule } from '../src/app.module';
import * as request from 'supertest';

export class TestHelper {
  private static app: INestApplication;
  private static module: TestingModule;

  static async setup() {
    this.module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    this.app = this.module.createNestApplication();
    this.app.useGlobalPipes(new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }));
    await this.app.init();

    return this.app;
  }

  static async teardown() {
    await this.app.close();
  }

  static getApp(): INestApplication {
    return this.app;
  }

  static getModule(): TestingModule {
    return this.module;
  }

  static getRequest() {
    return request(this.app.getHttpServer());
  }

  static async clearDatabase() {
    const dataSource = this.module.get('DataSource');
    const entities = dataSource.entityMetadatas;
    
    for (const entity of entities) {
      const repository = dataSource.getRepository(entity.name);
      await repository.clear();
    }
  }
}
```

### 5. 全局测试设置

创建 `test/setup.e2e.ts`：

```typescript
import { TestHelper } from './test-utils';

beforeAll(async () => {
  await TestHelper.setup();
});

afterAll(async () => {
  await TestHelper.teardown();
});

beforeEach(async () => {
  await TestHelper.clearDatabase();
});
```

---

## 端到端测试示例

### 1. 用户管理 E2E 测试

```typescript
// test/users.e2e-spec.ts
import { TestHelper } from './test-utils';
import { HttpStatus } from '@nestjs/common';

describe('Users (e2e)', () => {
  const testUser = {
    username: 'testuser',
    email: 'test@example.com',
    password: 'Password123!',
  };

  let createdUserId: number;

  describe('/users (POST)', () => {
    it('should create a new user', async () => {
      const response = await TestHelper.getRequest()
        .post('/users')
        .send(testUser)
        .expect(HttpStatus.CREATED);

      expect(response.body).toHaveProperty('id');
      expect(response.body.username).toBe(testUser.username);
      expect(response.body.email).toBe(testUser.email);
      expect(response.body).not.toHaveProperty('password');

      createdUserId = response.body.id;
    });

    it('should fail with invalid data', async () => {
      await TestHelper.getRequest()
        .post('/users')
        .send({
          username: 'te',
          email: 'invalid-email',
        })
        .expect(HttpStatus.BAD_REQUEST);
    });

    it('should fail with duplicate email', async () => {
      await TestHelper.getRequest()
        .post('/users')
        .send(testUser)
        .expect(HttpStatus.CONFLICT);
    });
  });

  describe('/users (GET)', () => {
    it('should return all users', async () => {
      const response = await TestHelper.getRequest()
        .get('/users')
        .expect(HttpStatus.OK);

      expect(Array.isArray(response.body)).toBe(true);
      expect(response.body.length).toBeGreaterThan(0);
    });
  });

  describe('/users/:id (GET)', () => {
    it('should return a single user', async () => {
      const response = await TestHelper.getRequest()
        .get(`/users/${createdUserId}`)
        .expect(HttpStatus.OK);

      expect(response.body.id).toBe(createdUserId);
      expect(response.body.username).toBe(testUser.username);
    });

    it('should return 404 for non-existent user', async () => {
      await TestHelper.getRequest()
        .get('/users/999999')
        .expect(HttpStatus.NOT_FOUND);
    });
  });

  describe('/users/:id (PATCH)', () => {
    it('should update user', async () => {
      const updateData = { username: 'updateduser' };

      const response = await TestHelper.getRequest()
        .patch(`/users/${createdUserId}`)
        .send(updateData)
        .expect(HttpStatus.OK);

      expect(response.body.username).toBe(updateData.username);
    });
  });

  describe('/users/:id (DELETE)', () => {
    it('should delete user', async () => {
      await TestHelper.getRequest()
        .delete(`/users/${createdUserId}`)
        .expect(HttpStatus.NO_CONTENT);

      await TestHelper.getRequest()
        .get(`/users/${createdUserId}`)
        .expect(HttpStatus.NOT_FOUND);
    });
  });
});
```

### 2. 认证流程 E2E 测试

```typescript
// test/auth.e2e-spec.ts
import { TestHelper } from './test-utils';
import { HttpStatus } from '@nestjs/common';

describe('Auth (e2e)', () => {
  const testUser = {
    username: 'authuser',
    email: 'auth@example.com',
    password: 'Password123!',
  };

  let authToken: string;

  describe('Registration', () => {
    it('should register a new user', async () => {
      const response = await TestHelper.getRequest()
        .post('/auth/register')
        .send(testUser)
        .expect(HttpStatus.CREATED);

      expect(response.body).toHaveProperty('accessToken');
      expect(response.body).toHaveProperty('user');
      authToken = response.body.accessToken;
    });
  });

  describe('Login', () => {
    it('should login with valid credentials', async () => {
      const response = await TestHelper.getRequest()
        .post('/auth/login')
        .send({
          email: testUser.email,
          password: testUser.password,
        })
        .expect(HttpStatus.OK);

      expect(response.body).toHaveProperty('accessToken');
      expect(response.body).toHaveProperty('user');
      authToken = response.body.accessToken;
    });

    it('should fail with invalid credentials', async () => {
      await TestHelper.getRequest()
        .post('/auth/login')
        .send({
          email: testUser.email,
          password: 'wrongpassword',
        })
        .expect(HttpStatus.UNAUTHORIZED);
    });
  });

  describe('Protected Routes', () => {
    it('should access protected route with valid token', async () => {
      await TestHelper.getRequest()
        .get('/auth/profile')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(HttpStatus.OK);
    });

    it('should fail without token', async () => {
      await TestHelper.getRequest()
        .get('/auth/profile')
        .expect(HttpStatus.UNAUTHORIZED);
    });

    it('should fail with invalid token', async () => {
      await TestHelper.getRequest()
        .get('/auth/profile')
        .set('Authorization', 'Bearer invalid-token')
        .expect(HttpStatus.UNAUTHORIZED);
    });
  });

  describe('Token Refresh', () => {
    it('should refresh access token', async () => {
      const response = await TestHelper.getRequest()
        .post('/auth/refresh')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(HttpStatus.OK);

      expect(response.body).toHaveProperty('accessToken');
    });
  });
});
```

### 3. 产品管理 E2E 测试（带关联）

```typescript
// test/products.e2e-spec.ts
import { TestHelper } from './test-utils';
import { HttpStatus } from '@nestjs/common';

describe('Products (e2e)', () => {
  let adminToken: string;
  let userToken: string;
  let categoryId: number;
  let productId: number;

  beforeAll(async () => {
    // 创建管理员用户并获取 token
    const adminResponse = await TestHelper.getRequest()
      .post('/auth/register')
      .send({
        username: 'admin',
        email: 'admin@example.com',
        password: 'Admin123!',
        role: 'admin',
      });
    adminToken = adminResponse.body.accessToken;

    // 创建普通用户并获取 token
    const userResponse = await TestHelper.getRequest()
      .post('/auth/register')
      .send({
        username: 'user',
        email: 'user@example.com',
        password: 'User123!',
      });
    userToken = userResponse.body.accessToken;
  });

  describe('Categories', () => {
    it('should create a category as admin', async () => {
      const response = await TestHelper.getRequest()
        .post('/categories')
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          name: 'Electronics',
          description: 'Electronic products',
        })
        .expect(HttpStatus.CREATED);

      expect(response.body.name).toBe('Electronics');
      categoryId = response.body.id;
    });

    it('should fail to create category as regular user', async () => {
      await TestHelper.getRequest()
        .post('/categories')
        .set('Authorization', `Bearer ${userToken}`)
        .send({
          name: 'Unauthorized',
        })
        .expect(HttpStatus.FORBIDDEN);
    });
  });

  describe('Products', () => {
    it('should create a product as admin', async () => {
      const response = await TestHelper.getRequest()
        .post('/products')
        .set('Authorization', `Bearer ${adminToken}`)
        .send({
          name: 'Laptop',
          description: 'High-performance laptop',
          price: 999.99,
          stock: 10,
          categoryId,
        })
        .expect(HttpStatus.CREATED);

      expect(response.body.name).toBe('Laptop');
      expect(response.body.categoryId).toBe(categoryId);
      productId = response.body.id;
    });

    it('should get all products', async () => {
      const response = await TestHelper.getRequest()
        .get('/products')
        .expect(HttpStatus.OK);

      expect(Array.isArray(response.body.items)).toBe(true);
      expect(response.body.items.length).toBeGreaterThan(0);
    });

    it('should filter products by category', async () => {
      const response = await TestHelper.getRequest()
        .get(`/products?categoryId=${categoryId}`)
        .expect(HttpStatus.OK);

      response.body.items.forEach((product: any) => {
        expect(product.categoryId).toBe(categoryId);
      });
    });

    it('should update product stock', async () => {
      const response = await TestHelper.getRequest()
        .patch(`/products/${productId}/stock`)
        .set('Authorization', `Bearer ${adminToken}`)
        .send({ stock: 20 })
        .expect(HttpStatus.OK);

      expect(response.body.stock).toBe(20);
    });
  });

  describe('Orders', () => {
    let orderId: number;

    it('should create an order', async () => {
      const response = await TestHelper.getRequest()
        .post('/orders')
        .set('Authorization', `Bearer ${userToken}`)
        .send({
          items: [
            {
              productId,
              quantity: 2,
            },
          ],
        })
        .expect(HttpStatus.CREATED);

      expect(response.body).toHaveProperty('id');
      expect(response.body.total).toBeGreaterThan(0);
      orderId = response.body.id;
    });

    it('should get user orders', async () => {
      const response = await TestHelper.getRequest()
        .get('/orders')
        .set('Authorization', `Bearer ${userToken}`)
        .expect(HttpStatus.OK);

      expect(Array.isArray(response.body)).toBe(true);
    });

    it('should get order details', async () => {
      const response = await TestHelper.getRequest()
        .get(`/orders/${orderId}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(HttpStatus.OK);

      expect(response.body.id).toBe(orderId);
    });
  });
});
```

---

## 数据库集成测试

### 1. 使用内存数据库

```typescript
// test/database.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { TypeOrmModule } from '@nestjs/typeorm';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Database Integration', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [
        TypeOrmModule.forRoot({
          type: 'sqlite',
          database: ':memory:',
          entities: [__dirname + '/../**/*.entity{.ts,.js}'],
          synchronize: true,
          dropSchema: true,
        }),
        AppModule,
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should handle database operations', async () => {
    const response = await request(app.getHttpServer())
      .post('/users')
      .send({
        username: 'dbuser',
        email: 'db@example.com',
        password: 'Password123!',
      })
      .expect(201);

    expect(response.body).toHaveProperty('id');
  });
});
```

### 2. 事务测试

```typescript
// test/transactions.e2e-spec.ts
import { TestHelper } from './test-utils';
import { HttpStatus } from '@nestjs/common';

describe('Transaction Tests', () => {
  it('should rollback transaction on error', async () => {
    const initialResponse = await TestHelper.getRequest()
      .get('/products')
      .expect(HttpStatus.OK);

    const initialCount = initialResponse.body.items.length;

    try {
      await TestHelper.getRequest()
        .post('/products')
        .send({
          name: 'Invalid Product',
          price: -100, // 无效价格
        });
    } catch (error) {
      // 预期失败
    }

    const finalResponse = await TestHelper.getRequest()
      .get('/products')
      .expect(HttpStatus.OK);

    expect(finalResponse.body.items.length).toBe(initialCount);
  });

  it('should commit transaction on success', async () => {
    const response = await TestHelper.getRequest()
      .post('/products')
      .send({
        name: 'Valid Product',
        price: 99.99,
        stock: 10,
      })
      .expect(HttpStatus.CREATED);

    expect(response.body).toHaveProperty('id');
  });
});
```

### 3. 数据库迁移测试

```typescript
// test/migrations.e2e-spec.ts
import { DataSource } from 'typeorm';
import { TestHelper } from './test-utils';

describe('Database Migrations', () => {
  let dataSource: DataSource;

  beforeAll(async () => {
    dataSource = TestHelper.getModule().get('DataSource');
  });

  it('should have all tables created', async () => {
    const tables = await dataSource.query(
      "SELECT name FROM sqlite_master WHERE type='table'"
    );

    expect(tables.length).toBeGreaterThan(0);
  });

  it('should have correct table structure', async () => {
    const columns = await dataSource.query('PRAGMA table_info(users)');

    const columnNames = columns.map((col: any) => col.name);
    expect(columnNames).toContain('id');
    expect(columnNames).toContain('username');
    expect(columnNames).toContain('email');
  });
});
```

---

## 外部服务集成测试

### 1. Mock 外部 API

```typescript
// test/external-api.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { HttpModule } from '@nestjs/axios';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('External API Integration', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [
        HttpModule.register({
          baseURL: 'http://mock-api.example.com',
          timeout: 5000,
        }),
        AppModule,
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should handle external API call', async () => {
    // 假设有一个端点调用外部 API
    const response = await request(app.getHttpServer())
      .get('/external/data')
      .expect(HttpStatus.OK);

    expect(response.body).toHaveProperty('data');
  });
});
```

### 2. 使用 TestContainers（可选）

```typescript
// test/testcontainers.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { TypeOrmModule } from '@nestjs/typeorm';
import { INestApplication } from '@nestjs/common';
import { PostgreSqlContainer } from '@testcontainers/postgresql';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('TestContainers Integration', () => {
  let app: INestApplication;
  let postgresContainer: PostgreSqlContainer;

  beforeAll(async () => {
    postgresContainer = await new PostgreSqlContainer('postgres:15')
      .withDatabase('testdb')
      .withUsername('testuser')
      .withPassword('testpass')
      .start();

    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [
        TypeOrmModule.forRoot({
          type: 'postgres',
          host: postgresContainer.getHost(),
          port: postgresContainer.getMappedPort(5432),
          username: postgresContainer.getUsername(),
          password: postgresContainer.getPassword(),
          database: postgresContainer.getDatabase(),
          entities: [__dirname + '/../**/*.entity{.ts,.js}'],
          synchronize: true,
        }),
        AppModule,
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
    await postgresContainer.stop();
  });

  it('should work with PostgreSQL container', async () => {
    const response = await request(app.getHttpServer())
      .get('/health')
      .expect(HttpStatus.OK);

    expect(response.body.status).toBe('ok');
  });
});
```

### 3. WebSocket 集成测试

```typescript
// test/websocket.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import { IoAdapter } from '@nestjs/platform-socket.io';
import * as io from 'socket.io-client';
import { AppModule } from '../src/app.module';

describe('WebSocket Integration', () => {
  let app: INestApplication;
  let clientSocket: any;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useWebSocketAdapter(new IoAdapter(app));
    await app.init();

    await app.listen(3000);
  });

  afterAll(async () => {
    if (clientSocket) {
      clientSocket.disconnect();
    }
    await app.close();
  });

  it('should connect to WebSocket server', (done) => {
    clientSocket = io('http://localhost:3000');

    clientSocket.on('connect', () => {
      expect(clientSocket.connected).toBe(true);
      done();
    });

    clientSocket.on('connect_error', (error: any) => {
      done(error);
    });
  });

  it('should receive messages', (done) => {
    clientSocket.on('message', (data: any) => {
      expect(data).toHaveProperty('content');
      done();
    });

    clientSocket.emit('message', { content: 'test message' });
  });
});
```

---

## 性能测试

### 1. 负载测试

```typescript
// test/performance/load.e2e-spec.ts
import { TestHelper } from './test-utils';
import { HttpStatus } from '@nestjs/common';

describe('Load Testing', () => {
  const concurrentRequests = 100;
  const endpoint = '/products';

  it('should handle concurrent requests', async () => {
    const requests = Array(concurrentRequests).fill(null).map(() =>
      TestHelper.getRequest().get(endpoint)
    );

    const startTime = Date.now();
    const responses = await Promise.all(requests);
    const endTime = Date.now();

    responses.forEach(response => {
      expect(response.status).toBe(HttpStatus.OK);
    });

    const totalTime = endTime - startTime;
    const averageTime = totalTime / concurrentRequests;

    console.log(`Total time: ${totalTime}ms`);
    console.log(`Average time per request: ${averageTime}ms`);

    expect(averageTime).toBeLessThan(1000); // 每个请求应在 1 秒内完成
  });
});
```

### 2. 响应时间测试

```typescript
// test/performance/response-time.e2e-spec.ts
import { TestHelper } from './test-utils';
import { HttpStatus } from '@nestjs/common';

describe('Response Time Testing', () => {
  const endpoints = [
    { path: '/users', maxTime: 500 },
    { path: '/products', maxTime: 300 },
    { path: '/orders', maxTime: 400 },
  ];

  endpoints.forEach(({ path, maxTime }) => {
    it(`should respond to ${path} within ${maxTime}ms`, async () => {
      const startTime = Date.now();
      await TestHelper.getRequest()
        .get(path)
        .expect(HttpStatus.OK);
      const endTime = Date.now();

      const responseTime = endTime - startTime;
      expect(responseTime).toBeLessThan(maxTime);
    });
  });
});
```

### 3. 内存使用测试

```typescript
// test/performance/memory.e2e-spec.ts
import { TestHelper } from './test-utils';

describe('Memory Usage Testing', () => {
  it('should not leak memory on repeated requests', async () => {
    const initialMemory = process.memoryUsage().heapUsed;

    for (let i = 0; i < 1000; i++) {
      await TestHelper.getRequest().get('/users');
    }

    // 强制垃圾回收（如果可用）
    if (global.gc) {
      global.gc();
    }

    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;

    console.log(`Memory increase: ${memoryIncrease} bytes`);

    // 内存增长不应超过 10MB
    expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
  });
});
```

---

## 最佳实践

### 1. 测试数据管理

```typescript
// test/fixtures/user-fixtures.ts
export class UserFixtures {
  static validUser() {
    return {
      username: 'testuser',
      email: 'test@example.com',
      password: 'Password123!',
    };
  }

  static adminUser() {
    return {
      ...this.validUser(),
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
    };
  }

  static invalidUser() {
    return {
      username: 'te',
      email: 'invalid-email',
      password: '123',
    };
  }
}

// 在测试中使用
import { UserFixtures } from '../fixtures/user-fixtures';

it('should create valid user', async () => {
  await TestHelper.getRequest()
    .post('/users')
    .send(UserFixtures.validUser())
    .expect(201);
});
```

### 2. 测试隔离

```typescript
// 每个测试套件独立运行
describe('Feature 1', () => {
  beforeAll(async () => {
    await TestHelper.setup();
  });

  afterAll(async () => {
    await TestHelper.teardown();
  });

  beforeEach(async () => {
    await TestHelper.clearDatabase();
  });

  it('test 1', async () => {});
  it('test 2', async () => {});
});

describe('Feature 2', () => {
  beforeAll(async () => {
    await TestHelper.setup();
  });

  afterAll(async () => {
    await TestHelper.teardown();
  });

  beforeEach(async () => {
    await TestHelper.clearDatabase();
  });

  it('test 1', async () => {});
  it('test 2', async () => {});
});
```

### 3. 测试超时设置

```typescript
// 设置合理的超时时间
describe('Long Running Tests', () => {
  jest.setTimeout(30000); // 30 秒

  it('should complete within timeout', async () => {
    // 长时间运行的测试
  });
});
```

### 4. 并行测试执行

```typescript
// jest.config.js
module.exports = {
  // ... 其他配置
  maxWorkers: 4, // 并行执行测试
  testTimeout: 10000,
};
```

### 5. 测试报告

```typescript
// package.json
{
  "scripts": {
    "test:e2e": "jest --config ./test/jest-e2e.json",
    "test:e2e:coverage": "jest --config ./test/jest-e2e.json --coverage",
    "test:e2e:verbose": "jest --config ./test/jest-e2e.json --verbose"
  }
}
```

### 6. 环境变量管理

```typescript
// test/config/test.config.ts
export const testConfig = {
  database: {
    type: 'sqlite',
    path: ':memory:',
  },
  server: {
    port: 3001,
  },
  jwt: {
    secret: 'test-secret',
    expiresIn: '1h',
  },
};

// 在测试中使用
import { testConfig } from '../config/test.config';

beforeAll(async () => {
  process.env.DATABASE_TYPE = testConfig.database.type;
  // ...
});
```

### 7. 测试清理

```typescript
// test/cleanup.ts
export async function cleanupDatabase(dataSource: DataSource) {
  const entities = dataSource.entityMetadatas;
  
  for (const entity of entities) {
    const repository = dataSource.getRepository(entity.name);
    await repository.query(`DELETE FROM ${entity.tableName}`);
  }
}

// 在测试中使用
import { cleanupDatabase } from '../cleanup';

afterEach(async () => {
  const dataSource = TestHelper.getModule().get('DataSource');
  await cleanupDatabase(dataSource);
});
```

### 8. 测试数据工厂

```typescript
// test/factories/user.factory.ts
export class UserFactory {
  static create(overrides = {}) {
    return {
      username: `user_${Date.now()}`,
      email: `user_${Date.now()}@example.com`,
      password: 'Password123!',
      ...overrides,
    };
  }

  static async createMany(count: number, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides));
  }
}

// 在测试中使用
import { UserFactory } from '../factories/user.factory';

it('should create multiple users', async () => {
  const users = UserFactory.createMany(5);
  
  for (const user of users) {
    await TestHelper.getRequest()
      .post('/users')
      .send(user)
      .expect(201);
  }
});
```

### 9. 断言辅助函数

```typescript
// test/assertions/user.assertions.ts
import { Response } from 'supertest';

export class UserAssertions {
  static assertUserResponse(response: Response) {
    expect(response.body).toHaveProperty('id');
    expect(response.body).toHaveProperty('username');
    expect(response.body).toHaveProperty('email');
    expect(response.body).not.toHaveProperty('password');
  }

  static assertUserListResponse(response: Response) {
    expect(Array.isArray(response.body)).toBe(true);
    response.body.forEach(UserAssertions.assertUserResponse);
  }
}

// 在测试中使用
import { UserAssertions } from '../assertions/user.assertions';

it('should return user list', async () => {
  const response = await TestHelper.getRequest()
    .get('/users')
    .expect(200);

  UserAssertions.assertUserListResponse(response);
});
```

### 10. CI/CD 集成

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  e2e:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run E2E tests
        run: npm run test:e2e
        env:
          DATABASE_TYPE: postgres
          DATABASE_HOST: localhost
          DATABASE_PORT: 5432
          DATABASE_USERNAME: test
          DATABASE_PASSWORD: test
          DATABASE_NAME: testdb
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/e2e/lcov.info
```

---

## 总结

本指南涵盖了 NestJS 集成测试的各个方面，包括：

1. **测试环境配置**: 完整的 E2E 测试环境设置
2. **端到端测试示例**: 用户管理、认证、产品管理等实际案例
3. **数据库集成测试**: 内存数据库、事务、迁移测试
4. **外部服务集成测试**: API Mock、TestContainers、WebSocket 测试
5. **性能测试**: 负载测试、响应时间测试、内存使用测试
6. **最佳实践**: 测试数据管理、隔离、清理等建议

遵循这些指南可以帮助您构建全面、可靠的集成测试套件，确保应用程序的各个组件正确协同工作。
