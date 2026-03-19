---
name: nestjs-helper
description: 该skill提供NestJS项目开发辅助功能，包括项目初始化、代码生成、最佳实践指导、数据库集成、测试部署指南和代码审查功能，当用户需要NestJS开发帮助或请求审查NestJS项目时调用
---

# NestJS Helper Skill

## 功能概述

NestJS Helper 是一个专门为 NestJS 开发者设计的辅助 skill，提供全方位的开发支持，帮助开发者快速构建高质量、可维护的 NestJS 应用程序。

## 核心功能

### 1. 项目初始化
- 快速创建新的 NestJS 项目结构
- 配置项目基础设置（TypeScript、ESLint、Prettier 等）
- 设置模块化架构和目录结构
- 配置环境变量和配置管理
- 初始化 Git 仓库和 .gitignore

### 2. 代码生成
- 生成模块（Module）、控制器（Controller）、服务（Service）
- 创建 DTO（Data Transfer Object）和实体（Entity）
- 生成中间件（Middleware）、守卫（Guard）、拦截器（Interceptor）
- 创建管道（Pipe）和异常过滤器（Exception Filter）
- 生成数据库迁移文件和种子数据

### 3. 最佳实践指导
- 遵循 SOLID 原则和设计模式
- 实现依赖注入和模块化设计
- 代码组织结构和命名规范
- 错误处理和日志记录最佳实践
- 性能优化和安全建议

### 4. 数据库集成
- TypeORM 集成和配置
- Prisma ORM 集成和配置
- Mongoose（MongoDB）集成
- 数据库连接池管理
- 事务处理和数据验证

### 5. 测试部署指南
- 单元测试编写（Jest）
- 集成测试和端到端测试
- 测试覆盖率配置
- Docker 容器化部署
- CI/CD 流水线配置
- 环境配置管理（开发、测试、生产）

### 6. 代码审查功能
- 代码质量分析和改进建议
- 安全漏洞检测
- 性能瓶颈识别
- 代码风格一致性检查
- 架构设计评估

### 7. Swagger 配置功能
- 快速安装和配置 Swagger 依赖
- 生成 Swagger 配置代码和模板
- 支持自定义 Swagger 选项
- 提供 Swagger 配置最佳实践指导
- 自动扫描和文档化 API 端点

## 使用场景

### 场景一：创建新项目
当用户需要创建一个新的 NestJS 项目时，该 skill 可以：
- 引导用户选择项目模板和配置选项
- 自动生成项目骨架和基础代码
- 配置开发环境和工具链

### 场景二：添加新功能
当用户需要为现有项目添加新功能时，该 skill 可以：
- 分析现有代码结构
- 生成符合项目规范的代码模板
- 提供功能实现建议和最佳实践

### 场景三：代码优化
当用户需要优化现有代码时，该 skill 可以：
- 识别代码中的问题和改进点
- 提供重构建议和示例
- 确保代码符合 NestJS 最佳实践

### 场景四：问题排查
当用户遇到开发问题时，该 skill 可以：
- 分析错误日志和堆栈跟踪
- 提供问题诊断和解决方案
- 推荐相关的文档和资源

### 场景五：项目审查
当用户请求审查 NestJS 项目时，该 skill 可以：
- 全面检查项目结构和代码质量
- 识别潜在的安全风险和性能问题
- 提供详细的审查报告和改进建议

### 场景六：Swagger 配置
当用户需要为 NestJS 项目配置 Swagger 时，该 skill 可以：
- 自动安装必要的 Swagger 依赖
- 生成符合最佳实践的 Swagger 配置代码
- 提供自定义 Swagger 选项的指导
- 帮助用户使用装饰器为 API 添加文档信息

## 调用时机

### 自动触发
- 当用户提到 "NestJS"、"nestjs" 等关键词时
- 当用户请求创建、修改或审查 NestJS 项目时
- 当用户询问 NestJS 相关的开发问题时

### 手动调用
用户可以通过以下方式主动调用该 skill：
- "帮我创建一个 NestJS 项目"
- "审查一下我的 NestJS 代码"
- "生成一个 NestJS 模块"
- "如何集成数据库到 NestJS 项目"
- "优化我的 NestJS 应用性能"
- "为我的 NestJS 项目配置 Swagger"
- "添加 Swagger 文档到我的 NestJS 应用"
- "如何使用 Swagger 装饰器"
- "Swagger 配置最佳实践"

## 技术栈支持

### 核心框架
- NestJS（最新稳定版）
- TypeScript
- Express / Fastify

### 数据库
- PostgreSQL
- MySQL
- MongoDB
- SQLite

### ORM/ODM
- TypeORM
- Prisma
- Mongoose

### 认证授权
- JWT
- Passport
- OAuth2

### 测试
- Jest
- Supertest
- Testing Library

### 部署
- Docker
- Kubernetes
- AWS / Azure / GCP

## 注意事项

1. 该 skill 始终遵循 NestJS 官方文档和最佳实践
2. 生成的代码会考虑项目的具体需求和上下文
3. 提供的建议会根据项目规模和复杂度进行调整
4. 始终优先考虑代码的可维护性和可扩展性
5. 安全性和性能是代码审查的重点关注领域

## 相关资源

- [NestJS 官方文档](https://docs.nestjs.com/)
- [NestJS 中文文档](https://docs.nestjs.cn/)
- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)
- [TypeORM 文档](https://typeorm.io/)
- [Prisma 文档](https://www.prisma.io/docs)
