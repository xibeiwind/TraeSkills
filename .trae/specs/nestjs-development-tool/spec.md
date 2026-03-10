# NestJS开发辅助工具 Spec

## Why
开发者在构建NestJS项目时需要遵循官方推荐的架构设计原则，但缺乏统一的开发辅助工具来指导项目初始化、代码生成、最佳实践应用以及项目审查。该工具将提供端到端的开发支持，提高开发效率和代码质量。

## What Changes
- 创建NestJS开发辅助工具skill，提供项目初始化、代码生成、最佳实践指导等功能
- 支持模块、控制器、服务的创建规范和代码生成
- 提供依赖注入、中间件、拦截器、管道、守卫等核心功能的代码模板
- 集成TypeORM、Sequelize等数据库配置指南
- 提供调试、测试、部署的完整流程说明
- 包含性能优化、错误处理、日志管理等进阶技巧
- 提供NestJS项目代码审查功能，输出改进意见清单

## Impact
- Affected specs: 无现有规格受影响
- Affected code: 将创建新的skill目录和相关文档

## ADDED Requirements

### Requirement: NestJS项目初始化与配置
系统应提供NestJS项目初始化指导，包括项目结构、配置文件、模块组织等。

#### Scenario: 初始化新项目
- **WHEN** 用户请求创建新的NestJS项目
- **THEN** 系统应提供项目结构模板、配置文件示例、模块组织建议

### Requirement: 代码生成与最佳实践
系统应支持NestJS核心功能的代码生成，并提供最佳实践建议。

#### Scenario: 生成控制器代码
- **WHEN** 用户请求创建控制器
- **THEN** 系统应生成符合TypeScript类型安全的控制器代码，包含装饰器和路由定义

#### Scenario: 生成服务代码
- **WHEN** 用户请求创建服务
- **THEN** 系统应生成使用依赖注入的服务代码，包含业务逻辑模板

#### Scenario: 生成中间件
- **WHEN** 用户请求创建中间件
- **THEN** 系统应生成符合NestJS中间件规范的代码

#### Scenario: 生成拦截器
- **WHEN** 用户请求创建拦截器
- **THEN** 系统应生成可复用的拦截器代码，包含响应转换、日志记录等示例

#### Scenario: 生成管道
- **WHEN** 用户请求创建管道
- **THEN** 系统应生成数据验证和转换的管道代码

#### Scenario: 生成守卫
- **WHEN** 用户请求创建守卫
- **THEN** 系统应生成权限验证和认证的守卫代码

### Requirement: 数据库集成
系统应提供NestJS与主流数据库ORM的配置和使用指南。

#### Scenario: TypeORM集成
- **WHEN** 用户请求配置TypeORM
- **THEN** 系统应提供配置文件示例、实体定义、Repository使用示例

#### Scenario: Sequelize集成
- **WHEN** 用户请求配置Sequelize
- **THEN** 系统应提供配置文件示例、模型定义、查询示例

### Requirement: 调试、测试与部署
系统应提供完整的开发工作流指导。

#### Scenario: 单元测试
- **WHEN** 用户需要编写单元测试
- **THEN** 系统应提供测试框架配置、测试用例示例、Mock使用指南

#### Scenario: 集成测试
- **WHEN** 用户需要编写集成测试
- **THEN** 系统应提供测试环境配置、端到端测试示例

#### Scenario: 部署流程
- **WHEN** 用户准备部署应用
- **THEN** 系统应提供构建配置、环境变量管理、Docker化部署指南

### Requirement: 进阶开发技巧
系统应提供性能优化、错误处理、日志管理等进阶主题的指导。

#### Scenario: 性能优化
- **WHEN** 用户需要优化应用性能
- **THEN** 系统应提供缓存策略、数据库查询优化、异步处理等建议

#### Scenario: 错误处理
- **WHEN** 用户需要实现错误处理
- **THEN** 系统应提供全局异常过滤器、自定义错误类、错误日志记录方案

#### Scenario: 日志管理
- **WHEN** 用户需要实现日志管理
- **THEN** 系统应提供日志配置、日志级别管理、结构化日志方案

### Requirement: 代码审查
系统应能够对NestJS项目进行审查并提供改进意见。

#### Scenario: 项目代码审查
- **WHEN** 用户请求审查NestJS项目
- **THEN** 系统应分析项目结构、代码质量、最佳实践遵循情况，输出改进意见清单

#### Scenario: 改进意见清单
- **WHEN** 审查完成
- **THEN** 系统应输出包含以下内容的清单：
  - 架构设计问题
  - 代码质量问题
  - 性能优化建议
  - 安全性问题
  - 最佳实践违反项
  - 优先级排序的改进建议

## MODIFIED Requirements
无

## REMOVED Requirements
无
