import requests
import json
import pandas as pd 
import numpy as np
import datetime

def economic_info(category, token, historic_data=False):
    """
    A function created to take in spesific inputs and return a Pandas data fram with the desired information held in INEGI's bank of economic information (BIE)

    Parameters
    ----------
    category : int: must be the corresponsing number according to INEGI's catalouge for the desired category you want to make the api request for
    
    historic_data: bool: set as False, this returns the historical series by defaul. True value return most current value only. 
    
    token: str: unique token obtained by the user to make api request 

    Returns
    -------
	A new pandas data frame for the corresponding arguments in the function.

    Example
    --------
    >>> economic_info('category', historic_data=False, key)

        >>> category = 628208

        >>> historic_data = True

        >>> key = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'


    |INDICADOR      | OBSERVATIONS.TIME_PERIOD  | OBSERVATIONS.OBS_VALUE      |			
    |---------------|---------------------------|-----------------------------|
    | 0 |628208     |2022/11                    |7.8                          |
    |  1|628208     |2022/10                    |8.41                         | 
    |  2|628208     |2022/09                    |8.7                          |  

    """
    #transform the value from the argumen to meet the api call
    
    if historic_data is False: 
        data='true'
    else: 
        data='false'
    
    #create a url for the call with the spesific arguments provided by the user
    url=f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{category}/es/0700/{data}/BIE/2.0/{token}?type=json'
    print(url)
    #save as an object the get from the url
    response = requests.get(url)

    #print out the responsre of the status for the API call 
    print(response.status_code)
    
    if response.status_code== 200:
        data=response.json()
    
        #use expand method to acess the neste items of the api call
        df1 = pd.DataFrame(data['Series']).explode('OBSERVATIONS')

        #Consolidate the data frame and assign it to a variable
        df=pd.json_normalize(json.loads(df1.to_json(orient='records')))

        return df 
    
    else:
        raise ConnectionError('proper connection with the API was not established, check the order of the arguments')


def Socio_demographics_info(category, token, historic_data=False):
    """
    A function created to take in spesific inputs and return a Pandas data fram with the desired socio-demographic information captured by INEGI. 

    Parameters
    ----------
    category : int: must be the corresponsing number according to INEGI's catalouge for the desired category you want to make the api request for
    
    historic_data: bool: set as False, this returns the historical series by defaul. True value return most current value only. 
    
    token: str: unique token obtained by the user to make api request 

    Returns
    -------
	A new pandas data frame for the corresponding arguments in the function.

    Example
    --------
    >>>  ('category', historic_data=False, key)

        >>> category = 1007000012

        >>> historic_data = False

        >>> key = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'


    |INDICADOR      | OBSERVATIONS.TIME_PERIOD  | OBSERVATIONS.OBS_VALUE      | 			
    |---------------|---------------------------|-----------------------------|
    | 0 |1007000012 |1994                       |98183.00000000000000000000	  | 
    |  1|1007000012 |1995                       |113250.00000000000000000000  |  
    |  2|1007000012 |1996                       |99005.00000000000000000000	  |  
    
    """
    #transform the value from the argumen to meet the api call
    
    if historic_data is False: 
        data='true'
    else: 
        data='false'

    #create a url for the call with the spesific arguments provided by the user
    url=f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{category}/es/0700/{data}/BISE/2.0/{token}?type=json'

    #save as an object the get from the url
    response = requests.get(url)
    
    if response.status_code== 200:
        data=response.json()
    
        #use expand method to acess the neste items of the api call
        df1 = pd.DataFrame(data['Series']).explode('OBSERVATIONS')

        #Consolidate the data frame and assign it to a variable
        df=pd.json_normalize(json.loads(df1.to_json(orient='records')))

        return df 
    
    else:
        raise ConnectionError( 'proper connection with the API was not established, check the order of the arguments')

    
def poverty_line_actualization(token, poverty_line, start_date, end_date): 
    """
    This function is meant to take any poverty line, or mexican peso ammount and covert it ,using monthly intra year inflation data, into an ammount in the desired time.  

    Parameters
    ----------
    token: str: unique token obtained by the user to make api request 

    poverty_line: int: mexian peso ammount of poverty line

    start_date: str: start date format-> year/month

    end_date:str: end date format-> year/month

    Returns
    -------
	A peso ammount equivalnet to the poverty line converted from the start date to the end dates given

    Example
    --------
    >>> poverty_line_actualization(token,3542.14,'2021/1','2022/12')

        >>> token = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

        >>> poverty_line= 3542.14

        >>> start_date= '2021/1'

        >>> end_date= '2022/12'
    
    3792.569298
    """
    #API call for intramonthly inflation
    url=f'https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/628208/es/0700/false/BIE/2.0/{token}?type=json'
    response = requests.get(url)

    if response.status_code== 200:

        data=response.json()
    
        df1 = pd.DataFrame(data['Series']).explode('OBSERVATIONS')

        #Consolidate the data frame and assign it to a variable
        df=pd.json_normalize(json.loads(df1.to_json(orient='records')))
        
        #create target reference date for the inputs in the function 
        end_year=int(end_date[:4])
        end_month=int(end_date[5:7])
        start_year=int(start_date[:4])
        start_month=int(start_date[5:7])

        #Doing data transformation for the calculation of the poverty line
        df['year'] = pd.DatetimeIndex(df['OBSERVATIONS.TIME_PERIOD']).year
        df['month'] = pd.DatetimeIndex(df['OBSERVATIONS.TIME_PERIOD']).month
        df['OBSERVATIONS.OBS_VALUE']=pd.to_numeric(df['OBSERVATIONS.OBS_VALUE']) 
        
        #Check the values for each month for the years withing the given dates 
        for x,j in df.iterrows():
            values=[]
            a=df[df['year']>=start_year]
            b=a[a['month']== start_month]
            
            #extracting the values for the month within the given dates 
            for j in b['OBSERVATIONS.OBS_VALUE']:
                values.append(j)
                final_values=[1+(x/100) for x in values]
                result=1
                
                #multiplying the values of inflation times the basket to return the updated bascket
                for y in final_values: 
                    result= result*y
                    return poverty_line*result
    
    else: 
        raise ConnectionError( 'proper connection with the API was not established')


def work_force_poverty(token, poverty_line, start_date, end_date, working_days=22, min_salary=172.87):
    """
    This function is meant to calculate the working population that is under the poverty line by earning minimum wage.   
    The arguments can be changes to reflect different poverty lines, working days in a month and minimum salary. 

    Parameters
    ----------
    token: str: unique token obtained by the user to make api request 

    poverty_line: int: mexian peso ammount of poverty line

    start_date: str: start date format-> year/month

    end_date: str: end date format-> year/month

    working_days: int: working days in the month for the desired calculation. 

    min_salary: int: set as 172.87, this value can be adjusted when the new meassurements are updated to reflect the increase in the minimum wage
    
    Returns
    -------
	A proportion corresponding to the ammount of people who work and earn a minimum wage but are not able to afford the minimum necesities basket

    Example
    --------
    >>> work_force_poverty(token, 3900, '2022/11', '2022/12', working_days=22, min_salary=500)

        >>> token = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

        >>> poverty_line= 3900

        >>> start_date= '2021/11'

        >>> end_date= '2022/12'

        >>> working_days=22
        
        >>> min_salary=500

    The proportion of Mexicans earining minimum salary, as of 23/11/2022 is 14.523654129162638% 
    With the specified data, the minimum salary is able to cover necesities in the poverty line
    
    """
    #get latest population data
    df1=Socio_demographics_info(1002000001, token, historic_data=False)
    
    #extract must updated prpulation data
    population=pd.to_numeric(df1['OBSERVATIONS.OBS_VALUE'][0])
   
    df2=Socio_demographics_info(6200032080, token, historic_data=False)
    pop_minwage=pd.to_numeric(df2['OBSERVATIONS.OBS_VALUE'][0])
    last_update= df2['LASTUPDATE'][0]

    # we calculate the monthly income based on the min salary and monthy work days provided
    monthly_income= working_days*min_salary
    # caling in the poverty line function to calculate the desired poverty line
    poverty_line=poverty_line_actualization(token, poverty_line, start_date, end_date)

    proportion=(pop_minwage/population)*100

    print(f'The proportion of Mexicans earining minimum salary, as of {last_update} is {proportion}% ')
    
    #filter for instances in whihc the imput might yiled a salary below or above the poverty line
    if monthly_income<poverty_line:
        
        print(f'The proportion of Mexican who has a salary below the selected poverty line was{(pop_minwage/population)*100}% ')
    else: 
        print('With the specified data, the minimum salary is able to cover necesities in the poverty line')

