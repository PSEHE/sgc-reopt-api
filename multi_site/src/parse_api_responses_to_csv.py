import csv
import pandas as pd
from collections import OrderedDict


def get_nested_output(key, resp, obj=None):

    if '|' in key:
        obj = key[:key.index('|')]
        val = key[key.index('|') + 1:]

        return resp['outputs']['Scenario']['Site'][obj][val]

    else:
        site = resp['outputs']['Scenario']['Site']

        for d in site.values():

            if isinstance(d,dict):
                if key in d.keys():
                    return d[key]

    return None


def parse_responses_to_csv_with_template(csv_template, responses, output_csv, input_csv=None, n_custom_columns=0):
    """

    :param csv_template: path to csv file with headers for output fields, and rows for input scenarios
    :param responses: list of dicts, each dict is API response for input scenario (in same order is input csv)
    :param output_csv: str, path to output csv that parser writes summary to.
    :param input_csv: str, path to input csv to copy custom columns from
    :param n_custom_columns: number of custom columns to copy from input scenarios csv to output_csv
        (columns that are not modified by script)
    :return: None (writes results to csv).
    """

    results = OrderedDict()

    # open template and initialize results dict with custom cols filled in and black output columns
    with open(csv_template, 'r') as f:
        reader = csv.reader(f)
        outputs = next(reader)  # names of parameters to pull out of responses and put in output_csv

    if input_csv is not None:
        # copy and paste custom columns' values

        with open(input_csv, 'r') as f:
            reader = csv.reader(f)
            hdr = next(reader)
            for i in range(n_custom_columns):
                results[hdr[i]] = []

            for row in reader:
                for i in range(n_custom_columns):
                    results[hdr[i]].append(row[i])

    for output in outputs:
        results[output] = []

    for i, resp in enumerate(responses):

        for output in outputs:
            results[output].append(get_nested_output(output, resp))

    df = pd.DataFrame.from_dict(results)
    df.index = df.iloc[:, 0]
    df.drop(df.columns[0], axis=1, inplace=True)
    df.to_csv(output_csv)


if __name__ == '__main__':
    """
    Test script for response parser
    """
    import os
    import json
    resp1 = json.load(open(os.path.join('..', 'outputs', 'site3-No-PV.json'), 'rb'))
    resp2 = json.load(open(os.path.join('..', 'outputs', 'site3-With-PV.json'), 'rb'))

    parse_responses_to_csv_with_template(os.path.join('..', 'outputs', 'results_template.csv'), responses=[resp1, resp2],
                                         output_csv='test_results.csv', input_csv=os.path.join('..', 'inputs', 'scenarios.csv'),
                                         n_custom_columns=2)

