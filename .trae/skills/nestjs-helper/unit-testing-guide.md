# NestJS 单元测试指南

## 目录
1. [Jest 测试框架配置](#jest-测试框架配置)
2. [测试用例示例](#测试用例示例)
3. [Mock 使用指南](#mock-使用指南)
4. [最佳实践](#最佳实践)

---

## Jest 测试框架配置

### 1. 安装依赖

```bash
npm install --save-dev jest @types/jest ts-jest
npm install --save-dev @nestjs/testing
```

### 2. Jest 配置文件

在项目根目录创建 `jest.config.js`：

```javascript
module.exports = {
  moduleFileExtensions: ['js', 'json', 'ts'],
  rootDir: '.',
  testRegex: '.*\\.spec\\.ts$',
  transform: {
    '^.+\\.(t|j)s$': 'ts-jest',
  },
  collectCoverageFrom: [
    '**/*.(t|j)s',
    '!**/*.spec.(t|j)s',
    '!**/node_modules/**',
    '!**/dist/**',
  ],
  coverageDirectory: './coverage',
  testEnvironment: 'node',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/test/setup.ts'],
};
```

### 3. 测试环境设置文件

创建 `test/setup.ts`：

```typescript
import { Test } from '@nestjs/testing';

// 全局测试配置
beforeAll(async () => {
  // 在所有测试之前执行的代码
});

afterAll(async () => {
  // 在所有测试之后执行的代码
});

beforeEach(() => {
  // 在每个测试之前执行的代码
});

afterEach(() => {
  // 在每个测试之后执行的代码
});
```

### 4. package.json 脚本配置

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:cov": "jest --coverage",
    "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
    "test:e2e": "jest --config ./test/jest-e2e.json"
  }
}
```

---

## 测试用例示例

### 1. Service 单元测试

#### 待测试的 Service

```typescript
// src/users/users.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async findAll(): Promise<User[]> {
    return this.userRepository.find();
  }

  async findOne(id: number): Promise<User> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  }

  async create(userData: Partial<User>): Promise<User> {
    const user = this.userRepository.create(userData);
    return this.userRepository.save(user);
  }

  async update(id: number, userData: Partial<User>): Promise<User> {
    await this.findOne(id);
    await this.userRepository.update(id, userData);
    return this.findOne(id);
  }

  async remove(id: number): Promise<void> {
    await this.findOne(id);
    await this.userRepository.delete(id);
  }
}
```

#### Service 测试文件

```typescript
// src/users/users.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { NotFoundException } from '@nestjs/common';
import { Repository } from 'typeorm';
import { UsersService } from './users.service';
import { User } from './entities/user.entity';

describe('UsersService', () => {
  let service: UsersService;
  let repository: Repository<User>;

  const mockUserRepository = {
    find: jest.fn(),
    findOne: jest.fn(),
    create: jest.fn(),
    save: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  };

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    password: 'hashedpassword',
    createdAt: new Date(),
    updatedAt: new Date(),
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
    repository = module.get<Repository<User>>(getRepositoryToken(User));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('findAll', () => {
    it('should return an array of users', async () => {
      const expectedUsers = [mockUser];
      mockUserRepository.find.mockResolvedValue(expectedUsers);

      const result = await service.findAll();

      expect(result).toEqual(expectedUsers);
      expect(repository.find).toHaveBeenCalled();
    });
  });

  describe('findOne', () => {
    it('should return a user when found', async () => {
      mockUserRepository.findOne.mockResolvedValue(mockUser);

      const result = await service.findOne(1);

      expect(result).toEqual(mockUser);
      expect(repository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });
    });

    it('should throw NotFoundException when user not found', async () => {
      mockUserRepository.findOne.mockResolvedValue(null);

      await expect(service.findOne(999)).rejects.toThrow(NotFoundException);
      await expect(service.findOne(999)).rejects.toThrow('User with ID 999 not found');
    });
  });

  describe('create', () => {
    it('should create and return a new user', async () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
      };

      mockUserRepository.create.mockReturnValue(mockUser);
      mockUserRepository.save.mockResolvedValue(mockUser);

      const result = await service.create(userData);

      expect(result).toEqual(mockUser);
      expect(repository.create).toHaveBeenCalledWith(userData);
      expect(repository.save).toHaveBeenCalledWith(mockUser);
    });
  });

  describe('update', () => {
    it('should update and return the user', async () => {
      const updateData = { username: 'updateduser' };
      const updatedUser = { ...mockUser, username: 'updateduser' };

      mockUserRepository.findOne.mockResolvedValue(mockUser);
      mockUserRepository.update.mockResolvedValue(undefined);
      mockUserRepository.findOne.mockResolvedValueOnce(mockUser).mockResolvedValueOnce(updatedUser);

      const result = await service.update(1, updateData);

      expect(result).toEqual(updatedUser);
      expect(repository.update).toHaveBeenCalledWith(1, updateData);
    });
  });

  describe('remove', () => {
    it('should delete the user', async () => {
      mockUserRepository.findOne.mockResolvedValue(mockUser);
      mockUserRepository.delete.mockResolvedValue(undefined);

      await service.remove(1);

      expect(repository.delete).toHaveBeenCalledWith(1);
    });
  });
});
```

### 2. Controller 单元测试

#### 待测试的 Controller

```typescript
// src/users/users.controller.ts
import { Controller, Get, Post, Put, Delete, Body, Param } from '@nestjs/common';
import { UsersService } from './users.service';
import { User } from './entities/user.entity';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(): Promise<User[]> {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string): Promise<User> {
    return this.usersService.findOne(+id);
  }

  @Post()
  create(@Body() userData: Partial<User>): Promise<User> {
    return this.usersService.create(userData);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() userData: Partial<User>): Promise<User> {
    return this.usersService.update(+id, userData);
  }

  @Delete(':id')
  remove(@Param('id') id: string): Promise<void> {
    return this.usersService.remove(+id);
  }
}
```

#### Controller 测试文件

```typescript
// src/users/users.controller.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { User } from './entities/user.entity';

describe('UsersController', () => {
  let controller: UsersController;
  let service: UsersService;

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    password: 'hashedpassword',
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockUsersService = {
    findAll: jest.fn(),
    findOne: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    remove: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [
        {
          provide: UsersService,
          useValue: mockUsersService,
        },
      ],
    }).compile();

    controller = module.get<UsersController>(UsersController);
    service = module.get<UsersService>(UsersService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('findAll', () => {
    it('should return an array of users', async () => {
      const expectedUsers = [mockUser];
      mockUsersService.findAll.mockResolvedValue(expectedUsers);

      const result = await controller.findAll();

      expect(result).toEqual(expectedUsers);
      expect(service.findAll).toHaveBeenCalled();
    });
  });

  describe('findOne', () => {
    it('should return a single user', async () => {
      mockUsersService.findOne.mockResolvedValue(mockUser);

      const result = await controller.findOne('1');

      expect(result).toEqual(mockUser);
      expect(service.findOne).toHaveBeenCalledWith(1);
    });
  });

  describe('create', () => {
    it('should create and return a new user', async () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
      };

      mockUsersService.create.mockResolvedValue(mockUser);

      const result = await controller.create(userData);

      expect(result).toEqual(mockUser);
      expect(service.create).toHaveBeenCalledWith(userData);
    });
  });

  describe('update', () => {
    it('should update and return the user', async () => {
      const updateData = { username: 'updateduser' };
      const updatedUser = { ...mockUser, username: 'updateduser' };

      mockUsersService.update.mockResolvedValue(updatedUser);

      const result = await controller.update('1', updateData);

      expect(result).toEqual(updatedUser);
      expect(service.update).toHaveBeenCalledWith(1, updateData);
    });
  });

  describe('remove', () => {
    it('should remove the user', async () => {
      mockUsersService.remove.mockResolvedValue(undefined);

      await controller.remove('1');

      expect(service.remove).toHaveBeenCalledWith(1);
    });
  });
});
```

### 3. 使用 e2e 测试进行完整流程测试

```typescript
// test/users.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';

describe('Users (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe());
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('/users (POST)', () => {
    it('should create a new user', () => {
      return request(app.getHttpServer())
        .post('/users')
        .send({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123',
        })
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty('id');
          expect(res.body.username).toBe('testuser');
          expect(res.body.email).toBe('test@example.com');
        });
    });
  });

  describe('/users (GET)', () => {
    it('should return all users', () => {
      return request(app.getHttpServer())
        .get('/users')
        .expect(200)
        .expect((res) => {
          expect(Array.isArray(res.body)).toBe(true);
        });
    });
  });

  describe('/users/:id (GET)', () => {
    it('should return a single user', () => {
      return request(app.getHttpServer())
        .get('/users/1')
        .expect(200)
        .expect((res) => {
          expect(res.body).toHaveProperty('id');
          expect(res.body.id).toBe(1);
        });
    });
  });
});
```

---

## Mock 使用指南

### 1. Mock Repository

```typescript
const mockRepository = {
  find: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  save: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
  count: jest.fn(),
};

// 在测试中使用
beforeEach(async () => {
  const module: TestingModule = await Test.createTestingModule({
    providers: [
      UsersService,
      {
        provide: getRepositoryToken(User),
        useValue: mockRepository,
      },
    ],
  }).compile();
});
```

### 2. Mock Service

```typescript
const mockUsersService = {
  findAll: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  remove: jest.fn(),
};

// 在测试中使用
beforeEach(async () => {
  const module: TestingModule = await Test.createTestingModule({
    controllers: [UsersController],
    providers: [
      {
        provide: UsersService,
        useValue: mockUsersService,
      },
    ],
  }).compile();
});
```

### 3. Mock 外部依赖

```typescript
// Mock HTTP 客户端
const mockHttpService = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};

// Mock 配置服务
const mockConfigService = {
  get: jest.fn((key: string) => {
    const config = {
      'API_KEY': 'test-api-key',
      'API_URL': 'https://api.example.com',
    };
    return config[key];
  }),
};

// Mock Logger
const mockLogger = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
};
```

### 4. Mock 返回值和行为

```typescript
// Mock 返回值
mockRepository.find.mockResolvedValue([mockUser]);
mockRepository.findOne.mockResolvedValue(mockUser);
mockRepository.create.mockReturnValue(mockUser);
mockRepository.save.mockResolvedValue(mockUser);

// Mock 抛出错误
mockRepository.findOne.mockRejectedValue(new NotFoundException('User not found'));

// Mock 多次调用返回不同值
mockRepository.findOne
  .mockResolvedValueOnce(mockUser)
  .mockResolvedValueOnce(null)
  .mockResolvedValue(mockUser);

// Mock 实现自定义逻辑
mockRepository.findOne.mockImplementation(async (options) => {
  if (options.where.id === 999) {
    return null;
  }
  return mockUser;
});
```

### 5. 验证 Mock 调用

```typescript
// 验证方法是否被调用
expect(mockRepository.find).toHaveBeenCalled();
expect(mockRepository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });

// 验证调用次数
expect(mockRepository.save).toHaveBeenCalledTimes(1);
expect(mockRepository.find).toHaveBeenCalledTimes(2);

// 验证调用参数
expect(mockRepository.findOne).toHaveBeenCalledWith(
  expect.objectContaining({
    where: expect.objectContaining({
      id: expect.any(Number),
    }),
  })
);

// 验证最后一次调用
expect(mockRepository.findOne).toHaveBeenLastCalledWith({ where: { id: 2 } });
```

### 6. 使用 Jest Mock 函数

```typescript
// 创建 Mock 函数
const mockCallback = jest.fn();

// 在测试中使用
service.processData(mockCallback);

// 验证调用
expect(mockCallback).toHaveBeenCalled();
expect(mockCallback).toHaveBeenCalledWith(expect.any(Object));

// 获取调用历史
const calls = mockCallback.mock.calls;
expect(calls).toHaveLength(1);
expect(calls[0][0]).toHaveProperty('id');

// 清除 Mock
mockCallback.mockClear();
mockCallback.mockReset();
mockCallback.mockRestore();
```

### 7. Mock 模块

```typescript
// Mock 整个模块
jest.mock('./external-service', () => ({
  ExternalService: jest.fn().mockImplementation(() => ({
    fetchData: jest.fn().mockResolvedValue({ data: 'test' }),
  })),
}));

// 或者使用 jest.mockImplementation
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

// 在测试中
import axios from 'axios';
axios.get.mockResolvedValue({ data: 'test' });
```

---

## 最佳实践

### 1. 测试组织

```typescript
describe('UsersService', () => {
  let service: UsersService;

  beforeEach(async () => {
    // 设置测试环境
  });

  afterEach(() => {
    // 清理
  });

  describe('findAll', () => {
    it('should return an array of users', async () => {
      // 测试正常情况
    });

    it('should return empty array when no users exist', async () => {
      // 测试边界情况
    });
  });

  describe('findOne', () => {
    it('should return a user when found', async () => {
      // 测试正常情况
    });

    it('should throw NotFoundException when user not found', async () => {
      // 测试异常情况
    });
  });
});
```

### 2. 测试覆盖率目标

- **行覆盖率**: 80% 以上
- **分支覆盖率**: 75% 以上
- **函数覆盖率**: 85% 以上
- **语句覆盖率**: 80% 以上

### 3. 测试命名规范

```typescript
// 好的测试命名
it('should return user when valid id is provided', async () => {});
it('should throw NotFoundException when user does not exist', async () => {});
it('should create user with valid data', async () => {});

// 避免的测试命名
it('test user', async () => {});
it('should work', async () => {});
```

### 4. AAA 模式

```typescript
it('should update user successfully', async () => {
  // Arrange - 准备测试数据
  const userId = 1;
  const updateData = { username: 'updated' };
  mockRepository.findOne.mockResolvedValue(mockUser);
  mockRepository.update.mockResolvedValue(undefined);

  // Act - 执行被测试的代码
  const result = await service.update(userId, updateData);

  // Assert - 验证结果
  expect(result).toBeDefined();
  expect(mockRepository.update).toHaveBeenCalledWith(userId, updateData);
});
```

### 5. 避免测试实现细节

```typescript
// 好的测试 - 测试行为
it('should return user by id', async () => {
  const result = await service.findOne(1);
  expect(result).toEqual(mockUser);
});

// 避免的测试 - 测试实现细节
it('should call repository.findOne with correct parameters', async () => {
  await service.findOne(1);
  expect(mockRepository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });
});
```

### 6. 使用测试工具函数

```typescript
// test/utils.ts
export const createMockUser = (overrides = {}): User => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  password: 'hashedpassword',
  createdAt: new Date(),
  updatedAt: new Date(),
  ...overrides,
});

export const setupTestingModule = async (providers: any[]) => {
  return Test.createTestingModule({ providers }).compile();
};

// 在测试中使用
import { createMockUser } from '../utils';

it('should create user', async () => {
  const mockUser = createMockUser({ username: 'custom' });
  // ...
});
```

### 7. 异步测试处理

```typescript
// 使用 async/await
it('should return user', async () => {
  const result = await service.findOne(1);
  expect(result).toBeDefined();
});

// 使用 Promise
it('should return user', () => {
  return service.findOne(1).then(result => {
    expect(result).toBeDefined();
  });
});

// 使用 done 回调（不推荐）
it('should return user', (done) => {
  service.findOne(1).then(result => {
    expect(result).toBeDefined();
    done();
  });
});
```

### 8. 测试隔离

```typescript
// 每个测试应该独立运行
beforeEach(() => {
  // 重置所有 mock
  jest.clearAllMocks();
});

// 使用不同的测试数据
it('test 1', async () => {
  mockRepository.find.mockResolvedValue([user1]);
  const result = await service.findAll();
  expect(result).toEqual([user1]);
});

it('test 2', async () => {
  mockRepository.find.mockResolvedValue([user2]);
  const result = await service.findAll();
  expect(result).toEqual([user2]);
});
```

### 9. 测试超时设置

```typescript
// 设置全局超时
jest.setTimeout(10000);

// 为特定测试设置超时
it('should complete within 5 seconds', async () => {
  // 测试代码
}, 5000);
```

### 10. 持续集成配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:cov
      - uses: codecov/codecov-action@v2
```

---

## 总结

本指南涵盖了 NestJS 单元测试的各个方面，包括：

1. **Jest 配置**: 完整的测试环境设置
2. **测试用例示例**: Service、Controller 和 e2e 测试的实际案例
3. **Mock 使用**: 各种依赖的 Mock 技巧
4. **最佳实践**: 编写高质量测试的建议

遵循这些指南可以帮助您构建健壮、可维护的测试套件，确保代码质量和可靠性。
