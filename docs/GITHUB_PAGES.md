# GitHub Pages 配置指南

## 📖 概述

本项目使用 GitHub Pages 来托管生成的节点订阅文件，让用户可以通过公开链接订阅节点。

## 🚀 快速配置

### 1. 确保仓库是公开的

GitHub Pages 免费版仅支持公开仓库。

**操作步骤：**
1. 访问：https://github.com/miaolitao/V2Ray/settings
2. 滚动到最底部的 "Danger Zone"
3. 点击 "Change visibility" → "Make public"
4. 输入 `miaolitao/V2Ray` 确认

### 2. 启用 GitHub Pages

**操作步骤：**

1. **访问仓库设置**  
   https://github.com/miaolitao/V2Ray/settings/pages

2. **配置 Source（源）**
   - **Branch（分支）**：选择 `gh-pages`
   - **Folder（目录）**：选择 `/ (root)`
   - 点击 **Save（保存）**

3. **等待部署完成**
   - 通常需要 1-2 分钟
   - 成功后会显示：`Your site is live at https://miaolitao.github.io/V2Ray/`

### 3. 验证部署

访问以下链接验证部署是否成功：

```
🌐 主页：
https://miaolitao.github.io/V2Ray/

📱 订阅链接：
https://miaolitao.github.io/V2Ray/nodes.txt
https://miaolitao.github.io/V2Ray/clash.yaml
https://miaolitao.github.io/V2Ray/surge.conf
https://miaolitao.github.io/V2Ray/quantumult.conf
```

## 📋 工作流程

### 自动部署流程

```
[GitHub Actions 运行]
        ↓
[收集并测速节点]
        ↓
[生成各种格式文件]
        ↓
[创建 index.html]
        ↓
[部署到 gh-pages 分支]
        ↓
[GitHub Pages 自动发布]
        ↓
[订阅链接更新]
```

### 触发方式

1. **定时触发**：每 6 小时自动运行
2. **手动触发**：在 Actions 页面手动触发
3. **代码推送**：（如果需要可以添加）

## 🎨 自定义订阅页面

订阅页面的 HTML 在 GitHub Actions 工作流中生成（`.github/workflows/update-nodes.yml`）。

### 修改页面内容

编辑工作流中的 `index.html` 部分：

```yaml
- name: 准备 GitHub Pages 内容
  run: |
    cat > gh-pages/index.html << 'EOF'
    <!DOCTYPE html>
    ...你的自定义 HTML...
    EOF
```

### 自定义样式

修改 `<style>` 标签内的 CSS：

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* 修改为你喜欢的颜色 */
}
```

## 🔧 高级配置

### 使用自定义域名

1. **购买域名**（如：v2ray.example.com）

2. **添加 DNS 记录**
   ```
   类型: CNAME
   名称: v2ray
   值: miaolitao.github.io
   ```

3. **在仓库中配置**
   - 访问：https://github.com/miaolitao/V2Ray/settings/pages
   - 在 "Custom domain" 输入：`v2ray.example.com`
   - 点击 Save
   - 勾选 "Enforce HTTPS"

4. **创建 CNAME 文件**
   
   在工作流中添加：
   ```yaml
   - name: 准备 GitHub Pages 内容
     run: |
       echo "v2ray.example.com" > gh-pages/CNAME
   ```

### CDN 加速

如果访问速度慢，可以使用 CDN：

**推荐方案：Cloudflare**

1. 将域名托管到 Cloudflare
2. 启用 Cloudflare CDN（橙色云朵）
3. 配置缓存规则：
   ```
   - *.yaml: 缓存 1 小时
   - *.txt: 缓存 1 小时
   - *.conf: 缓存 1 小时
   ```

## 📊 监控和分析

### 查看访问统计

**方法 1：使用 Google Analytics**

在 `index.html` 中添加：

```html
<head>
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>
</head>
```

**方法 2：使用 Cloudflare Analytics**

如果使用了 Cloudflare，可以在其后台查看详细的访问分析。

## ⚠️ 注意事项

### 配额限制

GitHub Pages 免费版限制：
- 存储空间：1GB
- 带宽：100GB/月
- 构建：10次/小时

**你的项目预估：**
- 存储使用：< 10MB ✅
- 带宽使用：~30GB/月 ✅
- 完全够用！

### 安全建议

1. **不要在订阅文件中包含敏感信息**
2. **定期检查节点质量**
3. **添加免责声明**

### 访问速度

GitHub Pages 在中国访问可能较慢，建议：

1. 使用 CDN（如 Cloudflare）
2. 使用镜像站点
3. 提供多个订阅源

## 🐛 常见问题

### Q1: 页面显示 404

**解决方案：**
1. 确认 gh-pages 分支已创建
2. 检查 Settings → Pages 配置是否正确
3. 等待 2-3 分钟让 Pages 完成部署

### Q2: 文件无法访问

**解决方案：**
1. 检查文件是否在 gh-pages 分支根目录
2. 确认文件名拼写正确（区分大小写）
3. 清除浏览器缓存

### Q3: Actions 部署失败

**解决方案：**
1. 检查 Actions 日志
2. 确认 `peaceiris/actions-gh-pages@v3` 有权限
3. 检查工作流 YAML 语法

### Q4: 订阅链接不更新

**解决方案：**
1. 确认 Actions 运行成功
2. 清除客户端缓存
3. 检查 gh-pages 分支的提交时间

## 📞 获取帮助

- **GitHub Issues**：https://github.com/miaolitao/V2Ray/issues
- **GitHub Discussions**：https://github.com/miaolitao/V2Ray/discussions
- **参考文档**：https://docs.github.com/pages

## 🎉 完成！

配置完成后，你的订阅链接将：
- ✅ 每 6 小时自动更新
- ✅ 提供美观的订阅页面
- ✅ 支持多种客户端格式
- ✅ 完全免费托管

享受你的免费节点订阅服务吧！🚀

