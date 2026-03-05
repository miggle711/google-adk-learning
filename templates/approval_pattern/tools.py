"""
Template for tools that require human-in-the-loop approval.

HOW TO USE:
1. Replace `expensive_operation` with your actual tool function
2. Define your approval condition in `needs_approval()`
3. Implement `do_the_actual_work()` with your business logic
4. Update the hint message in `request_confirmation()`
"""

from google.adk.tools.tool_context import ToolContext


# =============================================================================
# CUSTOMIZE: Define when approval is needed
# =============================================================================
def needs_approval(amount: float, threshold: float) -> bool:
    """Determine if the operation needs approval.

    Examples:
        - amount > threshold (cost-based)
        - num_items > limit (bulk operations)
        - is_sensitive_data (data access)
        - is_destructive_action (deletions)
    """
    return amount > threshold


# =============================================================================
# CUSTOMIZE: Your actual business logic
# =============================================================================
async def do_the_actual_work(params: dict) -> dict:
    """Execute the actual operation after approval.

    Replace this with your real implementation:
        - API calls
        - Database operations
        - External service calls
        - File operations
    """
    # Placeholder - replace with actual implementation
    return {
        "result": f"Processed with params: {params}",
        "data": []
    }


# =============================================================================
# TEMPLATE: Tool with approval pattern (customize the parameters and logic)
# =============================================================================
async def expensive_operation(
    description: str,
    amount: float,
    tool_context: ToolContext  # ADK injects this automatically
) -> dict:
    """Template tool that requires approval for expensive operations.

    Scenarios:
    1. Below threshold: Auto-approved, executes immediately
    2. Above threshold, first call: Pauses for approval, returns "pending"
    3. Above threshold, approved: Executes operation, returns "approved"
    4. Above threshold, rejected: Returns "rejected" without executing

    Args:
        description (str): Description of the operation.
        amount (float): The cost/size/impact of the operation.
        tool_context (ToolContext): ADK-provided context for approval workflow.

    Returns:
        dict: Status and result of the operation.
    """
    APPROVAL_THRESHOLD = 100.0  # CUSTOMIZE: Your threshold

    # 1. AUTO-APPROVE: Below threshold
    if not needs_approval(amount, APPROVAL_THRESHOLD):
        result = await do_the_actual_work({"description": description, "amount": amount})
        return {
            "status": "success",
            "result": result
        }

    # ABOVE THRESHOLD: Requires confirmation

    # 2. REQUEST CONFIRMATION (first call - tool_confirmation is None)
    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            # CUSTOMIZE: Your approval message
            hint=f"This operation costs ${amount:.2f} which exceeds the ${APPROVAL_THRESHOLD:.2f} threshold. Proceed?",
            payload={
                "description": description,
                "amount": amount
            }
        )
        return {
            "status": "pending",
            "message": f"Operation requires approval. Amount: ${amount:.2f}"
        }

    # 3. APPROVED: User confirmed
    if tool_context.tool_confirmation.confirmed:
        result = await do_the_actual_work({"description": description, "amount": amount})
        return {
            "status": "approved",
            "result": result
        }

    # 4. REJECTED: User denied
    else:
        return {
            "status": "rejected",
            "message": "Operation was denied by user."
        }
