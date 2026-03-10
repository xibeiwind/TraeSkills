# Sequelize 集成指南

## 安装依赖

```bash
npm install sequelize
npm install mysql2  # MySQL驱动
# 或
npm install pg  # PostgreSQL驱动
# 或
npm install sqlite3  # SQLite驱动
npm install --save-dev @types/sequelize
```

## 配置文件示例

### 基础配置

```typescript
import { Sequelize } from 'sequelize';

const sequelize = new Sequelize('nestjs_db', 'root', 'password', {
  host: 'localhost',
  port: 3306,
  dialect: 'mysql', // 数据库类型: mysql, postgres, sqlite, mssql
  timezone: '+08:00',
  define: {
    timestamps: true, // 自动添加 createdAt 和 updatedAt
    underscored: true, // 使用下划线命名
    freezeTableName: true, // 禁止表名复数化
  },
  pool: {
    max: 10, // 连接池最大连接数
    min: 0, // 连接池最小连接数
    acquire: 30000, // 获取连接的最大等待时间
    idle: 10000, // 连接空闲时间
  },
  logging: console.log, // 启用SQL日志
});

export default sequelize;
```

### 模块配置

```typescript
import { Module, DynamicModule } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { User } from './entities/user.entity';
import { Role } from './entities/role.entity';

@Module({})
export class DatabaseModule {
  static register(): DynamicModule {
    return {
      module: DatabaseModule,
      imports: [
        SequelizeModule.forRoot({
          dialect: 'mysql',
          host: 'localhost',
          port: 3306,
          username: 'root',
          password: 'password',
          database: 'nestjs_db',
          models: [User, Role],
          autoLoadModels: true, // 自动加载模型
          synchronize: true, // 自动同步数据库结构
          timezone: '+08:00',
          define: {
            timestamps: true,
            underscored: true,
          },
          pool: {
            max: 10,
            min: 0,
            acquire: 30000,
            idle: 10000,
          },
          logging: true,
        }),
      ],
      exports: [SequelizeModule],
    };
  }
}
```

### 环境变量配置

```typescript
import { Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { User } from './entities/user.entity';
import { Role } from './entities/role.entity';

@Module({
  imports: [
    SequelizeModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        dialect: configService.get<'mysql' | 'postgres'>('DB_DIALECT', 'mysql'),
        host: configService.get('DB_HOST', 'localhost'),
        port: configService.get<number>('DB_PORT', 3306),
        username: configService.get('DB_USERNAME', 'root'),
        password: configService.get('DB_PASSWORD', ''),
        database: configService.get('DB_DATABASE', 'nestjs_db'),
        models: [User, Role],
        autoLoadModels: true,
        synchronize: configService.get('DB_SYNCHRONIZE', false),
        timezone: '+08:00',
        logging: configService.get('DB_LOGGING', false),
        pool: {
          max: configService.get('DB_POOL_MAX', 10),
          min: configService.get('DB_POOL_MIN', 0),
          acquire: configService.get('DB_POOL_ACQUIRE', 30000),
          idle: configService.get('DB_POOL_IDLE', 10000),
        },
      }),
    }),
  ],
  exports: [SequelizeModule],
})
export class DatabaseModule {}
```

### 多数据源配置

```typescript
import { Module } from '@nestjs/common';
import { SequelizeModule } from '@nestjs/sequelize';
import { User } from './entities/user.entity';
import { Log } from './entities/log.entity';

@Module({
  imports: [
    SequelizeModule.forRoot({
      name: 'default',
      dialect: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'nestjs_db',
      models: [User],
      autoLoadModels: true,
      synchronize: false,
    }),
    SequelizeModule.forRoot({
      name: 'secondary',
      dialect: 'postgres',
      host: 'localhost',
      port: 5432,
      username: 'postgres',
      password: 'password',
      database: 'nestjs_logs',
      models: [Log],
      autoLoadModels: true,
      synchronize: false,
    }),
  ],
  exports: [SequelizeModule],
})
export class DatabaseModule {}
```

## 模型定义示例

### 基础模型

```typescript
import { Table, Column, Model, DataType, CreatedAt, UpdatedAt } from 'sequelize-typescript';

@Table({
  tableName: 'users',
  timestamps: true,
  underscored: true,
})
export class User extends Model<User> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(50),
    allowNull: false,
    unique: true,
  })
  username: string;

  @Column({
    type: DataType.STRING(255),
    allowNull: false,
  })
  password: string;

  @Column({
    type: DataType.STRING(100),
    allowNull: true,
  })
  email: string;

  @Column({
    type: DataType.INTEGER,
    defaultValue: 0,
  })
  age: number;

  @Column({
    type: DataType.BOOLEAN,
    defaultValue: true,
    field: 'is_active',
  })
  isActive: boolean;

  @CreatedAt
  @Column({ field: 'created_at' })
  createdAt: Date;

  @UpdatedAt
  @Column({ field: 'updated_at' })
  updatedAt: Date;
}
```

### 一对一关系

```typescript
import { Table, Column, Model, DataType, ForeignKey, BelongsTo } from 'sequelize-typescript';
import { User } from './user.entity';

@Table({
  tableName: 'profiles',
  timestamps: true,
  underscored: true,
})
export class Profile extends Model<Profile> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(100),
    allowNull: false,
  })
  firstName: string;

  @Column({
    type: DataType.STRING(100),
    allowNull: false,
  })
  lastName: string;

  @Column({
    type: DataType.TEXT,
    allowNull: true,
  })
  bio: string;

  @ForeignKey(() => User)
  @Column({
    type: DataType.INTEGER,
    field: 'user_id',
  })
  userId: number;

  @BelongsTo(() => User)
  user: User;
}

@Table({
  tableName: 'users',
  timestamps: true,
  underscored: true,
})
export class User extends Model<User> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(50),
    allowNull: false,
    unique: true,
  })
  username: string;

  @Column({
    type: DataType.STRING(255),
    allowNull: false,
  })
  password: string;

  @HasOne(() => Profile)
  profile: Profile;
}
```

### 一对多关系

```typescript
import { Table, Column, Model, DataType, ForeignKey, BelongsTo, HasMany } from 'sequelize-typescript';

@Table({
  tableName: 'categories',
  timestamps: true,
  underscored: true,
})
export class Category extends Model<Category> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(100),
    allowNull: false,
  })
  name: string;

  @HasMany(() => Product)
  products: Product[];
}

@Table({
  tableName: 'products',
  timestamps: true,
  underscored: true,
})
export class Product extends Model<Product> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(200),
    allowNull: false,
  })
  name: string;

  @Column({
    type: DataType.DECIMAL(10, 2),
    allowNull: false,
  })
  price: number;

  @ForeignKey(() => Category)
  @Column({
    type: DataType.INTEGER,
    field: 'category_id',
  })
  categoryId: number;

  @BelongsTo(() => Category)
  category: Category;
}
```

### 多对多关系

```typescript
import { Table, Column, Model, DataType, BelongsToMany } from 'sequelize-typescript';

@Table({
  tableName: 'roles',
  timestamps: true,
  underscored: true,
})
export class Role extends Model<Role> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(50),
    allowNull: false,
  })
  name: string;

  @BelongsToMany(() => Permission, () => RolePermission)
  permissions: Permission[];
}

@Table({
  tableName: 'permissions',
  timestamps: true,
  underscored: true,
})
export class Permission extends Model<Permission> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(100),
    allowNull: false,
  })
  name: string;

  @BelongsToMany(() => Role, () => RolePermission)
  roles: Role[];
}

@Table({
  tableName: 'role_permissions',
  timestamps: true,
  underscored: true,
})
export class RolePermission extends Model<RolePermission> {
  @ForeignKey(() => Role)
  @Column({
    type: DataType.INTEGER,
    field: 'role_id',
  })
  roleId: number;

  @ForeignKey(() => Permission)
  @Column({
    type: DataType.INTEGER,
    field: 'permission_id',
  })
  permissionId: number;
}
```

### 使用装饰器的完整模型

```typescript
import { 
  Table, 
  Column, 
  Model, 
  DataType, 
  CreatedAt, 
  UpdatedAt,
  Index,
  Unique,
  Default,
  Is
} from 'sequelize-typescript';

@Table({
  tableName: 'articles',
  timestamps: true,
  underscored: true,
})
@Unique(['slug'])
@Index(['authorId', 'status'])
export class Article extends Model<Article> {
  @Column({
    type: DataType.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  })
  id: number;

  @Column({
    type: DataType.STRING(200),
    allowNull: false,
  })
  title: string;

  @Column({
    type: DataType.STRING(255),
    allowNull: false,
    unique: true,
  })
  slug: string;

  @Column({
    type: DataType.TEXT,
    allowNull: true,
  })
  content: string;

  @Column({
    type: DataType.ENUM('draft', 'published', 'archived'),
    defaultValue: 'draft',
    allowNull: false,
  })
  status: 'draft' | 'published' | 'archived';

  @Column({
    type: DataType.INTEGER,
    field: 'author_id',
    allowNull: false,
  })
  authorId: number;

  @Column({
    type: DataType.JSON,
    allowNull: true,
  })
  metadata: Record<string, any>;

  @Column({
    type: DataType.DATE,
    allowNull: true,
    field: 'published_at',
  })
  publishedAt: Date;

  @CreatedAt
  @Column({ field: 'created_at' })
  createdAt: Date;

  @UpdatedAt
  @Column({ field: 'updated_at' })
  updatedAt: Date;

  @Column({
    type: DataType.INTEGER,
    defaultValue: 0,
  })
  version: number;
}
```

### 使用 Sequelize 原生定义

```typescript
import { Sequelize, DataTypes, Model } from 'sequelize';

const sequelize = new Sequelize('nestjs_db', 'root', 'password', {
  host: 'localhost',
  dialect: 'mysql',
});

class User extends Model {
  public id!: number;
  public username!: string;
  public password!: string;
  public email!: string | null;
  public age!: number;
  public isActive!: boolean;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

User.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    username: {
      type: DataTypes.STRING(50),
      allowNull: false,
      unique: true,
    },
    password: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
    email: {
      type: DataTypes.STRING(100),
      allowNull: true,
    },
    age: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true,
      field: 'is_active',
    },
  },
  {
    sequelize,
    tableName: 'users',
    timestamps: true,
    underscored: true,
  }
);

export default User;
```

## 查询示例

### Service 中使用模型

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectModel(User)
    private userModel: typeof User,
  ) {}

  async create(userData: Partial<User>): Promise<User> {
    return await this.userModel.create(userData);
  }

  async findAll(): Promise<User[]> {
    return await this.userModel.findAll();
  }

  async findOne(id: number): Promise<User> {
    const user = await this.userModel.findByPk(id);
    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }
    return user;
  }

  async findByUsername(username: string): Promise<User | null> {
    return await this.userModel.findOne({ where: { username } });
  }

  async update(id: number, userData: Partial<User>): Promise<User> {
    const user = await this.findOne(id);
    await user.update(userData);
    return user;
  }

  async remove(id: number): Promise<void> {
    const user = await this.findOne(id);
    await user.destroy();
  }
}
```

### 高级查询示例

```typescript
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { Op } from 'sequelize';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectModel(User)
    private userModel: typeof User,
  ) {}

  // 分页查询
  async paginate(page: number = 1, limit: number = 10): Promise<{ data: User[]; total: number }> {
    const offset = (page - 1) * limit;
    const { count, rows } = await this.userModel.findAndCountAll({
      offset,
      limit,
      order: [['createdAt', 'DESC']],
    });
    return { data: rows, total: count };
  }

  // 模糊查询
  async search(keyword: string): Promise<User[]> {
    return await this.userModel.findAll({
      where: {
        [Op.or]: [
          { username: { [Op.like]: `%${keyword}%` } },
          { email: { [Op.like]: `%${keyword}%` } },
        ],
      },
    });
  }

  // 范围查询
  async findByAgeRange(minAge: number, maxAge: number): Promise<User[]> {
    return await this.userModel.findAll({
      where: {
        age: {
          [Op.between]: [minAge, maxAge],
        },
      },
    });
  }

  // IN 查询
  async findByIds(ids: number[]): Promise<User[]> {
    return await this.userModel.findAll({
      where: {
        id: {
          [Op.in]: ids,
        },
      },
    });
  }

  // 比较查询
  async findActiveUsers(): Promise<User[]> {
    return await this.userModel.findAll({
      where: {
        isActive: true,
      },
    });
  }

  // 关联查询
  async findWithProfile(userId: number): Promise<User | null> {
    return await this.userModel.findByPk(userId, {
      include: ['profile'],
    });
  }

  // 多重关联查询
  async findWithRelations(userId: number): Promise<User | null> {
    return await this.userModel.findByPk(userId, {
      include: [
        {
          association: 'profile',
        },
        {
          association: 'roles',
          include: ['permissions'],
        },
      ],
    });
  }

  // 选择特定字段
  async findSelectFields(): Promise<Partial<User>[]> {
    return await this.userModel.findAll({
      attributes: ['id', 'username', 'email'],
    });
  }

  // 排序和限制
  async findTopUsers(limit: number): Promise<User[]> {
    return await this.userModel.findAll({
      order: [['createdAt', 'DESC']],
      limit,
    });
  }

  // 复杂条件查询
  async findComplexQuery(): Promise<User[]> {
    return await this.userModel.findAll({
      where: {
        isActive: true,
        age: {
          [Op.gte]: 18,
        },
        createdAt: {
          [Op.gte]: new Date('2024-01-01'),
        },
      },
      order: [['createdAt', 'DESC']],
      limit: 100,
    });
  }
}
```

### 使用 Sequelize 查询构建器

```typescript
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectModel(User)
    private userModel: typeof User,
  ) {}

  async findActiveUsersWithQueryBuilder(): Promise<User[]> {
    return await this.userModel.findAll({
      where: {
        isActive: true,
      },
      order: [['createdAt', 'DESC']],
    });
  }

  async findUsersWithRole(roleName: string): Promise<User[]> {
    return await this.userModel.findAll({
      include: [
        {
          association: 'roles',
          where: { name: roleName },
        },
      ],
    });
  }

  async countActiveUsers(): Promise<number> {
    return await this.userModel.count({
      where: {
        isActive: true,
      },
    });
  }

  async findUsersWithPagination(page: number, limit: number): Promise<User[]> {
    const offset = (page - 1) * limit;
    return await this.userModel.findAll({
      offset,
      limit,
    });
  }

  async updateUserStatus(userId: number, isActive: boolean): Promise<[number, User[]]> {
    return await this.userModel.update(
      { isActive },
      {
        where: { id: userId },
      }
    );
  }

  async bulkUpdateStatus(userIds: number[], isActive: boolean): Promise<[number, User[]]> {
    return await this.userModel.update(
      { isActive },
      {
        where: {
          id: {
            [Op.in]: userIds,
          },
        },
      }
    );
  }

  async findUsersWithAttributes(): Promise<User[]> {
    return await this.userModel.findAll({
      attributes: {
        include: [
          [sequelize.fn('COUNT', sequelize.col('id')), 'userCount'],
        ],
      },
      group: ['isActive'],
    });
  }
}
```

### 事务处理

```typescript
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { Sequelize, Transaction } from 'sequelize';
import { User } from './entities/user.entity';
import { Profile } from './entities/profile.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectModel(User)
    private userModel: typeof User,
    @InjectModel(Profile)
    private profileModel: typeof Profile,
    private sequelize: Sequelize,
  ) {}

  async createUserWithProfile(userData: Partial<User>, profileData: Partial<Profile>): Promise<User> {
    const transaction = await this.sequelize.transaction();

    try {
      const user = await this.userModel.create(userData, { transaction });
      
      await this.profileModel.create(
        {
          ...profileData,
          userId: user.id,
        },
        { transaction }
      );

      await transaction.commit();
      return user;
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }

  async transferFunds(fromUserId: number, toUserId: number, amount: number): Promise<void> {
    const transaction = await this.sequelize.transaction();

    try {
      const fromUser = await this.userModel.findByPk(fromUserId, { transaction });
      const toUser = await this.userModel.findByPk(toUserId, { transaction });

      if (!fromUser || !toUser) {
        throw new Error('User not found');
      }

      if (fromUser.balance < amount) {
        throw new Error('Insufficient balance');
      }

      await fromUser.update({ balance: fromUser.balance - amount }, { transaction });
      await toUser.update({ balance: toUser.balance + amount }, { transaction });

      await transaction.commit();
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }
}
```

### 聚合查询

```typescript
import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/sequelize';
import { Op, fn, col, literal } from 'sequelize';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectModel(User)
    private userModel: typeof User,
  ) {}

  // 统计用户数量
  async countUsers(): Promise<number> {
    return await this.userModel.count();
  }

  // 统计活跃用户数量
  async countActiveUsers(): Promise<number> {
    return await this.userModel.count({
      where: { isActive: true },
    });
  }

  // 计算平均年龄
  async getAverageAge(): Promise<number> {
    const result = await this.userModel.findOne({
      attributes: [[fn('AVG', col('age')), 'averageAge']],
    });
    return result?.getDataValue('averageAge') || 0;
  }

  // 按状态分组统计
  async groupByStatus(): Promise<any[]> {
    return await this.userModel.findAll({
      attributes: [
        'isActive',
        [fn('COUNT', col('id')), 'count'],
      ],
      group: ['isActive'],
      raw: true,
    });
  }

  // 查找最大年龄用户
  async findOldestUser(): Promise<User | null> {
    return await this.userModel.findOne({
      order: [['age', 'DESC']],
    });
  }

  // 查找最小年龄用户
  async findYoungestUser(): Promise<User | null> {
    return await this.userModel.findOne({
      order: [['age', 'ASC']],
    });
  }
}
```

## 迁移管理

### 创建迁移

```bash
npx sequelize-cli migration:generate --name create-user-table
```

### 运行迁移

```bash
npx sequelize-cli db:migrate
```

### 回滚迁移

```bash
npx sequelize-cli db:migrate:undo
```

### 创建模型

```bash
npx sequelize-cli model:generate --name User --attributes username:string,password:string
```

## 最佳实践

1. **生产环境关闭 synchronize**：在生产环境中应该使用迁移而不是自动同步
2. **使用环境变量**：敏感信息如数据库密码应该使用环境变量
3. **连接池配置**：根据应用负载合理配置连接池大小
4. **索引优化**：为经常查询的字段添加索引
5. **软删除**：考虑使用软删除而不是物理删除
6. **DTO 验证**：使用 class-validator 对输入数据进行验证
7. **错误处理**：妥善处理数据库操作中的异常
8. **使用事务**：对于涉及多个表的操作，使用事务保证数据一致性
9. **避免 N+1 查询**：使用 include 预加载关联数据
10. **使用原始 SQL**：对于复杂查询，考虑使用原始 SQL 提高性能
