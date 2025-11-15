import os
import base64
from io import BytesIO
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_SECRET"))
model = "gpt-3.5-turbo"

# Generate ChatGPT analysis
def chatgpt_analysis(df, model, report_month):
    prompt = f"""
        Analyze this sales data for {report_month}:
        - Top 3 products by sales and profit.
        - Regions with highest/lowest growth.
        - Any anomalies or trends.
        - 3 actionable recommendations.
        Data sample: {df.head().to_dict()}
        """
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# Generate sales graph
def generate_sales_graph(df, report_month):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="Date", y="Sales", hue="Region")
    plt.title(f"Sales by Region - {report_month}")
    sales_graph_buffer = BytesIO()
    plt.savefig(sales_graph_buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    sales_graph_buffer.seek(0)
    return base64.b64encode(sales_graph_buffer.getvalue()).decode("utf-8")

# Generate profit graph
def generate_profit_graph(df, report_month):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="Product", y="Profit")
    plt.title(f"Profit by Product - {report_month}")
    profit_graph_buffer = BytesIO()
    plt.savefig(profit_graph_buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    profit_graph_buffer.seek(0)
    return base64.b64encode(profit_graph_buffer.getvalue()).decode("utf-8")

# Generating Sales Report
def generate_sales_report(request):
    try:
        # Parse request
        request_json = request.get_json()
        headers = request_json["headers"]
        rows = request_json["rows"]
        report_month = request_json["reportMonth"]

        # Convert to Pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Generate graphs
        sales_graph_base64 = generate_sales_graph(df, report_month)
        profit_graph_base64 = generate_profit_graph(df, report_month)

        # Generate ChatGPT analysis
        analysis_text = chatgpt_analysis(df, model, report_month)

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
        # Decode the base64 image and create an Image object
        sales_graph_image = Image(BytesIO(base64.b64decode(sales_graph_base64)), width=400, height=250)
        story.append(sales_graph_image)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Profit by Product", styles["Heading2"]))
        profit_graph_image = Image(BytesIO(base64.b64decode(profit_graph_base64)), width=400, height=250)
        story.append(profit_graph_image)
        story.append(Spacer(1, 12))

        # Add ChatGPT analysis
        story.append(Paragraph("AI Analysis", styles["Heading2"]))
        story.append(Paragraph(analysis_text, styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        # Return PDF as HTTP response
        return (
            buffer.getvalue(),
            200,
            {
                "Content-Type": "application/pdf",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        return {"error": str(e), "status": "error"}, 500
