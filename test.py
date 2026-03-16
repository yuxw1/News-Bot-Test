import os
import feedparser
from openai import OpenAI
from datetime import datetime

# ================= 0. 准备文件名 =================
# 获取今天的日期，用来做文件名，比如: 2026-03-12
today_str = datetime.now().strftime("%Y-%m-%d")
filename = f"AI_News_{today_str}.md"

# ================= 1. 抓取真实新闻 =================
print("📡 正在去全网抓取最新的 AI 新闻...")
rss_url = "https://hnrss.org/newest?q=AI" 
feed = feedparser.parse(rss_url)

news_text = ""
# 稍微加量：提取前 5 条最新新闻喂给 AI，让日报更丰富
for i, entry in enumerate(feed.entries[:5]):
    news_text += f"第{i+1}条新闻标题: {entry.title}\n链接: {entry.link}\n\n"

print("✅ 抓取成功！准备交给 AI 处理...")

# ================= 2. 初始化 AI 大脑 =================
# ⚠️ 安全升级：从环境变量读取密钥，千万不要把明文密钥写在代码里！
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("找不到 API Key，请检查环境变量或 GitHub Secrets 配置！")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key, 
)

# ================= 3. 让 AI 编写日报 =================
prompt = f"""
你是一个专业的 AI 领域新闻编辑。请帮我把下面刚抓取到的英文新闻整理成一份优美的中文日报。

要求：
1. 必须用中文输出。
2. 每条新闻格式：### [一句话精炼标题](原文链接)\n- 核心看点（用大白话解释，不要太啰嗦）。
3. 语气要像专业的科技媒体。

以下是今日抓取到的生肉数据：
{news_text}
"""

print("🧠 正在呼叫 AI 进行翻译和总结，请稍候...")
response = client.chat.completions.create(
    model="arcee-ai/trinity-large-preview:free", # 保留了你选定的免费模型
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)
report_content = response.choices[0].message.content

# ================= 4. 保存为 Markdown 文件 =================
print(f"\n📝 正在生成文件: {filename}")
# 将 AI 的输出写入到 markdown 文件中
with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# 🚀 AI 每日情报站 ({today_str})\n\n")
    f.write(report_content)

print("="*40)
print("✅ 你的专属 AI 自动化简报生成并保存完毕！")
print("="*40)