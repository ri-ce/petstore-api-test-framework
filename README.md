# Software Testing Automation Portfolio

软件测试自动化作品集导航仓库。两个测试项目已分别存放在独立 GitHub 仓库中，
当前仓库只负责作品集网站和项目导航，不再包含测试代码。

## 项目入口

| 项目 | 测试方向 | 用例数 | 源码 | 在线报告 |
| --- | --- | ---: | --- | --- |
| Swagger Petstore API Automation | 接口自动化测试 | 22 | [GitHub](https://github.com/ri-ce/petstore-api-automation) | [测试报告](https://ri-ce.github.io/petstore-api-automation/test-report.html) |
| SauceDemo UI Automation | 网页自动化测试 | 12 | [GitHub](https://github.com/ri-ce/saucedemo-ui-automation) | [测试报告](https://ri-ce.github.io/saucedemo-ui-automation/test-report.html) |

两个项目合计 **34 条自动化用例，最近一次均全部通过**。

## 作品集网站

- 总入口：`https://ri-ce.github.io/qa-automation-portfolio/`
- 接口项目主页：`https://ri-ce.github.io/petstore-api-automation/`
- 网页项目主页：`https://ri-ce.github.io/saucedemo-ui-automation/`

## 项目一：接口自动化

使用 Python、Pytest、Requests 和 OpenAPI 测试 Swagger 官方公开 Petstore API。

覆盖内容：

- OpenAPI 契约和接口路径。
- 宠物创建、查询、修改和删除。
- 宠物状态筛选。
- 库存和订单生命周期。
- 404 和 400 异常响应。
- 唯一 ID、自动清理和网络重试。

仓库：`https://github.com/ri-ce/petstore-api-automation`

## 项目二：网页自动化

使用 Python、Pytest 和 Playwright 测试 Sauce Labs 公开 SauceDemo 演示商城。

覆盖内容：

- 登录、错误密码和锁定账号。
- 商品列表与排序。
- 购物车增加和移除。
- 结算表单校验。
- 完整下单流程。
- 页面对象、显式等待和失败截图。

仓库：`https://github.com/ri-ce/saucedemo-ui-automation`

## 仓库定位

本仓库是展示与导航页面。每个项目的测试代码、运行脚本、自动测试配置和测试报告
均位于各自独立仓库，可以单独下载、运行和查看提交历史。
