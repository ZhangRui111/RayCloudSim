from core.base_scenario import BaseScenario

ROOT_PATH = 'eval/benchmarks/Pakistan/data'


class Scenario(BaseScenario):
    
    def __init__(self, config_file, flag):
        """
        :param flag: '25N50E', '50N50E', '100N150E' or 'MilanCityCenter'
        """
        assert flag in ['Tuple30K', 'Tuple50K', 'Tuple100K'], \
            f"Invalid flag={flag}"
        super().__init__(config_file)
        
        # # Load the test dataset (not recommended)
        # data = pd.read_csv(f"{ROOT_PATH}/{flag}/testset.csv")
        # self.testset = list(data.iloc[:].values)
    
    def status(self):
        pass
