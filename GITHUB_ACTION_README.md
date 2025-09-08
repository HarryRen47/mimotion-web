# MiMotion GitHub Action 使用指南

本项目新增了 GitHub Action 自动化功能，可以在 GitHub 的服务器上定时自动同步小米运动步数，无需本地运行。

## 🌟 特性

- **自动定时同步**：每小时自动执行一次步数同步
- **智能时间控制**：根据时间自动计算合理的步数，模拟真实运动轨迹
- **多账号支持**：支持同时管理多个小米运动账号
- **安全配置**：使用 GitHub Secrets 安全存储账号信息
- **失败重试**：同步失败时会记录详细日志
- **手动触发**：支持手动触发同步操作

## 🚀 快速开始

### 步骤 1: Fork 或 Clone 项目

```bash
# Fork 项目到你的 GitHub 账号，或者 clone 到本地后推送到你的仓库
git clone https://github.com/HarryRen47/mimotion-web.git
cd mimotion-web
```

### 步骤 2: 配置 GitHub Secrets

在你的 GitHub 仓库中，进入 `Settings` -> `Secrets and variables` -> `Actions`，添加以下 secrets：

#### 方式一：单个账号配置

| Secret 名称 | 必填 | 说明 | 示例 |
|------------|------|------|------|
| `MI_USER` | ✅ | 小米运动账号 | `your_phone_or_email` |
| `MI_PASSWORD` | ✅ | 小米运动密码 | `your_password` |
| `MIN_STEP` | ❌ | 最小步数 | `18000` (默认) |
| `MAX_STEP` | ❌ | 最大步数 | `25000` (默认) |
| `SYNC_START_HOUR` | ❌ | 同步开始时间 | `8` (默认，8点) |
| `SYNC_END_HOUR` | ❌ | 同步结束时间 | `22` (默认，22点) |

#### 方式二：多账号配置 (推荐)

如果你有多个小米运动账号，可以使用 JSON 格式配置：

| Secret 名称 | 值 |
|------------|------|
| `MI_ACCOUNTS_JSON` | JSON 格式的账号列表 |

`MI_ACCOUNTS_JSON` 的格式示例：

```json
[
  {
    "mi_user": "138xxxx8888",
    "mi_password": "password1",
    "min_step": 18000,
    "max_step": 25000,
    "sync_start_hour": 8,
    "sync_end_hour": 22
  },
  {
    "mi_user": "your_email@example.com",
    "mi_password": "password2", 
    "min_step": 15000,
    "max_step": 20000,
    "sync_start_hour": 9,
    "sync_end_hour": 21
  }
]
```

### 步骤 3: 启用 GitHub Actions

1. 在你的仓库中，点击 `Actions` 标签页
2. 如果提示启用 workflows，点击 `I understand my workflows, go ahead and enable them`
3. 找到 `MiMotion Step Sync` workflow
4. 如果需要，点击 `Enable workflow`

### 步骤 4: 测试运行

你可以手动触发一次同步来测试配置：

1. 进入 `Actions` -> `MiMotion Step Sync`
2. 点击 `Run workflow`
3. 点击绿色的 `Run workflow` 按钮
4. 等待执行完成，检查日志输出

## ⏰ 定时规则

默认配置为每小时的第 5 分钟执行同步：

```yaml
schedule:
  - cron: '5 * * * *'  # 每小时第5分钟执行
```

你可以根据需要修改 `.github/workflows/mimotion-sync.yml` 文件中的 cron 表达式。

### 常用 Cron 表达式

| 表达式 | 说明 |
|--------|------|
| `'5 * * * *'` | 每小时第5分钟 |
| `'0 */2 * * *'` | 每2小时执行一次 |
| `'0 8,12,18,22 * * *'` | 每天8、12、18、22点执行 |
| `'30 6-22 * * *'` | 每天6点到22点，每小时30分执行 |

## 🔧 高级配置

### 自定义步数算法

脚本会根据当前时间智能计算步数：

- **时间进度率**：以22点为满值，当前小时/22
- **当前步数** = 时间进度率 × (最小步数 到 最大步数的随机值)

例如：如果现在是下午2点(14时)，设置最小步数18000，最大步数25000：
- 时间进度率 = 14/22 ≈ 0.64
- 当前步数范围：11520 - 16000 之间的随机值

### 修改工作流

如果需要自定义 GitHub Action 的行为，可以编辑 `.github/workflows/mimotion-sync.yml` 文件：

```yaml
name: MiMotion Step Sync

on:
  schedule:
    - cron: '5 * * * *'  # 修改定时规则
  workflow_dispatch:     # 保留手动触发

jobs:
  sync-steps:
    runs-on: ubuntu-latest
    steps:
      # ... 其他步骤
      - name: Run step sync
        env:
          # 在这里修改环境变量配置
        run: python action_sync.py
```

## 📊 监控和日志

### 查看执行状态

1. 进入仓库的 `Actions` 页面
2. 点击 `MiMotion Step Sync` workflow
3. 查看最近的执行记录

### 日志说明

- ✅ **成功日志**：显示 "账号 xxx 同步成功"
- ❌ **失败日志**：显示 "账号 xxx 同步失败" 和具体错误信息
- ℹ️ **跳过日志**：显示 "不在同步时间范围内"

### 失败处理

如果同步失败，GitHub Action 会：

1. 记录详细的错误日志
2. 以非零状态码退出，标记此次执行为失败
3. GitHub 会发送邮件通知（如果启用了通知）

## 🔐 安全注意事项

1. **永远不要** 在代码中硬编码账号密码
2. **务必使用** GitHub Secrets 存储敏感信息
3. **定期检查** Actions 执行日志，确保没有意外泄露信息
4. **谨慎分享** 包含你配置的仓库

## ❓ 常见问题

### Q: GitHub Action 不执行怎么办？

A: 检查以下几点：
- 确保仓库启用了 Actions
- 确保工作流文件路径正确：`.github/workflows/mimotion-sync.yml`
- 检查 cron 表达式是否正确
- 确保仓库不是 private 且有足够的 Actions 配额

### Q: 同步失败怎么办？

A: 检查以下几点：
- 验证 Secrets 中的账号密码是否正确
- 检查小米运动账号是否正常（可以手机登录测试）
- 查看详细的错误日志确定具体问题

### Q: 可以修改同步时间吗？

A: 可以通过以下方式修改：
- 调整 `SYNC_START_HOUR` 和 `SYNC_END_HOUR` Secrets
- 修改 workflow 文件中的 cron 表达式

### Q: 支持邮箱账号吗？

A: 支持，`MI_USER` 可以是手机号或邮箱地址。

### Q: 为什么步数不是固定值？

A: 为了模拟真实的运动轨迹，脚本会：
- 根据时间进度计算合理的步数范围
- 在范围内随机选择具体数值
- 避免每次都是相同的步数，减少被检测的风险

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目基于 MIT 许可证开源。