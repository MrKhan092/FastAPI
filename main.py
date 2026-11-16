
from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse

from pydantic import BaseModel,Field, computed_field
from typing import Annotated, Literal, Optional
import json
app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi= round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


        
def load_data():
    with open('patients.json') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)
        

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

@app.post('/create')
def add_patient(patient:Patient):
    data=load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail='patient id already exists')

    pdata=patient.model_dump(exclude=['id'])
    data[patient.id]=pdata

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient created successfully'})


@app.put('/update/{patient_id}')
def update_patient(patient_id,patient:PatientUpdate):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404 , detail='Patient_id not found')


    existing_data=data[patient_id]

    received_data=patient.model_dump(exclude_unset=True)

    for key , value in received_data.items():
        existing_data[key]=value

    height = existing_data['height']
    weight = existing_data['weight']

    bmi = round(weight / (height ** 2), 2)

    if bmi < 18.5:
        verdict = 'Underweight'
    elif bmi < 25:
        verdict = 'Normal'
    elif bmi < 30:
        verdict = 'Overweight'
    else:
        verdict = 'Obese'

    existing_data['bmi'] = bmi
    existing_data['verdict'] = verdict

    data[patient_id]=existing_data 
    save_data(data)

    return JSONResponse(status_code=200 , content='patient updated successfully')


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    if patient_id not in load_data():
        raise HTTPException(status_code=404,detail='patient not found') 

    data=load_data()
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient deleted successfully'})