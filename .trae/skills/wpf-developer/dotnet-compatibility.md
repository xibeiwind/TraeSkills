# WPF .NET 最新框架兼容指南

## 目录

- [概述](#概述)
- [迁移策略](#迁移策略)
- [.NET 6+ 新特性利用](#net-6-新特性利用)
- [性能优化](#性能优化)
- [现代化改进](#现代化改进)
- [兼容性考虑](#兼容性考虑)

## 概述

随着 .NET 6、7、8 的发布，WPF 也获得了许多新特性和性能改进。本指南介绍如何将 WPF 应用迁移到最新的 .NET 框架，并充分利用新框架的优势。

## 迁移策略

### 1. 从 .NET Framework 迁移到 .NET 6+

#### 步骤 1: 评估现有项目
- 检查项目依赖（NuGet 包）
- 识别使用的 WPF API
- 检查 COM 互操作和 Win32 API 调用

#### 步骤 2: 创建新项目
使用 .NET 6+ 模板创建新项目，然后迁移代码：

```bash
dotnet new wpf -n MyWpfApp
```

#### 步骤 3: 迁移代码
- 复制现有代码文件
- 更新命名空间引用
- 修复编译错误

#### 步骤 4: 更新依赖
- 更新 NuGet 包版本
- 替换过时的包（如 `System.Windows.Interactivity`）

### 2. 逐步迁移策略

对于大型项目，建议采用逐步迁移：

```csharp
// .NET Framework 兼容性模式
#if NETFRAMEWORK
    // 旧代码
#else
    // .NET 6+ 新代码
#endif
```

## .NET 6+ 新特性利用

### 1. C# 语言特性

#### 顶级语句（C# 9+）

```csharp
// 简化 Program.cs
using System;
using System.Windows;

var app = new App();
app.Run();
```

#### 记录类型（C# 9+）

```csharp
public record User(string Name, string Email);

// 使用 with 表达式
var updatedUser = user with { Email = "new@example.com" };
```

#### 空值判断（C# 8+）

```csharp
// 空合并赋值
string name = null;
name ??= "Default Name";

// 空条件运算符
var length = text?.Length ?? 0;
```

#### 文件范围命名空间（C# 10+）

```csharp
namespace MyWpfApp.ViewModels;

public class MainViewModel { }
```

### 2. 性能改进

#### Span 和 Memory

```csharp
public void ProcessData(Span<byte> buffer)
{
    // 零分配操作
    buffer.Fill(0);
}
```

#### 异步流（C# 8+）

```csharp
public async IAsyncEnumerable<User> GetUsersAsync()
{
    using var db = new DatabaseContext();
    await foreach (var user in db.Users.AsAsyncEnumerable())
    {
        yield return user;
    }
}
```

### 3. WPF 特定改进

#### .NET 6 WPF 改进

- **触摸和笔支持增强**
- **高 DPI 改进**
- **性能分析工具集成**

#### .NET 7 WPF 改进

- **Windows 11 视觉效果支持**
- **改进的窗口管理**
- **性能优化**

#### .NET 8 WPF 改进

- **Native AOT 支持**（预览）
- **更好的 ARM64 支持**
- **更多性能改进**

## 性能优化

### 1. 使用 .NET 6+ 的性能特性

#### 泛型缓存

```csharp
[MethodImpl(MethodImplOptions.AggressiveInlining)]
public static T GetService<T>(this IServiceProvider provider)
{
    return (T)provider.GetService(typeof(T));
}
```

#### ValueTask

```csharp
public async ValueTask<string> GetDataAsync()
{
    // 快速路径返回同步结果
    if (_cachedData != null)
        return _cachedData;
    
    // 慢速路径异步获取
    return await _service.FetchDataAsync();
}
```

### 2. UI 虚拟化增强

```xml
<ListBox ItemsSource="{Binding Items}">
    <ListBox.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingStackPanel VirtualizationMode="Recycling" />
        </ItemsPanelTemplate>
    </ListBox.ItemsPanel>
</ListBox>
```

### 3. 编译优化

```xml
<!-- .csproj -->
<PropertyGroup>
    <Optimize>true</Optimize>
    <TieredCompilation>true</TieredCompilation>
    <PublishReadyToRun>true</PublishReadyToRun>
</PropertyGroup>
```

## 现代化改进

### 1. 使用 MSBuild SDK 风格项目

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

### 2. 依赖注入集成

```csharp
public partial class App : Application
{
    private IHost _host;

    protected override void OnStartup(StartupEventArgs e)
    {
        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                services.AddSingleton<IMainViewModel, MainViewModel>();
                services.AddSingleton<MainWindow>();
            })
            .Build();

        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _host.Dispose();
        base.OnExit(e);
    }
}
```

### 3. 配置管理

```csharp
public class AppSettings
{
    public string ApiUrl { get; set; }
    public int Timeout { get; set; }
}

// 在 Startup 中
var settings = builder.Configuration.GetSection("AppSettings").Get<AppSettings>();
services.AddSingleton(settings);
```

## 兼容性考虑

### 1. API 兼容性

| .NET Framework | .NET 6+ |
|----------------|---------|
| `System.Windows.Interactivity` | `Microsoft.Xaml.Behaviors.Wpf` |
| `System.Drawing` | `System.Drawing.Common` (Windows 仅) |
| `System.Web` | `System.Net.Http` |

### 2. COM 互操作

```csharp
using System.Runtime.InteropServices;

[ComImport]
[Guid("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMyComInterface
{
    void DoSomething();
}
```

### 3. 打包和部署

#### MSIX 打包

```xml
<!-- Package.appxmanifest -->
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10">
    <Identity Name="MyWpfApp" Version="1.0.0.0" Publisher="CN=MyCompany" />
    <Properties>
        <DisplayName>My WPF App</DisplayName>
        <PublisherDisplayName>My Company</PublisherDisplayName>
    </Properties>
</Package>
```

## 迁移检查清单

- [ ] 更新项目文件为 SDK 风格
- [ ] 升级 NuGet 包到最新版本
- [ ] 替换过时的 API
- [ ] 启用可空引用类型
- [ ] 配置依赖注入
- [ ] 测试性能改进
- [ ] 验证所有功能正常

## 总结

迁移到 .NET 6+ 可以获得：

1. **更好的性能**：JIT 改进、内存优化
2. **现代语言特性**：记录类型、顶级语句、空值安全
3. **更好的开发体验**：SDK 风格项目、更好的工具支持
4. **长期支持**：.NET 8 是 LTS 版本

通过逐步迁移和充分利用新特性，可以显著提升 WPF 应用的质量和开发效率。