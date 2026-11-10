# Shadowrocket 规则与策略组分离包

本项目把配置分成两个层次：

- `config.template`：你自己维护的 General、Proxy Group、Host、URL Rewrite、MITM。
- `scripts/build.py`：只从官方 `lazy_group.conf` 提取 `[Rule]` 区域。
- `dist/cellular.conf`：蜂窝配置，地区 url-test 间隔 86400 秒。
- `dist/wifi.conf`：Wi-Fi 配置，地区 url-test 间隔 600 秒。

## 为什么同步 `lazy_group.conf`，不是 `lazy.conf`？

`lazy_group.conf` 的规则目标会指向 `AI`、`YouTube`、`Netflix`、`游戏平台` 等策略组。`lazy.conf` 则把这些流量归到通用 `PROXY`，无法充分利用自定义应用策略组。

构建脚本只提取 `[Rule]`，不会把官方 `[Proxy Group]`、`[General]` 等部分覆盖到你的模板中。

## 部署到自己的 GitHub 仓库

1. 新建一个 **Private 或 Public** GitHub 仓库（建议 Private 也可以；Raw 文件是否可供 Shadowrocket 读取，建议先用浏览器测试；若访问受限则改为 Public）。
2. 把本压缩包中的全部文件上传到仓库根目录，保留 `.github/workflows/update.yml` 路径。
3. 在仓库 Settings → Actions → General → Workflow permissions 中，允许 Actions 写入仓库（Read and write permissions）。
4. 进入 Actions，选择 `Sync Shadowrocket rules`，点击 `Run workflow`，先手动运行一次。
5. 确认仓库出现 `dist/cellular.conf` 和 `dist/wifi.conf`。
6. 后续每天北京时间约 08:15 自动检查官方规则；规则有变化才提交更新。

## Shadowrocket 导入地址

把 `<用户名>` 和 `<仓库名>` 换成自己的 GitHub 信息：

蜂窝：
`https://raw.githubusercontent.com/<用户名>/<仓库名>/main/dist/cellular.conf`

Wi-Fi：
`https://raw.githubusercontent.com/<用户名>/<仓库名>/main/dist/wifi.conf`

如果你的默认分支不是 `main`，把 URL 中的 `main` 换成实际分支名。

在 Shadowrocket → 配置 → 右上角 `+`，分别添加以上两个远程配置。然后在场景中设置：
- 蜂窝数据 → cellular.conf
- Wi-Fi → wifi.conf

注意：Shadowrocket 的场景必须确实能识别网络条件并切换配置；如果你的版本或 iOS 权限无法按 Wi-Fi/蜂窝自动切换，两个配置仍可手动切换，但同一份配置不会自动改变 interval。

## 重要注意

- 这套脚本使用官方 `lazy_group.conf` 的 `[Rule]`，因为规则目标需要和自定义策略组名称匹配。
- 规则源的 `[Rule]` 中若新增一个目标策略组，你必须在 `config.template` 中补上同名策略组，否则该规则无法按预期分流。
- 如果官方改变规则段结构，构建会失败，不会用空规则覆盖现有配置。
- 节点订阅仍然在 Shadowrocket 首页独立维护；配置中的 `[Proxy]` 不包含你的节点。
- `86400` 是测速检查间隔，不等于绝对保证每天恰好只发生一次网络请求；应用启动、手动测速、节点状态等因素也可能触发测试。
- 先在 Shadowrocket 中导入测试，检查策略组是否都出现、规则日志命中是否正确，再把它设为日常场景配置。
