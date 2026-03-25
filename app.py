import streamlit as st
from openai import OpenAI
import dashscope
from dashscope import ImageSynthesis

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="我的 AI 创意画板", page_icon="🎨", layout="centered")
st.title("🎨 我的专属 AI 创意画板")
st.markdown("告诉我想画什么，AI 大脑会自动帮你构思细节，并呼叫阿里云画师为你作画！")

# --- 2. 安全读取 API Keys ---
# 部署到云端时，它会自动从后台加密库里读取你的 Key，防泄露！
try:
    deepseek_key = st.secrets["DEEPSEEK_KEY"]
    dashscope_key = st.secrets["DASHSCOPE_KEY"]
except:
    st.warning("⚠️ 警告：找不到 API Key，请先在 Streamlit 后台的 Secrets 中配置。")
    st.stop()

# 初始化 AI 客户端
client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
dashscope.api_key = dashscope_key

# --- 3. 界面交互与核心逻辑 ---
user_input = st.text_input("请输入你的脑洞：", placeholder="例如：一只穿着宇航服的柯基犬在月球上吃热狗")

if st.button("🚀 一键生成画作"):
    if not user_input:
        st.warning("请先输入你的脑洞哦！")
    else:
        with st.spinner('🤖 AI 大脑正在构思，画师正在挥毫泼墨，请稍等大约 5-10 秒...'):
            try:
                # 第一步：呼叫 DeepSeek 出主意
                llm_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "你是一个顶级的 AI 绘画提示词专家。请根据用户的简单中文描述，直接输出一句高质量的英文Prompt用于画图。不要废话。"},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7
                )
                perfect_prompt = llm_response.choices[0].message.content.strip()

                # 第二步：呼叫阿里云画图
                img_response = ImageSynthesis.call(
                    model=ImageSynthesis.Models.wanx_v1,
                    prompt=perfect_prompt,
                    n=1,
                    size='1024*1024'
                )

                # 第三步：展示结果
                if img_response.status_code == 200:
                    image_url = img_response.output.results[0].url
                    st.success("🎉 创作完成！")
                    st.image(image_url, caption="由阿里云通义万相生成", use_container_width=True)
                    with st.expander("👀 查看 AI 构思的专业提示词"):
                        st.code(perfect_prompt)
                else:
                    st.error(f"阿里云画师报错: {img_response.code} - {img_response.message}")

            except Exception as e:
                st.error(f"系统运行出错: {str(e)}")