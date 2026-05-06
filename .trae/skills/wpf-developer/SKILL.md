---
name: wpf-developer
description: 该skill提供WPF项目开发辅助功能，包括项目初始化、代码生成、MVVM模式指导、数据绑定最佳实践、性能优化建议和代码审查功能，帮助开发者遵循WPF开发的基本原则，提高代码质量和可维护性
---

# WPF Developer Skill

## 功能概述

WPF Developer 是一个专门为 WPF（Windows Presentation Foundation）开发者设计的辅助 skill，提供全方位的开发支持，帮助开发者快速构建高质量、可维护的 WPF 应用程序。

## 核心功能

### 1. 项目初始化
- 快速创建标准的 WPF 项目结构
- 配置 MVVM 框架（Prism、MVVM Light、Caliburn.Micro）
- 设置依赖注入容器
- 配置样式资源和主题
- 创建基础的视图和视图模型结构

### 2. 代码生成
- 生成 View 和 ViewModel 模板
- 创建自定义控件和用户控件
- 生成命令类（ICommand 实现）
- 创建转换器（ValueConverter）
- 生成数据模板和样式

### 3. MVVM 模式指导
- 视图与视图模型分离原则
- 数据绑定最佳实践
- 命令模式实现
- 消息传递机制（EventAggregator/Messenger）
- 依赖注入配置

### 4. 数据绑定原则
- 单向绑定 vs 双向绑定
- 更新源触发器配置
- 绑定验证和错误提示
- 绑定性能优化
- 避免内存泄漏

### 5. 样式和资源管理
- 资源字典组织
- 样式继承和覆盖
- 模板定义和使用
- 主题切换实现
- 资源共享和复用

### 6. 服务注册和依赖注入
- Microsoft DI 容器配置
- Prism 容器集成
- 服务生命周期管理（Singleton/Scoped/Transient）
- ViewModel 注入模式
- 配置管理集成

### 7. 性能优化
- UI 虚拟化技术
- 数据绑定优化
- 异步加载策略
- 内存管理
- 渲染性能优化

### 8. 测试策略
- 单元测试 ViewModel
- UI 自动化测试
- 集成测试
- 测试覆盖率配置

### 8. 代码审查功能
- 代码质量分析和改进建议
- MVVM 模式合规检查
- 数据绑定问题检测
- 性能瓶颈识别
- 代码风格一致性检查

## 使用场景

### 场景一：创建新项目
当用户需要创建一个新的 WPF 项目时，该 skill 可以：
- 引导用户选择 MVVM 框架和项目结构
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
- 确保代码符合 WPF 最佳实践

### 场景四：问题排查
当用户遇到开发问题时，该 skill 可以：
- 分析错误日志和堆栈跟踪
- 提供问题诊断和解决方案
- 推荐相关的文档和资源

### 场景五：项目审查
当用户请求审查 WPF 项目时，该 skill 可以：
- 全面检查项目结构和代码质量
- 识别潜在的性能问题和内存泄漏
- 提供详细的审查报告和改进建议

## 调用时机

### 自动触发
- 当用户提到 "WPF"、"Windows Presentation Foundation" 等关键词时
- 当用户请求创建、修改或审查 WPF 项目时
- 当用户询问 WPF 相关的开发问题时

### 手动调用
用户可以通过以下方式主动调用该 skill：
- "帮我创建一个 WPF 项目"
- "审查一下我的 WPF 代码"
- "生成一个 WPF ViewModel"
- "如何实现 MVVM 模式"
- "优化我的 WPF 应用性能"
- "WPF 数据绑定最佳实践"
- "WPF 内存泄漏问题"

## 技术栈支持

### 核心框架
- .NET Framework 4.8+ / .NET 6+
- WPF (Windows Presentation Foundation)

### MVVM 框架
- Prism
- MVVM Light
- Caliburn.Micro
- ReactiveUI

### 依赖注入
- Unity
- Autofac
- Ninject
- Microsoft DI

### 测试
- xUnit
- NUnit
- MSTest
- Prism.Testing

### 工具
- Visual Studio 2022+
- Resharper/Rider
- Snoop (WPF Debugger)

## WPF 开发规范

### 1. 架构设计规范

#### 1.1 MVVM 架构原则
- **视图层（View）**：仅负责 UI 展示，不包含业务逻辑
- **视图模型层（ViewModel）**：包含 UI 逻辑和数据，实现 INotifyPropertyChanged
- **模型层（Model）**：包含业务数据和业务逻辑，不依赖 UI 层

#### 1.2 项目结构
```
MyWpfApp/
├── Views/                    # 视图目录
├── ViewModels/               # 视图模型目录
├── Models/                   # 模型目录
├── Commands/                 # 命令目录
├── Converters/               # 转换器目录
├── Services/                 # 服务目录
├── Resources/                # 资源目录
│   ├── Themes/               # 主题文件
│   └── Controls/             # 控件样式
└── App.xaml                  # 应用配置
```

#### 1.3 依赖注入

##### 1.3.1 容器选择
- 新项目推荐使用 **Microsoft DI**
- Prism 项目使用 **Prism Container**
- 需要高级特性使用 **Autofac**

##### 1.3.2 服务生命周期
| 生命周期 | 适用场景 | 示例 |
|----------|----------|------|
| Singleton | 无状态服务、工具类 | 缓存服务、事件聚合器 |
| Scoped | 数据库上下文、业务服务 | 用户服务、订单服务 |
| Transient | 轻量级服务、工厂对象 | 日志服务、映射器 |

##### 1.3.3 注册模式
- 使用接口抽象服务
- 通过构造函数注入依赖
- 在 `ConfigureServices` 中集中注册

##### 1.3.4 配置管理
- 使用强类型配置类
- 通过 `IOptions<T>` 注入配置
- 支持 JSON/XML/环境变量配置源

##### 1.3.5 启动配置
```csharp
var host = Host.CreateDefaultBuilder()
    .ConfigureServices((_, services) =>
    {
        services.AddSingleton<IDataService, DataService>();
        services.AddScoped<IUserService, UserService>();
        services.Configure<AppSettings>(Configuration.GetSection("AppSettings"));
    })
    .Build();
```

### 2. 数据绑定规范

#### 2.1 绑定模式选择
| 场景 | 推荐模式 |
|------|----------|
| 显示数据 | OneWay |
| 输入控件 | TwoWay |
| 静态数据 | OneTime |
| 仅更新源 | OneWayToSource |

#### 2.2 更新源触发器
- 输入控件使用 `UpdateSourceTrigger=PropertyChanged`
- 大数据量输入使用 `UpdateSourceTrigger=LostFocus`

#### 2.3 空值处理
- 使用 `FallbackValue` 设置默认值
- 使用 `TargetNullValue` 处理空值

#### 2.4 绑定验证
- 实现 `IDataErrorInfo` 或 `INotifyDataErrorInfo`
- 设置 `ValidatesOnDataErrors=True`

### 3. 命令模式规范

#### 3.1 命令实现
- 使用 `RelayCommand`（MVVM Light）或 `DelegateCommand`（Prism）
- 所有用户交互通过 `ICommand` 实现

#### 3.2 命令组织
- 将相关命令分组
- 使用 `CanExecute` 控制命令可用性
- 条件变化时调用 `RaiseCanExecuteChanged`

### 4. 样式和资源规范

#### 4.1 资源字典组织
- 使用资源字典集中管理样式
- 按功能拆分资源字典（Buttons.xaml、TextBoxes.xaml 等）

#### 4.2 样式继承
- 使用 `BasedOn` 继承现有样式
- 避免在每个控件中重复定义样式

#### 4.3 资源引用
- 静态资源使用 `StaticResource`
- 动态主题资源使用 `DynamicResource`

### 5. 性能优化规范

#### 5.1 UI 虚拟化
- 对大量数据使用 `VirtualizingStackPanel`
- 使用 `Recycling` 模式重用容器
- 设置合理的 `CacheLength`

#### 5.2 异步操作
- 将耗时操作移到后台线程
- 使用 `Task.Run` 或 `BackgroundWorker`
- 使用 `IProgress` 报告进度

#### 5.3 渲染优化
- 使用 `RenderOptions.CachingHint=Cache`
- 避免过度使用阴影和透明度
- 使用 `DrawingImage` 替代 `BitmapImage`

### 6. 内存管理规范

#### 6.1 事件订阅管理
- 在对象销毁时取消所有事件订阅
- 使用 `WeakEventManager` 避免强引用

#### 6.2 资源释放
- 实现 `IDisposable` 接口
- 及时释放 `Timer` 等定时资源
- 使用 `using` 语句管理数据库连接

### 7. .NET 框架兼容规范

#### 7.1 目标框架
- 推荐使用 `.NET 8`（LTS 版本）
- 支持 `.NET 6+` 和 `.NET Framework 4.8+`

#### 7.2 项目文件配置
```xml
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>net8.0-windows</TargetFramework>
        <UseWPF>true</UseWPF>
        <Nullable>enable</Nullable>
        <ImplicitUsings>enable</ImplicitUsings>
    </PropertyGroup>
</Project>
```

#### 7.3 语言特性利用
- 使用 C# 9+ 顶级语句
- 使用记录类型简化数据对象
- 使用空值安全特性

#### 7.4 API 兼容性
| .NET Framework | .NET 6+ 替代 |
|----------------|--------------|
| `System.Windows.Interactivity` | `Microsoft.Xaml.Behaviors.Wpf` |
| `System.Drawing` | `System.Drawing.Common` |

### 8. 代码质量规范

#### 8.1 命名规范
- 文件命名：PascalCase（如 `MainViewModel.cs`）
- 类命名：PascalCase
- 方法命名：PascalCase
- 变量命名：camelCase
- 私有字段：`_camelCase`

#### 8.2 代码结构
- 每个类只负责一个功能（单一职责）
- 方法代码不超过 50 行
- 使用提取方法消除重复代码

#### 8.3 错误处理
- 捕获特定异常，不捕获所有异常
- 记录异常信息便于排查
- 向用户显示友好的错误信息

### 9. 安全性规范

#### 9.1 输入验证
- 所有用户输入都进行验证
- 数据库操作使用参数化查询
- 文件路径输入进行验证

#### 9.2 敏感数据
- 密码存储使用加密
- 日志中不记录敏感信息
- 网络传输使用 HTTPS

### 10. 测试规范

#### 10.1 单元测试
- 使用 xUnit 或 NUnit
- 测试 ViewModel 的属性和命令
- 测试覆盖率不低于 80%

#### 10.2 UI 测试
- 使用 CodedUI 或 Playwright
- 测试主要用户流程
- 定期运行回归测试

## 注意事项

1. 该 skill 始终遵循 WPF 官方文档和最佳实践
2. 生成的代码会考虑项目的具体需求和上下文
3. 提供的建议会根据项目规模和复杂度进行调整
4. 始终优先考虑代码的可维护性和可扩展性
5. 性能和内存管理是代码审查的重点关注领域

## 相关资源

- [WPF 官方文档](https://learn.microsoft.com/zh-cn/dotnet/desktop/wpf/)
- [Prism 框架文档](https://prismlibrary.com/docs/)
- [MVVM Light 文档](https://mvvmlight.net/)
- [WPF 性能优化指南](https://learn.microsoft.com/zh-cn/dotnet/desktop/wpf/advanced/optimizing-wpf-application-performance)