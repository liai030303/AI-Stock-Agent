import os

# 强行清空环境变量中的代理，防止幽灵代理干扰
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['ALL_PROXY'] = ''
os.environ['NO_PROXY'] = '*'

import akshare as ak

print("⏳ 正在尝试连接【新浪财经】获取数据...")
try:
    # 换用新浪的 A 股日线接口，注意代码前面要加 sh 或 sz
    df = ak.stock_zh_a_daily(symbol="sz002463", start_date="20230101", end_date="20240301")
    print("✅ 新浪接口测试成功！数据如下：")
    print(df.tail(3))
except Exception as e:
    print(f"❌ 新浪接口也失败了！报错信息：\n{e}")