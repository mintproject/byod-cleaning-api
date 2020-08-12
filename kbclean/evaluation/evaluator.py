import csv
from functools import reduce
from logging import log
from pathlib import Path

import numpy as np
import pandas as pd
import rapidjson as json
from sklearn.metrics import classification_report, confusion_matrix
from loguru import logger
from kbclean.utils.data.helpers import diff_dfs, equal


class Evaluator:
    def __init__(self):
        pass

    def read_dataset(self, data_path):
        data_path = Path(data_path)

        raw_path = data_path / "raw"
        cleaned_path = data_path / "cleaned"

        name2raw = {}
        name2cleaned = {}
        name2groundtruth = {}

        for file_path in list(raw_path.iterdir()):
            name = file_path.name
            name2raw[name] = (
                pd.read_csv(raw_path / name, keep_default_na=False, dtype=str)
                .head(10000)
                .applymap(lambda x: x[:100])
            )
            name2cleaned[name] = (
                pd.read_csv(cleaned_path / name, keep_default_na=False, dtype=str)
                .head(10000)
                .applymap(lambda x: x[:100])
            )

            name2groundtruth[name] = name2raw[name] == name2cleaned[name]
        return name2raw, name2cleaned, name2groundtruth

    def average_report(self, *reports):
        report_list = list()
        for report in reports:
            splited = [" ".join(x.split()) for x in report.split("\n\n")]
            header = [x for x in splited[0].split(" ")]
            data = np.array(splited[1].split(" ")).reshape(-1, len(header) + 1)
            data = np.delete(data, 0, 1).astype(float)
            avg_total = (
                np.array([x for x in splited[2].split(" ")][3:])
                .astype(float)
                .reshape(-1, len(header))
            )
            df = pd.DataFrame(np.concatenate((data, avg_total)), columns=header)
            report_list.append(df)
        res = reduce(lambda x, y: x.add(y, fill_value=0), report_list) / len(
            report_list
        )
        return res.rename(index={res.index[-1]: "avg / total"})

    def debug(self, raw_df, cleaned_df, groundtruth_df, result_df):
        def get_result(x):
            return result_df.loc[x["id"], x["col"]]

        fn_df = diff_dfs(raw_df, cleaned_df)
        fn_df["prediction"] = fn_df.apply(get_result, axis=1)
        fn_df = fn_df[fn_df["prediction"] == True]

        diff_mask = equal(groundtruth_df, result_df)
        ne_stacked = diff_mask.stack()
        changed = ne_stacked[ne_stacked]
        changed.index.names = ["id", "col"]
        difference_locations = np.where(diff_mask)
        changed_from = raw_df.values[difference_locations]
        changed_to = cleaned_df.values[difference_locations]
        fp_df = pd.DataFrame({"from": changed_from, "to": changed_to}, index=changed.index)
        fp_df["id"] = fp_df.index.get_level_values("id")
        fp_df["col"] = fp_df.index.get_level_values("col")
        fp_df["prediction"] = fp_df.apply(get_result, axis=1)
        fp_df = fp_df[fp_df["prediction"] == False]

        concat_df = pd.concat([fp_df, fn_df], ignore_index=True)
        return concat_df

    def evaluate_df(self, detector, raw_df, cleaned_df, groundtruth_df):
        detected_df = detector.detect(raw_df)

        flat_result = detected_df.stack().values.tolist()
        ground_truth = groundtruth_df.stack().values.tolist()

        report = pd.DataFrame(
            classification_report(ground_truth, flat_result, output_dict=True)
        ).transpose()

        matrix = pd.DataFrame(
            confusion_matrix(ground_truth, flat_result, labels=[True, False]),
            columns=["True", "False"],
        )

        debug = self.debug(raw_df, cleaned_df, groundtruth_df, detected_df)

        return report, matrix, debug

    def fake_ievaluate_df(self, detector, raw_df, cleaned_df, groundtruth_df):
        detected_df = detector.fake_idetect(raw_df, cleaned_df)

        flat_result = detected_df.stack().values.tolist()
        ground_truth = groundtruth_df.stack().values.tolist()

        report = pd.DataFrame(
            classification_report(ground_truth, flat_result, output_dict=True)
        ).transpose()

        matrix = pd.DataFrame(
            confusion_matrix(ground_truth, flat_result, labels=[True, False]),
            columns=["True", "False"],
        )

        debug = self.debug(raw_df, cleaned_df, groundtruth_df, detected_df)
        logger.info("\n" + str(report))
        return report, matrix, debug

    def evaluate(self, detector, dataset, output_path=None):
        name2raw, name2cleaned, name2groundtruth = self.read_dataset(dataset)

        name2report = {}

        report_path = Path(output_path) / "report"
        debug_path = Path(output_path) / "debug"
        matrix_path = Path(output_path) / "matrix"

        report_path.mkdir(parents=True, exist_ok=True)
        debug_path.mkdir(parents=True, exist_ok=True)
        matrix_path.mkdir(parents=True, exist_ok=True)

        for name in name2raw.keys():
            logger.info(f"Evaluating on {name}...")

            report, matrix, debug = self.evaluate_df(
                detector, name2raw[name], name2cleaned[name], name2groundtruth[name]
            )

            report["index"] = report.index
            report.to_csv(report_path / f"{name}", index=False, quoting=csv.QUOTE_ALL)

            debug.to_csv(debug_path / f"{name}", index=False, quoting=csv.QUOTE_ALL)

            matrix["index"] = pd.Series(["True", "False"])
            matrix.to_csv(matrix_path / f"{name}", index=None, quoting=csv.QUOTE_ALL)

            name2report[name] = report

        return name2report

    def fake_ievaluate(self, detector, dataset, output_path=None):
        name2raw, name2cleaned, name2groundtruth = self.read_dataset(dataset)

        name2report = {}

        report_path = Path(output_path) / "report"
        debug_path = Path(output_path) / "debug"
        matrix_path = Path(output_path) / "matrix"

        report_path.mkdir(parents=True, exist_ok=True)
        debug_path.mkdir(parents=True, exist_ok=True)
        matrix_path.mkdir(parents=True, exist_ok=True)

        for name in name2raw.keys():
            logger.info(f"Evaluating on {name}...")

            report, matrix, debug = self.fake_ievaluate_df(
                detector, name2raw[name], name2cleaned[name], name2groundtruth[name]
            )

            report["index"] = report.index
            report.to_csv(report_path / f"{name}", index=False, quoting=csv.QUOTE_ALL)

            debug.to_csv(debug_path / f"{name}", index=False, quoting=csv.QUOTE_ALL)

            matrix["index"] = pd.Series(["True", "False"])
            matrix.to_csv(matrix_path / f"{name}", index=None, quoting=csv.QUOTE_ALL)

            name2report[name] = report

        return name2report