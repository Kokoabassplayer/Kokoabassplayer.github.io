import pandas as pd
from pandas_profiling import ProfileReport
import os

class DataProfiler:
    def __init__(self, filepath):
        """
        Initialize the DataProfiler with the path to the CSV file.
        """
        self.filepath = filepath
        self.df = None

    def load_csv(self):
        """
        Load data from the CSV file.
        """
        try:
            self.df = pd.read_csv(self.filepath)
            print("CSV file loaded successfully.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")

    def generate_profile(self):
        """
        Generate the Pandas Profiling report and save it as an HTML file.
        The report name is automatically generated from the CSV file name.
        """
        if self.df is not None:
            try:
                base_name = os.path.splitext(os.path.basename(self.filepath))[0]
                report_name = f"{base_name}_data_profile_report.html"
                profile = ProfileReport(self.df, title='Pandas Profiling Report', explorative=True)
                profile.to_file(report_name)
                print(f"Profile report saved as {report_name}.")
            except Exception as e:
                print(f"Error generating profile report: {e}")
        else:
            print("Dataframe is empty. Load the CSV file first.")

# Usage example
profiler = DataProfiler(r'C:\Users\nuttapong.but\Downloads\Learn Pulse - resonses Extract_Extract.csv')
profiler.load_csv()
profiler.generate_profile()
