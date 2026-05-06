# WPF 性能优化指南

## 目录

- [概述](#概述)
- [UI 虚拟化](#ui虚拟化)
- [数据绑定优化](#数据绑定优化)
- [渲染优化](#渲染优化)
- [内存管理](#内存管理)
- [异步编程](#异步编程)
- [样式优化](#样式优化)
- [性能分析工具](#性能分析工具)

## 概述

WPF 应用程序的性能问题通常表现为：
- UI 响应缓慢
- 内存占用过高
- 启动时间过长
- 卡顿和闪烁

本指南提供系统性的优化策略，帮助您创建高性能的 WPF 应用。

## UI 虚拟化

### 1. 虚拟化面板

对于大量数据，使用虚拟化面板可以显著提高性能。

```xml
<ListBox ItemsSource="{Binding Items}" VirtualizingStackPanel.IsVirtualizing="True">
    <ListBox.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingStackPanel />
        </ItemsPanelTemplate>
    </ListBox.ItemsPanel>
</ListBox>
```

### 2. VirtualizingWrapPanel

对于网格布局，使用 `VirtualizingWrapPanel`。

```xml
<ItemsControl ItemsSource="{Binding Items}">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingWrapPanel />
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
</ItemsControl>
```

### 3. 虚拟化配置

```xml
<ListBox 
    VirtualizingStackPanel.IsVirtualizing="True"
    VirtualizingStackPanel.VirtualizationMode="Recycling"
    VirtualizingStackPanel.CacheLength="20"
    >
```

- **VirtualizationMode**：`Recycling` 模式重用容器，性能更好
- **CacheLength**：预加载的项数

## 数据绑定优化

### 1. 减少绑定数量

- 避免在每个数据项上使用过多绑定
- 合并相关属性

### 2. 使用 ObservableCollection

`ObservableCollection` 提供高效的集合变更通知。

```csharp
private ObservableCollection<Item> _items = new ObservableCollection<Item>();
public ObservableCollection<Item> Items => _items;
```

### 3. 批量更新

使用 `AddRange` 扩展方法批量添加项。

```csharp
public static void AddRange<T>(this ObservableCollection<T> collection, IEnumerable<T> items)
{
    foreach (var item in items)
    {
        collection.Add(item);
    }
}
```

### 4. 关闭通知进行批量操作

```csharp
public class RangeObservableCollection<T> : ObservableCollection<T>
{
    private bool _suppressNotification = false;

    protected override void OnCollectionChanged(NotifyCollectionChangedEventArgs e)
    {
        if (!_suppressNotification)
            base.OnCollectionChanged(e);
    }

    public void AddRange(IEnumerable<T> items)
    {
        _suppressNotification = true;
        try
        {
            foreach (var item in items)
            {
                Items.Add(item);
            }
        }
        finally
        {
            _suppressNotification = false;
            OnCollectionChanged(new NotifyCollectionChangedEventArgs(NotifyCollectionChangedAction.Reset));
        }
    }
}
```

## 渲染优化

### 1. 使用 GPU 加速

WPF 默认使用软件渲染，启用硬件加速。

```xml
<Window RenderOptions.ProcessRenderMode="Default">
```

### 2. 减少视觉效果

- 避免过度使用阴影和模糊效果
- 减少透明度使用

```xml
<Border Effect="{x:Null}">
```

### 3. 缓存可视化对象

对于复杂的视觉元素，使用缓存。

```xml
<Grid RenderOptions.CachingHint="Cache">
```

### 4. 使用 DrawingImage

对于静态图像，使用 `DrawingImage` 替代 `BitmapImage`。

```xml
<Image Source="{StaticResource MyDrawingImage}" />
```

## 内存管理

### 1. 及时释放资源

- 取消事件订阅
- 释放一次性对象

```csharp
public void Dispose()
{
    _eventAggregator.UnsubscribeAll();
    _timer?.Dispose();
}
```

### 2. 使用 WeakEventManager

避免强引用导致的内存泄漏。

```csharp
WeakEventManager<SomeClass, EventArgs>.AddHandler(
    source, 
    nameof(source.SomeEvent), 
    OnSomeEvent);
```

### 3. 限制数据量

- 使用分页加载
- 按需加载数据

```csharp
public async Task LoadPage(int pageNumber, int pageSize)
{
    var newItems = await _service.GetItems(pageNumber, pageSize);
    Items.AddRange(newItems);
}
```

## 异步编程

### 1. 后台线程执行

将耗时操作移到后台线程。

```csharp
private async void LoadData()
{
    IsLoading = true;
    try
    {
        Data = await Task.Run(() => _service.GetData());
    }
    finally
    {
        IsLoading = false;
    }
}
```

### 2. 使用 IProgress 报告进度

```csharp
private async void LoadData()
{
    var progress = new Progress<int>(percent => Progress = percent);
    await Task.Run(() => _service.LoadData(progress));
}
```

### 3. 避免阻塞 UI 线程

- 避免在 UI 线程执行数据库操作
- 使用异步 API

## 样式优化

### 1. 资源字典组织

将样式集中管理，避免重复定义。

```xml
<ResourceDictionary.MergedDictionaries>
    <ResourceDictionary Source="Styles/Common.xaml" />
    <ResourceDictionary Source="Styles/Buttons.xaml" />
</ResourceDictionary.MergedDictionaries>
```

### 2. 使用 StaticResource

对于静态资源，使用 `StaticResource` 提高性能。

```xml
<Button Style="{StaticResource PrimaryButtonStyle}" />
```

### 3. 避免复杂触发器

减少触发器的复杂度，使用代码逻辑代替。

## 性能分析工具

### 1. Snoop

WPF UI 调试工具，可以查看可视化树和数据绑定。

### 2. Visual Studio Performance Profiler

- CPU 使用分析
- 内存分配分析
- UI 响应时间分析

### 3. .NET Memory Profiler

专业的内存分析工具，检测内存泄漏。

### 4. Perforator

WPF 性能分析工具，分析渲染性能。

## 性能检查清单

- [ ] 使用 UI 虚拟化处理大量数据
- [ ] 使用 ObservableCollection 管理集合
- [ ] 批量更新集合时关闭通知
- [ ] 使用异步操作加载数据
- [ ] 避免在 UI 线程执行耗时操作
- [ ] 使用 DrawingImage 替代 BitmapImage
- [ ] 缓存复杂的视觉元素
- [ ] 及时取消事件订阅
- [ ] 使用 WeakEventManager 避免强引用
- [ ] 启用硬件加速

## 常见性能问题

### 问题 1: 列表滚动卡顿

**原因**：未使用虚拟化

**解决方案**：使用 `VirtualizingStackPanel`

### 问题 2: 内存持续增长

**原因**：事件订阅未取消

**解决方案**：使用 `WeakEventManager` 或及时取消订阅

### 问题 3: 启动时间过长

**原因**：同步加载大量数据

**解决方案**：使用异步加载和延迟加载

### 问题 4: UI 响应缓慢

**原因**：在 UI 线程执行耗时操作

**解决方案**：移到后台线程

## 总结

WPF 性能优化需要系统性的方法：

1. **虚拟化**：处理大量数据的关键
2. **异步**：避免阻塞 UI 线程
3. **内存管理**：防止内存泄漏
4. **渲染优化**：使用 GPU 加速和缓存
5. **测量**：使用性能分析工具定位问题

通过遵循这些原则，您可以创建流畅、高效的 WPF 应用程序。