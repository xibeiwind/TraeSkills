# WPF MVVM 最佳实践

## 目录

- [概述](#概述)
- [视图层（View）原则](#视图层view原则)
- [视图模型层（ViewModel）原则](#视图模型层viewmodel原则)
- [模型层（Model）原则](#模型层model原则)
- [命令模式](#命令模式)
- [数据绑定](#数据绑定)
- [消息传递](#消息传递)
- [依赖注入](#依赖注入)
- [常见错误](#常见错误)

## 概述

MVVM（Model-View-ViewModel）是 WPF 开发的核心架构模式，它将应用程序分为三个主要层次：

- **View**：负责 UI 展示
- **ViewModel**：包含 UI 逻辑和数据
- **Model**：包含业务数据和业务逻辑

正确的 MVVM 实现可以提高代码的可测试性、可维护性和可扩展性。

## 视图层（View）原则

### 1. 仅负责 UI 展示
- View 不应包含业务逻辑
- 所有用户交互应通过命令绑定
- 避免在 Code-behind 中编写复杂逻辑

### 2. 数据上下文设置
- 使用 `DataContext` 绑定到 ViewModel
- 优先使用 XAML 声明方式
- 避免在代码中直接设置 DataContext（除非必要）

```xml
<Window.DataContext>
    <viewModels:MainViewModel/>
</Window.DataContext>
```

### 3. 避免代码隐藏
- 禁止在 Code-behind 中处理业务逻辑
- 仅保留 UI 相关的初始化代码
- 事件处理应通过命令绑定

### 4. 使用数据模板
- 使用 `DataTemplate` 定义数据展示方式
- 使用 `DataTemplateSelector` 动态选择模板
- 避免在 View 中硬编码数据展示逻辑

## 视图模型层（ViewModel）原则

### 1. 实现 INotifyPropertyChanged
- 所有绑定属性必须触发 `PropertyChanged` 事件
- 使用基类封装属性更改通知

```csharp
public class ViewModelBase : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler PropertyChanged;
    
    protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
    
    protected bool Set<T>(ref T field, T value, [CallerMemberName] string propertyName = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value)) return false;
        field = value;
        OnPropertyChanged(propertyName);
        return true;
    }
}
```

### 2. ViewModel 应独立于 View
- ViewModel 不应引用 View 类型
- 不依赖特定的 UI 控件
- 可在没有 View 的情况下进行测试

### 3. 属性命名规范
- 使用 PascalCase 命名属性
- 属性名称应清晰描述其用途
- 避免使用缩写（除非约定俗成）

### 4. 命令组织
- 将相关命令分组
- 使用 `RelayCommand` 或 `DelegateCommand`
- 命令逻辑应简洁

## 模型层（Model）原则

### 1. 业务逻辑封装
- Model 包含核心业务逻辑
- 不依赖 UI 层
- 可独立测试

### 2. 数据验证
- 在 Model 层进行数据验证
- 使用 `IDataErrorInfo` 或 `INotifyDataErrorInfo`
- 验证逻辑应可复用

### 3. 实体设计
- 保持实体简洁
- 使用自动属性
- 避免在实体中包含 UI 相关逻辑

```csharp
public class User
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public DateTime CreatedAt { get; set; }
}
```

## 命令模式

### 1. 使用 ICommand 实现
- 所有用户操作通过命令执行
- 使用 `RelayCommand`（MVVM Light）或 `DelegateCommand`（Prism）

```csharp
public ICommand SaveCommand { get; }
public ICommand DeleteCommand { get; }

public UserViewModel()
{
    SaveCommand = new RelayCommand(Save, CanSave);
    DeleteCommand = new RelayCommand(Delete, CanDelete);
}

private void Save()
{
    // 保存逻辑
}

private bool CanSave()
{
    return !string.IsNullOrEmpty(Name);
}
```

### 2. 命令参数传递
- 使用 `CommandParameter` 传递参数
- 保持参数类型明确

```xml
<Button Command="{Binding DeleteCommand}" 
        CommandParameter="{Binding SelectedItem}">
    删除
</Button>
```

### 3. 命令状态管理
- 使用 `CanExecute` 控制命令可用性
- 当条件变化时调用 `RaiseCanExecuteChanged`

## 数据绑定

### 1. 绑定模式选择
- **OneWay**：从源到目标（默认）
- **TwoWay**：双向绑定（用于输入控件）
- **OneTime**：一次性绑定（静态数据）
- **OneWayToSource**：从目标到源

### 2. 更新源触发器
- **PropertyChanged**：属性变化时立即更新
- **LostFocus**：失去焦点时更新（默认）
- **Explicit**：手动触发更新

```xml
<TextBox Text="{Binding Name, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}"/>
```

### 3. 空值处理
- 使用 `FallbackValue` 设置默认值
- 使用 `TargetNullValue` 处理空值

```xml
<TextBlock Text="{Binding MiddleName, FallbackValue='(无)', TargetNullValue='(空)'}" />
```

### 4. 绑定验证
- 使用 `ValidatesOnDataErrors` 启用验证
- 使用 `Validation.ErrorTemplate` 自定义错误显示

```xml
<TextBox Text="{Binding Email, ValidatesOnDataErrors=True}">
    <Validation.ErrorTemplate>
        <ControlTemplate>
            <DockPanel>
                <TextBlock Foreground="Red" Text="*" DockPanel.Dock="Right"/>
                <AdornedElementPlaceholder/>
            </DockPanel>
        </ControlTemplate>
    </Validation.ErrorTemplate>
</TextBox>
```

## 消息传递

### 1. 使用 EventAggregator/Messenger
- 在不相关的组件间传递消息
- Prism 使用 `IEventAggregator`
- MVVM Light 使用 `IMessenger`

### 2. 消息定义
- 创建强类型消息类
- 包含必要的数据

```csharp
public class UserSavedMessage
{
    public User User { get; }
    
    public UserSavedMessage(User user)
    {
        User = user;
    }
}
```

### 3. 订阅和发布
- 在 ViewModel 中订阅消息
- 在适当的位置发布消息

```csharp
// 订阅
_messenger.Register<UserSavedMessage>(this, OnUserSaved);

// 发布
_messenger.Send(new UserSavedMessage(user));
```

## 依赖注入

### 1. 使用 DI 容器
- Prism 使用 Unity/Autofac
- MVVM Light 使用 SimpleIoc
- 注册服务和 ViewModel

### 2. 构造函数注入
- 通过构造函数注入依赖
- 避免属性注入

```csharp
public MainViewModel(IUserService userService, IEventAggregator eventAggregator)
{
    _userService = userService;
    _eventAggregator = eventAggregator;
}
```

### 3. 服务注册
- 在模块初始化时注册服务
- 使用适当的生命周期（Singleton/Transient）

## 常见错误

### 1. ViewModel 引用 View
- **问题**：ViewModel 直接引用 UI 控件
- **解决方案**：使用数据绑定和命令

### 2. 未实现 INotifyPropertyChanged
- **问题**：属性变化时 UI 不更新
- **解决方案**：所有绑定属性必须触发 PropertyChanged

### 3. 在 UI 线程执行耗时操作
- **问题**：UI 卡顿
- **解决方案**：使用 `Task.Run` 或 `BackgroundWorker`

### 4. 事件订阅未取消
- **问题**：内存泄漏
- **解决方案**：在 ViewModel 销毁时取消订阅

### 5. 过度使用双向绑定
- **问题**：性能问题和难以追踪的数据流
- **解决方案**：优先使用单向绑定

## 总结

遵循这些 MVVM 最佳实践可以帮助您创建：
- **可测试的**：ViewModel 可独立测试
- **可维护的**：职责清晰，易于理解
- **可扩展的**：便于添加新功能
- **高性能的**：避免常见的性能陷阱

始终牢记：**View 负责展示，ViewModel 负责逻辑，Model 负责数据**。