# 微信每日推送 · 减脂增肌计划

每天 07:00（北京时间）自动把当天的训练和饮食计划推送到微信。

## 免费准备

二选一：

- PushPlus：到 [pushplus.plus](https://www.pushplus.plus) 登录，复制你的 token。
- Server酱：到 [sct.ftqq.com](https://sct.ftqq.com) 登录，复制 SendKey。

## 使用方法

1. 把整个 `fitness-push` 目录上传到一个 GitHub 仓库。
2. 在仓库 `Settings` -> `Secrets and variables` -> `Actions` 中新增 Secret：
   - 用 PushPlus：变量名 `PUSHPLUS_TOKEN`，值填你的 token。
   - 用 Server酱：变量名 `SERVERCHAN_SENDKEY`，值填你的 SendKey。
   - 如果改用 Server酱，再新增 Variable：变量名 `PUSH_PROVIDER`，值填 `serverchan`。
3. 进入仓库 `Actions` 页面，找到 `Daily Fitness Push`，点 `Run workflow` 测试一次。
4. 以后每天 07:00 会自动执行，也可以在 `Actions` 页面手动重新运行。

## 修改计划

训练、饮食、备注都放在 `plans/weekly.json`，直接改里面的文字即可。每天的 `diet` 可以增加或删除餐次。

## 调整推送时间

编辑 `.github/workflows/daily-push.yml` 里的 `cron`：

- `0 23 * * *` = 每天 07:00 北京时间
- `30 22 * * *` = 每天 06:30 北京时间
- `0 1 * * *` = 每天 09:00 北京时间

注意 GitHub 的定时任务是按 UTC 时间触发的，北京时间需要减 8 小时。
