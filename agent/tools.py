"""
Tools for the AutoStream LeadFlux Agent.

Contains the mock lead capture function that simulates
sending lead data to a CRM or database.
"""


def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Simulate capturing a lead in a CRM system.

    In production, this would call an external API (e.g., HubSpot,
    Salesforce) or write to a database. For this demo, it prints
    the captured information and returns a confirmation.

    Args:
        name: The lead's full name.
        email: The lead's email address.
        platform: The lead's primary content creation platform.

    Returns:
        A confirmation string.
    """
    print(f"\n{'='*50}")
    print(f"  [SUCCESS] LEAD CAPTURED SUCCESSFULLY")
    print(f"{'='*50}")
    print(f"  Name:     {name}")
    print(f"  Email:    {email}")
    print(f"  Platform: {platform}")
    print(f"{'='*50}\n")

    return f"Lead captured successfully: {name}, {email}, {platform}"
