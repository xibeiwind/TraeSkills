# WPF 数据绑定指南

## 目录

- [概述](#概述)
- [绑定基础](#绑定基础)
- [绑定模式](#绑定模式)
- [更新源触发器](#更新源触发器)
- [绑定路径](#绑定路径)
- [值转换器](#值转换器)
- [绑定验证](#绑定验证)
- [绑定性能](#绑定性能)
- [常见问题](#常见问题)

## 概述

数据绑定是 WPF 的核心特性，它允许 UI 元素与数据源自动同步。正确使用数据绑定可以减少样板代码，提高代码可维护性。

## 绑定基础

### 1. 绑定语法

```xml
<TextBlock Text="{Binding Path=PropertyName}" />
```

### 2. DataContext

每个元素都有 `DataContext` 属性，绑定会自动查找该属性作为数据源。

```xml
<Window DataContext="{StaticResource MainViewModel}">
    <TextBlock Text="{Binding WelcomeMessage}" />
</Window>
```

### 3. 绑定目标和源

- **目标**：UI 控件的属性（如 TextBlock.Text）
- **源**：DataContext 中的属性（如 ViewModel.Name）

## 绑定模式

### 1. OneWay（单向绑定）

从源到目标的绑定，适用于只读数据。

```xml
<TextBlock Text="{Binding Name, Mode=OneWay}" />
```

### 2. TwoWay（双向绑定）

双向同步，适用于输入控件。

```xml
<TextBox Text="{Binding UserName, Mode=TwoWay}" />
```

### 3. OneTime（一次性绑定）

只绑定一次，适用于静态数据。

```xml
<TextBlock Text="{Binding Version, Mode=OneTime}" />
```

### 4. OneWayToSource（反向绑定）

从目标到源，适用于需要更新源但不需要显示的场景。

```xml
<Slider Value="{Binding Volume, Mode=OneWayToSource}" />
```

### 选择建议

| 场景 | 推荐模式 |
|------|----------|
| 显示数据 | OneWay |
| 输入控件 | TwoWay |
| 静态数据 | OneTime |
| 仅更新源 | OneWayToSource |

## 更新源触发器

### 1. PropertyChanged

属性变化时立即更新源。

```xml
<TextBox Text="{Binding Name, UpdateSourceTrigger=PropertyChanged}" />
```

### 2. LostFocus（默认）

失去焦点时更新源。

```xml
<TextBox Text="{Binding Name, UpdateSourceTrigger=LostFocus}" />
```

### 3. Explicit

手动调用 `UpdateSource()` 更新。

```xml
<TextBox x:Name="txtName" Text="{Binding Name, UpdateSourceTrigger=Explicit}" />
```

```csharp
BindingExpression be = txtName.GetBindingExpression(TextBox.TextProperty);
be.UpdateSource();
```

## 绑定路径

### 1. 简单路径

```xml
<TextBlock Text="{Binding FirstName}" />
```

### 2. 嵌套路径

```xml
<TextBlock Text="{Binding Customer.Name}" />
```

### 3. 索引器

```xml
<TextBlock Text="{Binding Items[0].Name}" />
```

### 4. 附加属性

```xml
<TextBlock Text="{Binding Path=(Canvas.Left), ElementName=myCanvas}" />
```

### 5. 不建议的路径

避免复杂的绑定路径，可能导致性能问题和难以维护。

## 值转换器

### 1. IValueConverter

实现自定义转换逻辑。

```csharp
public class BooleanToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        bool isVisible = (bool)value;
        return isVisible ? Visibility.Visible : Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        Visibility visibility = (Visibility)value;
        return visibility == Visibility.Visible;
    }
}
```

### 2. 在 XAML 中使用转换器

```xml
<Window.Resources>
    <local:BooleanToVisibilityConverter x:Key="BoolToVis" />
</Window.Resources>

<StackPanel Visibility="{Binding IsLoading, Converter={StaticResource BoolToVis}}">
    <!-- 加载内容 -->
</StackPanel>
```

### 3. 多值转换器

使用 `IMultiValueConverter` 处理多个值。

```csharp
public class FullNameConverter : IMultiValueConverter
{
    public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
    {
        string firstName = values[0] as string;
        string lastName = values[1] as string;
        return $"{firstName} {lastName}";
    }

    public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
```

```xml
<TextBlock>
    <TextBlock.Text>
        <MultiBinding Converter="{StaticResource FullNameConverter}">
            <Binding Path="FirstName" />
            <Binding Path="LastName" />
        </MultiBinding>
    </TextBlock.Text>
</TextBlock>
```

## 绑定验证

### 1. IDataErrorInfo

实现数据验证接口。

```csharp
public class User : IDataErrorInfo
{
    public string Name { get; set; }
    public string Email { get; set; }

    public string Error => null;

    public string this[string columnName]
    {
        get
        {
            if (columnName == nameof(Name) && string.IsNullOrEmpty(Name))
                return "姓名不能为空";
            if (columnName == nameof(Email) && !IsValidEmail(Email))
                return "邮箱格式不正确";
            return null;
        }
    }
}
```

### 2. 启用验证

```xml
<TextBox Text="{Binding Name, ValidatesOnDataErrors=True, UpdateSourceTrigger=PropertyChanged}">
    <Validation.ErrorTemplate>
        <ControlTemplate>
            <StackPanel>
                <AdornedElementPlaceholder />
                <TextBlock Foreground="Red" Text="{Binding [0].ErrorContent}" />
            </StackPanel>
        </ControlTemplate>
    </Validation.ErrorTemplate>
</TextBox>
```

### 3. INotifyDataErrorInfo（推荐）

更强大的验证接口，支持异步验证。

```csharp
public class User : INotifyDataErrorInfo
{
    private readonly Dictionary<string, List<string>> _errors = new Dictionary<string, List<string>>();

    public bool HasErrors => _errors.Any();

    public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

    public IEnumerable GetErrors(string propertyName)
    {
        return _errors.TryGetValue(propertyName, out var errors) ? errors : Enumerable.Empty<string>();
    }

    private void AddError(string propertyName, string error)
    {
        if (!_errors.ContainsKey(propertyName))
            _errors[propertyName] = new List<string>();
        
        if (!_errors[propertyName].Contains(error))
        {
            _errors[propertyName].Add(error);
            OnErrorsChanged(propertyName);
        }
    }

    private void OnErrorsChanged(string propertyName)
    {
        ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
    }
}
```

## 绑定性能

### 1. 使用虚拟化

对于大量数据，使用 `VirtualizingStackPanel`。

```xml
<ListBox ItemsSource="{Binding Items}" VirtualizingStackPanel.IsVirtualizing="True">
    <ListBox.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingStackPanel />
        </ItemsPanelTemplate>
    </ListBox.ItemsPanel>
</ListBox>
```

### 2. 避免不必要的绑定

- 静态文本直接写在 XAML 中
- 避免嵌套过深的绑定路径

### 3. 使用 Binding.IsAsync

对于耗时的数据获取，使用异步绑定。

```xml
<TextBlock Text="{Binding SlowData, IsAsync=True}" />
```

### 4. 批量更新

使用 `DeferRefresh` 批量更新绑定。

```csharp
using (CollectionViewSource.GetDefaultView(Items).DeferRefresh())
{
    // 批量操作
}
```

## 常见问题

### 问题 1: 绑定不生效

**原因**：
- DataContext 未设置
- 属性未实现 INotifyPropertyChanged
- 绑定路径错误

**解决方案**：
- 检查 DataContext
- 确保属性触发 PropertyChanged
- 验证绑定路径

### 问题 2: 双向绑定不更新源

**原因**：
- UpdateSourceTrigger 设置不当
- 属性没有 setter

**解决方案**：
- 使用适当的 UpdateSourceTrigger
- 确保属性有 public setter

### 问题 3: 验证错误不显示

**原因**：
- 未启用 ValidatesOnDataErrors
- ErrorTemplate 未定义

**解决方案**：
- 设置 ValidatesOnDataErrors=True
- 定义 Validation.ErrorTemplate

### 问题 4: 性能问题

**原因**：
- 大量数据未使用虚拟化
- 复杂的绑定路径
- 频繁的属性变更

**解决方案**：
- 使用虚拟化
- 简化绑定路径
- 合并属性变更通知

## 总结

数据绑定是 WPF 的强大特性，正确使用可以显著提高开发效率和代码质量。关键要点：

1. 选择合适的绑定模式
2. 正确设置更新源触发器
3. 使用转换器处理数据转换
4. 实现数据验证
5. 注意性能优化

遵循这些原则，您可以创建高效、可维护的 WPF 应用程序。