import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .calculator import Calculator
from .cycletime import CycleTimeCalculator
from .utils import set_chart_style

class AgeingWIPChartCalculator(Calculator):
    """Draw an ageing WIP chart
    """

    def is_enabled(self):
        return self.settings['ageing_wip_chart']

    def run(self):
        cycle_data = self.get_result(CycleTimeCalculator)
        cycle_names = [s['name'] for s in self.settings['cycle']]

        start_column = self.settings['committed_column'] or cycle_names[1]
        end_column = self.settings['final_column'] or cycle_names[-2]
        done_column = self.settings['done_column'] or cycle_names[-1]
        
        today = pd.Timestamp.now().date()

        # remove items that are done
        ageing_wip_data = cycle_data[pd.isnull(cycle_data[done_column])].copy()

        # calculate current status and age for each item
        def extract_status(row):
            last_valid = row.last_valid_index()
            if last_valid is None:
                return np.NaN
            return last_valid

        def extract_age(row):
            started = row[start_column]
            if pd.isnull(started):
                return np.NaN
            return (today - started.date()).days

        ageing_wip_data['status'] = ageing_wip_data.apply(extract_status, axis=1)
        ageing_wip_data['age'] = ageing_wip_data.apply(extract_age, axis=1)

        # remove blank rows
        ageing_wip_data.dropna(how='any', inplace=True, subset=['status', 'age'])

        # reorder columns so we get key, summary, status, age, and then all the cycle stages
        ageing_wip_data = pd.concat((
            ageing_wip_data[['key', 'summary', 'status', 'age']],
            ageing_wip_data.ix[:, start_column:end_column]
        ), axis=1)

        return ageing_wip_data
    
    def write(self):
        output_file = self.settings['ageing_wip_chart']
        chart_data = self.get_result()

        if len(chart_data.index) < 0:
            print("WARNING: Cannot draw ageing WIP chart with no completed items")
        else:

            fig, ax = plt.subplots()
            
            if self.settings['ageing_wip_chart_title']:
                ax.set_title(self.settings['ageing_wip_chart_title'])

            sns.swarmplot(x='status', y='age', order=chart_data.columns[4:], data=chart_data, ax=ax)

            ax.set_xlabel("Status")
            ax.set_ylabel("Age (days)")

            ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=90)

            _, top = ax.get_ylim()
            ax.set_ylim(0, top)

            set_chart_style('whitegrid')

            fig = ax.get_figure()
            fig.savefig(output_file, bbox_inches='tight', dpi=300)
