# 眼镜店进销存系统

## 功能

- 产品管理:
  - 添加新产品，包括名称、类别、品牌、规格和条形码等详细信息。 
  - 查看、编辑和删除现有产品。 
  - 跟踪产品数量并更新库存水平。 
- 销售管理(暂未实现):
  - 记录销售交易，包括销售人员、价格、数量和销售日期。 
  - 查看和跟踪销售历史。

# 入门指南
## 前提条件
+ Python (版本 3.6 或更高)
+ Flask (Python 网络应用框架)
+ SQLAlchemy (Python SQL 工具包和对象关系映射器)
+ SQLite(数据库)

## 安装
+ 将仓库克隆到本地计算机：
  + bash
  + Copy code
  + git clone <repository_url>
+ 使用 pip 安装所需的 Python 包： 
  + Copy code 
  + pip install -r requirements.txt
+ 数据库设置 
  + 为应用程序创建新的 SQLite 数据库。 
  + 在 config.py 文件中更新数据库连接设置 
  + 初始化数据库并创建必要的表格：
+ 运行应用程序： 
  + python app.py 
  + 现在，您可以在网络浏览器中访问 http://localhost:5000 来访问应用程序。
# 贡献
如果您想为该项目做出贡献或报告任何问题，请创建新的拉取请求或在 GitHub 上开启一个问题。

# 许可证
进销存系统是根据 MIT 许可证的开源软件。请参阅 LICENSE 文件获取更多详细信息。

# 联系方式
如果您有任何问题或需要进一步帮助，请联系geebeeboper@gmail.com

