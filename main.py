import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import os
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from flask import make_response, jsonify
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_sales_report(request):
    try:
        # Parse request
        request_json = request.get_json()
        headers = request_json["headers"]
        rows = request_json["rows"]
        report_month = request_json["reportMonth"]

        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)
        logger.info(f"DataFrame shape: {df.shape}")

        # Generate graphs
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x="Date", y="Sales", hue="Region")
        plt.title(f"Sales by Region - {report_month}")
        sales_graph_buffer = BytesIO()
        plt.savefig(sales_graph_buffer, format='png', bbox_inches='tight')
        plt.close()
        sales_graph_buffer.seek(0)

        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="Product", y="Profit")
        plt.title(f"Profit by Product - {report_month}")
        profit_graph_buffer = BytesIO()
        plt.savefig(profit_graph_buffer, format='png', bbox_inches='tight')
        plt.close()
        profit_graph_buffer.seek(0)

        # Generate ChatGPT analysis
        prompt = f"""
        Analyze this sales data for {report_month}:
        - Top 3 products by sales and profit.
        - Regions with highest/lowest growth.
        - Any anomalies or trends.
        - 3 actionable recommendations.
        Data sample: {df.head().to_dict()}
        """
        chatgpt_analysis = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        ).choices[0].message.content

        # Create PDF report
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        story.append(Paragraph(f"Sales Report - {report_month}", styles["Title"]))
        story.append(Spacer(1, 24))

        # Add graphs
        story.append(Paragraph("Sales by Region", styles["Heading2"]))
        story.append(Image(sales_graph_buffer, width=400, height=250))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Profit by Product", styles["Heading2"]))
        story.append(Image(profit_graph_buffer, width=400, height=250))
        story.append(Spacer(1, 12))

        # Add ChatGPT analysis
        story.append(Paragraph("AI Analysis", styles["Heading2"]))
        story.append(Paragraph(chatgpt_analysis, styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        # Return PDF
        response = make_response(buffer.getvalue())
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
