from openai import OpenAI
import json
from typing import List, Dict, Any

# Local imports
from app.services import scraper
from dotenv import load_dotenv
import os


load_dotenv()
# Initialize the OpenAI client
# It will automatically look for the OPENAI_API_KEY environment variable
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Warning: OpenAI client could not be initialized. {e}")
    client = None

# --- Step 1: Define the Toolbox ---
# This is a registry that maps a function name to the actual Python function.
tool_map = {
    "get_stock_price_data": scraper.get_stock_price_data,
    "get_price_earning_data": scraper.get_price_earning_data,
    "get_financial_statement": scraper.get_financial_statement,
    "get_company_profile": scraper.get_company_profile,
    "get_latest_news": scraper.get_latest_news,
}

# This is the JSON schema for the tools that we will send to the LLM.
# It describes what the functions do and what their parameters are.
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price_data",
            "description": "Fetches the latest stock price and key trading data for a given company ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol. For Indian companies on the NSE, it must end with '.NS'. For example, 'RELIANCE.NS' or 'TCS.NS'."
                    }
                },
                "required": ["ticker_symbol"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_earning_data",
            "description": "Fetches the Trailing P/E ratio and Forward P/E ratio for a given company ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol. For Indian companies on the NSE, it must end with '.NS'. For example, 'RELIANCE.NS' or 'TCS.NS'."
                    }
                },
                "required": ["ticker_symbol"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_statement",
            "description": "Fetches a company's financial statements (income statement, balance sheet, or cash flow).",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g., 'RELIANCE.NS'."
                    },
                    "statement_type": {
                        "type": "string",
                        "enum": ["income", "balance", "cashflow"],
                        "description": "The type of financial statement to fetch."
                    },
                    "frequency": {
                        "type": "string",
                        "enum": ["annual", "quarterly"],
                        "description": "The frequency of the report. Defaults to 'annual'."
                    }
                },
                "required": ["ticker_symbol", "statement_type"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_profile",
            "description": "Fetches key profile information for a company, such as sector, industry, and business summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g., 'RELIANCE.NS'."
                    }
                },
                "required": ["ticker_symbol"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_news",
            "description": "Fetches the latest news articles for a given company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g., 'RELIANCE.NS'."
                    }
                },
                "required": ["ticker_symbol"],
            },
        }
    }
]


# --- Step 2: The Decider (Orchestrator) ---
def decide_on_tool(query: str) -> List[Dict[str, Any]]:
    """
    Takes a user query, sends it to the LLM with a list of available tools,
    and returns the tool(s) the LLM decides to call.
    """
    if not client:
        return [{"error": "OpenAI client not configured. Please set the OPENAI_API_KEY."}]

    system_prompt = """
    You are an expert financial assistant. Your job is to understand the user's query
    and select the appropriate tool to get the necessary financial data.
    You must respond only by calling the functions you have been provided.
    If the user asks about an Indian company, ensure the ticker symbol ends with '.NS'.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo", # Or any model that supports tool calling
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            tools=tools_schema,
            tool_choice="auto",  # Let the model decide whether to call a tool
        )
        
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            # Manually construct a list of dictionaries from the tool_call objects
            # to avoid JSON serialization errors with the complex OpenAI object.
            parsed_tool_calls = []
            for call in tool_calls:
                parsed_tool_calls.append({
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                })
            return parsed_tool_calls
        else:
            # The LLM decided not to call any tool. It might be a general question.
            # For now, we'll handle this as "no action taken".
            return []

    except Exception as e:
        return [{"error": f"An error occurred with the OpenAI API: {e}"}]


# --- Step 3: The Executor ---
def execute_tool_call(tool_call: Dict[str, Any]) -> Any:
    """
    Takes a single tool call object from the LLM's response and executes
    the corresponding Python function.
    """
    function_name = tool_call['function']['name']
    function_to_call = tool_map.get(function_name)

    if not function_to_call:
        return f"Error: Tool '{function_name}' not found."

    try:
        function_args = json.loads(tool_call['function']['arguments'])
        
        # Security check: Ensure the arguments are what we expect
        # For now, we assume the LLM is trusted. In a production system,
        # you would add validation here (e.g., using Pydantic).
        
        result = function_to_call(**function_args)
        return result
    except json.JSONDecodeError:
        return "Error: Invalid arguments format from LLM."
    except Exception as e:
        return f"Error executing function '{function_name}': {e}"

