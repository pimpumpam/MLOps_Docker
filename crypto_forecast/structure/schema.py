import json

PANDAS_TYPES = {
    "string": "object",
    "integer": "int32",
    "float": "float32",
    "double": "float64",
    "boolean": "bool",
    "date": "datetime64[ns]",
    "timestamp": "datetime64[ns]"
}

class SchemaManager:

    def __init__(self, filepath):

        self.filepath = filepath
        self.schema = self.__load_schema__()


    def __load_schema__(self):
        """
        스키마 JSON 파일 불러오기

        """
        with open(self.filepath, 'r') as f:
            return json.load(f)

    
    def __convert_to_pandas_dtype__(self):
        """
        스키마 파일의 컬럼 별 타입 값을 Pandas DataFrame의 데이터 타입으로 변환

        """

        for col in self.schema["schema"].get("columns", []):

            if col["type"] in PANDAS_TYPES:
                col["type"] = PANDAS_TYPES[col["type"]]
            else:
                raise ValueError(f"\'{col['type']}\' is unsupported data type for pandas.DataFrame")
            

    def build_schema(self, task):
        """
        데이터 타입 처리를 위한 스키마 정보. QC 단계에서 활용 가능.

        Args:
            task(str): 스키마 정보를 적용할 task 명.

        Returns:
            fields(list): 컬럼명, 컬럼타입, Null허용여부로 구성된 정보

        """
        fields = []

        for col in self.schema["schema"].get("columns", []):
            if ("task" in col) and (task in col["task"]):
                field = {
                    "name": col["name"],
                    "dataType": PANDAS_TYPES[col["type"]],
                    "nullable": col["nullable"]
                }

            fields.append(field)

        return fields
    

    def get_columns_by_filter(self, **kwargs):

        """
        Schema 파일에 정의 된 조건에 따른 컬럼 선별

        Args:
            kwarg:
                type(str): 데이터 타입
                nullable(bool): Null 허용 여부
                is_categorical(bool): 범주형 변수 여부
                is_feature(bool): feature 컬럼 여부
                is_label(bool): label 컬럼 여부
                usage(str): 컬럼 활용 정보
                task(str, list): 컬럼 사용 태스크 정보

        Returns:
            columns(list): 조건에 맞는 컬럼을 선별한 리스트

        """

        columns = []

        for col in self.schema["schema"].get("columns", []):

            matched = True

            for key, val in kwargs.items():
                if key == "tasks":
                    if isinstance(val, str):
                        val = [val]

                    if not set(val).issubset(set(col["tasks"])):
                        matched = False
                        break
                
                else:
                    if col[key] != val:
                        matched = False
                        break
            
            if matched:
                columns.append(col["name"].lower())

        return columns