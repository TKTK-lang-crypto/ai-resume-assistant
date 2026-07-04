# utils/file_parser.py
import io
import PyPDF2
import docx

def parse_pdf(file_bytes: bytes) -> str:
    """使用 PyPDF2 解析 PDF（纯 Python，无系统依赖）"""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            return text
        else:
            raise ValueError("PDF 解析结果为空，可能是扫描件或图片型 PDF。")
    except Exception as e:
        # 如果 PyPDF2 失败，尝试使用 pdfplumber（如果已安装）
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text
                else:
                    raise ValueError("pdfplumber 解析也为空。")
        except ImportError:
            # 如果 pdfplumber 未安装，直接抛出原始错误
            raise ValueError(f"PyPDF2 解析失败且 pdfplumber 未安装：{str(e)}")
        except Exception as e2:
            raise ValueError(f"所有 PDF 解析方法均失败：{str(e2)}")

def parse_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        if text.strip():
            return text
        else:
            raise ValueError("DOCX 文件内容为空。")
    except Exception as e:
        raise ValueError(f"DOCX 解析失败：{str(e)}")

def parse_txt(file_bytes: bytes) -> str:
    encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
    for enc in encodings:
        try:
            text = file_bytes.decode(enc)
            if text.strip():
                return text
        except UnicodeDecodeError:
            continue
    raise ValueError("无法识别 TXT 文件编码，请保存为 UTF-8 或 GBK 格式。")

def parse_resume_file(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        return parse_pdf(file_bytes)
    elif file_type == "docx":
        return parse_docx(file_bytes)
    elif file_type == "txt":
        return parse_txt(file_bytes)
    else:
        raise ValueError(f"不支持的文件类型：{file_type}")
