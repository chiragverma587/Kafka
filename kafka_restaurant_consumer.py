import argparse

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
import pandas as pd
import json
import csv


API_KEY = 'JW5RWTWGIYOBEL3N'
ENDPOINT_SCHEMA_URL  = 'https://psrc-mw731.us-east-2.aws.confluent.cloud'
API_SECRET_KEY = 'tXcQymxxHkKNKkG7hQkWW/EfHJWYgJQVUWQzgWrAFbdyHEmmf5376wRu4sca/i7G'
BOOTSTRAP_SERVER = 'pkc-6ojv2.us-west4.gcp.confluent.cloud:9092'
SECURITY_PROTOCOL = 'SASL_SSL'
SSL_MACHENISM = 'PLAIN'
SCHEMA_REGISTRY_API_KEY = '2LLACZNDO3G2KLEQ'
SCHEMA_REGISTRY_API_SECRET = '/BkfdfGnhEZzJ6cSy1xPvPzw+qFo9PZU88u67DbydKmG6Wd5C7dFGQEnmvzL9eIx'
schema_id = "100011"

def sasl_conf():

    sasl_conf = {'sasl.mechanism': SSL_MACHENISM,
                 # Set to SASL_SSL to enable TLS support.
                #  'security.protocol': 'SASL_PLAINTEXT'}
                'bootstrap.servers':BOOTSTRAP_SERVER,
                'security.protocol': SECURITY_PROTOCOL,
                'sasl.username': API_KEY,
                'sasl.password': API_SECRET_KEY
                }
    return sasl_conf



def schema_config():
    return {'url':ENDPOINT_SCHEMA_URL,
    
    'basic.auth.user.info':f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}"

    }


class Order:   
    def __init__(self,record:dict):
        for k,v in record.items():
            setattr(self,k,v)
        
        self.record=record
   
    @staticmethod
    def dict_to_order(data:dict,ctx):
        return Order(record=data)

    def __str__(self):
        return f"{self.record}"


def main(topic):

    schema_registry_conf = schema_config()
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    schema_str1 = schema_registry_client.get_schema(schema_id).schema_str
    json_deserializer = JSONDeserializer(schema_str1,
                                         from_dict=Order.dict_to_order)

    consumer_conf = sasl_conf()
    consumer_conf.update({
                     'group.id': 'group1',
                     'auto.offset.reset': "earliest"})

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    count=0
    df=pd.DataFrame()
    mydict=[]
    columns=['order_number', 'order_date', 'item_name', 'quantity', 'product_price', 'total_products']
    
    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            order = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))

            if order is not None:
                count=count+1
                mydict.append(order.__dict__)

                print(order.__dict__)
        except KeyboardInterrupt:
            break
    print(count)
    print(type(order.__dict__))
    
    filename = "/Users/ADMIN/Desktop/Kafka/Output.csv"
    with open(filename, 'w') as csvfile: 
      writer = csv.DictWriter(csvfile, fieldnames = columns,extrasaction='ignore', delimiter = ',') 
      writer.writeheader()  
      writer.writerows(mydict) 


    # df.to_csv("Output.csv")
    consumer.close()

main("restaurant_topic")
