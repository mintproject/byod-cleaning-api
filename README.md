# B-Clean

B-Clean is a library built to support `Bring Your Own Data (BYOD)` project. B-Clean provides different functionalities to detect outliers in tabular datasets and suggest possible transformations to clean the data.

Outlier Detection
-----------------


### Background
We define and detect three different types of outliers as follows:
* Global outliers: values that rarely appear in the real-world data. 
* Local outliers: values that are different from other values in the same attribute. 
* Null outliers: values that have no meaning

### Usage
1. Use the outlier detection service [here](http://data-trans.mint.isi.edu:10011/detect)
2. Submit a `POST` request with data as follows:
    ```json
    {
        'table':{
            'column1': ['val1', 'val2'],
            'column2': ['val3', 'val4']
        }
    }
    ```
3. Receive response in the form:
    ```json
        {
            'table':{
                'column1': ['[[[val1]]]', 'val2'],
                'column2': ['val3', 'val4']
            }
        }
    ```
    where outliers are annotated as `[[[value]]]`

An example of outlier detection method is shown in our demo notebook [here](ocde_demo.ipynb).

Data Transformation
-------------------
Work in progress. 
