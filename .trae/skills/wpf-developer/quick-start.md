# WPF Developer Skill 快速开始指南

欢迎使用 WPF Developer Skill！本指南将帮助您快速上手，使用该 skill 进行高效的 WPF 项目开发。

## 目录

- [简介](#简介)
- [前提条件](#前提条件)
- [快速安装](#快速安装)
- [创建第一个项目](#创建第一个项目)
- [核心功能概览](#核心功能概览)
- [项目结构](#项目结构)
- [常见问题](#常见问题)

## 简介

WPF Developer Skill 是一个专门为 WPF 开发者设计的智能辅助工具，提供以下核心功能：

- 🚀 **项目初始化** - 快速创建标准化的 WPF 项目结构
- 📝 **代码生成** - 自动生成 View、ViewModel、命令等代码模板
- 💡 **MVVM 指导** - 提供符合 MVVM 模式的开发建议
- ⚡ **性能优化** - 识别性能瓶颈和内存泄漏问题
- 🔍 **代码审查** - 自动检测代码质量和潜在问题

## 前提条件

在使用 WPF Developer Skill 之前，请确保您的开发环境满足以下要求：

### 必需环境

- **Visual Studio 2022** 或更高版本
- **.NET Framework 4.8** 或 **.NET 6/7/8**
- **WPF 开发工具**（Visual Studio 安装时勾选）

### 可选工具

- **Resharper** 或 **Rider** - 代码分析工具
- **Snoop** - WPF UI 调试工具
- **.NET Memory Profiler** - 内存分析工具

## 快速安装

### 1. 安装 Visual Studio 2022

确保安装了 WPF 开发工作负载：

1. 打开 Visual Studio Installer
2. 选择 "修改" 您的 Visual Studio 安装
3. 勾选 ".NET 桌面开发" 工作负载
4. 点击 "修改" 完成安装

### 2. 创建新项目

使用 WPF Developer Skill 创建新项目：

```
请帮我创建一个 WPF 项目，包含以下配置：
- 使用 Prism 作为 MVVM 框架
- 使用 Unity 作为依赖注入容器
- 创建基础的主窗口和视图模型
- 配置资源字典
```

## 创建第一个项目

### 步骤 1: 项目初始化

使用 WPF Developer Skill 进行项目初始化：

```
创建一个 WPF 应用程序，使用 MVVM Light 框架，包含：
- MainWindow 和 MainViewModel
- 示例数据绑定
- 命令绑定示例
```

### 步骤 2: 配置 App.xaml

更新 `App.xaml` 文件，配置资源字典和启动窗口：

```xml
<Application x:Class="MyWpfApp.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:local="clr-namespace:MyWpfApp">
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="Resources/Styles.xaml"/>
                <ResourceDictionary Source="Resources/Templates.xaml"/>
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>
</Application>
```

### 步骤 3: 创建 ViewModel

创建 `MainViewModel.cs`：

```csharp
using GalaSoft.MvvmLight;
using GalaSoft.MvvmLight.Command;

namespace MyWpfApp.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private string _welcomeMessage;
        
        public string WelcomeMessage
        {
            get => _welcomeMessage;
            set => Set(ref _welcomeMessage, value);
        }

        public ICommand GreetCommand { get; }

        public MainViewModel()
        {
            WelcomeMessage = "欢迎使用 WPF Developer Skill!";
            GreetCommand = new RelayCommand(ShowGreeting);
        }

        private void ShowGreeting()
        {
            WelcomeMessage = "Hello, WPF!";
        }
    }
}
```

### 步骤 4: 创建 View

创建 `MainWindow.xaml`：

```xml
<Window x:Class="MyWpfApp.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:viewModels="clr-namespace:MyWpfApp.ViewModels"
        Title="WPF App" Height="450" Width="800">
    
    <Window.DataContext>
        <viewModels:MainViewModel/>
    </Window.DataContext>
    
    <Grid>
        <StackPanel HorizontalAlignment="Center" VerticalAlignment="Center" Spacing="20">
            <TextBlock Text="{Binding WelcomeMessage}" FontSize="24"/>
            <Button Content="点击问候" Command="{Binding GreetCommand}" Width="150"/>
        </StackPanel>
    </Grid>
</Window>
```

### 步骤 5: 启动应用

按 F5 启动应用程序，查看效果。

## 核心功能概览

### 1. 代码生成

使用 WPF Developer Skill 快速生成代码：

```
生成一个用户管理模块，包含：
- UserView 和 UserViewModel
- 用户列表绑定
- 添加/编辑/删除命令
```

### 2. MVVM 模式

```
帮我设计一个符合 MVVM 模式的订单管理界面
```

### 3. 数据绑定

```
WPF 数据绑定最佳实践是什么？
```

### 4. 性能优化

```
我的 WPF 应用加载很慢，如何优化？
```

### 5. 代码审查

```
审查我的 WPF 项目代码，检查 MVVM 模式合规性
```

## 项目结构示例

WPF Developer Skill 生成的标准项目结构：

```
MyWpfApp/
├── App.xaml                    # 应用配置
├── App.xaml.cs
├── MainWindow.xaml             # 主窗口
├── MainWindow.xaml.cs
├── Views/                      # 视图目录
│   ├── MainWindow.xaml
│   ├── UserView.xaml
│   └── OrderView.xaml
├── ViewModels/                 # 视图模型目录
│   ├── MainViewModel.cs
│   ├── UserViewModel.cs
│   └── OrderViewModel.cs
├── Models/                     # 模型目录
│   ├── User.cs
│   └── Order.cs
├── Commands/                   # 命令目录
│   └── RelayCommand.cs
├── Converters/                 # 转换器目录
│   └── BooleanToVisibilityConverter.cs
├── Services/                   # 服务目录
│   └── DataService.cs
├── Resources/                  # 资源目录
│   ├── Styles.xaml
│   └── Templates.xaml
└── Properties/
    └── AssemblyInfo.cs
```

## 开发工作流

### 1. 需求分析

```
我需要创建一个客户管理系统，包含客户列表、添加客户、编辑客户功能
```

### 2. 设计架构

```
帮我设计客户管理系统的模块结构，使用 MVVM 模式
```

### 3. 生成代码

```
生成客户管理模块，包含 CustomerView 和 CustomerViewModel
```

### 4. 编写测试

```
为 CustomerViewModel 编写单元测试
```

### 5. 代码审查

```
审查客户管理系统的代码，提供优化建议
```

## 常见问题

### 问题 1: 数据绑定不生效

检查以下几点：
- DataContext 是否已正确设置
- 属性是否实现了 INotifyPropertyChanged
- 绑定路径是否正确

### 问题 2: 内存泄漏

常见原因：
- 事件订阅未取消
- 强引用的命令
- StaticResource 引用

### 问题 3: UI 卡顿

优化建议：
- 使用 UI 虚拟化
- 将耗时操作移到后台线程
- 优化数据模板

## 下一步

恭喜您完成了快速开始！现在您可以：

1. 📖 阅读 [MVVM 最佳实践文档](./mvvm-best-practices.md) 了解更多详细用法
2. 📚 查看 [数据绑定指南](./data-binding-guide.md) 解决遇到的问题
3. 🔍 探索项目中的其他文档文件，了解各个功能的详细信息
4. 🚀 开始构建您的 WPF 应用

---

祝您开发愉快！🎉