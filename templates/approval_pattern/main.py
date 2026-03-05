"""
Example usage of the approval pattern template.

Run with: python -m templates.approval_pattern.main
"""

import asyncio
from .workflow import run_approval_workflow, extract_results


async def main():
    # Scenario 1: Below threshold (auto-approved, no confirmation needed)
    print("\n" + "=" * 60)
    print("SCENARIO 1: Below threshold (auto-approved)")
    print("=" * 60)
    result = await run_approval_workflow(
        query="Process an order worth $50",
        auto_approve=True  # Won't matter - below threshold
    )
    print(f"Needed approval: {result['needed_approval']}")
    for r in extract_results(result['events']):
        print(f"  {r['type']}: {r['content']}")

    # Scenario 2: Above threshold (approved)
    print("\n" + "=" * 60)
    print("SCENARIO 2: Above threshold (approved)")
    print("=" * 60)
    result = await run_approval_workflow(
        query="Process an order worth $500",
        auto_approve=True
    )
    print(f"Needed approval: {result['needed_approval']}")
    print(f"Status: {result['status']}")
    for r in extract_results(result['events']):
        print(f"  {r['type']}: {r['content']}")

    # Scenario 3: Above threshold (rejected)
    print("\n" + "=" * 60)
    print("SCENARIO 3: Above threshold (rejected)")
    print("=" * 60)
    result = await run_approval_workflow(
        query="Process an order worth $1000",
        auto_approve=False
    )
    print(f"Needed approval: {result['needed_approval']}")
    print(f"Status: {result['status']}")
    for r in extract_results(result['events']):
        print(f"  {r['type']}: {r['content']}")


if __name__ == "__main__":
    asyncio.run(main())
