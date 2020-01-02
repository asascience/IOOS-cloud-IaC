#!/usr/bin/env python3

from prefect import Flow, task, Parameter

@task
def sayhi(name):
  print("Hi! My name is ", name)

with Flow("Test paramater") as flow:
  name = Parameter('name')

  sayhi(name=name)

flow.run(parameters=dict(name='Patrick'))

