from inegi_api_ import inegi_api_
import requests
import json
import pandas as pd 
import numpy as np
import datetime
import pytest 
from src.key_INEGI import token

def economic_info(category, token, historic_data=False):
    if historic_data is False: 
        data='true'
    else: 
        data='false'
    url=f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{category}/es/0700/{data}/BIE/2.0/{token}?type=json'
    print(url)
    response = requests.get(url)
    print(response.status_code)
    if response.status_code== 200:
        data=response.json()
    
        df1 =pd.DataFrame(data['Series']).explode('OBSERVATIONS')
        df=pd.json_normalize(json.loads(df1.to_json(orient='records')))
        return df 
    else:
        raise ConnectionError('proper connection with the API was not established, check the order of the arguments')

def test_economic_info(): 
    actual= economic_info(628208, token, historic_data=False)
    expected = economic_info(628208, token, historic_data=False)
    assert actual == expected
    #beavis.assert_pd_equality(actual, expected)

def Socio_demographics_info(category, token, historic_data=False):    
    if historic_data is False: 
        data='true'
    else: 
        data='false'
    url=f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{category}/es/0700/{data}/BISE/2.0/{token}?type=json'
    response = requests.get(url)
    if response.status_code== 200:
        data=response.json()
        df1 = pd.DataFrame(data['Series']).explode('OBSERVATIONS')
        df=pd.json_normalize(json.loads(df1.to_json(orient='records')))
        return df 
    else:
        raise ConnectionError( 'proper connection with the API was not established, check the order of the arguments')

def test_Socio_demographics_info():
    actual= economic_info(6200032080, token, historic_data=False)
    expected = economic_info(6200032080, token, historic_data=False)
    assert actual == expected
    #beavis.assert_pd_equality(actual, expected) 

    
def poverty_line_actualization(token, poverty_line, start_date, end_date): 
    url=f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/628208/es/0700/false/BIE/2.0/{token}?type=json'
    response = requests.get(url)
    if response.status_code== 200:
        data=response.json()
        df1 = pd.DataFrame(data['Series']).explode('OBSERVATIONS')
        df=pd.json_normalize(json.loads(df1.to_json(orient='records')))
        end_year=int(end_date[:4])
        end_month=int(end_date[5:7])
        start_year=int(start_date[:4])
        start_month=int(start_date[5:7])
        df['year'] = pd.DatetimeIndex(df['OBSERVATIONS.TIME_PERIOD']).year
        df['month'] = pd.DatetimeIndex(df['OBSERVATIONS.TIME_PERIOD']).month
        df['OBSERVATIONS.OBS_VALUE']=pd.to_numeric(df['OBSERVATIONS.OBS_VALUE']) 
        for x,j in df.iterrows():
            values=[]
            a=df[df['year']>=start_year]
            b=a[a['month']== start_month]            
            for j in b['OBSERVATIONS.OBS_VALUE']:
                values.append(j)
                final_values=[1+(x/100) for x in values]
                result=1
                for y in final_values: 
                    result= result*y
                    return poverty_line*result
    else: 
        raise ConnectionError( 'proper connection with the API was not established')


def test_poverty_line_actualization(): 
    actual= economic_info(token, 3542.14,'2021/1','2022/12')
    expected = economic_info(token, 3542.14,'2021/1','2022/12')
    assert actual == expected
    #beavis.assert_pd_equality(actual, expected)


def work_force_poverty(token, poverty_line, start_date, end_date, working_days=22, min_salary=172.87):
    df1=Socio_demographics_info(1002000001, token, historic_data=False)
    population=pd.to_numeric(df1['OBSERVATIONS.OBS_VALUE'][0])
    df2=Socio_demographics_info(6200032080, token, historic_data=False)
    pop_minwage=pd.to_numeric(df2['OBSERVATIONS.OBS_VALUE'][0])
    last_update= df2['LASTUPDATE'][0]
    monthly_income= working_days*min_salary
    poverty_line=poverty_line_actualization(token, poverty_line, start_date, end_date)
    proportion=(pop_minwage/population)*100
    print(f'The proportion of Mexicans earining minimum salary, as of {last_update} is {proportion}% ')
    if monthly_income<poverty_line:
        
        print(f'The proportion of Mexican who has a salary below the selected poverty line was{(pop_minwage/population)*100}% ')
    else: 
        print('With the specified data, the minimum salary is able to cover necesities in the poverty line')


def test_work_force_poverty(): 
    actual=work_force_poverty(token, 3900, '2021/11', '2022/11', working_days=22, min_salary=500)
    expected=work_force_poverty(token, 3900, '2021/11', '2022/11', working_days=22, min_salary=500)
    assert actual == expected
