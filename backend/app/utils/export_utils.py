from typing import List, Dict, Any
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def export_to_excel(data: List[Dict[str, Any]], filename: str, sheet_name: str = "数据") -> str:
    """导出数据到Excel文件"""
    # 确保文件名以.xlsx结尾
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 保存到临时目录
    from app.config import settings
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    # 确保目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    df.to_excel(file_path, index=False, sheet_name=sheet_name)

    # 返回绝对路径（修复：之前返回相对路径导致 FileResponse 找不到文件）
    return file_path


def export_to_pdf(data: List[Dict[str, Any]], filename: str, title: str = "数据报表") -> str:
    """导出数据到PDF文件"""
    # 确保文件名以.pdf结尾
    if not filename.endswith('.pdf'):
        filename += '.pdf'

    from app.config import settings
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    # 确保目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 创建PDF文档
    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    # 注册中文字体（使用系统字体或项目字体）
    # 这里使用默认字体，实际部署时需要配置中文字体
    elements = []

    # 添加标题
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # 准备表格数据
    if len(data) > 0:
        # 表头
        headers = list(data[0].keys())
        table_data = [headers]

        # 表格内容
        for row in data[:100]:  # 限制100行，避免PDF过大
            table_data.append([str(row.get(col, '')) for col in headers])

        # 创建表格
        table = Table(table_data)

        # 设置表格样式
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ])
        table.setStyle(style)

        elements.append(table)

    # 生成PDF
    doc.build(elements)

    # 返回绝对路径（修复：之前返回相对路径导致 FileResponse 找不到文件）
    return file_path


def dataframe_to_excel(df: pd.DataFrame, filename: str, sheet_name: str = "数据") -> str:
    """将DataFrame导出为Excel"""
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'

    from app.config import settings
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    # 确保目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    df.to_excel(file_path, index=False, sheet_name=sheet_name)

    # 返回绝对路径
    return file_path


def dataframe_to_pdf(df: pd.DataFrame, filename: str, title: str = "数据报表") -> str:
    """将DataFrame导出为PDF"""
    return export_to_pdf(df.to_dict('records'), filename, title)
