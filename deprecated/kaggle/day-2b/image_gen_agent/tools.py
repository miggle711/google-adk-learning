from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.adk.tools.tool_context import ToolContext
import os

async def generate_images(
    prompt: str,
    num_images: int,
    tool_context: ToolContext # ADK provides this automatically, no need to pass it in manually
) -> dict:
    """Generates images based on the given prompt and number of images.

    Scenarios:
    1. Single image (num_images <= 1): Auto-approved, generates immediately
    2. Bulk request, first call: Pauses for user approval, returns "pending"
    3. Bulk request, approved: Generates images, returns "approved"
    4. Bulk request, rejected: Returns "rejected" without generating

    Args:
        prompt (str): The text prompt for image generation.
        num_images (int): The number of images to generate.
        tool_context (ToolContext): The context for the tool execution.

    Returns:
        dict: The response containing the status and generated images.
    """
    NUM_IMAGE_GENERATION_LIMIT = 1

    # 1. AUTO-APPROVE SINGLE IMAGE GENERATION
    if num_images <= NUM_IMAGE_GENERATION_LIMIT:
        # we can automatically generate the image without user approval
        # connect to the image generation mcp

        result = await _mcp_image_generation(prompt, num_images)
        return {
            "status": "success",
            "images": result.get("images", [])
        }
    
    # BULK IMAGE GENERATION REQUIRES CONFIRMATION
    
    # 2. REQUEST CONFIRMATION FOR BULK IMAGE GENERATION
    if not tool_context.tool_confirmation: # tool_confirmation is None on first call
        tool_context.request_confirmation(  # request user confirmation
            hint=f"You are requesting to generate {num_images} images which exceeds the limit of {NUM_IMAGE_GENERATION_LIMIT}. Do you want to proceed?",
            payload={
                "prompt": prompt,
                "num_images": num_images
            }
        )
        return {
            "status": "pending",
            "message": f"Generating {num_images} images requires user approval. Confirmation requested."
        }
    # 3. APPROVED BULK IMAGE GENERATION
    if tool_context.tool_confirmation.confirmed:
        # User has confirmed, proceed with image generation
        result = await _mcp_image_generation(
            prompt=prompt,
            num_images=num_images
        )
        return {
            "status": "approved",
            "images": result.get("images", [])
        }
    # 4. REJECTED BULK IMAGE GENERATION
    else:
        # User has denied the request
        return {
            "status": "rejected",
            "message": "Bulk image generation request was denied by the user."
        }

async def _mcp_image_generation(
    prompt: str,
    num_images: int,
) -> dict:
    
    # we're not using McpToolset since this is just an auxiliary function called by the tool
    # and not a tool itself
    image_gen_connection = StdioServerParameters(
        command="npx",
        args=["-y", "@gongrzhe/image-gen-server"], # -y to auto install
        env={"REPLICATE_API_TOKEN": os.environ.get("REPLICATE_API_TOKEN")}
    )

    # Using Gongrzhe's image generation server: (https://github.com/GongRzhe/Image-Generation-MCP-Server)
        # prompt (required): Text description of the image to generate
        # seed (optional): Random seed for reproducible generation
        # aspect_ratio (optional): Image aspect ratio (default: "1:1")
        # output_format (optional): Output format - "webp", "jpg", or "png" (default: "webp")
        # num_outputs (optional): Number of images to generate (1-4, default: 1)
    

    # We will use the mcp connection pattern here: https://modelcontextprotocol.io/docs/develop/build-client#server-connection-management
    async with stdio_client(image_gen_connection) as (read, write): 
        # runs npx -y @gongrzhe/image-gen-server as a subprocess
        # read stream is for reading responses from the server (stdout from the subprocess/server)
        # write stream is for sending requests to the server (stdin to the subprocess/server)

        async with ClientSession(read, write) as session:
            # slaps a mcp protocol on top of the raw read/write streams
                # standarises json format for requests and responses (JSON-RPC 2.0: https://medium.com/@dan.avila7/why-model-context-protocol-uses-json-rpc-64d466112338)

            await session.initialize() # handshake with the server 
            result = await session.call_tool("generate_image", 
                                {"prompt": prompt, 
                                "num_outputs": num_images}
                            ) # call the tool on the server with the given parameters
            return {
                "success": not result.is_error, # not an error is a success lolz
                "images": result.content
            }


    



