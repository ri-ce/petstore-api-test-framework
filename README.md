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

## 作品集综合简历描述

```text
完成接口与网页自动化测试作品集，分别维护 Swagger Petstore 接口测试项目
和 SauceDemo Playwright 网页测试项目，合计设计 34 条自动化用例，覆盖接口契约、
CRUD、异常响应、网页登录、商品排序、购物车及完整结算流程；使用数据隔离、
自动清理、页面对象和显式等待提升测试可靠性，并通过 GitHub Actions 实现持续集成。
```

## 仓库定位

本仓库是展示与导航页面。每个项目的测试代码、运行脚本、自动测试配置和测试报告
均位于各自独立仓库，可以单独下载、运行和查看提交历史。
