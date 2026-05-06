# WPF 样式和资源管理指南

## 目录

- [概述](#概述)
- [资源字典组织](#资源字典组织)
- [样式定义](#样式定义)
- [数据模板](#数据模板)
- [主题切换](#主题切换)
- [资源查找机制](#资源查找机制)
- [性能优化](#性能优化)

## 概述

WPF 的样式和资源系统是其强大的特性之一，允许开发者集中管理 UI 外观，实现主题切换和样式复用。

## 资源字典组织

### 1. 推荐结构

```
Resources/
├── Themes/
│   ├── Light.xaml
│   ├── Dark.xaml
│   └── HighContrast.xaml
├── Controls/
│   ├── Buttons.xaml
│   ├── TextBoxes.xaml
│   └── DataGrid.xaml
├── Converters.xaml
├── Templates.xaml
└── Common.xaml
```

### 2. 合并资源字典

在 `App.xaml` 中合并所有资源字典：

```xml
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceDictionary Source="Resources/Common.xaml" />
            <ResourceDictionary Source="Resources/Converters.xaml" />
            <ResourceDictionary Source="Resources/Controls/Buttons.xaml" />
            <ResourceDictionary Source="Resources/Controls/TextBoxes.xaml" />
            <ResourceDictionary Source="Resources/Themes/Light.xaml" />
        </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
</Application.Resources>
```

## 样式定义

### 1. 基础样式

```xml
<Style x:Key="PrimaryButtonStyle" TargetType="Button">
    <Setter Property="Background" Value="#0078D4" />
    <Setter Property="Foreground" Value="White" />
    <Setter Property="Padding" Value="12,8" />
    <Setter Property="BorderThickness" Value="0" />
    <Setter Property="CornerRadius" Value="4" />
</Style>
```

### 2. 样式继承

使用 `BasedOn` 继承现有样式：

```xml
<Style x:Key="PrimaryButtonLargeStyle" TargetType="Button" BasedOn="{StaticResource PrimaryButtonStyle}">
    <Setter Property="FontSize" Value="16" />
    <Setter Property="Padding" Value="20,12" />
</Style>
```

### 3. 触发器样式

```xml
<Style x:Key="PrimaryButtonStyle" TargetType="Button">
    <Setter Property="Background" Value="#0078D4" />
    <Style.Triggers>
        <Trigger Property="IsMouseOver" Value="True">
            <Setter Property="Background" Value="#106EBE" />
        </Trigger>
        <Trigger Property="IsPressed" Value="True">
            <Setter Property="Background" Value="#005A9E" />
        </Trigger>
        <Trigger Property="IsEnabled" Value="False">
            <Setter Property="Background" Value="#A8A8A8" />
        </Trigger>
    </Style.Triggers>
</Style>
```

### 4. 隐式样式

不设置 `x:Key`，自动应用到所有同类型控件：

```xml
<Style TargetType="Button">
    <Setter Property="FontFamily" Value="Segoe UI" />
    <Setter Property="FontSize" Value="14" />
</Style>
```

## 数据模板

### 1. 简单数据模板

```xml
<DataTemplate x:Key="UserTemplate" DataType="{x:Type models:User}">
    <StackPanel Orientation="Horizontal" Spacing="10">
        <Image Source="{Binding Avatar}" Width="40" Height="40" />
        <StackPanel>
            <TextBlock Text="{Binding Name}" FontWeight="Bold" />
            <TextBlock Text="{Binding Email}" Foreground="Gray" />
        </StackPanel>
    </StackPanel>
</DataTemplate>
```

### 2. 数据模板选择器

```csharp
public class UserTemplateSelector : DataTemplateSelector
{
    public DataTemplate AdminTemplate { get; set; }
    public DataTemplate NormalUserTemplate { get; set; }

    public override DataTemplate SelectTemplate(object item, DependencyObject container)
    {
        if (item is User user)
        {
            return user.IsAdmin ? AdminTemplate : NormalUserTemplate;
        }
        return base.SelectTemplate(item, container);
    }
}
```

```xml
<local:UserTemplateSelector x:Key="UserTemplateSelector"
    AdminTemplate="{StaticResource AdminTemplate}"
    NormalUserTemplate="{StaticResource NormalUserTemplate}" />

<ListBox ItemsSource="{Binding Users}" ItemTemplateSelector="{StaticResource UserTemplateSelector}" />
```

## 主题切换

### 1. 定义主题资源

**Light.xaml:**
```xml
<ResourceDictionary>
    <SolidColorBrush x:Key="PrimaryColor" Color="#0078D4" />
    <SolidColorBrush x:Key="BackgroundColor" Color="#FFFFFF" />
    <SolidColorBrush x:Key="TextColor" Color="#333333" />
</ResourceDictionary>
```

**Dark.xaml:**
```xml
<ResourceDictionary>
    <SolidColorBrush x:Key="PrimaryColor" Color="#2563EB" />
    <SolidColorBrush x:Key="BackgroundColor" Color="#1E1E1E" />
    <SolidColorBrush x:Key="TextColor" Color="#FFFFFF" />
</ResourceDictionary>
```

### 2. 实现主题切换

```csharp
public void ChangeTheme(string themeName)
{
    var newTheme = new ResourceDictionary
    {
        Source = new Uri($"Resources/Themes/{themeName}.xaml", UriKind.Relative)
    };
    
    var appResources = Application.Current.Resources;
    
    foreach (var key in newTheme.Keys)
    {
        if (appResources.Contains(key))
        {
            appResources[key] = newTheme[key];
        }
        else
        {
            appResources.Add(key, newTheme[key]);
        }
    }
}
```

## 资源查找机制

### 1. 查找顺序

1. 元素本身的 Resources
2. 父元素的 Resources（向上遍历）
3. Window/UserControl 的 Resources
4. Application 的 Resources
5. 系统主题资源

### 2. StaticResource vs DynamicResource

| 特性 | StaticResource | DynamicResource |
|------|----------------|-----------------|
| 解析时机 | 加载时 | 使用时 |
| 性能 | 更快 | 稍慢 |
| 动态更新 | 不支持 | 支持 |
| 适用场景 | 静态资源 | 主题切换 |

```xml
<!-- 静态资源 -->
<Button Style="{StaticResource PrimaryButtonStyle}" />

<!-- 动态资源 -->
<Button Background="{DynamicResource PrimaryColor}" />
```

## 性能优化

### 1. 资源字典拆分

将资源字典按功能拆分，按需加载。

### 2. 使用 SharedSizeGroup

对于需要对齐的控件，使用 `SharedSizeGroup`。

```xml
<Grid Grid.IsSharedSizeScope="True">
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="Auto" SharedSizeGroup="LabelColumn" />
        <ColumnDefinition Width="*" />
    </Grid.ColumnDefinitions>
</Grid>
```

### 3. 避免过度样式化

- 减少不必要的样式定义
- 重用现有样式

## 最佳实践

### 1. 集中管理

将所有样式和资源集中在资源字典中，便于维护。

### 2. 使用命名规范

```
{ControlType}{StyleName}Style
例如：ButtonPrimaryStyle, TextBoxErrorStyle
```

### 3. 保持一致性

整个应用使用统一的设计语言和样式规范。

### 4. 可访问性

确保样式满足可访问性要求：
- 足够的对比度
- 清晰的焦点指示
- 支持高对比度模式

## 常见问题

### 问题 1: 资源找不到

**原因**：资源字典未正确合并

**解决方案**：检查 `MergedDictionaries` 路径

### 问题 2: 样式不生效

**原因**：TargetType 不匹配或样式被覆盖

**解决方案**：检查 TargetType 和样式优先级

### 问题 3: 主题切换不生效

**原因**：使用了 StaticResource 而不是 DynamicResource

**解决方案**：改为使用 DynamicResource

## 总结

良好的样式和资源管理可以：
- 提高代码可维护性
- 实现主题切换
- 保持 UI 一致性
- 提高开发效率

遵循这些原则，您可以创建专业、可维护的 WPF 应用程序。