import markdown
import pdfkit
import os
import re
import feedparser
from openai import OpenAI
from datetime import datetime

# ================= 0. 准备文件名与日期 =================
today_str = datetime.now().strftime("%Y-%m-%d")
filename = f"AI_News_{today_str}.md"

# ================= 1. 全网搜集真实新闻 =================
print("📡 正在通过搜索引擎聚合全网 AI 资讯...")

# 利用 Google News 的“全网搜索”接口，限定抓取过去 24 小时 (when:1d) 的全网报道
search_urls = [
    # 1. 搜索全网中文 AI 新闻
    "https://news.google.com/rss/search?q=人工智能+大模型+when:1d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    # 2. 搜索全网英文 AI 新闻 (涵盖全球最前沿动态)
    "https://news.google.com/rss/search?q=Artificial+Intelligence+LLM+when:1d&hl=en-US&gl=US&ceid=US:en",
    # 3. 补充：机器之心
    "https://www.jiqizhixin.com/"
    
]

news_text = ""
article_count = 1

# 遍历我们设定的所有搜索引擎和数据源
for url in search_urls:
    try:
        feed = feedparser.parse(url)
        # 每个搜索源提取前 15 条最相关/最新的新闻，总共约 45 条
        for entry in feed.entries[:15]:
            # 清洗摘要中的 HTML 标签，只保留纯文本，避免消耗过多 AI Token
            raw_summary = entry.get('summary', '')
            clean_summary = re.sub(r'<[^>]+>', '', raw_summary).strip()
            
            news_text += f"【第{article_count}条】\n标题: {entry.title}\n链接: {entry.link}\n摘要: {clean_summary}\n\n"
            article_count += 1
    except Exception as e:
        print(f"⚠️ 抓取 {url} 时出现小错误: {e}")

print(f"✅ 成功从全网抓取到 {article_count-1} 条最新资讯！准备交给 AI 深度提炼...")

# ================= 2. 初始化 AI 大脑 =================
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("❌ 找不到 API Key，请检查 GitHub Secrets (OPENROUTER_API_KEY) 是否配置正确！")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key, 
)

# ================= 3. 让 AI 编写研报级日报 =================
prompt = f"""
你是一个顶级的 AI 行业分析师和新闻主编。请严格按照以下结构和格式，记住是严格按照，将我提供的多语种新闻生肉数据，整理、翻译并深加工成一份高质量的《全球AI领域关键动态报告》。

【分类结构要求】
请尽量将新闻归入以下分类（如果没有相关新闻，则直接省略该分类标题，不要硬编）：
## 一、宏观与政策 (如政府报告、监管政策、行业倡议、法律诉讼等)
## 二、投融资与战略 (如收购、融资、大厂战略合作、高管变动等)
## 三、技术与产业发展
### 3.1 算力与硬件 (芯片、服务器、智能终端设备)
### 3.2 算法与模型 (大模型发布、架构创新、开源动态)
### 3.3 数据与安全 (数据集、AI风险、对齐、隐私)
### 3.4 赋能应用 (AI在各类垂直行业中的落地产品和案例)
### 3.5 新兴领域探索 (具身智能机器人、脑机接口、前沿黑科技等)

【排版与内容格式要求】
对于每一条具有价值的新闻，必须严格采用以下 Markdown 列表格式输出：
  * **[精炼的新闻核心短标题]* 
  **🔗 原文链接**：这里必须原样复制对应的 http 网址，绝不能省略！**
  * **事件描述**：用客观、精炼的中文简述该事件的核心事实（人物、事件、时间、地点）。
  * **重要性分析**：以资深分析师的视角，深度点评该事件对行业格局、技术演进或商业生态的深远影响。

⚠️ 强制核心要求（至关重要）：
1. 拒绝过度精简！请务必保证报告的丰富度和信息量，在输入数据充足的情况下，**请至少输出 15 到 20 条独立的新闻动态！** 不要随意抛弃科技厂商的产品更新、融资信息或前沿研究。
2. 真实链接！标题后面的括号里必须原样保留我提供的真实新闻链接（http开头的网址），绝对不能用占位符替代！
【Tone / 语气】
专业、客观、深度、宏大，类似于顶级智库或商业投行的行业洞察报告。剔除无关紧要的噪音信息，只保留真正有价值的行业动态。

以下是今日抓取到的全网生肉数据：
{news_text}
"""

print("🧠 正在呼叫 AI 进行深度分析与研报生成，这可能需要几十秒到一分钟，请稍候...")
try:
    response = client.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free", # 保持使用你之前选定的免费模型
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    report_content = response.choices[0].message.content
except Exception as e:
    print(f"❌ AI 生成失败: {e}")
    report_content = "> ⚠️ AI 生成报告时遇到网络或接口问题，请检查 API 状态或稍后再试。"

# ================= 4. 保存为 Markdown 文件 =================
print(f"\n📝 正在生成文件: {filename}")
with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# 📊 全球 AI 领域关键动态报告 ({today_str})\n\n")
    f.write("> 本报告由 AI 自动聚合全网资讯并深度分析生成，旨在提供宏观与微观层面的产业洞察。\n\n")
    f.write(report_content)

print("="*40)
print("✅ 研报级 AI 自动化简报生成并保存完毕！")
print("="*40)
# ================= 5. 生成精美的 PDF 文件 =================
print(f"📄 正在将报告排版并导出为 PDF: {filename.replace('.md', '.pdf')} ...")

# 1. 先把 Markdown 转换成带样式的 HTML
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* 这里是我们给 PDF 定制的排版样式，让它看起来像专业研报 */
        body {{ 
            font-family: 'WenQuanYi Micro Hei', 'Microsoft YaHei', sans-serif; 
            padding: 40px; 
            line-height: 1.8; 
            color: #333;
        }}
        h1 {{ color: #1D4ED8; text-align: center; border-bottom: 2px solid #1D4ED8; padding-bottom: 10px; }}
        h2 {{ color: #2563EB; margin-top: 30px; }}
        h3 {{ color: #3B82F6; }}
        a {{ color: #1D4ED8; text-decoration: none; }}
        li {{ margin-bottom: 12px; }}
    </style>
</head>
<body>
    <h1>📊 全球 AI 领域关键动态报告 ({today_str})</h1>
    <p><em>本报告由 AI 自动聚合全网资讯并深度分析生成，旨在提供宏观与微观层面的产业洞察。</em></p>
    <hr>
    {markdown.markdown(report_content)}
</body>
</html>
"""

# 2. 调用引擎生成 PDF
try:
    pdf_filename = f"AI_News_{today_str}.pdf"
    pdfkit.from_string(html_content, pdf_filename)
    print("✅ PDF 导出成功！")
except Exception as e:
    print(f"❌ PDF 生成失败，请检查环境配置: {e}")