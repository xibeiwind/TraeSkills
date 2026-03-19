# TypeORM 集成指南

## 安装依赖

```bash
npm install @nestjs/typeorm typeorm
npm install mysql2  # MySQL驱动
# 或
npm install pg  # PostgreSQL驱动
# 或
npm install sqlite3  # SQLite驱动
```

## 项目级别配置

### 基本配置

在 `app.module.ts` 文件中配置 TypeORM：

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql', // 数据库类型: mysql, postgres, sqlite, mssql, oracle
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'nestjs_db',
      entities: [__dirname + '/**/*.entity{.ts,.js}'], // 使用通配符路径自动加载实体
      synchronize: true, // 自动同步数据库结构（生产环境建议关闭）
      logging: true, // 启用SQL日志
      timezone: '+08:00', // 时区设置
      charset: 'utf8mb4', // 字符集
      extra: {
        connectionLimit: 10, // 连接池大小
      },
    }),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
```

### 环境变量集成

使用 `@nestjs/config` 从环境变量读取配置：

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: configService.get<'mysql' | 'postgres' | 'sqlite'>('DATABASE_TYPE', 'mysql'),
        host: configService.get('DATABASE_HOST', 'localhost'),
        port: configService.get<number>('DATABASE_PORT', 3306),
        username: configService.get('DATABASE_USERNAME', 'root'),
        password: configService.get('DATABASE_PASSWORD', ''),
        database: configService.get('DATABASE_NAME', 'nestjs_db'),
        entities: [__dirname + '/**/*.entity{.ts,.js}'], // 使用通配符路径自动加载实体
        synchronize: configService.get('DATABASE_SYNCHRONIZE', false),
        logging: configService.get('DATABASE_LOGGING', false),
        timezone: configService.get('DATABASE_TIMEZONE', '+08:00'),
        charset: configService.get('DATABASE_CHARSET', 'utf8mb4'),
        extra: {
          connectionLimit: configService.get('DATABASE_CONNECTION_LIMIT', 10),
        },
      }),
    }),
  ],
})
export class AppModule {}
```

### 多数据源配置

配置多个数据源：

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      name: 'default',
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: configService.get('DATABASE_TYPE', 'mysql'),
        host: configService.get('DATABASE_HOST', 'localhost'),
        port: configService.get('DATABASE_PORT', 3306),
        username: configService.get('DATABASE_USERNAME', 'root'),
        password: configService.get('DATABASE_PASSWORD', ''),
        database: configService.get('DATABASE_NAME', 'nestjs_db'),
        entities: [__dirname + '/**/*.entity{.ts,.js}'], // 使用通配符路径自动加载实体
        synchronize: false,
        logging: configService.get('DATABASE_LOGGING', false),
      }),
    }),
    TypeOrmModule.forRootAsync({
      name: 'secondary',
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: configService.get('SECONDARY_DATABASE_TYPE', 'postgres'),
        host: configService.get('SECONDARY_DATABASE_HOST', 'localhost'),
        port: configService.get('SECONDARY_DATABASE_PORT', 5432),
        username: configService.get('SECONDARY_DATABASE_USERNAME', 'postgres'),
        password: configService.get('SECONDARY_DATABASE_PASSWORD', ''),
        database: configService.get('SECONDARY_DATABASE_NAME', 'nestjs_secondary_db'),
        entities: [__dirname + '/**/*.entity{.ts,.js}'], // 使用通配符路径自动加载实体
        synchronize: false,
        logging: configService.get('DATABASE_LOGGING', false),
      }),
    }),
  ],
})
export class AppModule {}
```

## 迁移管理

### 配置迁移命令

在 `package.json` 中添加迁移命令：

```json
{
  "scripts": {
    "typeorm": "ts-node -r tsconfig-paths/register ./node_modules/typeorm/cli.js",
    "migration:generate": "npm run typeorm -- migration:generate -d src/database/data-source.ts",
    "migration:run": "npm run typeorm -- migration:run -d src/database/data-source.ts",
    "migration:revert": "npm run typeorm -- migration:revert -d src/database/data-source.ts"
  }
}
```

### 创建数据源配置文件

创建 `src/database/data-source.ts` 文件：

```typescript
import { DataSource } from 'typeorm';
import { ConfigService } from '@nestjs/config';
import * as dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

const configService = new ConfigService();

export const AppDataSource = new DataSource({
  type: configService.get<'mysql' | 'postgres' | 'sqlite'>('DATABASE_TYPE', 'mysql'),
  host: configService.get('DATABASE_HOST', 'localhost'),
  port: configService.get<number>('DATABASE_PORT', 3306),
  username: configService.get('DATABASE_USERNAME', 'root'),
  password: configService.get('DATABASE_PASSWORD', ''),
  database: configService.get('DATABASE_NAME', 'nestjs_db'),
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  migrations: [__dirname + '/migrations/*{.ts,.js}'],
  synchronize: false,
  logging: configService.get('DATABASE_LOGGING', false),
});
```

### 迁移命令示例

```bash
# 生成迁移文件
npm run migration:generate -- -n CreateUsersTable

# 运行迁移
npm run migration:run

# 回滚迁移
npm run migration:revert
```

## 最佳实践

1. **生产环境关闭 synchronize**：在生产环境中应该使用迁移而不是自动同步
2. **使用环境变量**：敏感信息如数据库密码应该使用环境变量
3. **连接池配置**：根据应用负载合理配置连接池大小
4. **使用通配符路径**：使用 `__dirname + '/**/*.entity{.ts,.js}'` 自动加载实体
5. **迁移管理**：使用 TypeORM 迁移功能管理数据库结构变更
6. **错误处理**：妥善处理数据库操作中的异常
7. **日志配置**：根据环境合理配置日志级别
8. **时区设置**：正确设置数据库时区，避免时间处理问题

## 数据库类型配置示例

### MySQL 配置

```typescript
TypeOrmModule.forRoot({
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  username: 'root',
  password: 'password',
  database: 'nestjs_db',
  entities: [__dirname + '/**/*.entity{.ts,.js}'],
  synchronize: false,
  logging: true,
  timezone: '+08:00',
  charset: 'utf8mb4',
  extra: {
    connectionLimit: 10,
  },
});
```

### PostgreSQL 配置

```typescript
TypeOrmModule.forRoot({
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  username: 'postgres',
  password: 'postgres',
  database: 'nestjs_db',
  entities: [__dirname + '/**/*.entity{.ts,.js}'],
  synchronize: false,
  logging: true,
  extra: {
    max: 10,
  },
});
```

### SQLite 配置

```typescript
TypeOrmModule.forRoot({
  type: 'sqlite',
  database: 'nestjs.db',
  entities: [__dirname + '/**/*.entity{.ts,.js}'],
  synchronize: true,
  logging: true,
});
```

## 总结

TypeORM 是 NestJS 中常用的 ORM 框架，通过本文档的配置指南，您可以：

1. 快速配置 TypeORM 连接到不同类型的数据库
2. 使用环境变量管理数据库配置
3. 配置多数据源支持
4. 使用迁移管理数据库结构变更
5. 遵循 TypeORM 最佳实践

通过使用通配符路径自动加载实体，您可以专注于业务逻辑的实现，而不需要手动管理实体配置。