# NestJS 守卫模板

## 基础守卫模板

```typescript
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';

@Injectable()
export class {{GuardName}} implements CanActivate {
  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    return true;
  }
}
```

## 守卫实现示例

### 1. 认证守卫（JWT）

```typescript
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException, Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';
import { Observable } from 'rxjs';

@Injectable()
export class AuthGuard implements CanActivate {
  private readonly logger = new Logger(AuthGuard.name);

  constructor(private readonly jwtService: JwtService) {}

  canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    const token = this.extractTokenFromHeader(request);

    if (!token) {
      this.logger.warn('Authentication failed: No token provided');
      throw new UnauthorizedException('No token provided');
    }

    try {
      const payload = this.jwtService.verify(token);
      request['user'] = payload;
      return true;
    } catch (error) {
      this.logger.error(`Authentication failed: ${error.message}`);
      throw new UnauthorizedException('Invalid or expired token');
    }
  }

  private extractTokenFromHeader(request: Request): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}
```

### 2. 角色守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>('roles', [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles) {
      return true;
    }

    const { user } = context.switchToHttp().getRequest();

    if (!user) {
      throw new ForbiddenException('User not authenticated');
    }

    const hasRole = requiredRoles.some((role) => user.roles?.includes(role));

    if (!hasRole) {
      throw new ForbiddenException('Insufficient permissions');
    }

    return true;
  }
}
```

### 3. 权限守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredPermissions = this.reflector.getAllAndOverride<string[]>('permissions', [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredPermissions) {
      return true;
    }

    const { user } = context.switchToHttp().getRequest();

    if (!user) {
      throw new ForbiddenException('User not authenticated');
    }

    const hasPermission = requiredPermissions.some((permission) =>
      user.permissions?.includes(permission)
    );

    if (!hasPermission) {
      throw new ForbiddenException('Insufficient permissions');
    }

    return true;
  }
}
```

### 4. API Key 守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class ApiKeyGuard implements CanActivate {
  private readonly logger = new Logger(ApiKeyGuard.name);
  private readonly validApiKeys: string[];

  constructor(private readonly configService: ConfigService) {
    this.validApiKeys = this.configService.get<string>('API_KEYS')?.split(',') || [];
  }

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const apiKey = request.headers['x-api-key'] || request.query.apiKey;

    if (!apiKey) {
      this.logger.warn('API Key authentication failed: No API key provided');
      throw new UnauthorizedException('API key is required');
    }

    if (!this.validApiKeys.includes(apiKey)) {
      this.logger.warn(`API Key authentication failed: Invalid API key: ${apiKey}`);
      throw new UnauthorizedException('Invalid API key');
    }

    return true;
  }
}
```

### 5. 所有者守卫（资源所有权验证）

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { UserService } from '../user/user.service';

@Injectable()
export class OwnerGuard implements CanActivate {
  constructor(private readonly userService: UserService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const { user, params } = request;

    if (!user) {
      throw new ForbiddenException('User not authenticated');
    }

    const resource = await this.userService.findOne(params.id);

    if (!resource) {
      throw new ForbiddenException('Resource not found');
    }

    if (resource.userId !== user.id && !user.roles?.includes('admin')) {
      throw new ForbiddenException('You do not have permission to access this resource');
    }

    return true;
  }
}
```

### 6. IP 白名单守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class IpWhitelistGuard implements CanActivate {
  private readonly logger = new Logger(IpWhitelistGuard.name);
  private readonly allowedIps: string[];

  constructor(private readonly configService: ConfigService) {
    this.allowedIps = this.configService.get<string>('ALLOWED_IPS')?.split(',') || [];
  }

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const clientIp = request.ip || request.connection.remoteAddress;

    if (this.allowedIps.length === 0) {
      return true;
    }

    const isAllowed = this.allowedIps.some(allowedIp => {
      if (allowedIp.includes('/')) {
        return this.isIpInCidr(clientIp, allowedIp);
      }
      return clientIp === allowedIp;
    });

    if (!isAllowed) {
      this.logger.warn(`IP whitelist check failed: ${clientIp}`);
      throw new ForbiddenException('Access denied from your IP address');
    }

    return true;
  }

  private isIpInCidr(ip: string, cidr: string): boolean {
    const [network, prefixLength] = cidr.split('/');
    const mask = parseInt(prefixLength, 10);
    const ipInt = this.ipToInt(ip);
    const networkInt = this.ipToInt(network);
    const maskInt = ~((1 << (32 - mask)) - 1);

    return (ipInt & maskInt) === (networkInt & maskInt);
  }

  private ipToInt(ip: string): number {
    return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0;
  }
}
```

### 7. 邮箱验证守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';

@Injectable()
export class EmailVerifiedGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const { user } = context.switchToHttp().getRequest();

    if (!user) {
      throw new ForbiddenException('User not authenticated');
    }

    if (!user.isEmailVerified) {
      throw new ForbiddenException('Email verification required');
    }

    return true;
  }
}
```

### 8. 账户状态守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';

@Injectable()
export class AccountStatusGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const { user } = context.switchToHttp().getRequest();

    if (!user) {
      throw new ForbiddenException('User not authenticated');
    }

    if (user.status === 'suspended') {
      throw new ForbiddenException('Account suspended');
    }

    if (user.status === 'banned') {
      throw new ForbiddenException('Account banned');
    }

    if (user.status === 'inactive') {
      throw new ForbiddenException('Account inactive');
    }

    return true;
  }
}
```

### 9. 速率限制守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, HttpException, HttpStatus, Logger } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

interface RateLimitStore {
  count: number;
  resetTime: number;
}

@Injectable()
export class RateLimitGuard implements CanActivate {
  private readonly logger = new Logger(RateLimitGuard.name);
  private readonly store = new Map<string, RateLimitStore>();
  private readonly defaultLimit = 100;
  private readonly defaultWindow = 60 * 1000; // 1分钟

  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const limit = this.reflector.get<number>('rateLimit', context.getHandler()) || this.defaultLimit;
    const window = this.reflector.get<number>('rateLimitWindow', context.getHandler()) || this.defaultWindow;

    const request = context.switchToHttp().getRequest();
    const key = `${request.ip}:${request.route.path}`;

    const now = Date.now();
    let record = this.store.get(key);

    if (!record || now > record.resetTime) {
      record = {
        count: 1,
        resetTime: now + window,
      };
      this.store.set(key, record);
    } else {
      record.count++;
    }

    if (record.count > limit) {
      this.logger.warn(`Rate limit exceeded for key: ${key}`);
      throw new HttpException(
        'Too many requests, please try again later',
        HttpStatus.TOO_MANY_REQUESTS
      );
    }

    return true;
  }
}
```

### 10. 维护模式守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, HttpException, HttpStatus, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Reflector } from '@nestjs/core';

@Injectable()
export class MaintenanceGuard implements CanActivate {
  private readonly logger = new Logger(MaintenanceGuard.name);

  constructor(
    private readonly configService: ConfigService,
    private readonly reflector: Reflector,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const isMaintenanceMode = this.configService.get<boolean>('MAINTENANCE_MODE', false);
    const bypassMaintenance = this.reflector.get<boolean>('bypassMaintenance', context.getHandler());

    if (!isMaintenanceMode || bypassMaintenance) {
      return true;
    }

    const { user } = context.switchToHttp().getRequest();

    if (user && user.roles?.includes('admin')) {
      return true;
    }

    this.logger.warn('Access denied: Maintenance mode is active');
    throw new HttpException(
      'Service is under maintenance. Please try again later.',
      HttpStatus.SERVICE_UNAVAILABLE
    );
  }
}
```

### 11. 时间窗口守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException, Logger } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

@Injectable()
export class TimeWindowGuard implements CanActivate {
  private readonly logger = new Logger(TimeWindowGuard.name);

  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const timeWindow = this.reflector.get<{ start: string; end: string }>(
      'timeWindow',
      context.getHandler()
    );

    if (!timeWindow) {
      return true;
    }

    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();

    const [startHour, startMin] = timeWindow.start.split(':').map(Number);
    const [endHour, endMin] = timeWindow.end.split(':').map(Number);

    const startTime = startHour * 60 + startMin;
    const endTime = endHour * 60 + endMin;

    if (currentTime < startTime || currentTime > endTime) {
      this.logger.warn(`Access denied: Outside time window (${timeWindow.start}-${timeWindow.end})`);
      throw new ForbiddenException('Access is only allowed during specific hours');
    }

    return true;
  }
}
```

### 12. 条件守卫

```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

@Injectable()
export class ConditionalGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const condition = this.reflector.get<boolean>('condition', context.getHandler());

    if (condition === undefined) {
      return true;
    }

    if (!condition) {
      throw new ForbiddenException('Feature is currently disabled');
    }

    return true;
  }
}
```

## 装饰器定义

### 角色装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const ROLES_KEY = 'roles';
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);
```

### 权限装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const PERMISSIONS_KEY = 'permissions';
export const Permissions = (...permissions: string[]) => SetMetadata(PERMISSIONS_KEY, permissions);
```

### 公共路由装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

### 速率限制装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const RATE_LIMIT_KEY = 'rateLimit';
export const RATE_LIMIT_WINDOW_KEY = 'rateLimitWindow';

export const RateLimit = (limit: number, window?: number) =>
  SetMetadata(RATE_LIMIT_KEY, limit);

export const RateLimitWindow = (window: number) =>
  SetMetadata(RATE_LIMIT_WINDOW_KEY, window);
```

### 维护模式绕过装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const BYPASS_MAINTENANCE_KEY = 'bypassMaintenance';
export const BypassMaintenance = () => SetMetadata(BYPASS_MAINTENANCE_KEY, true);
```

### 时间窗口装饰器

```typescript
import { SetMetadata } from '@nestjs/common';

export const TIME_WINDOW_KEY = 'timeWindow';

export const TimeWindow = (start: string, end: string) =>
  SetMetadata(TIME_WINDOW_KEY, { start, end });
```

## 守卫应用

### 全局应用守卫

```typescript
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { AuthGuard } from './guards/auth.guard';
import { RolesGuard } from './guards/roles.guard';

@Module({
  providers: [
    {
      provide: APP_GUARD,
      useClass: AuthGuard,
    },
    {
      provide: APP_GUARD,
      useClass: RolesGuard,
    },
  ],
})
export class AppModule {}
```

### 在控制器上应用守卫

```typescript
import { Controller, UseGuards } from '@nestjs/common';
import { AuthGuard } from '../guards/auth.guard';
import { RolesGuard } from '../guards/roles.guard';
import { Roles } from '../decorators/roles.decorator';

@Controller('users')
@UseGuards(AuthGuard, RolesGuard)
@Roles('admin')
export class UsersController {
  // 控制器方法
}
```

### 在方法上应用守卫

```typescript
import { Controller, Get, Post, UseGuards } from '@nestjs/common';
import { AuthGuard } from '../guards/auth.guard';
import { Public } from '../decorators/public.decorator';

@Controller('auth')
@UseGuards(AuthGuard)
export class AuthController {
  @Public()
  @Post('login')
  login() {
    // 公开路由，不需要认证
  }

  @Get('profile')
  getProfile() {
    // 需要认证的路由
  }
}
```

### 组合守卫

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import { AuthGuard } from '../guards/auth.guard';
import { RolesGuard } from '../guards/roles.guard';
import { PermissionsGuard } from '../guards/permissions.guard';
import { Roles } from '../decorators/roles.decorator';
import { Permissions } from '../decorators/permissions.decorator';

@Controller('admin')
@UseGuards(AuthGuard, RolesGuard, PermissionsGuard)
@Roles('admin')
export class AdminController {
  @Get('users')
  @Permissions('user:read')
  getUsers() {
    // 需要认证、admin角色和user:read权限
  }

  @Get('settings')
  @Permissions('settings:read')
  getSettings() {
    // 需要认证、admin角色和settings:read权限
  }
}
```

### 条件守卫应用

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import { ConditionalGuard } from '../guards/conditional.guard';
import { TimeWindow } from '../decorators/time-window.decorator';

@Controller('special')
@UseGuards(ConditionalGuard)
export class SpecialController {
  @Get('feature')
  @TimeWindow('09:00', '18:00')
  specialFeature() {
    // 仅在工作时间可用
  }
}
```

## 守卫最佳实践

1. **单一职责**: 每个守卫只负责一个验证任务
2. **错误信息**: 提供清晰、有用的错误信息
3. **性能考虑**: 避免在守卫中执行耗时操作
4. **可配置性**: 通过装饰器或构造函数参数使守卫可配置
5. **日志记录**: 记录重要的安全事件
6. **测试覆盖**: 为守卫编写单元测试
7. **文档说明**: 为复杂守卫添加注释和文档
8. **组合使用**: 合理组合多个守卫实现复杂权限控制
9. **默认拒绝**: 默认拒绝访问，明确允许的情况才放行
10. **类型安全**: 使用 TypeScript 类型确保类型安全
