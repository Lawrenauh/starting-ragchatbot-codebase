import google.genai as genai
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Google's Gemini API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- **One search per query maximum**
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        
        # Pre-build base API parameters
        self.base_params = {
            "temperature": 0,
            "max_output_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        
        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            
        Returns:
            Generated response as string
        """
        
        # Build system content efficiently - avoid string ops when possible
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history 
            else self.SYSTEM_PROMPT
        )
        
        # Prepare API call parameters efficiently
        api_params = {
            "model": self.model_name,
            "contents": [{"role": "user", "parts": [{"text": query}]}]
        }
        
        # Add generation config
        if self.base_params:
            api_params["config"] = self.base_params
        
        # Add system instructions
        if system_content:
            api_params["config"] = api_params.get("config", {})
            api_params["config"]["system_instruction"] = {"parts": [{"text": system_content}]}
        
        # Add tools if available
        if tools:
            # Convert tools to Google GenAI format and add to config
            api_params["config"] = api_params.get("config", {})
            gemini_tools = []
            for tool in tools:
                gemini_tool = {
                    "function_declarations": [tool]
                }
                gemini_tools.append(gemini_tool)
            api_params["config"]["tools"] = gemini_tools
        
        # Get response from Gemini
        response = self.client.models.generate_content(**api_params)
        
        # Handle tool execution if needed
        if response.candidates[0].finish_reason == "STOP" and tool_manager:
            return self._handle_tool_execution(response, api_params, tool_manager)
        
        # Return direct response
        return response.text
    
    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tool_manager):
        """
        Handle execution of tool calls and get follow-up response.
        
        Args:
            initial_response: The response containing tool use requests
            base_params: Base API parameters
            tool_manager: Manager to execute tools
            
        Returns:
            Final response text after tool execution
        """
        # Start with existing contents
        contents = base_params["contents"].copy()
        
        # Add AI's tool use response
        contents.append({"role": "model", "parts": initial_response.candidates[0].content.parts})
        
        # Execute all tool calls and collect results
        tool_results = []
        for part in initial_response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call is not None:
                function_call = part.function_call
                # Make sure we have the required 'query' parameter
                tool_args = dict(function_call.args) if function_call.args else {}
                if 'query' not in tool_args and function_call.name == 'search_course_content':
                    # This is a workaround - we need to get the query from the original request
                    # In a real implementation, this should be handled more properly
                    tool_args['query'] = 'default query'
                
                tool_result = tool_manager.execute_tool(
                    function_call.name, 
                    **tool_args
                )
                
                tool_results.append({
                    "function_response": {
                        "name": function_call.name,
                        "response": {
                            "content": tool_result
                        }
                    }
                })
        
        # Add tool results as single message
        if tool_results:
            contents.append({"role": "user", "parts": tool_results})
        
        # Prepare final API call without tools
        final_params = {
            "model": self.model_name,
            "contents": contents
        }
        
        # Add generation config
        if self.base_params:
            final_params["config"] = self.base_params
            
        # Add system instructions
        if base_params.get("config", {}).get("system_instruction"):
            final_params["config"] = final_params.get("config", {})
            final_params["config"]["system_instruction"] = base_params["config"]["system_instruction"]
        
        # Get final response
        final_response = self.client.models.generate_content(**final_params)
        return final_response.text