# NestJS 管道模板

## 基础管道模板

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class {{PipeName}} implements PipeTransform {
  transform(value: any, metadata: ArgumentMetadata) {
    return value;
  }
}
```

## 管道实现示例

### 1. 验证管道（使用 class-validator）

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';
import { validate } from 'class-validator';
import { plainToClass } from 'class-transformer';

@Injectable()
export class ValidationPipe implements PipeTransform<any> {
  async transform(value: any, metadata: ArgumentMetadata) {
    if (!value) {
      throw new BadRequestException('No data submitted');
    }

    const { metatype } = metadata;

    if (!metatype || !this.toValidate(metatype)) {
      return value;
    }

    const object = plainToClass(metatype, value);
    const errors = await validate(object);

    if (errors.length > 0) {
      const messages = this.extractErrorMessages(errors);
      throw new BadRequestException({
        message: 'Validation failed',
        errors: messages,
      });
    }

    return value;
  }

  private toValidate(metatype: Function): boolean {
    const types: Function[] = [String, Boolean, Number, Array, Object];
    return !types.includes(metatype);
  }

  private extractErrorMessages(errors: any[]): string[] {
    return errors.reduce((acc, error) => {
      const constraints = error.constraints || {};
      acc.push(...Object.values(constraints));
      return acc;
    }, []);
  }
}
```

### 2. 解析整数管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class ParseIntPipe implements PipeTransform<string, number> {
  transform(value: string, metadata: ArgumentMetadata): number {
    const val = parseInt(value, 10);

    if (isNaN(val)) {
      throw new BadRequestException(
        `Validation failed. "${value}" is not an integer.`
      );
    }

    return val;
  }
}
```

### 3. 解析浮点数管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class ParseFloatPipe implements PipeTransform<string, number> {
  transform(value: string, metadata: ArgumentMetadata): number {
    const val = parseFloat(value);

    if (isNaN(val)) {
      throw new BadRequestException(
        `Validation failed. "${value}" is not a valid number.`
      );
    }

    return val;
  }
}
```

### 4. 解析布尔值管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class ParseBoolPipe implements PipeTransform<string, boolean> {
  transform(value: string, metadata: ArgumentMetadata): boolean {
    if (value === 'true' || value === '1') {
      return true;
    }

    if (value === 'false' || value === '0') {
      return false;
    }

    throw new BadRequestException(
      `Validation failed. "${value}" is not a boolean.`
    );
  }
}
```

### 5. 解析 UUID 管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class ParseUUIDPipe implements PipeTransform<string, string> {
  private readonly uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  transform(value: string, metadata: ArgumentMetadata): string {
    if (!this.uuidRegex.test(value)) {
      throw new BadRequestException(
        `Validation failed. "${value}" is not a valid UUID.`
      );
    }

    return value;
  }
}
```

### 6. 解析枚举管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

@Injectable()
export class ParseEnumPipe implements PipeTransform<string, UserRole> {
  constructor(private readonly enumType: any) {}

  transform(value: string, metadata: ArgumentMetadata): UserRole {
    const enumValues = Object.values(this.enumType);

    if (!enumValues.includes(value)) {
      throw new BadRequestException(
        `Validation failed. "${value}" is not a valid enum value. Valid values are: ${enumValues.join(', ')}`
      );
    }

    return value as UserRole;
  }
}
```

### 7. 邮箱验证管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class EmailValidationPipe implements PipeTransform<string, string> {
  private readonly emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  transform(value: string, metadata: ArgumentMetadata): string {
    if (!value || !this.emailRegex.test(value)) {
      throw new BadRequestException(
        `Validation failed. "${value}" is not a valid email address.`
      );
    }

    return value.toLowerCase();
  }
}
```

### 8. 密码强度验证管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

interface PasswordStrengthOptions {
  minLength?: number;
  requireUppercase?: boolean;
  requireLowercase?: boolean;
  requireNumbers?: boolean;
  requireSpecialChars?: boolean;
}

@Injectable()
export class PasswordStrengthPipe implements PipeTransform<string, string> {
  private readonly options: PasswordStrengthOptions;

  constructor(options: PasswordStrengthOptions = {}) {
    this.options = {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      ...options,
    };
  }

  transform(value: string, metadata: ArgumentMetadata): string {
    if (!value) {
      throw new BadRequestException('Password is required');
    }

    const errors: string[] = [];

    if (this.options.minLength && value.length < this.options.minLength) {
      errors.push(`Password must be at least ${this.options.minLength} characters long`);
    }

    if (this.options.requireUppercase && !/[A-Z]/.test(value)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (this.options.requireLowercase && !/[a-z]/.test(value)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (this.options.requireNumbers && !/[0-9]/.test(value)) {
      errors.push('Password must contain at least one number');
    }

    if (this.options.requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
      errors.push('Password must contain at least one special character');
    }

    if (errors.length > 0) {
      throw new BadRequestException({
        message: 'Password validation failed',
        errors,
      });
    }

    return value;
  }
}
```

### 9. 数组验证管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

interface ArrayValidationOptions {
  minLength?: number;
  maxLength?: number;
  unique?: boolean;
}

@Injectable()
export class ArrayValidationPipe implements PipeTransform<any, any[]> {
  constructor(private readonly options: ArrayValidationOptions = {}) {}

  transform(value: any, metadata: ArgumentMetadata): any[] {
    if (!Array.isArray(value)) {
      throw new BadRequestException('Value must be an array');
    }

    const errors: string[] = [];

    if (this.options.minLength !== undefined && value.length < this.options.minLength) {
      errors.push(`Array must contain at least ${this.options.minLength} elements`);
    }

    if (this.options.maxLength !== undefined && value.length > this.options.maxLength) {
      errors.push(`Array must contain at most ${this.options.maxLength} elements`);
    }

    if (this.options.unique) {
      const uniqueValues = new Set(value);
      if (uniqueValues.size !== value.length) {
        errors.push('Array must contain unique elements');
      }
    }

    if (errors.length > 0) {
      throw new BadRequestException({
        message: 'Array validation failed',
        errors,
      });
    }

    return value;
  }
}
```

### 10. 日期解析管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

@Injectable()
export class ParseDatePipe implements PipeTransform<string, Date> {
  transform(value: string, metadata: ArgumentMetadata): Date {
    const date = new Date(value);

    if (isNaN(date.getTime())) {
      throw new BadRequestException(
        `Validation failed. "${value}" is not a valid date.`
      );
    }

    return date;
  }
}
```

### 11. 范围验证管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

interface RangeValidationOptions {
  min?: number;
  max?: number;
  inclusive?: boolean;
}

@Injectable()
export class RangeValidationPipe implements PipeTransform<number, number> {
  constructor(private readonly options: RangeValidationOptions = {}) {}

  transform(value: number, metadata: ArgumentMetadata): number {
    const numValue = Number(value);

    if (isNaN(numValue)) {
      throw new BadRequestException('Value must be a number');
    }

    const errors: string[] = [];

    if (this.options.min !== undefined) {
      if (this.options.inclusive) {
        if (numValue < this.options.min) {
          errors.push(`Value must be at least ${this.options.min}`);
        }
      } else {
        if (numValue <= this.options.min) {
          errors.push(`Value must be greater than ${this.options.min}`);
        }
      }
    }

    if (this.options.max !== undefined) {
      if (this.options.inclusive) {
        if (numValue > this.options.max) {
          errors.push(`Value must be at most ${this.options.max}`);
        }
      } else {
        if (numValue >= this.options.max) {
          errors.push(`Value must be less than ${this.options.max}`);
        }
      }
    }

    if (errors.length > 0) {
      throw new BadRequestException({
        message: 'Range validation failed',
        errors,
      });
    }

    return numValue;
  }
}
```

### 12. 字符串修剪管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata } from '@nestjs/common';

@Injectable()
export class TrimPipe implements PipeTransform<string, string> {
  transform(value: string, metadata: ArgumentMetadata): string {
    if (typeof value !== 'string') {
      return value;
    }

    return value.trim();
  }
}
```

### 13. 字符串转小写管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata } from '@nestjs/common';

@Injectable()
export class ToLowerCasePipe implements PipeTransform<string, string> {
  transform(value: string, metadata: ArgumentMetadata): string {
    if (typeof value !== 'string') {
      return value;
    }

    return value.toLowerCase();
  }
}
```

### 14. 字符串转大写管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata } from '@nestjs/common';

@Injectable()
export class ToUpperCasePipe implements PipeTransform<string, string> {
  transform(value: string, metadata: ArgumentMetadata): string {
    if (typeof value !== 'string') {
      return value;
    }

    return value.toUpperCase();
  }
}
```

### 15. 默认值管道

```typescript
import { PipeTransform, Injectable, ArgumentMetadata } from '@nestjs/common';

@Injectable()
export class DefaultValuePipe<T = any> implements PipeTransform<T | undefined, T> {
  constructor(private readonly defaultValue: T) {}

  transform(value: T | undefined, metadata: ArgumentMetadata): T {
    return value !== undefined ? value : this.defaultValue;
  }
}
```

## DTO 示例

### 用户创建 DTO

```typescript
import { IsString, IsEmail, MinLength, IsOptional, IsEnum, IsArray } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

export class CreateUserDto {
  @ApiProperty({ example: 'John Doe' })
  @IsString()
  @MinLength(2)
  name: string;

  @ApiProperty({ example: 'john@example.com' })
  @IsEmail()
  email: string;

  @ApiProperty({ example: 'Password123!', minLength: 8 })
  @IsString()
  @MinLength(8)
  password: string;

  @ApiPropertyOptional({ enum: UserRole, default: UserRole.USER })
  @IsOptional()
  @IsEnum(UserRole)
  role?: UserRole;

  @ApiPropertyOptional({ type: [String], example: ['user', 'admin'] })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  permissions?: string[];
}
```

### 分页 DTO

```typescript
import { IsOptional, IsInt, Min, Max, IsPositive } from 'class-validator';
import { Type } from 'class-transformer';
import { ApiPropertyOptional } from '@nestjs/swagger';

export class PaginationDto {
  @ApiPropertyOptional({ default: 1, minimum: 1 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @IsPositive()
  page?: number = 1;

  @ApiPropertyOptional({ default: 10, minimum: 1, maximum: 100 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  limit?: number = 10;
}
```

## 管道应用

### 全局应用管道

```typescript
import { Module } from '@nestjs/common';
import { APP_PIPE } from '@nestjs/core';
import { ValidationPipe } from './pipes/validation.pipe';

@Module({
  providers: [
    {
      provide: APP_PIPE,
      useClass: ValidationPipe,
    },
  ],
})
export class AppModule {}
```

### 在控制器上应用管道

```typescript
import { Controller, Get, Param, UsePipes } from '@nestjs/common';
import { ParseIntPipe } from '../pipes/parse-int.pipe';
import { ParseUUIDPipe } from '../pipes/parse-uuid.pipe';

@Controller('users')
@UsePipes(ValidationPipe)
export class UsersController {
  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    // 方法实现
  }

  @Get('posts/:postId')
  findPost(@Param('postId', ParseUUIDPipe) postId: string) {
    // 方法实现
  }
}
```

### 在方法上应用管道

```typescript
import { Controller, Post, Body, UsePipes } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { EmailValidationPipe } from '../pipes/email-validation.pipe';
import { PasswordStrengthPipe } from '../pipes/password-strength.pipe';

@Controller('users')
export class UsersController {
  @Post()
  @UsePipes(EmailValidationPipe, PasswordStrengthPipe)
  create(@Body() createUserDto: CreateUserDto) {
    // 方法实现
  }
}
```

### 在参数上应用管道

```typescript
import { Controller, Get, Query, Param } from '@nestjs/common';
import { ParseIntPipe, DefaultValuePipe } from '../pipes';

@Controller('users')
export class UsersController {
  @Get()
  findAll(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number,
  ) {
    // 方法实现
  }
}
```

### 自定义验证管道选项

```typescript
import { Controller, Post, Body, UsePipes } from '@nestjs/common';
import { PasswordStrengthPipe } from '../pipes/password-strength.pipe';

@Controller('users')
export class UsersController {
  @Post()
  @UsePipes(new PasswordStrengthPipe({
    minLength: 12,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
  }))
  create(@Body() createUserDto: CreateUserDto) {
    // 方法实现
  }
}
```

## 管道最佳实践

1. **单一职责**: 每个管道只负责一个验证或转换任务
2. **错误信息**: 提供清晰、有用的错误信息
3. **类型安全**: 使用 TypeScript 泛型确保类型安全
4. **可配置性**: 通过构造函数参数使管道可配置
5. **性能考虑**: 避免在管道中执行耗时操作
6. **测试覆盖**: 为管道编写单元测试
7. **文档说明**: 为复杂管道添加注释和文档
8. **复用性**: 设计可复用的管道组件
