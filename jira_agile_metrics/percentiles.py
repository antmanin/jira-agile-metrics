from .calculator import Calculator
from .cycletime import CycleTimeCalculator
from .utils import get_extension

class PercentilesCalculator(Calculator):
    """Build percentiles for `cycle_time` in cycle data as a DataFrame
    """

    def is_enabled(self):
        return self.settings['percentiles_data']

    def run(self):
        cycle_data = self.get_result(CycleTimeCalculator)
        return cycle_data['cycle_time'].dropna().quantile(self.settings['quantiles'])

    def write(self):
        output_file = self.settings['percentiles_data']
        output_extension = get_extension(output_file)

        file_data = self.get_result()

        if output_extension == '.json':
            file_data.to_json(output_file, date_format='iso')
        elif output_extension == '.xlsx':
            file_data.to_frame(name='percentiles').to_excel(output_file, 'Percentiles', header=True)
        else:
            file_data.to_csv(output_file, header=True)
