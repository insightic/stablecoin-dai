import os
import yaml
import logging
from datetime import datetime
import pyinsightic
from yaml.scanner import ScannerError
from pyinsightic.social.helper import stablecoin_mapping
import log_config

# Configure logging at the start
log_config.setup_logging()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisRunner:
    def __init__(self, analysis_function, check_condition, subdir="stablecoin"):
        self.analysis_function = analysis_function
        self.check_condition = check_condition
        self.subdir = subdir  # New attribute to override directory

    def __call__(self, base_dir, data):
        project_dir = os.path.join(base_dir, self.subdir)  # Join base_dir with subdir
        if not self.check_condition(data):
            logger.info(
                f"Required conditions not met for {self.analysis_function.__name__} in {project_dir}. Skipping analysis."
            )
            return
        logger.info(f"Running {self.analysis_function.__name__} for {project_dir}")
        analysis = self.analysis_function(project_dir=project_dir)
        analysis.run_analysis()


# Condition check functions
def check_stablecoin(data):
    return any(
        item["title"] == "Technological Details"
        for item in data.get("security_and_compliance", [])
        if "Token launch" in (blockchain["title"] for blockchain in item.get("value", []))
    )


def check_linkedin(data):
    return "linkedin" in data.get("links", {}) and data["links"]["linkedin"] not in [
        None,
        "",
    ]


def check_twitter(data):
    return "twitter" in data.get("links", {}) and data["links"]["twitter"] not in [
        None,
        "",
    ]


def check_security_assessment(data):
    return bool(data.get("security_report"))


def check_smart_contract_validator(data):
    whitepaper_uri = data.get("whitepaper", "")
    code_uri = ""

    # Extracting code URI using the provided logic
    for item in data.get("security_and_compliance", []):
        if item["title"] == "Technological Details":
            for dic in item.get("value", []):
                if dic["title"] == "Smart Contract":
                    code_uri = dic["value"]
                    break
            if code_uri:  # Exit the loop early if code_uri is found
                break

    # Ensure both whitepaper and code URI exist and are not empty/None
    return bool(whitepaper_uri and code_uri)


def check_sosovalue(data):
    # will run for all projects
    return True


def check_sosovalue_news(data):
    if data["name"].lower() in stablecoin_mapping.keys():
        return True
    return False


# AnalysisRunner instances for each analysis
analyses = [
    # AnalysisRunner(pyinsightic.Stablecoin, check_stablecoin),
    # AnalysisRunner(pyinsightic.ZANAnalysis, check_stablecoin),
    #     AnalysisRunner(pyinsightic.Linkedin, check_linkedin),
    #     AnalysisRunner(pyinsightic.Twitter, check_twitter),
    #     AnalysisRunner(pyinsightic.SosoValue, check_sosovalue),
    #     AnalysisRunner(pyinsightic.SmartContractValidator, check_smart_contract_validator),
    #     AnalysisRunner(pyinsightic.SecurityAssessment, check_security_assessment),
    #     AnalysisRunner(pyinsightic.SosovalueNewsCrawler, check_sosovalue_news),
    #     AnalysisRunner(pyinsightic.DefiLlamaNewsCrawler, check_sosovalue),
    AnalysisRunner(pyinsightic.CoinGeckoCrawler, check_sosovalue, "cex"),
    AnalysisRunner(pyinsightic.CoinMarketCapCrawler, check_sosovalue, "cex"),
]


def main(test_folders=None):
    base_dir = "."  # Define the base directory for operations
    if test_folders is None:
        test_folders = [os.path.join(base_dir, "stablecoin"), os.path.join(base_dir, "cex")]

    for folder in test_folders:
        for dir in os.listdir(folder):
            dir_path = os.path.join(folder, dir)
            if os.path.isdir(dir_path) and os.path.exists(os.path.join(dir_path, "data.yml")):
                logger.info(f"Processing folder: {dir}")
                data_path = os.path.join(dir_path, "data.yml")
                try:
                    with open(data_path, "r") as file:
                        content = file.read()
                        fixed_content = content.replace("\t", "    ")
                        data = yaml.safe_load(fixed_content)
                except ScannerError:
                    logger.error("Invalid yaml format")
                    continue  # Continue to next directory instead of returning
                for analysis in analyses:
                    analysis(folder, data)  # Pass the modified folder path


if __name__ == "__main__":
    # main()
    # os.chdir("stablecoin")  # change directory for local test
    main()
