# 代码质量检查

本文档详细说明了 NestJS 项目代码质量检查的逻辑、评估标准和实施方法，帮助开发团队建立系统的代码质量保障体系。

## 目录

- [检查目标](#检查目标)
- [质量维度](#质量维度)
- [检查逻辑](#检查逻辑)
- [评估标准](#评估标准)
- [自动化检查](#自动化检查)
- [质量改进](#质量改进)

---

## 检查目标

代码质量检查的主要目标包括：

1. **代码可读性**：确保代码易于理解和维护
2. **代码可维护性**：降低修改和扩展的难度
3. **代码可靠性**：减少 bug 和错误
4. **代码性能**：优化执行效率和资源使用
5. **代码安全性**：防范常见安全漏洞
6. **代码一致性**：保持团队代码风格统一

---

## 质量维度

### 1. 代码可读性

#### 检查项

**命名规范**
- [ ] 变量名是否有意义且清晰
- [ ] 函数名是否准确描述其功能
- [ ] 类名是否使用名词且首字母大写
- [ ] 常量是否使用全大写和下划线
- [ ] 布尔变量是否使用 is/has/should 等前缀

**代码格式**
- [ ] 缩进是否一致（建议 2 或 4 空格）
- [ ] 行长度是否合理（建议不超过 120 字符）
- [ ] 空行使用是否合理（逻辑块之间）
- [ ] 运算符周围是否有适当的空格
- [ ] 括号对齐是否一致

**注释质量**
- [ ] 复杂逻辑是否有注释说明
- [ ] 函数是否有 JSDoc 注释
- [ ] 注释是否准确反映代码意图
- [ ] 是否避免无意义的注释
- [ ] 是否及时更新过时的注释

**示例**：
```typescript
// 不好的命名
const d = new Date();
const u = await getUser(id);
const f = (x, y) => x + y;

// 好的命名
const currentDate = new Date();
const user = await getUserById(userId);
const calculateSum = (firstNumber: number, secondNumber: number) => {
  return firstNumber + secondNumber;
};

// 不好的注释
// 获取用户
const user = await getUser(id);

// 好的注释
/**
 * 根据用户 ID 获取用户信息
 * @param userId - 用户唯一标识符
 * @returns 用户对象，如果不存在则返回 null
 * @throws {NotFoundException} 当用户不存在时抛出
 */
async getUserById(userId: string): Promise<User | null> {
  return this.userRepository.findOne({ where: { id: userId } });
}
```

### 2. 代码可维护性

#### 检查项

**函数复杂度**
- [ ] 函数长度是否合理（建议不超过 50 行）
- [ ] 函数参数数量是否合理（建议不超过 4 个）
- [ ] 圈复杂度是否合理（建议不超过 10）
- [ ] 嵌套层级是否合理（建议不超过 3 层）
- [ ] 是否避免过长的 if-else 链

**代码重复**
- [ ] 是否存在重复的代码块
- [ ] 重复逻辑是否提取为函数
- [ ] 是否使用工具函数减少重复
- [ ] 相似的类是否可以合并或继承

**模块耦合**
- [ ] 模块间依赖是否最小化
- [ ] 是否避免紧耦合
- [ ] 是否使用依赖注入解耦
- [ ] 接口是否定义清晰

**示例**：
```typescript
// 不好的做法：高复杂度
async processOrder(orderId: string) {
  const order = await this.orderRepository.findById(orderId);
  if (!order) {
    throw new NotFoundException('Order not found');
  }
  if (order.status === 'cancelled') {
    throw new BadRequestException('Order is cancelled');
  }
  if (order.status === 'completed') {
    throw new BadRequestException('Order is already completed');
  }
  if (order.items.length === 0) {
    throw new BadRequestException('Order has no items');
  }
  // ... 更多嵌套逻辑
}

// 好的做法：低复杂度
async processOrder(orderId: string) {
  const order = await this.validateOrder(orderId);
  await this.updateOrderStatus(order, 'processing');
  await this.sendOrderConfirmation(order);
  return order;
}

private async validateOrder(orderId: string): Promise<Order> {
  const order = await this.orderRepository.findById(orderId);
  if (!order) {
    throw new NotFoundException('Order not found');
  }
  this.validateOrderStatus(order);
  this.validateOrderItems(order);
  return order;
}

private validateOrderStatus(order: Order): void {
  const invalidStatuses = ['cancelled', 'completed'];
  if (invalidStatuses.includes(order.status)) {
    throw new BadRequestException(`Order is ${order.status}`);
  }
}

private validateOrderItems(order: Order): void {
  if (order.items.length === 0) {
    throw new BadRequestException('Order has no items');
  }
}
```

### 3. 代码可靠性

#### 检查项

**错误处理**
- [ ] 是否正确处理异步错误
- [ ] 是否使用 try-catch 捕获异常
- [ ] 是否避免吞掉异常
- [ ] 错误信息是否清晰有用
- [ ] 是否正确使用 NestJS 异常类

**空值处理**
- [ ] 是否正确处理 null/undefined
- [ ] 是否使用可选链操作符（`?.`）
- [ ] 是否使用空值合并操作符（`??`）
- [ ] 是否避免空指针异常

**类型安全**
- [ ] 是否避免使用 `any` 类型
- [ ] 是否正确使用 TypeScript 类型
- [ ] 是否定义清晰的接口
- [ ] 是否使用枚举替代魔法数字

**边界条件**
- [ ] 是否测试空数组、空字符串
- [ ] 是否测试最大/最小值
- [ ] 是否测试边界情况
- [ ] 是否处理异常输入

**示例**：
```typescript
// 不好的做法：缺少错误处理
async getUser(userId: string) {
  const user = await this.userRepository.findById(userId);
  return user;
}

// 好的做法：完整的错误处理
async getUser(userId: string): Promise<User> {
  try {
    const user = await this.userRepository.findById(userId);
    if (!user) {
      throw new NotFoundException(`User with ID ${userId} not found`);
    }
    return user;
  } catch (error) {
    if (error instanceof NotFoundException) {
      throw error;
    }
    this.logger.error(`Failed to get user ${userId}`, error.stack);
    throw new InternalServerErrorException('Failed to retrieve user');
  }
}

// 不好的做法：使用 any
function processData(data: any) {
  return data.value * 2;
}

// 好的做法：使用类型
interface ProcessableData {
  value: number;
  unit: string;
}

function processData(data: ProcessableData): number {
  return data.value * 2;
}
```

### 4. 代码性能

#### 检查项

**数据库查询**
- [ ] 是否避免 N+1 查询问题
- [ ] 是否正确使用索引
- [ ] 是否使用查询构建器优化
- [ ] 是否避免不必要的字段查询
- [ ] 是否使用分页处理大数据集

**内存使用**
- [ ] 是否避免内存泄漏
- [ ] 是否正确释放资源
- [ ] 是否使用流处理大数据
- [ ] 是否避免不必要的数据复制

**异步处理**
- [ ] 是否正确使用 async/await
- [ ] 是否避免阻塞主线程
- [ ] 是否使用 Promise.all 并行处理
- [ ] 是否使用队列处理耗时任务

**缓存策略**
- [ ] 是否使用缓存减少数据库访问
- [ ] 缓存键设计是否合理
- [ ] 缓存失效策略是否正确
- [ ] 是否考虑缓存穿透和雪崩

**示例**：
```typescript
// 不好的做法：N+1 查询
async getUsersWithOrders() {
  const users = await this.userRepository.find();
  for (const user of users) {
    user.orders = await this.orderRepository.findByUserId(user.id);
  }
  return users;
}

// 好的做法：使用关联查询
async getUsersWithOrders() {
  return this.userRepository.find({
    relations: ['orders'],
  });
}

// 不好的做法：串行处理
async processItems(items: Item[]) {
  const results = [];
  for (const item of items) {
    const result = await this.processItem(item);
    results.push(result);
  }
  return results;
}

// 好的做法：并行处理
async processItems(items: Item[]) {
  return Promise.all(items.map(item => this.processItem(item)));
}
```

### 5. 代码安全性

#### 检查项

**输入验证**
- [ ] 是否验证所有用户输入
- [ ] 是否使用 class-validator
- [ ] 是否防止 SQL 注入
- [ ] 是否防止 XSS 攻击
- [ ] 是否限制输入长度

**认证授权**
- [ ] 是否实现身份认证
- [ ] 是否实现权限控制
- [ ] 是否使用 JWT 或其他安全令牌
- [ ] 敏感操作是否有额外验证

**敏感数据**
- [ ] 密码是否使用安全哈希
- [ ] 是否避免在日志中记录敏感信息
- [ ] API 响应是否过滤敏感字段
- [ ] 是否使用 HTTPS 传输

**依赖安全**
- [ ] 是否定期更新依赖
- [ ] 是否检查安全漏洞
- [ ] 是否避免使用不安全的依赖

**示例**：
```typescript
// 不好的做法：缺少输入验证
@Post('users')
async createUser(@Body() body: any) {
  return this.userService.create(body);
}

// 好的做法：完整的输入验证
export class CreateUserDto {
  @IsString()
  @IsNotEmpty()
  @MinLength(3)
  @MaxLength(50)
  name: string;

  @IsEmail()
  email: string;

  @IsString()
  @MinLength(8)
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
  password: string;
}

@Post('users')
async createUser(@Body() createUserDto: CreateUserDto) {
  return this.userService.create(createUserDto);
}

// 不好的做法：密码明文存储
async createUser(createUserDto: CreateUserDto) {
  const user = this.userRepository.create({
    ...createUserDto,
    password: createUserDto.password, // 不安全
  });
  return this.userRepository.save(user);
}

// 好的做法：密码哈希存储
async createUser(createUserDto: CreateUserDto) {
  const hashedPassword = await bcrypt.hash(createUserDto.password, 10);
  const user = this.userRepository.create({
    ...createUserDto,
    password: hashedPassword,
  });
  return this.userRepository.save(user);
}
```

### 6. 代码一致性

#### 检查项

**代码风格**
- [ ] 是否使用 ESLint 统一代码风格
- [ ] 是否使用 Prettier 格式化代码
- [ ] 是否遵循团队编码规范
- [ ] 是否使用相同的命名约定

**架构模式**
- [ ] 是否遵循一致的分层架构
- [ ] 是否使用相同的设计模式
- [ ] 是否遵循相同的目录结构
- [ ] 是否使用相同的错误处理方式

**工具配置**
- [ ] 是否统一使用 TypeScript
- [ ] 是否统一使用相同的构建工具
- [ ] 是否统一使用相同的测试框架
- [ ] 是否统一使用相同的包管理器

---

## 检查逻辑

### 自动化检查流程

```
开始检查
    ↓
运行 ESLint
    ↓
运行 Prettier 检查
    ↓
运行 TypeScript 类型检查
    ↓
运行单元测试
    ↓
计算测试覆盖率
    ↓
运行安全扫描
    ↓
生成质量报告
```

### 手动检查流程

```
准备检查
    ↓
选择检查范围
    ↓
逐项检查质量维度
    ↓
记录问题和建议
    ↓
评估严重程度
    ↓
生成改进计划
```

### 检查工具集成

#### 1. ESLint 配置

```typescript
// .eslintrc.js
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    project: 'tsconfig.json',
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint/eslint-plugin'],
  extends: [
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
  ],
  root: true,
  env: {
    node: true,
    jest: true,
  },
  ignorePatterns: ['.eslintrc.js'],
  rules: {
    '@typescript-eslint/interface-name-prefix': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    complexity: ['warn', 10],
    'max-lines-per-function': ['warn', 50],
    'max-depth': ['warn', 3],
  },
};
```

#### 2. Prettier 配置

```json
// .prettierrc
{
  "singleQuote": true,
  "trailingComma": "all",
  "tabWidth": 2,
  "semi": true,
  "printWidth": 120,
  "arrowParens": "avoid"
}
```

#### 3. TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "skipLibCheck": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "strictBindCallApply": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

---

## 评估标准

### 质量评分体系

| 质量维度 | 权重 | 满分 | 评估方法 |
|----------|------|------|----------|
| 代码可读性 | 20% | 20 | 代码审查 + 工具检查 |
| 代码可维护性 | 25% | 25 | 复杂度分析 + 重复度检查 |
| 代码可靠性 | 25% | 25 | 测试覆盖率 + 错误处理检查 |
| 代码性能 | 15% | 15 | 性能测试 + 代码分析 |
| 代码安全性 | 10% | 10 | 安全扫描 + 代码审查 |
| 代码一致性 | 5% | 5 | 风格检查 + 规范审查 |
| **总分** | **100%** | **100** | 综合评估 |

### 评分等级

| 等级 | 分数范围 | 行动建议 |
|------|----------|----------|
| 优秀 | 90-100 | 保持当前质量水平 |
| 良好 | 75-89 | 针对薄弱环节改进 |
| 合格 | 60-74 | 需要制定改进计划 |
| 需改进 | 0-59 | 需要立即重构 |

### 详细评分标准

#### 代码可读性（20分）

| 评分项 | 分值 | 评分标准 |
|--------|------|----------|
| 命名规范 | 6 | 优秀(6)：命名清晰一致；良好(4-5)：基本规范；需改进(0-3)：命名混乱 |
| 代码格式 | 4 | 优秀(4)：格式统一；良好(3)：基本统一；需改进(0-2)：格式混乱 |
| 注释质量 | 6 | 优秀(6)：注释完整准确；良好(4-5)：注释基本完整；需改进(0-3)：注释不足 |
| 代码组织 | 4 | 优秀(4)：结构清晰；良好(3)：结构基本清晰；需改进(0-2)：结构混乱 |

#### 代码可维护性（25分）

| 评分项 | 分值 | 评分标准 |
|--------|------|----------|
| 函数复杂度 | 8 | 优秀(8)：复杂度低；良好(5-7)：复杂度中等；需改进(0-4)：复杂度高 |
| 代码重复 | 7 | 优秀(7)：无重复；良好(4-6)：少量重复；需改进(0-3)：大量重复 |
| 模块耦合 | 6 | 优秀(6)：耦合度低；良好(4-5)：耦合度中等；需改进(0-3)：耦合度高 |
| 可扩展性 | 4 | 优秀(4)：易扩展；良好(3)：可扩展；需改进(0-2)：难扩展 |

#### 代码可靠性（25分）

| 评分项 | 分值 | 评分标准 |
|--------|------|----------|
| 错误处理 | 8 | 优秀(8)：处理完善；良好(5-7)：处理基本完善；需改进(0-4)：处理不足 |
| 空值处理 | 5 | 优秀(5)：处理完善；良好(3-4)：处理基本完善；需改进(0-2)：处理不足 |
| 类型安全 | 7 | 优秀(7)：类型安全；良好(4-6)：基本安全；需改进(0-3)：存在类型问题 |
| 测试覆盖 | 5 | 优秀(5)：覆盖率>80%；良好(3-4)：覆盖率60-80%；需改进(0-2)：覆盖率<60% |

#### 代码性能（15分）

| 评分项 | 分值 | 评分标准 |
|--------|------|----------|
| 数据库优化 | 5 | 优秀(5)：查询优化；良好(3-4)：基本优化；需改进(0-2)：存在性能问题 |
| 内存使用 | 4 | 优秀(4)：内存高效；良好(3)：内存基本合理；需改进(0-2)：存在内存问题 |
| 异步处理 | 3 | 优秀(3)：异步处理合理；良好(2)：基本合理；需改进(0-1)：存在阻塞 |
| 缓存策略 | 3 | 优秀(3)：缓存完善；良好(2)：缓存基本完善；需改进(0-1)：缺少缓存 |

#### 代码安全性（10分）

| 评分项 | 分值 | 评分标准 |
|--------|------|----------|
| 输入验证 | 4 | 优秀(4)：验证完善；良好(2-3)：验证基本完善；需改进(0-1)：验证不足 |
| 认证授权 | 3 | 优秀(3)：认证授权完善；良好(2)：基本完善；需改进(0-1)：存在安全问题 |
| 敏感数据 | 2 | 优秀(2)：保护完善；良好(1)：基本保护；需改进(0)：存在泄露风险 |
| 依赖安全 | 1 | 优秀(1)：无安全漏洞；良好(0.5)：少量漏洞；需改进(0)：存在严重漏洞 |

#### 代码一致性（5分）

| 评分项 | 分值 | 评分标准 |
|--------|------|----------|
| 代码风格 | 2 | 优秀(2)：风格统一；良好(1)：基本统一；需改进(0)：风格混乱 |
| 架构模式 | 2 | 优秀(2)：模式一致；良好(1)：基本一致；需改进(0)：模式混乱 |
| 工具配置 | 1 | 优秀(1)：配置统一；良好(0.5)：基本统一；需改进(0)：配置混乱 |

---

## 自动化检查

### CI/CD 集成

#### GitHub Actions 配置

```yaml
# .github/workflows/code-quality.yml
name: Code Quality Check

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Run Prettier check
        run: npm run format:check

      - name: Run TypeScript check
        run: npm run type-check

      - name: Run tests
        run: npm run test

      - name: Generate coverage report
        run: npm run test:cov

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

      - name: Run security audit
        run: npm audit

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### 质量门禁

#### 质量指标阈值

```typescript
// quality-gates.config.ts
export const qualityGates = {
  // 代码覆盖率
  coverage: {
    statements: 80,    // 语句覆盖率
    branches: 75,      // 分支覆盖率
    functions: 80,     // 函数覆盖率
    lines: 80,         // 行覆盖率
  },

  // 代码复杂度
  complexity: {
    maxCyclomaticComplexity: 10,  // 最大圈复杂度
    maxCognitiveComplexity: 15,   // 最大认知复杂度
    maxFunctionLines: 50,         // 最大函数行数
    maxFileLines: 500,            // 最大文件行数
  },

  // 重复度
  duplication: {
    maxDuplicationPercentage: 5,  // 最大重复率
  },

  // 安全性
  security: {
    maxVulnerabilitySeverity: 'moderate',  // 最大漏洞严重程度
    allowDependenciesWithVulnerabilities: false,
  },

  // 代码风格
  style: {
    maxLintWarnings: 10,  // 最大 Lint 警告数
    allowLintErrors: false,
  },
};
```

### 质量报告生成

#### 报告模板

```typescript
// quality-report-generator.ts
import { qualityGates } from './quality-gates.config';

interface QualityMetrics {
  coverage: {
    statements: number;
    branches: number;
    functions: number;
    lines: number;
  };
  complexity: {
    averageCyclomaticComplexity: number;
    maxCyclomaticComplexity: number;
    averageCognitiveComplexity: number;
  };
  duplication: {
    percentage: number;
    blocks: number;
  };
  security: {
    vulnerabilities: Vulnerability[];
  };
  style: {
    lintErrors: number;
    lintWarnings: number;
  };
}

interface QualityReport {
  overallScore: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  metrics: QualityMetrics;
  gatesPassed: boolean;
  issues: QualityIssue[];
}

interface QualityIssue {
  type: 'coverage' | 'complexity' | 'duplication' | 'security' | 'style';
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  location?: string;
  suggestion?: string;
}

export class QualityReportGenerator {
  generateReport(metrics: QualityMetrics): QualityReport {
    const overallScore = this.calculateOverallScore(metrics);
    const grade = this.calculateGrade(overallScore);
    const gatesPassed = this.checkQualityGates(metrics);
    const issues = this.identifyIssues(metrics);

    return {
      overallScore,
      grade,
      metrics,
      gatesPassed,
      issues,
    };
  }

  private calculateOverallScore(metrics: QualityMetrics): number {
    const coverageScore = this.calculateCoverageScore(metrics.coverage);
    const complexityScore = this.calculateComplexityScore(metrics.complexity);
    const duplicationScore = this.calculateDuplicationScore(metrics.duplication);
    const securityScore = this.calculateSecurityScore(metrics.security);
    const styleScore = this.calculateStyleScore(metrics.style);

    return (
      coverageScore * 0.25 +
      complexityScore * 0.25 +
      duplicationScore * 0.15 +
      securityScore * 0.25 +
      styleScore * 0.10
    );
  }

  private calculateGrade(score: number): 'A' | 'B' | 'C' | 'D' | 'F' {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  }

  private checkQualityGates(metrics: QualityMetrics): boolean {
    return (
      metrics.coverage.statements >= qualityGates.coverage.statements &&
      metrics.complexity.maxCyclomaticComplexity <= qualityGates.complexity.maxCyclomaticComplexity &&
      metrics.duplication.percentage <= qualityGates.duplication.maxDuplicationPercentage &&
      this.checkSecurityGates(metrics.security) &&
      metrics.style.lintErrors === 0
    );
  }

  private calculateCoverageScore(coverage: QualityMetrics['coverage']): number {
    const avgCoverage =
      (coverage.statements + coverage.branches + coverage.functions + coverage.lines) / 4;
    return Math.min(100, (avgCoverage / qualityGates.coverage.statements) * 100);
  }

  private calculateComplexityScore(complexity: QualityMetrics['complexity']): number {
    const normalizedComplexity =
      complexity.maxCyclomaticComplexity / qualityGates.complexity.maxCyclomaticComplexity;
    return Math.max(0, 100 - (normalizedComplexity - 1) * 50);
  }

  private calculateDuplicationScore(duplication: QualityMetrics['duplication']): number {
    const normalizedDuplication =
      duplication.percentage / qualityGates.duplication.maxDuplicationPercentage;
    return Math.max(0, 100 - (normalizedDuplication - 1) * 50);
  }

  private calculateSecurityScore(security: QualityMetrics['security']): number {
    const criticalVulns = security.vulnerabilities.filter(v => v.severity === 'critical').length;
    const highVulns = security.vulnerabilities.filter(v => v.severity === 'high').length;
    const mediumVulns = security.vulnerabilities.filter(v => v.severity === 'medium').length;

    const penalty = criticalVulns * 50 + highVulns * 25 + mediumVulns * 10;
    return Math.max(0, 100 - penalty);
  }

  private calculateStyleScore(style: QualityMetrics['style']): number {
    const penalty = style.lintErrors * 10 + style.lintWarnings * 2;
    return Math.max(0, 100 - penalty);
  }

  private checkSecurityGates(security: QualityMetrics['security']): boolean {
    if (!qualityGates.security.allowDependenciesWithVulnerabilities) {
      return security.vulnerabilities.length === 0;
    }

    const maxSeverity = qualityGates.security.maxVulnerabilitySeverity;
    const severityOrder = ['low', 'moderate', 'high', 'critical'];
    const maxSeverityIndex = severityOrder.indexOf(maxSeverity);

    return security.vulnerabilities.every(
      vuln => severityOrder.indexOf(vuln.severity) <= maxSeverityIndex
    );
  }

  private identifyIssues(metrics: QualityMetrics): QualityIssue[] {
    const issues: QualityIssue[] = [];

    // Coverage issues
    if (metrics.coverage.statements < qualityGates.coverage.statements) {
      issues.push({
        type: 'coverage',
        severity: 'high',
        description: `语句覆盖率 ${metrics.coverage.statements}% 低于目标 ${qualityGates.coverage.statements}%`,
        suggestion: '增加测试用例以提高覆盖率',
      });
    }

    // Complexity issues
    if (metrics.complexity.maxCyclomaticComplexity > qualityGates.complexity.maxCyclomaticComplexity) {
      issues.push({
        type: 'complexity',
        severity: 'medium',
        description: `最大圈复杂度 ${metrics.complexity.maxCyclomaticComplexity} 超过目标 ${qualityGates.complexity.maxCyclomaticComplexity}`,
        suggestion: '重构复杂函数以降低复杂度',
      });
    }

    // Duplication issues
    if (metrics.duplication.percentage > qualityGates.duplication.maxDuplicationPercentage) {
      issues.push({
        type: 'duplication',
        severity: 'medium',
        description: `代码重复率 ${metrics.duplication.percentage}% 超过目标 ${qualityGates.duplication.maxDuplicationPercentage}%`,
        suggestion: '提取重复代码为可复用函数',
      });
    }

    // Security issues
    metrics.security.vulnerabilities.forEach(vuln => {
      issues.push({
        type: 'security',
        severity: vuln.severity === 'critical' || vuln.severity === 'high' ? 'critical' : 'high',
        description: `安全漏洞: ${vuln.description}`,
        location: vuln.package,
        suggestion: '更新依赖包到安全版本',
      });
    });

    // Style issues
    if (metrics.style.lintErrors > 0) {
      issues.push({
        type: 'style',
        severity: 'medium',
        description: `存在 ${metrics.style.lintErrors} 个 Lint 错误`,
        suggestion: '运行 npm run lint 修复代码风格问题',
      });
    }

    return issues.sort((a, b) => {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      return severityOrder[a.severity] - severityOrder[b.severity];
    });
  }
}
```

---

## 质量改进

### 改进流程

```
识别问题
    ↓
分析原因
    ↓
制定计划
    ↓
实施改进
    ↓
验证效果
    ↓
持续监控
```

### 改进策略

#### 1. 技术债务管理

```typescript
// technical-debt-tracker.ts
interface TechnicalDebt {
  id: string;
  type: 'code' | 'architecture' | 'documentation' | 'testing';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  location: string;
  estimatedHours: number;
  createdAt: Date;
  status: 'open' | 'in-progress' | 'resolved';
}

export class TechnicalDebtTracker {
  private debts: TechnicalDebt[] = [];

  addDebt(debt: Omit<TechnicalDebt, 'id' | 'createdAt' | 'status'>): void {
    this.debts.push({
      ...debt,
      id: this.generateId(),
      createdAt: new Date(),
      status: 'open',
    });
  }

  resolveDebt(id: string): void {
    const debt = this.debts.find(d => d.id === id);
    if (debt) {
      debt.status = 'resolved';
    }
  }

  getDebtsBySeverity(severity: TechnicalDebt['severity']): TechnicalDebt[] {
    return this.debts.filter(d => d.severity === severity && d.status !== 'resolved');
  }

  getTotalEstimatedHours(): number {
    return this.debts
      .filter(d => d.status !== 'resolved')
      .reduce((sum, debt) => sum + debt.estimatedHours, 0);
  }

  private generateId(): string {
    return `debt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

#### 2. 重构优先级

```typescript
// refactoring-prioritizer.ts
interface RefactoringCandidate {
  file: string;
  line: number;
  type: 'complexity' | 'duplication' | 'smell';
  severity: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  description: string;
}

export class RefactoringPrioritizer {
  prioritize(candidates: RefactoringCandidate[]): RefactoringCandidate[] {
    return candidates
      .map(candidate => ({
        ...candidate,
        priority: this.calculatePriority(candidate),
      }))
      .sort((a, b) => b.priority - a.priority);
  }

  private calculatePriority(candidate: RefactoringCandidate): number {
    const severityScore = { low: 1, medium: 2, high: 3 };
    const impactScore = { low: 1, medium: 2, high: 3 };
    const effortScore = { low: 3, medium: 2, high: 1 };

    return (
      severityScore[candidate.severity] * 3 +
      impactScore[candidate.impact] * 2 +
      effortScore[candidate.effort] * 1
    );
  }
}
```

### 持续改进

#### 质量趋势分析

```typescript
// quality-trend-analyzer.ts
interface QualitySnapshot {
  date: Date;
  score: number;
  coverage: number;
  complexity: number;
  duplication: number;
  issues: number;
}

export class QualityTrendAnalyzer {
  private snapshots: QualitySnapshot[] = [];

  addSnapshot(snapshot: Omit<QualitySnapshot, 'date'>): void {
    this.snapshots.push({
      ...snapshot,
      date: new Date(),
    });
  }

  getTrend(period: 'week' | 'month' | 'quarter'): TrendReport {
    const relevantSnapshots = this.getRelevantSnapshots(period);
    const latest = relevantSnapshots[relevantSnapshots.length - 1];
    const earliest = relevantSnapshots[0];

    return {
      period,
      scoreChange: latest.score - earliest.score,
      coverageChange: latest.coverage - earliest.coverage,
      complexityChange: latest.complexity - earliest.complexity,
      duplicationChange: latest.duplication - earliest.duplication,
      issuesChange: latest.issues - earliest.issues,
      trend: this.determineTrend(latest.score, earliest.score),
    };
  }

  private getRelevantSnapshots(period: string): QualitySnapshot[] {
    const now = new Date();
    const startDate = new Date();

    switch (period) {
      case 'week':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case 'quarter':
        startDate.setMonth(now.getMonth() - 3);
        break;
    }

    return this.snapshots.filter(s => s.date >= startDate);
  }

  private determineTrend(latest: number, earliest: number): 'improving' | 'stable' | 'declining' {
    const change = latest - earliest;
    if (change > 5) return 'improving';
    if (change < -5) return 'declining';
    return 'stable';
  }
}

interface TrendReport {
  period: string;
  scoreChange: number;
  coverageChange: number;
  complexityChange: number;
  duplicationChange: number;
  issuesChange: number;
  trend: 'improving' | 'stable' | 'declining';
}
```

---

## 总结

代码质量检查是确保软件质量的重要环节。通过系统化的检查流程、明确的评估标准和自动化工具，可以：

1. **持续提升代码质量**：通过定期检查和改进
2. **降低维护成本**：减少技术债务和 bug
3. **提高开发效率**：统一的规范和工具支持
4. **增强团队协作**：一致的代码风格和质量标准

建立完善的代码质量检查体系，结合 CI/CD 自动化和持续改进机制，可以确保项目的长期健康发展。
