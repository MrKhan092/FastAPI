
from fastapi import FastAPI,Path,HTTPException,Query
import json
app=FastAPI()

def load_data():
    with open('patients.json') as f:
        data = json.load(f)
    return data

@app.get("/")
def hello():
    return{'message':'Patient Management System'}   

@app.get('/about')
def about():
    return {'message':'A fully functional API to manage your patient records'}


@app.get('/view')
def view():
    data=load_data()
    return data


@app.get('/patient/{patient_id}')
def view_patient(patient_id:str=Path(...,description='ID of the patient in the Db' ,example='P008')):
    data=load_data()
    if patient_id in data:
        return data[patient_id]

    raise HTTPException(status_code=404,detail='patient not found')


@app.get('/sort')
def sort_patient(sort_by:str=Query(description='sort on basis of height , weight or bmi'),order:str=Query('asc',description='sort in asc or desc order')):
    values=['height','weight','bmi']
    if sort_by not in values:
        raise HTTPException(status_code=400 , detail=f'the value {sort_by} provided is not valid')

    value_order=['asc','desc']
    if order not in value_order:
        raise HTTPException(status_code=404,detail=f'the value {order} is not valid ')

    data=load_data()
    sort_order=False
    if order =='desc':
        sort_order=True 

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    return sorted_data
