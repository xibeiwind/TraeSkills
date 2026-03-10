# 实体/模型定义最佳实践

## 命名规范

### 表名和字段名

```typescript
// 推荐：使用复数形式作为表名
@Entity('users') // TypeORM
@Table({ tableName: 'users' }) // Sequelize

// 推荐：使用驼峰命名法定义属性，数据库使用下划线命名
@Column({ name: 'first_name' }) // TypeORM
@Column({ field: 'first_name' }) // Sequelize
firstName: string;

// 推荐：使用有意义的字段名
// 不推荐
@Column()
n1: string;

// 推荐
@Column({ name: 'user_name' })
username: string;
```

### 类名和属性名

```typescript
// 推荐：使用单数形式作为实体类名
export class User {} // 正确
export class Users {} // 不推荐

// 推荐：使用描述性的属性名
export class Article {
  @Column()
  title: string; // 清晰

  @Column()
  t: string; // 不清晰
}
```

## 主键设计

### 自增主键

```typescript
// TypeORM
@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;
}
```

### UUID 主键

```typescript
// TypeORM
@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({
    type: DataType.UUID,
    defaultValue: DataType.UUIDV4,
    primaryKey: true,
  })
  id: string;
}
```

### 复合主键

```typescript
// TypeORM
@Entity('user_roles')
export class UserRole {
  @PrimaryColumn()
  userId: number;

  @PrimaryColumn()
  roleId: number;
}

// Sequelize
@Table({ tableName: 'user_roles' })
export class UserRole extends Model<UserRole> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
  })
  userId: number;

  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
  })
  roleId: number;
}
```

## 字段类型选择

### 字符串类型

```typescript
// TypeORM
@Column({ type: 'varchar', length: 50 }) // 固定长度
@Column({ type: 'text' }) // 不定长度文本
@Column({ type: 'char', length: 1 }) // 固定长度字符

// Sequelize
@Column({ type: DataType.STRING(50) }) // 固定长度
@Column({ type: DataType.TEXT }) // 不定长度文本
@Column({ type: DataType.CHAR(1) }) // 固定长度字符
```

### 数值类型

```typescript
// TypeORM
@Column({ type: 'int' }) // 整数
@Column({ type: 'bigint' }) // 大整数
@Column({ type: 'decimal', precision: 10, scale: 2 }) // 精确小数
@Column({ type: 'float' }) // 浮点数
@Column({ type: 'boolean' }) // 布尔值

// Sequelize
@Column({ type: DataType.INTEGER }) // 整数
@Column({ type: DataType.BIGINT }) // 大整数
@Column({ type: DataType.DECIMAL(10, 2) }) // 精确小数
@Column({ type: DataType.FLOAT }) // 浮点数
@Column({ type: DataType.BOOLEAN }) // 布尔值
```

### 日期时间类型

```typescript
// TypeORM
@Column({ type: 'date' }) // 日期
@Column({ type: 'time' }) // 时间
@Column({ type: 'datetime' }) // 日期时间
@Column({ type: 'timestamp' }) // 时间戳

// Sequelize
@Column({ type: DataType.DATE }) // 日期时间
@Column({ type: DataType.DATEONLY }) // 仅日期
```

### JSON 类型

```typescript
// TypeORM
@Column({ type: 'json' }) // JSON 对象
@Column({ type: 'jsonb' }) // PostgreSQL 的 JSONB

// Sequelize
@Column({ type: DataType.JSON }) // JSON 对象
@Column({ type: DataType.JSONB }) // PostgreSQL 的 JSONB
```

### 枚举类型

```typescript
// TypeORM
@Column({
  type: 'enum',
  enum: ['active', 'inactive', 'pending'],
  default: 'pending'
})
status: 'active' | 'inactive' | 'pending';

// Sequelize
@Column({
  type: DataType.ENUM('active', 'inactive', 'pending'),
  defaultValue: 'pending'
})
status: 'active' | 'inactive' | 'pending';
```

## 索引优化

### 单列索引

```typescript
// TypeORM
@Entity('users')
@Index(['email'])
export class User {
  @Column({ unique: true })
  email: string;
}

// Sequelize
@Table({
  tableName: 'users',
  indexes: [
    {
      fields: ['email'],
      unique: true,
    },
  ],
})
export class User extends Model<User> {
  @Column({ unique: true })
  email: string;
}
```

### 复合索引

```typescript
// TypeORM
@Entity('articles')
@Index(['authorId', 'status'])
export class Article {
  @Column({ name: 'author_id' })
  authorId: number;

  @Column()
  status: string;
}

// Sequelize
@Table({
  tableName: 'articles',
  indexes: [
    {
      fields: ['authorId', 'status'],
    },
  ],
})
export class Article extends Model<Article> {
  @Column({ field: 'author_id' })
  authorId: number;

  @Column()
  status: string;
}
```

### 全文索引

```typescript
// TypeORM (PostgreSQL)
@Entity('articles')
export class Article {
  @Column({ type: 'tsvector' })
  searchVector: string;

  @Index('article_search_idx', { fulltext: true })
  @Column()
  content: string;
}
```

## 关系设计

### 一对一关系

```typescript
// TypeORM
@Entity('profiles')
export class Profile {
  @OneToOne(() => User, (user) => user.profile)
  @JoinColumn()
  user: User;
}

@Entity('users')
export class User {
  @OneToOne(() => Profile, (profile) => profile.user, { cascade: true })
  profile: Profile;
}

// Sequelize
@Table({ tableName: 'profiles' })
export class Profile extends Model<Profile> {
  @ForeignKey(() => User)
  @Column({ field: 'user_id' })
  userId: number;

  @BelongsTo(() => User)
  user: User;
}

@Table({ tableName: 'users' })
export class User extends Model<User> {
  @HasOne(() => Profile)
  profile: Profile;
}
```

### 一对多关系

```typescript
// TypeORM
@Entity('categories')
export class Category {
  @OneToMany(() => Product, (product) => product.category)
  products: Product[];
}

@Entity('products')
export class Product {
  @ManyToOne(() => Category, (category) => category.products)
  @JoinColumn({ name: 'category_id' })
  category: Category;
}

// Sequelize
@Table({ tableName: 'categories' })
export class Category extends Model<Category> {
  @HasMany(() => Product)
  products: Product[];
}

@Table({ tableName: 'products' })
export class Product extends Model<Product> {
  @ForeignKey(() => Category)
  @Column({ field: 'category_id' })
  categoryId: number;

  @BelongsTo(() => Category)
  category: Category;
}
```

### 多对多关系

```typescript
// TypeORM
@Entity('roles')
export class Role {
  @ManyToMany(() => Permission, (permission) => permission.roles)
  @JoinTable({
    name: 'role_permissions',
    joinColumn: { name: 'role_id' },
    inverseJoinColumn: { name: 'permission_id' }
  })
  permissions: Permission[];
}

@Entity('permissions')
export class Permission {
  @ManyToMany(() => Role, (role) => role.permissions)
  roles: Role[];
}

// Sequelize
@Table({ tableName: 'roles' })
export class Role extends Model<Role> {
  @BelongsToMany(() => Permission, () => RolePermission)
  permissions: Permission[];
}

@Table({ tableName: 'permissions' })
export class Permission extends Model<Permission> {
  @BelongsToMany(() => Role, () => RolePermission)
  roles: Role[];
}

@Table({ tableName: 'role_permissions' })
export class RolePermission extends Model<RolePermission> {
  @ForeignKey(() => Role)
  @Column({ field: 'role_id' })
  roleId: number;

  @ForeignKey(() => Permission)
  @Column({ field: 'permission_id' })
  permissionId: number;
}
```

## 时间戳管理

### 自动时间戳

```typescript
// TypeORM
@Entity('users')
export class User {
  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  @DeleteDateColumn({ name: 'deleted_at', nullable: true })
  deletedAt: Date;
}

// Sequelize
@Table({
  tableName: 'users',
  timestamps: true,
  underscored: true,
  paranoid: true, // 启用软删除
})
export class User extends Model<User> {
  @CreatedAt
  @Column({ field: 'created_at' })
  createdAt: Date;

  @UpdatedAt
  @Column({ field: 'updated_at' })
  updatedAt: Date;

  @DeletedAt
  @Column({ field: 'deleted_at' })
  deletedAt: Date;
}
```

### 自定义时间戳

```typescript
// TypeORM
@Entity('articles')
export class Article {
  @Column({ type: 'timestamp', nullable: true })
  publishedAt: Date;

  @Column({ type: 'timestamp', nullable: true })
  archivedAt: Date;
}

// Sequelize
@Table({ tableName: 'articles' })
export class Article extends Model<Article> {
  @Column({ type: DataType.DATE, field: 'published_at', allowNull: true })
  publishedAt: Date;

  @Column({ type: DataType.DATE, field: 'archived_at', allowNull: true })
  archivedAt: Date;
}
```

## 数据验证

### 必填字段

```typescript
// TypeORM
@Entity('users')
export class User {
  @Column({ nullable: false })
  username: string;
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({ allowNull: false })
  username: string;
}
```

### 唯一约束

```typescript
// TypeORM
@Entity('users')
export class User {
  @Column({ unique: true })
  email: string;
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({ unique: true })
  email: string;
}
```

### 默认值

```typescript
// TypeORM
@Entity('users')
export class User {
  @Column({ default: true })
  isActive: boolean;

  @Column({ default: 0 })
  loginCount: number;
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({ defaultValue: true })
  isActive: boolean;

  @Column({ defaultValue: 0 })
  loginCount: number;
}
```

### 长度限制

```typescript
// TypeORM
@Entity('users')
export class User {
  @Column({ type: 'varchar', length: 50 })
  username: string;

  @Column({ type: 'varchar', length: 255 })
  password: string;
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({ type: DataType.STRING(50) })
  username: string;

  @Column({ type: DataType.STRING(255) })
  password: string;
}
```

## 软删除

### TypeORM 软删除

```typescript
import { 
  Entity, 
  Column, 
  DeleteDateColumn,
} from 'typeorm';

@Entity('users')
export class User {
  @DeleteDateColumn({ name: 'deleted_at', nullable: true })
  deletedAt: Date;
}

// 使用软删除
await userRepository.softDelete(userId);

// 恢复软删除
await userRepository.restore(userId);

// 查找软删除的记录
await userRepository.find({ withDeleted: true });

// 只查找软删除的记录
await userRepository.find({ onlyDeleted: true });
```

### Sequelize 软删除

```typescript
import { Table, Column, DeletedAt } from 'sequelize-typescript';

@Table({
  tableName: 'users',
  paranoid: true, // 启用软删除
})
export class User extends Model<User> {
  @DeletedAt
  @Column({ field: 'deleted_at' })
  deletedAt: Date;
}

// 使用软删除
await user.destroy();

// 恢复软删除
await user.restore();

// 查找软删除的记录
await User.findAll({ paranoid: false });
```

## 版本控制

### TypeORM 版本控制

```typescript
import { VersionColumn } from 'typeorm';

@Entity('articles')
export class Article {
  @VersionColumn()
  version: number;
}
```

### Sequelize 版本控制

```typescript
@Table({ tableName: 'articles' })
export class Article extends Model<Article> {
  @Column({ type: DataType.INTEGER, defaultValue: 0 })
  version: number;
}
```

## 基础实体类

### TypeORM 基础实体

```typescript
import { 
  PrimaryGeneratedColumn, 
  CreateDateColumn, 
  UpdateDateColumn, 
  DeleteDateColumn,
  VersionColumn 
} from 'typeorm';

export abstract class BaseEntity {
  @PrimaryGeneratedColumn()
  id: number;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  @DeleteDateColumn({ name: 'deleted_at', nullable: true })
  deletedAt: Date;

  @VersionColumn()
  version: number;
}

// 使用基础实体
@Entity('users')
export class User extends BaseEntity {
  @Column({ type: 'varchar', length: 50 })
  username: string;
}
```

### Sequelize 基础模型

```typescript
import { 
  Table, 
  Column, 
  Model, 
  CreatedAt, 
  UpdatedAt, 
  DeletedAt,
  DataType 
} from 'sequelize-typescript';

@Table({
  timestamps: true,
  underscored: true,
  paranoid: true,
})
export abstract class BaseModel<T extends Model<T>> extends Model<T> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @CreatedAt
  @Column({ field: 'created_at' })
  createdAt: Date;

  @UpdatedAt
  @Column({ field: 'updated_at' })
  updatedAt: Date;

  @DeletedAt
  @Column({ field: 'deleted_at' })
  deletedAt: Date;

  @Column({ type: DataType.INTEGER, defaultValue: 0 })
  version: number;
}

// 使用基础模型
@Table({ tableName: 'users' })
export class User extends BaseModel<User> {
  @Column({ type: DataType.STRING(50) })
  username: string;
}
```

## 性能优化

### 选择性加载

```typescript
// TypeORM
userRepository.find({
  select: ['id', 'username', 'email'],
});

// Sequelize
User.findAll({
  attributes: ['id', 'username', 'email'],
});
```

### 关联加载优化

```typescript
// TypeORM
userRepository.find({
  relations: ['profile'],
});

// Sequelize
User.findAll({
  include: ['profile'],
});
```

### 分页查询

```typescript
// TypeORM
userRepository.find({
  skip: 0,
  take: 10,
  order: { createdAt: 'DESC' },
});

// Sequelize
User.findAll({
  offset: 0,
  limit: 10,
  order: [['createdAt', 'DESC']],
});
```

## 安全考虑

### 密码字段

```typescript
// TypeORM
@Entity('users')
export class User {
  @Column({ type: 'varchar', length: 255 })
  password: string;

  // 不应该在响应中返回密码
  toJSON() {
    const { password, ...rest } = this;
    return rest;
  }
}

// Sequelize
@Table({ tableName: 'users' })
export class User extends Model<User> {
  @Column({ type: DataType.STRING(255) })
  password: string;

  // 不应该在响应中返回密码
  toJSON() {
    const values = { ...this.get() };
    delete values.password;
    return values;
  }
}
```

### 敏感数据加密

```typescript
import * as crypto from 'crypto';

// TypeORM
@Entity('users')
export class User {
  @Column({ type: 'varchar', length: 255 })
  get encryptedEmail(): string {
    return this.email;
  }

  set encryptedEmail(value: string) {
    this.email = this.encrypt(value);
  }

  @Column({ name: 'email', select: false })
  private email: string;

  private encrypt(text: string): string {
    const algorithm = 'aes-256-cbc';
    const key = crypto.randomBytes(32);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
  }
}
```

## 最佳实践总结

1. **命名规范**
   - 使用有意义的表名和字段名
   - 遵循数据库命名约定（下划线命名）
   - 类名使用单数形式，表名使用复数形式

2. **主键设计**
   - 优先使用自增整数主键
   - 分布式系统考虑使用 UUID
   - 避免使用复合主键（除非必要）

3. **字段类型**
   - 选择合适的数据类型以节省存储空间
   - 使用固定长度字符串存储已知长度的数据
   - 使用 DECIMAL 存储金额等精确数值

4. **索引优化**
   - 为经常查询的字段创建索引
   - 为外键字段创建索引
   - 避免过多索引影响写入性能

5. **关系设计**
   - 明确定义实体间的关系
   - 使用级联操作谨慎处理关联数据
   - 考虑使用软删除保留数据历史

6. **时间戳管理**
   - 自动管理创建和更新时间
   - 使用软删除保留删除记录
   - 考虑时区问题

7. **数据验证**
   - 在数据库层面设置约束
   - 使用应用层验证增强安全性
   - 提供有意义的错误信息

8. **性能优化**
   - 选择性加载需要的字段
   - 使用分页查询避免大量数据加载
   - 合理使用关联查询避免 N+1 问题

9. **安全考虑**
   - 敏感数据加密存储
   - 不在响应中返回敏感字段
   - 使用参数化查询防止 SQL 注入

10. **代码组织**
    - 使用基础实体类减少重复代码
    - 合理组织实体文件结构
    - 保持实体定义简洁清晰
