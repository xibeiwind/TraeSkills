# WPF 服务注册和依赖注入指南

## 目录

- [概述](#概述)
- [依赖注入容器选择](#依赖注入容器选择)
- [Microsoft DI 集成](#microsoft-di-集成)
- [Prism 容器集成](#prism-容器集成)
- [服务注册模式](#服务注册模式)
- [ViewModel 注入](#viewmodel-注入)
- [最佳实践](#最佳实践)

## 概述

依赖注入（DI）是 WPF 应用程序的核心模式，它可以：
- 解耦组件
- 提高可测试性
- 便于替换实现
- 支持配置化

本指南介绍如何在 WPF 项目中实现服务注册和依赖注入。

## 依赖注入容器选择

### 推荐容器

| 容器 | 特点 | 适用场景 |
|------|------|----------|
| **Microsoft DI** | 轻量级、内置、跨平台 | .NET 6+ 新项目 |
| **Unity** | 功能强大、支持属性注入 | 传统 WPF 项目 |
| **Autofac** | 高性能、灵活配置 | 大型项目 |
| **Prism Container** | MVVM 集成、模块化支持 | Prism 项目 |

### 选择建议

- 新项目推荐使用 **Microsoft DI**
- 使用 Prism 框架推荐使用 **Prism Container**
- 需要高级特性推荐使用 **Autofac**

## Microsoft DI 集成

### 1. 配置服务容器

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

public partial class App : Application
{
    private IHost _host;

    protected override void OnStartup(StartupEventArgs e)
    {
        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                // 注册服务
                ConfigureServices(services);
            })
            .Build();

        // 启动主窗口
        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _host.Dispose();
        base.OnExit(e);
    }

    private void ConfigureServices(IServiceCollection services)
    {
        // 配置文件
        services.Configure<AppSettings>(Configuration.GetSection("AppSettings"));
        
        // 单例服务
        services.AddSingleton<IDataService, DataService>();
        services.AddSingleton<IEventAggregator, EventAggregator>();
        
        // 作用域服务
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IOrderService, OrderService>();
        
        // 临时服务
        services.AddTransient<ILogger, ConsoleLogger>();
        
        // ViewModel
        services.AddTransient<MainViewModel>();
        services.AddTransient<UserViewModel>();
        
        // Views
        services.AddTransient<MainWindow>();
        services.AddTransient<UserView>();
    }
}
```

### 2. 注入服务到 ViewModel

```csharp
public class MainViewModel : ViewModelBase
{
    private readonly IUserService _userService;
    private readonly IEventAggregator _eventAggregator;

    public MainViewModel(IUserService userService, IEventAggregator eventAggregator)
    {
        _userService = userService;
        _eventAggregator = eventAggregator;
    }

    public async Task LoadUsers()
    {
        Users = await _userService.GetUsersAsync();
    }
}
```

### 3. 注入到 View

```csharp
public partial class MainWindow : Window
{
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
```

## Prism 容器集成

### 1. 创建 Prism 应用

```csharp
public class Bootstrapper : PrismBootstrapper
{
    protected override DependencyObject CreateShell()
    {
        return Container.Resolve<MainWindow>();
    }

    protected override void RegisterTypes(IContainerRegistry containerRegistry)
    {
        // 注册服务
        containerRegistry.RegisterSingleton<IDataService, DataService>();
        containerRegistry.Register<IUserService, UserService>();
        
        // 注册 View 和 ViewModel
        containerRegistry.RegisterForNavigation<MainView, MainViewModel>();
        containerRegistry.RegisterForNavigation<UserView, UserViewModel>();
    }
}
```

### 2. 启动应用

```csharp
public partial class App : PrismApplication
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
    }

    protected override void RegisterTypes(IContainerRegistry containerRegistry)
    {
        // 注册服务
        containerRegistry.RegisterSingleton<IDataService, DataService>();
    }

    protected override Window CreateShell()
    {
        return Container.Resolve<MainWindow>();
    }
}
```

## 服务注册模式

### 1. 单例模式（Singleton）

适用于无状态服务、工具类、配置服务。

```csharp
services.AddSingleton<ICacheService, CacheService>();
```

### 2. 作用域模式（Scoped）

适用于数据库上下文、业务服务。

```csharp
services.AddScoped<IUnitOfWork, UnitOfWork>();
```

### 3. 临时模式（Transient）

适用于轻量级服务、工厂创建的对象。

```csharp
services.AddTransient<IMapper, Mapper>();
```

### 4. 工厂模式

适用于需要动态创建的对象。

```csharp
services.AddSingleton<Func<ITaskService>>(provider => 
    () => provider.GetRequiredService<ITaskService>()
);
```

## ViewModel 注入

### 1. 构造函数注入（推荐）

```csharp
public class UserViewModel : ViewModelBase
{
    private readonly IUserService _userService;

    public UserViewModel(IUserService userService)
    {
        _userService = userService;
    }
}
```

### 2. 属性注入（谨慎使用）

```csharp
public class UserViewModel : ViewModelBase
{
    [Dependency]
    public IUserService UserService { get; set; }
}
```

### 3. ViewModel 定位器

```csharp
public class ViewModelLocator
{
    public MainViewModel MainViewModel => 
        ServiceLocator.Current.GetInstance<MainViewModel>();
}
```

```xml
<Application.Resources>
    <local:ViewModelLocator x:Key="Locator" />
</Application.Resources>

<Window DataContext="{Binding MainViewModel, Source={StaticResource Locator}}">
```

## 配置管理

### 1. 强类型配置

```csharp
public class AppSettings
{
    public string ApiUrl { get; set; }
    public int Timeout { get; set; }
    public LogSettings Logging { get; set; }
}

public class LogSettings
{
    public string Level { get; set; }
    public string Path { get; set; }
}
```

### 2. 绑定配置

```csharp
services.Configure<AppSettings>(Configuration.GetSection("AppSettings"));
```

### 3. 使用配置

```csharp
public class DataService : IDataService
{
    private readonly AppSettings _settings;

    public DataService(IOptions<AppSettings> settings)
    {
        _settings = settings.Value;
    }

    public async Task<List<User>> GetUsers()
    {
        var url = _settings.ApiUrl + "/users";
        // 调用 API
    }
}
```

## 最佳实践

### 1. 接口优先

- 为服务定义接口
- 依赖抽象而非具体实现

```csharp
public interface IUserService { }
public class UserService : IUserService { }
```

### 2. 避免服务定位器反模式

**错误做法**：
```csharp
var service = ServiceLocator.Current.GetInstance<IUserService>();
```

**正确做法**：
```csharp
public class MyViewModel
{
    public MyViewModel(IUserService userService) { }
}
```

### 3. 服务分组注册

```csharp
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IOrderService, OrderService>();
        return services;
    }
    
    public static IServiceCollection AddViewModelServices(this IServiceCollection services)
    {
        services.AddTransient<MainViewModel>();
        services.AddTransient<UserViewModel>();
        return services;
    }
}
```

### 4. 测试支持

```csharp
[TestClass]
public class UserViewModelTests
{
    [TestMethod]
    public void LoadUsers_ShouldPopulateUsers()
    {
        // 使用 Mock 服务
        var mockService = new Mock<IUserService>();
        mockService.Setup(s => s.GetUsersAsync()).ReturnsAsync(new List<User>());
        
        var viewModel = new UserViewModel(mockService.Object);
        viewModel.LoadUsersCommand.Execute(null);
        
        Assert.IsNotNull(viewModel.Users);
    }
}
```

### 5. 容器验证

```csharp
// 在启动时验证容器配置
var provider = services.BuildServiceProvider();
provider.Validate();
```

## 常见问题

### 问题 1: 循环依赖

**原因**：两个服务相互依赖

**解决方案**：
- 重构代码，移除循环依赖
- 使用 `Lazy<T>` 延迟初始化

### 问题 2: 服务未注册

**原因**：忘记注册服务或注册顺序错误

**解决方案**：
- 检查服务注册代码
- 使用容器验证

### 问题 3: 生命周期问题

**原因**：服务生命周期不匹配

**解决方案**：
- 了解各种生命周期的含义
- 根据需求选择合适的生命周期

## 总结

依赖注入是 WPF 应用的基础架构模式，正确使用可以：
- 提高代码可测试性
- 降低组件耦合度
- 便于维护和扩展

推荐使用 **Microsoft DI** 作为默认容器，配合构造函数注入模式。