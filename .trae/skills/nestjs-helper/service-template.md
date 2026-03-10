# NestJS 服务模板

## 基础服务模板

```typescript
import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { {{EntityName}} } from './entities/{{entityFileName}}.entity';
import { Create{{EntityName}}Dto } from './dto/create-{{entityFileName}}.dto';
import { Update{{EntityName}}Dto } from './dto/update-{{entityFileName}}.dto';

@Injectable()
export class {{ServiceName}} {
  constructor(
    @InjectRepository({{EntityName}})
    private readonly {{entityName}}Repository: Repository<{{EntityName}}>,
  ) {}

  async findAll(query: any): Promise<{{EntityName}}[]> {
    return await this.{{entityName}}Repository.find(query);
  }

  async findOne(id: string): Promise<{{EntityName}}> {
    const {{entityName}} = await this.{{entityName}}Repository.findOne(id);
    if (!{{entityName}}) {
      throw new NotFoundException('{{EntityName}} not found');
    }
    return {{entityName}};
  }

  async create(create{{EntityName}}Dto: Create{{EntityName}}Dto): Promise<{{EntityName}}> {
    const {{entityName}} = this.{{entityName}}Repository.create(create{{EntityName}}Dto);
    return await this.{{entityName}}Repository.save({{entityName}});
  }

  async update(id: string, update{{EntityName}}Dto: Update{{EntityName}}Dto): Promise<{{EntityName}}> {
    const {{entityName}} = await this.findOne(id);
    Object.assign({{entityName}}, update{{EntityName}}Dto);
    return await this.{{entityName}}Repository.save({{entityName}});
  }

  async remove(id: string): Promise<void> {
    const {{entityName}} = await this.findOne(id);
    await this.{{entityName}}Repository.remove({{entityName}});
  }
}
```

## 依赖注入示例

### 1. 基础依赖注入

```typescript
import { Injectable } from '@nestjs/common';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { EmailService } from '../email/email.service';
import { LoggerService } from '../logger/logger.service';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly emailService: EmailService,
    private readonly loggerService: LoggerService,
  ) {}
}
```

### 2. 使用 @Inject() 注入自定义提供者

```typescript
import { Injectable, Inject, Optional } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AppService {
  constructor(
    @Inject(ConfigService) private readonly configService: ConfigService,
    @Optional() @Inject('CUSTOM_TOKEN') private readonly customService?: any,
  ) {}
}
```

### 3. 注入多个相同类型的提供者

```typescript
import { Injectable, Inject } from '@nestjs/common';

@Injectable()
export class NotificationService {
  constructor(
    @Inject('EMAIL_PROVIDER') private readonly emailProvider: any,
    @Inject('SMS_PROVIDER') private readonly smsProvider: any,
    @Inject('PUSH_PROVIDER') private readonly pushProvider: any,
  ) {}
}
```

### 4. 使用工厂提供者注入

```typescript
import { Injectable, Inject } from '@nestjs/common';

@Injectable()
export class DatabaseService {
  constructor(
    @Inject('DATABASE_CONNECTION') private readonly connection: any,
  ) {}
}

// 在模块中定义工厂提供者
@Module({
  providers: [
    {
      provide: 'DATABASE_CONNECTION',
      useFactory: async (configService: ConfigService) => {
        return await createConnection(configService.get('DATABASE_URL'));
      },
      inject: [ConfigService],
    },
    DatabaseService,
  ],
})
export class DatabaseModule {}
```

## 服务实现示例

### 1. 用户服务（完整示例）

```typescript
import { Injectable, NotFoundException, ConflictException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like, In } from 'typeorm';
import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { PaginationDto } from '../common/dto/pagination.dto';
import { PaginatedResult } from '../common/interfaces/paginated-result.interface';
import { EmailService } from '../email/email.service';
import { LoggerService } from '../logger/logger.service';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly emailService: EmailService,
    private readonly loggerService: LoggerService,
  ) {}

  async findAll(paginationDto: PaginationDto): Promise<PaginatedResult<User>> {
    const { page = 1, limit = 10, search } = paginationDto;
    const skip = (page - 1) * limit;

    const queryBuilder = this.userRepository.createQueryBuilder('user');

    if (search) {
      queryBuilder.where(
        'user.name LIKE :search OR user.email LIKE :search',
        { search: `%${search}%` }
      );
    }

    const [items, total] = await queryBuilder
      .skip(skip)
      .take(limit)
      .orderBy('user.createdAt', 'DESC')
      .getManyAndCount();

    return {
      items,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  async findOne(id: string): Promise<User> {
    const user = await this.userRepository.findOne(id, {
      relations: ['profile', 'posts'],
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    return user;
  }

  async findByEmail(email: string): Promise<User | null> {
    return await this.userRepository.findOne({ where: { email } });
  }

  async create(createUserDto: CreateUserDto): Promise<User> {
    const existingUser = await this.findByEmail(createUserDto.email);
    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }

    const user = this.userRepository.create(createUserDto);
    const savedUser = await this.userRepository.save(user);

    try {
      await this.emailService.sendWelcomeEmail(savedUser.email, savedUser.name);
      this.loggerService.log(`User created: ${savedUser.id}`);
    } catch (error) {
      this.loggerService.error(`Failed to send welcome email: ${error.message}`);
    }

    return savedUser;
  }

  async update(id: string, updateUserDto: UpdateUserDto): Promise<User> {
    const user = await this.findOne(id);

    if (updateUserDto.email && updateUserDto.email !== user.email) {
      const existingUser = await this.findByEmail(updateUserDto.email);
      if (existingUser) {
        throw new ConflictException('Email already in use');
      }
    }

    Object.assign(user, updateUserDto);
    return await this.userRepository.save(user);
  }

  async remove(id: string): Promise<void> {
    const user = await this.findOne(id);
    await this.userRepository.remove(user);
    this.loggerService.log(`User deleted: ${id}`);
  }

  async createBatch(createUserDtos: CreateUserDto[]): Promise<User[]> {
    const users = this.userRepository.create(createUserDtos);
    return await this.userRepository.save(users);
  }

  async findByIds(ids: string[]): Promise<User[]> {
    return await this.userRepository.find({
      where: { id: In(ids) },
    });
  }

  async updateLastLogin(id: string): Promise<void> {
    await this.userRepository.update(id, { lastLoginAt: new Date() });
  }

  async deactivateUser(id: string): Promise<User> {
    const user = await this.findOne(id);
    user.isActive = false;
    return await this.userRepository.save(user);
  }
}
```

### 2. 产品服务（使用复杂查询）

```typescript
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Between, MoreThan, LessThan } from 'typeorm';
import { Product } from './entities/product.entity';
import { CreateProductDto } from './dto/create-product.dto';
import { UpdateProductDto } from './dto/update-product.dto';
import { FilterProductDto } from './dto/filter-product.dto';

@Injectable()
export class ProductService {
  constructor(
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
  ) {}

  async findAll(filterDto: FilterProductDto): Promise<Product[]> {
    const { category, minPrice, maxPrice, inStock, search } = filterDto;

    const queryBuilder = this.productRepository.createQueryBuilder('product');

    if (category) {
      queryBuilder.andWhere('product.category = :category', { category });
    }

    if (minPrice !== undefined && maxPrice !== undefined) {
      queryBuilder.andWhere('product.price BETWEEN :minPrice AND :maxPrice', {
        minPrice,
        maxPrice,
      });
    } else if (minPrice !== undefined) {
      queryBuilder.andWhere('product.price >= :minPrice', { minPrice });
    } else if (maxPrice !== undefined) {
      queryBuilder.andWhere('product.price <= :maxPrice', { maxPrice });
    }

    if (inStock !== undefined) {
      queryBuilder.andWhere('product.stock > 0');
    }

    if (search) {
      queryBuilder.andWhere(
        '(product.name LIKE :search OR product.description LIKE :search)',
        { search: `%${search}%` }
      );
    }

    return await queryBuilder.getMany();
  }

  async findPopular(limit: number = 10): Promise<Product[]> {
    return await this.productRepository.find({
      order: { salesCount: 'DESC' },
      take: limit,
    });
  }

  async findNewArrivals(limit: number = 10): Promise<Product[]> {
    return await this.productRepository.find({
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }

  async findDiscounted(): Promise<Product[]> {
    return await this.productRepository
      .createQueryBuilder('product')
      .where('product.discountPrice IS NOT NULL')
      .andWhere('product.discountPrice < product.price')
      .getMany();
  }

  async updateStock(id: string, quantity: number): Promise<Product> {
    const product = await this.findOne(id);
    product.stock += quantity;
    return await this.productRepository.save(product);
  }

  async findOne(id: string): Promise<Product> {
    const product = await this.productRepository.findOne(id, {
      relations: ['reviews', 'category'],
    });

    if (!product) {
      throw new NotFoundException(`Product with ID ${id} not found`);
    }

    return product;
  }
}
```

### 3. 缓存服务（使用装饰器）

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { Cache, CACHE_MANAGER } from '@nestjs/cache-manager';
import { Inject } from '@nestjs/common';

@Injectable()
export class CacheService {
  private readonly logger = new Logger(CacheService.name);

  constructor(@Inject(CACHE_MANAGER) private readonly cacheManager: Cache) {}

  async get<T>(key: string): Promise<T | undefined> {
    try {
      return await this.cacheManager.get<T>(key);
    } catch (error) {
      this.logger.error(`Cache get error for key ${key}: ${error.message}`);
      return undefined;
    }
  }

  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    try {
      await this.cacheManager.set(key, value, ttl);
      this.logger.log(`Cache set for key ${key}`);
    } catch (error) {
      this.logger.error(`Cache set error for key ${key}: ${error.message}`);
    }
  }

  async del(key: string): Promise<void> {
    try {
      await this.cacheManager.del(key);
      this.logger.log(`Cache deleted for key ${key}`);
    } catch (error) {
      this.logger.error(`Cache delete error for key ${key}: ${error.message}`);
    }
  }

  async reset(): Promise<void> {
    try {
      await this.cacheManager.reset();
      this.logger.log('Cache reset');
    } catch (error) {
      this.logger.error(`Cache reset error: ${error.message}`);
    }
  }
}
```

### 4. 事务服务示例

```typescript
import { Injectable, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource } from 'typeorm';
import { Order } from './entities/order.entity';
import { OrderItem } from './entities/order-item.entity';
import { Product } from '../product/entities/product.entity';
import { CreateOrderDto } from './dto/create-order.dto';

@Injectable()
export class OrderService {
  constructor(
    @InjectRepository(Order)
    private readonly orderRepository: Repository<Order>,
    @InjectRepository(OrderItem)
    private readonly orderItemRepository: Repository<OrderItem>,
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
    private readonly dataSource: DataSource,
  ) {}

  async createOrder(createOrderDto: CreateOrderDto): Promise<Order> {
    const queryRunner = this.dataSource.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      const order = queryRunner.manager.create(Order, {
        userId: createOrderDto.userId,
        totalAmount: 0,
        status: 'pending',
      });

      const savedOrder = await queryRunner.manager.save(order);

      let totalAmount = 0;

      for (const itemDto of createOrderDto.items) {
        const product = await queryRunner.manager.findOne(Product, {
          where: { id: itemDto.productId },
        });

        if (!product) {
          throw new BadRequestException(`Product ${itemDto.productId} not found`);
        }

        if (product.stock < itemDto.quantity) {
          throw new BadRequestException(`Insufficient stock for product ${product.name}`);
        }

        const orderItem = queryRunner.manager.create(OrderItem, {
          orderId: savedOrder.id,
          productId: itemDto.productId,
          quantity: itemDto.quantity,
          price: product.price,
        });

        await queryRunner.manager.save(orderItem);

        product.stock -= itemDto.quantity;
        await queryRunner.manager.save(product);

        totalAmount += product.price * itemDto.quantity;
      }

      savedOrder.totalAmount = totalAmount;
      await queryRunner.manager.save(savedOrder);

      await queryRunner.commitTransaction();

      return savedOrder;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      throw error;
    } finally {
      await queryRunner.release();
    }
  }
}
```

## 服务装饰器

### 1. @Injectable()
标记类为可注入的服务

```typescript
@Injectable()
export class MyService {}
```

### 2. @Inject()
注入自定义提供者

```typescript
constructor(@Inject('MY_TOKEN') private readonly myService: MyService) {}
```

### 3. @Optional()
标记依赖为可选

```typescript
constructor(@Optional() private readonly optionalService?: OptionalService) {}
```

## 类型安全最佳实践

1. **明确的返回类型**: 所有方法应明确指定返回类型
2. **使用泛型**: 在 Repository 和缓存操作中使用泛型
3. **DTO 类型**: 使用 DTO 类型作为方法参数
4. **错误处理**: 使用 NestJS 内置异常类
5. **事务处理**: 在需要原子性操作时使用事务
6. **日志记录**: 在关键操作中添加日志
7. **缓存策略**: 合理使用缓存提高性能
8. **查询优化**: 使用查询构建器优化复杂查询
