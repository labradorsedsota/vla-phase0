# 代码块高亮测试

以下是一段 Python 代码：

```python
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# 调用示例
result = fibonacci(10)
print(f"第10个斐波那契数是: {result}")
```

以下是行内代码：使用 `pip install markdown` 安装依赖。
