# customer_support_agent_tools.py
#
# This script defines a set of tools for a customer support agent, initializes
# a Bedrock-powered agent with these tools, and provides examples of how to
# test its functionality.

# Note: This script was created from multiple notebook cells. The original
# notebook likely installed dependencies with the following command.
# You may need to run this in your environment:
# pip install -U -r requirements.txt -q
# (Assuming requirements.txt contains boto3, strands, ddgs-search, etc.)

import os
import time
import boto3
from boto3.session import Session

# These appear to be custom libraries for a specific framework (e.g., "strands")
# and a search library. Ensure they are installed in your environment.
try:
    from strands.tools import tool
    from strands import Agent
    from strands.models import BedrockModel
    from ddgs import DDGS
    from ddgs.exceptions import DDGSException, RatelimitException
    # The 'retrieve' tool is used in get_technical_support
    from strands_tools import retrieve
except ImportError as e:
    print(f"Warning: A required library is not installed. {e}")
    print("Please ensure 'strands', 'ddgs-search', and boto3 are installed.")
    # Define a dummy decorator if 'strands' is not available
    def tool(func):
        return func

# ==============================================================================
# SECTION 1: TOOL DEFINITIONS
# ==============================================================================

@tool
def get_return_policy(product_category: str) -> str:
    """
    Get return policy information for a specific product category.

    Args:
        product_category: Electronics category (e.g., 'smartphones', 'laptops', 'accessories')

    Returns:
        Formatted return policy details including timeframes and conditions
    """
    # Mock return policy database - in real implementation, this would query a database
    return_policies = {
        "smartphones": {
            "window": "30 days",
            "condition": "Original packaging, no physical damage, factory reset required",
            "process": "Online RMA portal or technical support",
            "refund_time": "5-7 business days after inspection",
            "shipping": "Free return shipping, prepaid label provided",
            "warranty": "1-year manufacturer warranty included"
        },
        "laptops": {
            "window": "30 days",
            "condition": "Original packaging, all accessories, no software modifications",
            "process": "Technical support verification required before return",
            "refund_time": "7-10 business days after inspection",
            "shipping": "Free return shipping with original packaging",
            "warranty": "1-year manufacturer warranty, extended options available"
        },
        "accessories": {
            "window": "30 days",
            "condition": "Unopened packaging preferred, all components included",
            "process": "Online return portal",
            "refund_time": "3-5 business days after receipt",
            "shipping": "Customer pays return shipping under $50",
            "warranty": "90-day manufacturer warranty"
        }
    }

    # Default policy for unlisted categories
    default_policy = {
        "window": "30 days",
        "condition": "Original condition with all included components",
        "process": "Contact technical support",
        "refund_time": "5-7 business days after inspection",
        "shipping": "Return shipping policies vary",
        "warranty": "Standard manufacturer warranty applies"
    }

    policy = return_policies.get(product_category.lower(), default_policy)
    return f"Return Policy - {product_category.title()}:\n\n" \
           f"• Return window: {policy['window']} from delivery\n" \
           f"• Condition: {policy['condition']}\n" \
           f"• Process: {policy['process']}\n" \
           f"• Refund timeline: {policy['refund_time']}\n" \
           f"• Shipping: {policy['shipping']}\n" \
           f"• Warranty: {policy['warranty']}"

@tool
def get_product_info(product_type: str) -> str:
    """
    Get detailed technical specifications and information for electronics products.

    Args:
        product_type: Electronics product type (e.g., 'laptops', 'smartphones', 'headphones', 'monitors')

    Returns:
        Formatted product information including warranty, features, and policies
    """
    # Mock product catalog - in a real implementation, this would query a product database
    products = {
        "laptops": {
            "warranty": "1-year manufacturer warranty + optional extended coverage",
            "specs": "Intel/AMD processors, 8-32GB RAM, SSD storage, various display sizes",
            "features": "Backlit keyboards, USB-C/Thunderbolt, Wi-Fi 6, Bluetooth 5.0",
            "compatibility": "Windows 11, macOS, Linux support varies by model",
            "support": "Technical support and driver updates included"
        },
        "smartphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "5G/4G connectivity, 128GB-1TB storage, multiple camera systems",
            "features": "Wireless charging, water resistance, biometric security",
            "compatibility": "iOS/Android, carrier unlocked options available",
            "support": "Software updates and technical support included"
        },
        "headphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "Wired/wireless options, noise cancellation, 20Hz-20kHz frequency",
            "features": "Active noise cancellation, touch controls, voice assistant",
            "compatibility": "Bluetooth 5.0+, 3.5mm jack, USB-C charging",
            "support": "Firmware updates via companion app"
        },
        "monitors": {
            "warranty": "3-year manufacturer warranty",
            "specs": "4K/1440p/1080p resolutions, IPS/OLED panels, various sizes",
            "features": "HDR support, high refresh rates, adjustable stands",
            "compatibility": "HDMI, DisplayPort, USB-C inputs",
            "support": "Color calibration and technical support"
        }
    }

    product = products.get(product_type.lower())
    if not product:
        return f"Technical specifications for {product_type} not available. Please contact our technical support team for detailed product"

    return f"Technical Information - {product_type.title()}:\n\n" \
           f"• Warranty: {product['warranty']}\n" \
           f"• Specifications: {product['specs']}\n" \
           f"• Key Features: {product['features']}\n" \
           f"• Compatibility: {product['compatibility']}\n" \
           f"• Support: {product['support']}"

@tool
def web_search(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
    """
    Search the web for updated information.

    Args:
        keywords (str): The search query keywords.
        region (str): The search region: wt-wt, us-en, uk-en, ru-ru, etc.
        max_results (int | None): The maximum number of results to return.

    Returns:
        List of dictionaries with search results.
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "No results found."
    except RatelimitException:
        return "Rate limit reached. Please try again later."
    except DDGSException as e:
        return f"Search error: {e}"
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def get_technical_support(issue_description: str) -> str:
    """Provides technical support by searching a knowledge base."""
    try:
        # Get KB ID from parameter store
        ssm = boto3.client('ssm')
        account_id = boto3.client('sts').get_caller_identity()['Account']
        region = boto3.Session().region_name
        
        kb_id_param_name = f"/{account_id}-{region}/kb/knowledge-base-id"
        kb_id = ssm.get_parameter(Name=kb_id_param_name)['Parameter']['Value']
        print(f"Successfully retrieved KB ID: {kb_id}")

        # Use strands retrieve tool
        tool_use = {
            "toolUseId": "tech_support_query",
            "input": {
                "text": issue_description,
                "knowledgeBaseId": kb_id,
                "region": region,
                "numberOfResults": 3,
                "score": 0.4
            }
        }
        # Assuming the 'retrieve' function is called with these parameters
        return retrieve(**tool_use)
    except Exception as e:
        return f"An error occurred while getting technical support: {str(e)}"

# ==============================================================================
# SECTION 2: KNOWLEDGE BASE MANAGEMENT FUNCTIONS
# ==============================================================================

def download_kb_files():
    """Downloads technical support files from S3 to a local directory."""
    print("\n--- Starting Knowledge Base File Download ---")
    s3 = boto3.client('s3')
    account_id = boto3.client('sts').get_caller_identity()['Account']
    region = boto3.Session().region_name
    bucket_name = f"{account_id}-{region}-kb-data-bucket"
    local_folder = "knowledge_base_data"

    os.makedirs(local_folder, exist_ok=True)
    
    print(f"Checking for files in bucket: {bucket_name}")
    s3_objects = s3.list_objects_v2(Bucket=bucket_name)
    files_to_download = s3_objects.get('Contents', [])

    if not files_to_download:
        print("No files found in the bucket to download.")
        return

    for obj in files_to_download:
        file_name = obj['Key']
        local_path = os.path.join(local_folder, file_name)
        print(f"Downloading: {file_name}")
        s3.download_file(bucket_name, file_name, local_path)
    
    print(f"All files saved to: {local_folder}/")

def sync_knowledge_base():
    """Syncs the knowledge base with product technical_support files from S3."""
    print("\n--- Starting Knowledge Base Sync Job ---")
    ssm = boto3.client('ssm')
    bedrock = boto3.client('bedrock-agent')
    s3 = boto3.client('s3')

    # Get parameters
    account_id = boto3.client('sts').get_caller_identity()['Account']
    region = boto3.Session().region_name
    
    kb_id = ssm.get_parameter(Name=f"/{account_id}-{region}/kb/knowledge-base-id")['Parameter']['Value']
    ds_id = ssm.get_parameter(Name=f"/{account_id}-{region}/kb/data-source-id")['Parameter']['Value']

    # Start sync job
    print("Starting Bedrock ingestion job...")
    response = bedrock.start_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=ds_id,
        description="Quick sync"
    )
    job_id = response['ingestionJob']['ingestionJobId']
    print(f"Bedrock knowledge base sync job started. Job ID: {job_id}")

    # Monitor until complete
    while True:
        job = bedrock.get_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id,
            ingestionJobId=job_id
        )['ingestionJob']
        status = job['status']
        print(f"Current job status: {status}...")
        if status in ['COMPLETE', 'FAILED']:
            break
        time.sleep(10)

    # Print final result
    if status == 'COMPLETE':
        print(f"✅ Bedrock Knowledge base sync job completed Successfully.")
    else:
        print(f"❌ Bedrock knowledge base sync job failed with status: {status}")

# ==============================================================================
# SECTION 3: MAIN EXECUTION BLOCK (CREATE AND TEST AGENT)
# ==============================================================================

if __name__ == '__main__':
    
    # --- Step 1: Define Agent Configuration ---
    boto_session = Session()
    region = boto_session.region_name

    SYSTEM_PROMPT = """You are a helpful and professional customer support assistant for an electronics e-commerce company.
    Your role is to:
    - Provide accurate information using the tools available to you
    - Support the customer with technical information and product specifications, and maintenance questions
    - Be friendly, patient, and understanding with customers
    - Always offer additional help after answering questions
    - If you can't help with something, direct customers to the appropriate contact

    You have access to the following tools:
    1. get_return_policy() - For warranty and return policy questions
    2. get_product_info() - To get information about a specific product
    3. web_search() - To access current technical documentation, or for updated information.
    4. get_technical_support() - For troubleshooting issues, setup guides, maintenance tips, and detailed technical assistance

    For any technical problems, setup questions, or maintenance concerns, always use the get_technical_support() tool as it contains our comprehensive knowledge base.
    Always use the appropriate tool to get accurate, up-to-date information rather than making assumptions about electronic products or specifications.
    """

    # --- Step 2: Create the Customer Support Agent ---
    print("Initializing Bedrock model...")
    model = BedrockModel(
        model_id="anthropic.claude-3-7-sonnet-20250219-v1:0",
        temperature=0.3,
        region_name=region
    )

    print("Creating the customer support agent with all tools...")
    agent = Agent(
        model=model,
        tools=[
            get_product_info,      # Tool 1: Simple product information lookup
            get_return_policy,     # Tool 2: Simple return policy lookup
            web_search,            # Tool 3: Access the web for updated information
            get_technical_support, # Tool 4: Technical support & troubleshooting
        ],
        system_prompt=SYSTEM_PROMPT,
    )
    print("✅ Customer Support Agent created successfully!")

    # --- Step 3: Test the Customer Support Agent ---
    print("\nNow testing the agent with sample queries...")

    print("\n--- Test 1: Return Policy Check ---")
    query1 = "What's the return policy for my thinkpad X1 Carbon?"
    print(f"Query: {query1}")
    response1 = agent(query1)
    print(f"Response: {response1}")

    print("\n--- Test 2: Troubleshooting ---")
    query2 = "I bought an iphone 14 last month. I don't like it because it heats up. How do I solve it?"
    print(f"Query: {query2}")
    response2 = agent(query2)
    print(f"Response: {response2}")

    print("\n--- Test 3: General Query ---")
    query3 = "How do I run your agent properly"
    print(f"Query: {query3}")
    response3 = agent(query3)
    print(f"Response: {response3}")

    # --- Optional: Run Knowledge Base Management ---
    # You can uncomment the following lines to download S3 files and sync the KB
    # print("\n--- Starting Knowledge Base Management ---")
    # download_kb_files()
    # sync_knowledge_base()