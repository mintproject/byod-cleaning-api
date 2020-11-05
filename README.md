# B-Clean

B-Clean is a library built to support `Bring Your Own Data (BYOD)` project. B-Clean provides different functionalities to detect outliers in tabular datasets and suggest possible transformations to clean the data.

## Roadmap
- [x] Statistical outlier detection
- [ ] Few-shot outlier detection
    - [x] Baseline model ([HoloDetect](https://arxiv.org/pdf/1904.02285.pdf))
    - [ ] Data-driven model (LSTM)
    - [ ] Improve performance
    - [ ] Decrease number of examples
- [ ] Active learning outlier detection
    - [ ] Automatic suggestion based on statistical model
    - [ ] Policy-based active learning model
- [ ] Data transformation


Outlier Detection
-----------------


### Background
We define and detect three different types of outliers as follows:
* Global outliers: values that rarely appear in the real-world data. 
* Local outliers: values that are different from other values in the same attribute. 
* Null outliers: values that have no meaning

### Usage
1. Install and activate  conda environment 
```
conda env create -f environment.yml
conda activate byod
```
2. For evaluation on demo dataset, run command
```
PYTHONPATH=.:$PYTHONPATH python kbclean/experiments/error_detection.py evaluate --data_path demo/data  --method lstm  -i -k 2 -e 5
```
