import json
import math
import boto3
from enum import Enum

class Constant(Enum):
    A = 1.40 * 10**-3
    B = 2.37 * 10**-4
    C = 9.90 * 10**-8

def getSns():
    sns = boto3.client("sns", region_name="us-east-1")
    return sns

def createSnsResponseTemperatureCritical(sns):
    response = sns.publish(TopicArn="arn:aws:sns:us-east-1:058459655457:sns_sensor_temperature",
                           Message="TEMPERATURE_CRITICAL",
                           Subject="Notification AWS SNS")
    return response

def initDynamoDbAndGetTable():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('sensors')
    return table

def isBrokenSensor(table, sensorId):
    response = table.get_item(Key={'sensor_id': sensorId})
    if 'Item' in response:
        return True
    return False

def calculateTemparatureInCelsius(resistance):
    
    if resistance == 0:
        return {
            'statusCode': 406,
            'error': 'VALUE_OUT_OF_RANGE'
        }

    temperatureInKelvins = 1/(Constant.A.value+ 
                              Constant.B.value*math.log(resistance)+ 
                              Constant.C.value*(math.log(resistance)**3)) 
    temperatureInCelsius = temperatureInKelvins - 273.15
    return temperatureInCelsius

def lambda_handler(event, context):
    table = initDynamoDbAndGetTable()
    sensorId = event['sensor_id']
    resistance = event['value']

    if isBrokenSensor(table, sensorId):
        return {
            'statusCode': 406,
            'error': 'VALUE_OUT_OF_RANGE'
        }

    temperature = calculateTemparatureInCelsius(resistance)

    if resistance < 1 or resistance > 20*10**3:
        table.put_item(Item={
            'sensor_id': sensorId,
            'broken': True
        })
        return {
            'statusCode': 406,
            'error': 'VALUE_OUT_OF_RANGE'
        } 
    elif temperature < 20:
        return {
            'statusCode': 200,
            'status': 'TEMPERATURE_TOO_LOW'
        }
    elif temperature >= 20 and temperature < 100:
        return {
            'statusCode': 200,
            'status': 'OK'
        }
    elif temperature >= 100 and temperature < 250:
        return {
            'statusCode': 200,
            'status': 'TEMPERATURE_TOO_HIGH'
        }
    elif temperature >= 250:
        sns = getSns()
        snsResponse = createSnsResponseTemperatureCritical(sns)
        return {
            'statusCode': 200,
            'status': 'TEMPERATURE_CRITICAL'
        }