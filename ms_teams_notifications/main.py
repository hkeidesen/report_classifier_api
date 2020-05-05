import re
import logging

import pandas as pd

from monitoring import report

logging.basicConfig(level=logging.DEBUG)


def submit_basic_report_to_teams():

    # Let's create some random variables:
    expectation_suite_name: str = "VesselInfo Failure Suite"
    failed_str: str = "{'columns': 'VesselID', 'expectation_type': 'expect_values_not_to_be_null'}"

    # Report the status to the monitoring service:
    report(
        "great_expectations",
        f"**Failure**: Data `{expectation_suite_name}` expectations were" " validated, but with **critical** failure.",
        f"The following expectations were not met:\n`{failed_str}`\n" "**The pipeline was STOPPED**.",
        is_info_message=True,
    )


def submit_dataframe_report_to_teams():

    # Create a random dataframe:
    results = pd.DataFrame(data={"my_first_column": [1, 2, 3, 4, 5], "my_second_column": [8, 7, 6, 5, 4]})

    # Do some pre-MS-Teams-Connector-Card formatting:
    re_results = results.to_string(index=False)
    # (\n\n is the teams-way of doing newline, many spaces preceding a line forces preformat (direct write to screen))
    re_results = re.sub("\n", "\n\n", re_results,)

    report(
        "IHS Statistics Engine",
        "Results from the simulated run of IHS on historical data with CV-models",
        f"Table of results (full output in Azure Files): \n\n   {re_results}",
        is_info_message=True,
    )


if __name__ == "__main__":
    logging.info("Submitting test-data to MS Teams webhook...")
    submit_basic_report_to_teams()
    submit_dataframe_report_to_teams()
