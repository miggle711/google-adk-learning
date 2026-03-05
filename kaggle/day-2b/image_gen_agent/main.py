import asyncio
from image_gen_agent import run_image_gen_workflow


async def main():
    # Scenario 1: Single image (auto-approved, no confirmation needed)
    print("\n" + "=" * 60)
    print("SCENARIO 1: Single image request (auto-approved)")
    print("=" * 60)
    await run_image_gen_workflow(
        query="Generate 1 image of a sunset over mountains",
        auto_approve=True
    )

    # Scenario 2: Bulk images (approved)
    print("\n" + "=" * 60)
    print("SCENARIO 2: Bulk image request (approved)")
    print("=" * 60)
    await run_image_gen_workflow(
        query="Generate 3 images of cute cats",
        auto_approve=True
    )

    # Scenario 3: Bulk images (rejected)
    print("\n" + "=" * 60)
    print("SCENARIO 3: Bulk image request (rejected)")
    print("=" * 60)
    await run_image_gen_workflow(
        query="Generate 4 images of dogs playing",
        auto_approve=False
    )


if __name__ == "__main__":
    asyncio.run(main())
