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

## 配置文件示例

### app.module.ts 配置

```typescript
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { User } from './entities/user.entity';
import { Role } from './entities/role.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql', // 数据库类型: mysql, postgres, sqlite, mssql, oracle
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'nestjs_db',
      entities: [User, Role], // 实体列表
      synchronize: true, // 自动同步数据库结构（生产环境建议关闭）
      logging: true, // 启用SQL日志
      timezone: '+08:00', // 时区设置
      charset: 'utf8mb4', // 字符集
      extra: {
        connectionLimit: 10, // 连接池大小
      },
    }),
    TypeOrmModule.forFeature([User, Role]), // 注册实体到模块
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
```

### 环境变量配置

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
        type: configService.get<'mysql' | 'postgres'>('DB_TYPE', 'mysql'),
        host: configService.get('DB_HOST', 'localhost'),
        port: configService.get<number>('DB_PORT', 3306),
        username: configService.get('DB_USERNAME', 'root'),
        password: configService.get('DB_PASSWORD', ''),
        database: configService.get('DB_DATABASE', 'nestjs_db'),
        entities: [__dirname + '/**/*.entity{.ts,.js}'],
        synchronize: configService.get('DB_SYNCHRONIZE', false),
        logging: configService.get('DB_LOGGING', false),
      }),
    }),
  ],
})
export class AppModule {}
```

### 多数据源配置

```typescript
@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      name: 'default',
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: 'mysql',
        host: configService.get('DB_HOST'),
        port: configService.get('DB_PORT'),
        username: configService.get('DB_USERNAME'),
        password: configService.get('DB_PASSWORD'),
        database: configService.get('DB_DATABASE'),
        entities: [User],
        synchronize: false,
      }),
    }),
    TypeOrmModule.forRootAsync({
      name: 'secondary',
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get('SECONDARY_DB_HOST'),
        port: configService.get('SECONDARY_DB_PORT'),
        username: configService.get('SECONDARY_DB_USERNAME'),
        password: configService.get('SECONDARY_DB_PASSWORD'),
        database: configService.get('SECONDARY_DB_DATABASE'),
        entities: [Log],
        synchronize: false,
      }),
    }),
  ],
})
export class AppModule {}
```

## 实体定义示例

### 基础实体

```typescript
import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 50, unique: true })
  username: string;

  @Column({ type: 'varchar', length: 255 })
  password: string;

  @Column({ type: 'varchar', length: 100, nullable: true })
  email: string;

  @Column({ type: 'int', default: 0 })
  age: number;

  @Column({ type: 'boolean', default: true })
  isActive: boolean;

  @CreateDateColumn({ type: 'timestamp' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt: Date;
}
```

### 一对一关系

```typescript
import { Entity, PrimaryGeneratedColumn, Column, OneToOne, JoinColumn } from 'typeorm';

@Entity('profiles')
export class Profile {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 100 })
  firstName: string;

  @Column({ type: 'varchar', length: 100 })
  lastName: string;

  @Column({ type: 'text', nullable: true })
  bio: string;

  @OneToOne(() => User, (user) => user.profile)
  @JoinColumn()
  user: User;
}

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 50, unique: true })
  username: string;

  @OneToOne(() => Profile, (profile) => profile.user, { cascade: true })
  profile: Profile;
}
```

### 一对多关系

```typescript
import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from 'typeorm';

@Entity('categories')
export class Category {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 100 })
  name: string;

  @OneToMany(() => Product, (product) => product.category)
  products: Product[];
}

@Entity('products')
export class Product {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 200 })
  name: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  price: number;

  @ManyToOne(() => Category, (category) => category.products)
  @JoinColumn({ name: 'categoryId' })
  category: Category;
}
```

### 多对多关系

```typescript
import { Entity, PrimaryGeneratedColumn, Column, ManyToMany, JoinTable } from 'typeorm';

@Entity('roles')
export class Role {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 50 })
  name: string;

  @ManyToMany(() => Permission, (permission) => permission.roles)
  @JoinTable({
    name: 'role_permissions',
    joinColumn: { name: 'roleId', referencedColumnName: 'id' },
    inverseJoinColumn: { name: 'permissionId', referencedColumnName: 'id' }
  })
  permissions: Permission[];
}

@Entity('permissions')
export class Permission {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'varchar', length: 100 })
  name: string;

  @ManyToMany(() => Role, (role) => role.permissions)
  roles: Role[];
}
```

### 使用装饰器的完整实体

```typescript
import { 
  Entity, 
  PrimaryGeneratedColumn, 
  Column, 
  CreateDateColumn, 
  UpdateDateColumn,
  VersionColumn,
  Index,
  Unique
} from 'typeorm';

@Entity('articles')
@Unique(['slug'])
@Index(['authorId', 'status'])
export class Article {
  @PrimaryGeneratedColumn('increment')
  id: number;

  @Column({ type: 'varchar', length: 200 })
  title: string;

  @Column({ type: 'varchar', length: 255, unique: true })
  slug: string;

  @Column({ type: 'text', nullable: true })
  content: string;

  @Column({ type: 'enum', enum: ['draft', 'published', 'archived'], default: 'draft' })
  status: 'draft' | 'published' | 'archived';

  @Column({ type: 'int', name: 'authorId' })
  authorId: number;

  @Column({ type: 'json', nullable: true })
  metadata: Record<string, any>;

  @Column({ type: 'timestamp', nullable: true })
  publishedAt: Date;

  @CreateDateColumn({ name: 'createdAt', type: 'timestamp' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updatedAt', type: 'timestamp' })
  updatedAt: Date;

  @VersionColumn()
  version: number;
}
```

## Repository 使用示例

### Service 中使用 Repository

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async create(userData: Partial<User>): Promise<User> {
    const user = this.userRepository.create(userData);
    return await this.userRepository.save(user);
  }

  async findAll(): Promise<User[]> {
    return await this.userRepository.find();
  }

  async findOne(id: number): Promise<User> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  }

  async findByUsername(username: string): Promise<User> {
    return await this.userRepository.findOne({ where: { username } });
  }

  async update(id: number, userData: Partial<User>): Promise<User> {
    await this.userRepository.update(id, userData);
    return this.findOne(id);
  }

  async remove(id: number): Promise<void> {
    const result = await this.userRepository.delete(id);
    if (result.affected === 0) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
  }
}
```

### 高级查询示例

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like, Between, In, MoreThan, LessThan } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  // 分页查询
  async paginate(page: number = 1, limit: number = 10): Promise<{ data: User[]; total: number }> {
    const [data, total] = await this.userRepository.findAndCount({
      skip: (page - 1) * limit,
      take: limit,
      order: { createdAt: 'DESC' },
    });
    return { data, total };
  }

  // 模糊查询
  async search(keyword: string): Promise<User[]> {
    return await this.userRepository.find({
      where: [
        { username: Like(`%${keyword}%`) },
        { email: Like(`%${keyword}%`) },
      ],
    });
  }

  // 范围查询
  async findByAgeRange(minAge: number, maxAge: number): Promise<User[]> {
    return await this.userRepository.find({
      where: {
        age: Between(minAge, maxAge),
      },
    });
  }

  // IN 查询
  async findByIds(ids: number[]): Promise<User[]> {
    return await this.userRepository.find({
      where: { id: In(ids) },
    });
  }

  // 比较查询
  async findActiveUsers(): Promise<User[]> {
    return await this.userRepository.find({
      where: { isActive: true },
    });
  }

  // 关联查询
  async findWithProfile(userId: number): Promise<User> {
    return await this.userRepository.findOne({
      where: { id: userId },
      relations: ['profile'],
    });
  }

  // 多重关联查询
  async findWithRelations(userId: number): Promise<User> {
    return await this.userRepository.findOne({
      where: { id: userId },
      relations: ['profile', 'roles', 'roles.permissions'],
    });
  }

  // 选择特定字段
  async findSelectFields(): Promise<Partial<User>[]> {
    return await this.userRepository.find({
      select: ['id', 'username', 'email'],
    });
  }

  // 排序和限制
  async findTopUsers(limit: number): Promise<User[]> {
    return await this.userRepository.find({
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }
}
```

### 使用 QueryBuilder

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async findActiveUsersWithQueryBuilder(): Promise<User[]> {
    return await this.userRepository
      .createQueryBuilder('user')
      .where('user.isActive = :isActive', { isActive: true })
      .orderBy('user.createdAt', 'DESC')
      .getMany();
  }

  async findUsersWithRole(roleName: string): Promise<User[]> {
    return await this.userRepository
      .createQueryBuilder('user')
      .leftJoinAndSelect('user.roles', 'role')
      .where('role.name = :roleName', { roleName })
      .getMany();
  }

  async countActiveUsers(): Promise<number> {
    return await this.userRepository
      .createQueryBuilder('user')
      .where('user.isActive = :isActive', { isActive: true })
      .getCount();
  }

  async findUsersWithPagination(page: number, limit: number): Promise<User[]> {
    return await this.userRepository
      .createQueryBuilder('user')
      .skip((page - 1) * limit)
      .take(limit)
      .getMany();
  }

  async updateUserStatus(userId: number, isActive: boolean): Promise<void> {
    await this.userRepository
      .createQueryBuilder()
      .update(User)
      .set({ isActive })
      .where('id = :id', { id: userId })
      .execute();
  }

  async softDeleteUser(userId: number): Promise<void> {
    await this.userRepository
      .createQueryBuilder()
      .softDelete()
      .from(User)
      .where('id = :id', { id: userId })
      .execute();
  }
}
```

### 事务处理

```typescript
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource } from 'typeorm';
import { User } from './entities/user.entity';
import { Profile } from './entities/profile.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(Profile)
    private profileRepository: Repository<Profile>,
    private dataSource: DataSource,
  ) {}

  async createUserWithProfile(userData: Partial<User>, profileData: Partial<Profile>): Promise<User> {
    const queryRunner = this.dataSource.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      const user = queryRunner.manager.create(User, userData);
      const savedUser = await queryRunner.manager.save(user);

      const profile = queryRunner.manager.create(Profile, {
        ...profileData,
        userId: savedUser.id,
      });
      await queryRunner.manager.save(profile);

      await queryRunner.commitTransaction();
      return savedUser;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      throw error;
    } finally {
      await queryRunner.release();
    }
  }
}
```

## 迁移管理

### 创建迁移

```bash
npm run typeorm migration:generate -- -n CreateUserTable
```

### 运行迁移

```bash
npm run typeorm migration:run
```

### 回滚迁移

```bash
npm run typeorm migration:revert
```

## 最佳实践

1. **生产环境关闭 synchronize**：在生产环境中应该使用迁移而不是自动同步
2. **使用环境变量**：敏感信息如数据库密码应该使用环境变量
3. **连接池配置**：根据应用负载合理配置连接池大小
4. **索引优化**：为经常查询的字段添加索引
5. **软删除**：考虑使用软删除而不是物理删除
6. **DTO 验证**：使用 class-validator 对输入数据进行验证
7. **错误处理**：妥善处理数据库操作中的异常
