from backend.analysis_pipeline import run_analysis


SALES_FILE = "data/sales.csv"
FEEDBACK_FILE = "data/customer_feedback.csv"
REGION = "North"
DATE = "2025-06-01"


def test_role_based_entitlements():

    executive = run_analysis(
        SALES_FILE,
        FEEDBACK_FILE,
        REGION,
        DATE,
        "Executive"
    )

    manager = run_analysis(
        SALES_FILE,
        FEEDBACK_FILE,
        REGION,
        DATE,
        "Manager"
    )

    analyst = run_analysis(
        SALES_FILE,
        FEEDBACK_FILE,
        REGION,
        DATE,
        "Analyst"
    )

    # --------------------------------------------------
    # Executive: restricted/high-level information
    # --------------------------------------------------

    assert executive["persona"] == "executive"

    for driver in executive["role_drivers"]:
        assert "driver" in driver
        assert "percentage_change" in driver
        assert "driver_score" in driver

        # Statistical details must not be exposed
        assert "correlation" not in driver
        assert "correlation_p_value" not in driver
        assert "historical_observations" not in driver

    # --------------------------------------------------
    # Manager: operational information + evidence
    # --------------------------------------------------

    assert manager["persona"] == "manager"

    for driver in manager["role_drivers"]:
        assert "driver" in driver
        assert "previous_value" in driver
        assert "current_value" in driver
        assert "percentage_change" in driver
        assert "driver_score" in driver
        assert "supporting_evidence" in driver

        # Manager should not receive full statistical detail
        assert "correlation_p_value" not in driver
        assert "historical_observations" not in driver

    # --------------------------------------------------
    # Analyst: full analytical information
    # --------------------------------------------------

    assert analyst["persona"] == "analyst"

    for driver in analyst["role_drivers"]:
        assert "driver" in driver
        assert "previous_value" in driver
        assert "current_value" in driver
        assert "percentage_change" in driver
        assert "correlation" in driver
        assert "correlation_p_value" in driver
        assert "historical_observations" in driver
        assert "correlation_significance" in driver

    # --------------------------------------------------
    # Entitlement ordering
    # --------------------------------------------------

    assert len(executive["role_drivers"]) <= 3
    assert len(manager["role_drivers"]) <= 5

    print("========== SECURITY / ENTITLEMENT TEST ==========")
    print("Executive: restricted business-level output")
    print("Manager  : operational drivers + evidence")
    print("Analyst  : full statistical analysis")
    print("TEST PASSED")


if __name__ == "__main__":
    test_role_based_entitlements()
    