#!/usr/bin/env python3
import subprocess
import json
import sys

def test_mcp_server():
    """Test the MCP server by sending a simple request"""
    
    # Start the server process
    process = subprocess.Popen(
        ['fastmcp', 'run', 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send an initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        # Send the initialize request
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read the initialize response
        response = process.stdout.readline()
        if response:
            print("Initialize response:", response.strip())
            response_data = json.loads(response)
            
            if "result" in response_data:
                print("✅ Server initialized successfully!")
                
                # Now request the list of tools
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                process.stdin.write(json.dumps(tools_request) + '\n')
                process.stdin.flush()
                
                # Read the tools response
                tools_response = process.stdout.readline()
                if tools_response:
                    print("Tools response:", tools_response.strip())
                    tools_data = json.loads(tools_response)
                    
                    if "result" in tools_data:
                        tools = tools_data["result"].get("tools", [])
                        print(f"Available tools ({len(tools)}):")
                        for tool in tools:
                            print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    else:
                        print("❌ Error getting tools:", tools_data.get("error", "Unknown error"))
                else:
                    print("❌ No tools response from server")
            else:
                print("❌ Initialization failed:", response_data.get("error", "Unknown error"))
        else:
            print("❌ No response from server")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_server()