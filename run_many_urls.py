import classifier
import pandas as pd

reports_to_classify = pd.DataFrame([])
data = pd.read_excel(open('urls_to_reports_to_classifiy.xlsx','rb'))
reports_to_classify = pd.DataFrame(data)

all_results_df = pd.DataFrame([])
# all_results_df = [classifier.main(urls) for urls in reports_to_classify['URLs']]

all_results_df = classifier.main('https://www.ptil.no/tilsyn/tilsynsrapporter/2020/equinor--oseberg-c--barrierestyring/')

