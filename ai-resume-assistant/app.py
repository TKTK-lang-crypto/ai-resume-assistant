import streamlit as st
from utils.llm_client import call_llm
from utils.prompt_templates import (
    build_keyword_prompt,
    build_match_score_prompt,
    build_gap_analysis_prompt,
    build_resume_optimization_prompt,
    build_interview_prompt,
    build_full_analysis_prompt,
)
from utils.file_parser import parse_resume_file
from utils.result_parser import extract_total_score, extract_scores, extract_keywords
import utils.db as db

# ---------- 页面配置 ----------
st.set_page_config(page_title="AI 简历优化助手", page_icon="📄", layout="wide")

# 初始化数据库
db.init_db()

# ---------- 初始化 session_state（统一使用 key 绑定） ----------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_description" not in st.session_state:
    st.session_state.job_description = ""

for key in ["keyword_result", "match_result", "gap_result", "optimization_result", "interview_result", "full_result"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ---------- 标题 ----------
st.title("📄 AI 简历优化助手")
st.caption("基于大模型的简历与岗位 JD 匹配分析工具")

# ---------- 侧边栏（不变，省略以节省篇幅，但实际代码中保留） ----------
# ...（此处省略侧边栏，实际替换时应保留完整侧边栏代码）

# ---------- 输入区域 ----------
st.subheader("1. 输入简历和岗位 JD")
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### 你的简历内容")
    uploaded_file = st.file_uploader(
        "上传简历文件（PDF / DOCX / TXT）",
        type=["pdf", "docx", "txt"],
        key="resume_uploader",
        help="上传后自动提取文本，将覆盖下方手动输入的内容。"
    )

    # 处理上传文件
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_type = uploaded_file.name.split(".")[-1].lower()
        try:
            parsed_text = parse_resume_file(file_bytes, file_type)
            if parsed_text.strip():
                # 直接更新 session_state.resume_text（text_area 的 key 绑定了它）
                st.session_state.resume_text = parsed_text
                st.success(f"✅ 解析成功！共提取 {len(parsed_text)} 个字符。")
                st.rerun()  # 刷新页面，让 text_area 显示新内容
            else:
                st.error("❌ 解析结果为空，可能是扫描件或图片型 PDF。请手动输入。")
        except Exception as e:
            st.error(f"❌ 文件解析失败：{str(e)}")

    # 简历文本输入框：key 直接绑定到 session_state.resume_text
    st.text_area(
        label="或手动粘贴简历文本",
        height=300,
        placeholder="例如：教育背景、技能、项目经历、实习经历等...",
        key="resume_text"  # 关键改动：这里绑定后，用户输入会自动更新 session_state.resume_text
    )

with col2:
    st.markdown("### 目标岗位 JD")
    st.text_area(
        label="请粘贴目标岗位描述",
        height=300,
        placeholder="例如：AI 应用开发实习生岗位要求、技能要求、加分项等...",
        key="job_description"  # 同样绑定
    )

# ---------- 功能按钮 ----------
# ...（按钮部分不变，但注意 check_inputs 和 safe_call_llm 需要从 st.session_state 读取数据）

# ---------- 输入校验 & 通用调用 ----------
def check_inputs(require_resume=True):
    if require_resume and not st.session_state.resume_text.strip():
        st.warning("请先输入简历内容或上传简历文件。", icon="⚠️")
        return False
    if not st.session_state.job_description.strip():
        st.warning("请先输入目标岗位 JD。", icon="⚠️")
        return False
    return True

def safe_call_llm(prompt, result_key, analysis_type, success_msg="分析完成！"):
    try:
        with st.spinner("正在调用大模型，请稍候..."):
            result = call_llm(prompt)
        st.session_state[result_key] = result
        db.save_record(
            analysis_type=analysis_type,
            resume_text=st.session_state.resume_text,
            job_description=st.session_state.job_description,
            result=result
        )
        st.success(success_msg)
    except Exception as e:
        st.error(f"调用失败：{str(e)}")
        st.session_state[result_key] = ""

# ---------- 按钮逻辑 ----------
# 按钮判断保持不变，但注意所有函数都从 st.session_state 获取 resume_text 和 job_description
# 例如：
if keyword_btn:
    if check_inputs(require_resume=False):
        prompt = build_keyword_prompt(st.session_state.job_description)
        safe_call_llm(prompt, "keyword_result", "keyword", "关键词提取完成！")

# ... 其他按钮同理

# ---------- 后续结果展示保持不变 ----------
# 但所有展示函数仍使用 st.session_state 中的数据

# 底部
st.divider()
st.caption("AI Resume Assistant v0.7 | 采用 key 绑定，上传与输入完全同步")
